from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import Tool
from datetime import datetime
import os

# For Google Calendar API
from googleapiclient.discovery import build
from google.oauth2 import service_account

# Wikipedia search tool using LangChain
wikipedia = WikipediaAPIWrapper()
wikipedia_tool = Tool(
    name="Wikipedia Search",
    func=wikipedia.run,
    description="Useful for searching Wikipedia for factual information."
)

# DuckDuckGo search tool using LangChain
duckduckgo_tool = DuckDuckGoSearchRun()

# Google Calendar event creation tool
def create_google_calendar_event(title: str, date: str, time: str, description: str = "") -> str:
    """
    Create an event in Google Calendar using a service account.
    Requires a service account JSON key and calendar ID in environment variables.
    """
    try:
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_CALENDAR_SERVICE_ACCOUNT")
        CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")

        if not SERVICE_ACCOUNT_FILE or not CALENDAR_ID:
            return "Google Calendar credentials not set in environment variables."

        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        service = build('calendar', 'v3', credentials=credentials)

        event_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': event_datetime.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': (event_datetime.replace(minute=event_datetime.minute + 30)).isoformat(),
                'timeZone': 'UTC',
            },
        }
        created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        return f"Event '{title}' created: {created_event.get('htmlLink')}"
    except Exception as e:
        return f"Google Calendar event creation error: {str(e)}"

calendar_tool = Tool(
    name="Google Calendar Event Creator",
    func=create_google_calendar_event,
    description="Creates a Google Calendar event. Requires title, date (YYYY-MM-DD), time (HH:MM), and optional description."
)

# List of tools to add to your agent
agent_tools = [
    wikipedia_tool,
    duckduckgo_tool,
    calendar_tool
]
