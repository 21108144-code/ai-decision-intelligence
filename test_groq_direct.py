import os
import sys
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
print(f"DEBUG: API Key found? {'Yes' if api_key else 'No'}")
if api_key:
    print(f"DEBUG: Key starts with: {api_key[:5]}...")

try:
    print("DEBUG: Initializing ChatGroq...")
    llm = ChatGroq(
        groq_api_key=api_key,
        model_name="llama-3.3-70b-versatile"
    )
    
    print("DEBUG: Sending test message...")
    response = llm.invoke("Hello, are you working?")
    print(f"DEBUG: Response received: {response.content}")
    print("SUCCESS: Groq API is working!")

except Exception as e:
    print(f"ERROR: Groq API failed. Details: {str(e)}")
