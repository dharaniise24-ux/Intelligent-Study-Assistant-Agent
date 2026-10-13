# Study Assistant Agent

A lightweight academic study assistant built with Streamlit and Google's Gemini API. It helps students understand CS concepts, answer course-related questions, and ground its responses in uploaded study notes.

## Features

- Ask programming and computer science questions in plain English
- Upload PDF, TXT, or Markdown notes for grounded answers
- Get prompt coaching suggestions to improve question quality
- Maintain a simple conversation history within the app
- Use course knowledge for CS/academic queries when no notes are uploaded

## Project Layout

- `app.py` — main Streamlit application
- `assistant.py` — CLI-based prompt engineering examples
- `knowledge_base.py` — guidance prompts and course knowledge base
- `test_api.py` — quick Gemini API connectivity test
- `.env` — local environment variables (not committed to source control)

## Requirements

Install the required Python packages:

```bash
pip install streamlit python-dotenv google-genai pypdf
```

## Environment Setup

Create a `.env` file in the project root with your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
```

## Run the App

From the project folder:

```bash
streamlit run app.py
```

Then open the local URL shown in the terminal, typically:

```text
http://localhost:8501
```

## How It Works

- The app loads your Gemini API key from `.env`
- It analyzes the user’s prompt and suggests a better version
- It combines the system instructions with uploaded notes if present
- It streams the AI response back into the chat interface

## Notes

- Uploaded files are used as context when available, so answers can reflect your lecture notes or study material.
- If no file is uploaded, the app still answers general academic questions using the built-in course knowledge base.
- The app currently targets the Gemini model `gemini-3.5-flash-lite`.

## Example Use Cases

- Explain DBMS normalization, recursion, or complexity analysis
- Ask about assignment deadlines and late policies
- Upload lecture notes and ask for clarification on a specific topic
- Use the app as a study companion for course review and concept reinforcement
