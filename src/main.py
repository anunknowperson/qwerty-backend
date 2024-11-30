import asyncio
import logging

from langchain_core.messages import HumanMessage, AIMessage

from rag.pipeline import stream_model_response

logging.basicConfig(level=logging.INFO)


async def main():
    messages = [{"role" : "user", "content":  "Я боб"}]
    query = input("Введите вопрос: ")

    messages += [HumanMessage(query)]

    while query != "-1":
        messages += [HumanMessage(query)]
        res = ""
        for token in stream_model_response({"messages": messages}):
            print(token, end='')
            res += token

        messages += [AIMessage(res)]

        query = input("Введите вопрос: ")
    print()
    query = input("Введите вопрос: ")
    messages += [HumanMessage(query)]


if __name__ == "__main__":
    asyncio.run(main())
