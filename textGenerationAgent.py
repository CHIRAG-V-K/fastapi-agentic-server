import os
import asyncio
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
from tools import agent_tools

load_dotenv()

finalModel = "meta-llama/Llama-3.1-8B-Instruct"

client = InferenceClient(
    provider="fireworks-ai",
    api_key=os.getenv("HF_TOKEN"),
)

def build_messages(context, message):
    """
    Build the messages list for the LLM API from context and the new user message.
    """
    messages = []
    if context and isinstance(context, list):
        for turn in context:
            role = turn.get("role", "user")
            content = turn.get("content", "")
            messages.append({"role": role, "content": content})
    # Add the new user message as the last turn
    messages.append({"role": "user", "content": message})
    return messages

async def ai_agent_stream(message="What is the capital of France?", context=None):
    loop = asyncio.get_event_loop()
    messages = build_messages(context, message)
    def sync_stream():
        return client.chat.completions.create(
            model=finalModel,
            messages=messages,
            stream=True,
        )
    stream = await loop.run_in_executor(None, sync_stream)
    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            yield f"{content}"

async def ai_agent_response(message="What is the capital of France?", context=None):
    loop = asyncio.get_event_loop()
    messages = build_messages(context, message)
    def sync_response():
        return client.chat.completions.create(
            model=finalModel,
            messages=messages,
            stream=False,
        )
    response = await loop.run_in_executor(None, sync_response)
    return {
        "tools": [tool.name for tool in agent_tools],
        "result": response.choices[0].message.content
    }