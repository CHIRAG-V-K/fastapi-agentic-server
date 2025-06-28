import multiprocessing
multiprocessing.set_start_method("spawn", force=True)  # Use spawn to avoid OSError on Windows

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
# from transformerAgent import ai_agent_stream, ai_agent_response  # for AI agent using transformers
from textGenerationAgent import ai_agent_stream, ai_agent_response  # FOR AI agent using text generation
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify a list of allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return {"Hello": "Agent"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


# --- AI agent streaming endpoint ---
@app.post("/chat")
async def ai_stream(request: Request):
    payload = await request.json()
    print("Received payload:", payload)  # Print the payload to the server console

    message = payload.get("message")
    conversation_id = payload.get("conversation_id", "default")
    stream = payload.get("stream", False)

    if stream:
        # Pass the message from the payload to the agent for streaming
        return StreamingResponse(ai_agent_stream(message), media_type="text/event-stream")
    else:
        # If not streaming, get the full response and return as JSON
        response_content = await ai_agent_response(message)
        return {
            "response": response_content,
            "conversation_id": conversation_id
        }