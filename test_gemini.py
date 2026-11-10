
import streamlit as st
from google import genai

print("Connecting to Gemini...")

try:
    client = genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )

    print("Sending question...")

    response = client.interactions.create(
        model="gemini-3.1-flash-lite",
        input="Explain Python in two simple sentences.",
        timeout=60000
    )

    print("\nSUCCESS!")
    print(response.output_text)

except Exception as e:
    print("\nERROR:")
    print(type(e).__name__)
    print(str(e))
