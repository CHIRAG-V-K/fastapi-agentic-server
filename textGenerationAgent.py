import os
import asyncio
from huggingface_hub import InferenceClient
from dotenv import load_dotenv  # Add this import
from tools import agent_tools  # Import your tools
load_dotenv()  # Load variables from .env

finalModel = "meta-llama/Llama-3.1-8B-Instruct"  # Default model
#  model="nvidia/Llama3-ChatQA-1.5-70B"

client = InferenceClient(
    provider="fireworks-ai",
    api_key=os.getenv("HF_TOKEN"),  # Use os.getenv to avoid KeyError if not set
)

async def ai_agent_stream(message="What is the capital of France?"):
    # Run the Hugging Face streaming in a thread to avoid blocking the event loop
    loop = asyncio.get_event_loop()
    def sync_stream():
        return client.chat.completions.create(
           
            model=finalModel,
            messages=[{"role": "user", "content": message}],
            stream=True,
        )
    stream = await loop.run_in_executor(None, sync_stream)
    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            yield f"{content}"

async def ai_agent_response(message="What is the capital of France?"):
    loop = asyncio.get_event_loop()
    def sync_response():
        return client.chat.completions.create(
            model=finalModel,
            messages=[{"role": "user", "content": message}],
            stream=False,
        )
    response = await loop.run_in_executor(None, sync_response)
    return {"tools": [tool.name for tool in agent_tools], "result": response.choices[0].message.content}