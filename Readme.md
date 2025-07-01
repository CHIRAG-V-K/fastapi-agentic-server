# FastAPI Agentic Server

## Setup Instructions

### 1. Clone the repository

```sh
git clone https://github.com/<your-username>/fastapi-agentic-server.git
cd fastapi-agentic-server
```

### 2. Create a virtual environment (Windows)

```sh
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install dependencies

```sh
pip install -r requirements.txt
```

### 4. Run the server

```sh
uvicorn main:app --reload
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The server will be available at [http://localhost:8000](http://localhost:8000).

---

## Example `requirements.txt`

If you don’t have a `requirements.txt`, create one with:

```
fastapi
uvicorn
```

Add any other dependencies your project needs.

---

## Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /chat` - AI agent streaming endpoint
