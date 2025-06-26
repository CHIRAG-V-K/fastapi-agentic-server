from typing import Optional, List
from pydantic import BaseModel

class WikipediaResult(BaseModel):
    type: str = "wikipedia"
    query: str
    summary: str

class DuckDuckGoResult(BaseModel):
    type: str = "duckduckgo"
    query: str
    snippet: str

class CalendarEventResult(BaseModel):
    type: str = "calendar_event"
    title: str
    date: str
    time: str
    description: Optional[str] = None
    event_link: Optional[str] = None
    status: str

# Example: You can use these classes to structure your tool outputs
# WikipediaResult(query="Python", summary="Python is a programming language.")
# DuckDuckGoResult(query="FastAPI", snippet="FastAPI is a modern web framework...")
# CalendarEventResult(title="Meeting", date="2024-07-01", time="15:00", status="created", event_link="https://...")