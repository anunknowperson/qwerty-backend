import logging
from typing import Literal

from langchain_core.documents import Document
from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.graph import START, MessagesState, StateGraph

from rag.models import model
from rag.vector_store import vector_store


class State(MessagesState):
    question: str
    theme: Literal["knowledge", "gov", "contacts", "none"]
    context: list[Document]
    answer: str


def get_theme(state: State):
    system_message_content = (
        "Прочитай следующий запрос."
        "Выбери, к какой теме из нижеперечисленных он относится."
        "Твой ответ должен содержать единственное число - номер пункта."
        "Список тем:"
        "1. Поиск контактов и номеров телефонов, основанный на Базе Контактов Санкт-Петербурга. "
        "При любом упоминании контактов или номеров всегда отвечай этой темой."
        "2. Поиск релевантной информации, ответ на вопрос основанный на Базе Знаний Санкт-Петербурга."
        "3. Поиск информации на сайте администрации Санкт-Петербурга"
        "4. Ни одна из вышеперечисленных тем."
    )

    logging.info(f"Message: {state["messages"][-1]}")
    prompt = [SystemMessage(system_message_content), state["messages"][-1]]
    response = model.invoke(prompt)
    logging.info(f"get_theme response: {response.content}")
    if "1" in response.content:
        return {"theme": "contacts"}

    if "2" in response.content:
        return {"theme": "knowledge"}

    if "3" in response.content:
        return {"theme": "gov"}

    return {"theme": "none"}


def retrieve(state: State):
    retrieved_docs = vector_store.similarity_search(state["messages"][-1].content, k=6, theme=state["theme"])
    logging.info(f"Retrieved {len(retrieved_docs)} documents")
    logging.info("".join(f"{i}: {doc.page_content}\n" for i, doc in enumerate(retrieved_docs)))

    return {"context": retrieved_docs}


def generate(state: State):

    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    system_message_content = (
        "Ты - умный и полезный ассистент. "
        "Используй следующий контекст, который может тебе помочь с ответом на вопрос. "
        "Если ты не знаешь ответ, то скажи что ответ тебе не известен."
        "\n\n"
        f"{docs_content}"
    )
    conversation_messages = [
        message for message in state["messages"] if message.type in ("human", "system") or message.type == "ai"
    ]

    prompt = [SystemMessage(system_message_content), *conversation_messages]
    response = model.invoke(prompt)

    return {"answer": response.content}


graph_builder = StateGraph(State).add_sequence([get_theme, retrieve, generate])
graph_builder.add_edge(START, "get_theme")
graph = graph_builder.compile()


def stream_model_response(messages: list[BaseMessage]):
    for step, *_ in graph.stream(messages, stream_mode="messages"):
        yield step.content
