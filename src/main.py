import asyncio
import logging
from langchain_core.messages import HumanMessage, AIMessage
from rag.pipeline import stream_model_response
import re

logging.basicConfig(level=logging.INFO)

# Mock tool functions
async def get_weather():
    print("weather")
    return "Today's weather is sunny, 22°C"

async def search(query):
    print("search")
    return f"Search results for '{query}': Some example search results..."

tools = ["get_weather", "search"]

async def execute_tool_call(tool_call):
    # Extract function name and arguments
    match = re.match(r'(\w+)\((.*)\)', tool_call)
    if not match:
        return None
    
    function_name, args = match.groups()
    args = [arg.strip(' "\'') for arg in args.split(',') if arg]
    
    if function_name == "get_weather":
        return await get_weather()
    elif function_name == "search":
        return await search(args[0] if args else "")
    return None

async def main():
    messages = [{"role": "user", "content": "Я боб"}]
    query = input("Введите вопрос: ")

    messages += [HumanMessage(content=query)]

    while query != "-1":
        messages += [HumanMessage(content=query)]
        res = ""
        for token in stream_model_response({"messages": messages}):
            print(token, end='')
            res += token

        # Check for tool calls in the response
        tool_call_pattern = r'(get_weather\(\)|search\([^)]+\))'
        tool_calls = re.findall(tool_call_pattern, res)

        if tool_calls:
            for tool_call in tool_calls:
                # Execute the tool call
                tool_result = await execute_tool_call(tool_call)
                if tool_result:
                    # Add tool result to messages
                    messages += [AIMessage(content=res)]
                    messages += [AIMessage(content=f"Tool result: {tool_result}")]
                    
                    # Stream new response with tool results
                    res = ""
                    for token in stream_model_response({"messages": messages}):
                        print(token, end='')
                        res += token

        messages += [AIMessage(content=res)]
        query = input("\nВведите вопрос: ")

    print()
    query = input("Введите вопрос: ")
    messages += [HumanMessage(content=query)]


if __name__ == "__main__":
    asyncio.run(main())