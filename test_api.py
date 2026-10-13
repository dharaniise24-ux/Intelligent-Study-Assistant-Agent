import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print("1. Connecting to API...")
client = genai.Client(api_key=api_key)

print("2. Sending test prompt...")
response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents="Reply with the word 'Connected' and nothing else."
)

print("3. Response received:")
print(response.text)