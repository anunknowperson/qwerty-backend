import logging

from langchain_core.documents import Document
from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.graph import START, MessagesState, StateGraph

from rag.models import model
from rag.vector_store import vector_store


class State(MessagesState):
    question: str
    context: list[Document]
    answer: str


def retrieve(state: State):

    retrieved_docs = vector_store.similarity_search(state["messages"][-1].content, k=10)
    logging.info(f"Retrieved {len(retrieved_docs)} documents")
    logging.info("".join(f"{i}: {doc.page_content}\n" for i, doc in enumerate(retrieved_docs)))

    return {"context": retrieved_docs}


def generate(state: State):

    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    system_message_content = (
        "Ты - Сайга, умный и полезный ассистент. "
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


graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()


def stream_model_response(messages: list[BaseMessage]):
    for step, *_ in graph.stream(messages, stream_mode="messages"):
        yield step.content
