from langchain_core.documents import Document
from langgraph.graph import START, MessagesState, StateGraph

from rag.models import model
from rag.prompt import prompt
from rag.vector_store import vector_store


class State(MessagesState):
    question: str
    context: list[Document]
    answer: str


def retrieve(state: State):
    retrieved_docs = vector_store.similarity_search(state["question"])
    return {"context": retrieved_docs}


def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = model.invoke(messages)
    return {"answer": response.content}


graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()


async def stream_model_response(question: str):
    async for step, *_ in graph.astream({"question": question}, stream_mode="messages"):
        yield step.content
