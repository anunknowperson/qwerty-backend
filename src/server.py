import logging

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from rag.pipeline import stream_model_response
import asyncio
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

logging.basicConfig(level=logging.DEBUG)


@app.post("/query")
async def query(request: Request):
    try:
        data = await request.json()
        # user_input = data.get("messages")[0].get("content")

        # logging.debug(f"Received input: {user_input}")

        print(data.get("messages"))

        async def stream_response():
            
                logging.debug("Starting stream response")
                res = ""
                for token in stream_model_response({'messages': data.get("messages")}):
                    logging.debug(f"Yielding token: {token}")
                    await asyncio.sleep(0.001)
                    res += token
                    yield f"data: {token}\n\n"

                    #if "get_weather()" in res:
                    #    break

                #yield f"data:  Weather: +22 \n\n"
                #res=""
                #for token in stream_model_response({'messages': [{'role' : 'user', 'content':user_input}, {'role' : 'tool', 'content':'Weather: +22'}]}):
                #    logging.debug(f"Yielding token: {token}")
                #    await asyncio.sleep(0.001)
                #    res += token
                #    yield f"data: {token}\n\n"#

                #    if "get_weather()" in res:
                #        break

                logging.debug("Finished streaming tokens")
                yield "data: [DONE]\n\n"
            

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

    uvicorn.run(app, host="0.0.0.0", port=35420, loop="asyncio")