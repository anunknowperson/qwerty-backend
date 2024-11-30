import logging

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

from rag.pipeline import stream_model_response

app = FastAPI()


logging.basicConfig(level=logging.DEBUG)


@app.post("/query")
async def query(request: Request):
    try:
        data = await request.json()
        user_input = data.get("messages")[0].get("content")

        logging.debug(f"Received input: {user_input}")

        async def stream_response():
            try:
                logging.debug("Starting stream response")
                async for token in stream_model_response(user_input):
                    logging.debug(f"Yielding token: {token}")
                    yield f"data: {token}\n\n"
                logging.debug("Finished streaming tokens")
                yield "data: [DONE]\n\n"
            except Exception as e:
                logging.error(f"Error in stream_response: {e}")
                yield f"data: Error: {str(e)}\n\n"

        return StreamingResponse(
            stream_response(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Transfer-Encoding": "chunked",
            },
        )
    except Exception as e:
        logging.error(f"Error in query endpoint: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, loop="asyncio")
