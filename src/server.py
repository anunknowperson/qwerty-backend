import json
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import asyncio
import aiohttp

app = FastAPI()

@app.post("/query")
async def query(request: Request):
    data = await request.json()
    user_input = data.get("messages")[0].get("content")
    api_url = "http://37.194.195.213:35411/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
    }
    payload = {
        "model": "saiga",
        "messages": [
            {
                "role": "user",
                "content": user_input
            }
        ],
        "stream": True,
        "max_tokens": data.get("max_tokens", 100)
    }

    async def stream_response():
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, headers=headers, json=payload) as response:
                if response.status == 200:
                    async for line in response.content:
                        if line.startswith(b"data:") and line != b'\r\n':
                            decoded_line = line.decode('utf-8')
                            yield decoded_line
                            # await asyncio.sleep(0)  # Allow other tasks to run
                else:
                    yield f"data: Error: {response.status}\n\n"

    return StreamingResponse(
        stream_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Transfer-Encoding": "chunked",
        }
    )

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        loop="asyncio"
    )