from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from agent_1 import ai_agent_stream  # Assuming ai_agent_stream is defined in agent-1.py
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
    return StreamingResponse(ai_agent_stream(), media_type="text/event-stream")