import asyncio
import logging

from langchain_core.messages import HumanMessage

from rag.pipeline import stream_model_response

logging.basicConfig(level=logging.INFO)


async def main():
    messages = [HumanMessage("Меня зовут Боб")]
    query = input("Введите вопрос: ")
    messages += [HumanMessage(query)]

    while query != "-1":
        for token in stream_model_response({"messages": messages}):
            print(token, end="")
        print()
        query = input("Введите вопрос: ")
        messages += [HumanMessage(query)]


if __name__ == "__main__":
    asyncio.run(main())
