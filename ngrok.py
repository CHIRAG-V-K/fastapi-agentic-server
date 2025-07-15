import multiprocessing
multiprocessing.set_start_method("spawn", force=True)  # Use spawn to avoid OSError on Windows

from pyngrok import ngrok,conf


import logging
import uvicorn
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import List, Optional
import json

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


def extract_file_content(file: UploadFile):
    import io
    filename = file.filename.lower()
    content = ""
    file_bytes = file.file.read()
    if filename.endswith(".pdf"):
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            content = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        except Exception as e:
            content = f"[PDF extraction error: {e}]"
    elif filename.endswith((".jpg", ".jpeg", ".png")):
        try:
            from PIL import Image
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            image = Image.open(io.BytesIO(file_bytes))
            ocr_text = pytesseract.image_to_string(image).strip()
            if ocr_text:
                content = f"[Image OCR text]: {ocr_text}"
            else:
                # If OCR fails or is empty, provide a generic description
                content = "[Image file attached: No readable text found. Please analyze the image content.]"
        except Exception as e:
            content = f"[Image OCR error: {e} | Please analyze the image content.]"
    elif filename.endswith(".txt"):
        try:
            content = file_bytes.decode("utf-8")
        except Exception as e:
            content = f"[Text file decode error: {e}]"
    elif filename.endswith((".csv", ".xlsx", ".xls")):
        try:
            import pandas as pd
            if filename.endswith(".csv"):
                df = pd.read_csv(io.BytesIO(file_bytes))
            else:
                df = pd.read_excel(io.BytesIO(file_bytes))
            content = df.to_csv(index=False)
        except Exception as e:
            content = f"[Spreadsheet extraction error: {e}]"
    else:
        content = "[Unsupported file type]"
    return {"filename": file.filename, "content": content}


# --- AI agent streaming endpoint ---
@app.post("/chat")
async def ai_stream(
    message: str = Form(...),
    context: str = Form("[]"),
    stream: bool = Form(False),
    files: Optional[List[UploadFile]] = File(None)
):
    # Parse context JSON string to list
    try:
        context_list = json.loads(context)
    except Exception:
        context_list = []

    # Extract content from all files
    extracted_files = []
    if files:
        for file in files:
            extracted_files.append(extract_file_content(file))

    # Combine all extracted file contents into a single string (or structure as needed)
    files_content = "\n\n".join(f["content"] for f in extracted_files if f["content"])

    # Optionally, add file content to context or message
    # Here, we append it to the message for the model
    if files_content:
        message = f"{message}\n\n[Attached file content(s)]:\n{files_content}"

    if stream:
        return StreamingResponse(ai_agent_stream(message, context_list), media_type="text/event-stream")
    else:
        response_content = await ai_agent_response(message, context_list)
        return response_content
    

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    port = 8000
    # Start ngrok tunnel
    public_url = ngrok.connect(port)
    logging.info(f"ngrok tunnel available at: {public_url}")
    # Start Uvicorn server
    uvicorn.run("ngrok:app", host="0.0.0.0", port=port, reload=False)