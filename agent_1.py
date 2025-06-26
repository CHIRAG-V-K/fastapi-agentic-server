import asyncio

async def ai_agent_stream():
    for i in range(10):
        yield f"data: AI agent response chunk {i}\n"
        await asyncio.sleep(1)