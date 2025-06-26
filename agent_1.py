import os
import asyncio
from huggingface_hub import InferenceClient
from dotenv import load_dotenv  # Add this import

load_dotenv()  # Load variables from .env

client = InferenceClient(
    provider="fireworks-ai",
    api_key=os.getenv("HF_TOKEN"),  # Use os.getenv to avoid KeyError if not set
)

async def ai_agent_stream(message="What is the capital of France?"):
    # Run the Hugging Face streaming in a thread to avoid blocking the event loop
    loop = asyncio.get_event_loop()
    def sync_stream():
        return client.chat.completions.create(
            model="meta-llama/Llama-3.1-8B-Instruct",
            messages=[{"role": "user", "content": message}],
            stream=True,
        )
    stream = await loop.run_in_executor(None, sync_stream)
    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            yield f"{content}\n"
            await asyncio.sleep(0)  # Yield control to the event loop

            

async def ai_agent_response(message="What is the capital of France?"):
    loop = asyncio.get_event_loop()
    def sync_response():
        return client.chat.completions.create(
            model="meta-llama/Llama-3.1-8B-Instruct",
            messages=[{"role": "user", "content": message}],
            stream=False,
        )
    response = await loop.run_in_executor(None, sync_response)
    return response.choices[0].message.content