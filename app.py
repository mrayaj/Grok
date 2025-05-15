import os 
import streamlit as st  
from pathlib import Path 
from dotenv import load_dotenv
from groq import Groq  

load_dotenv()

class GroqAPI:
    """Handles API operations with Groq to generate chat responses."""
    def __init__(self, model_name: str):
        # API key from environment variable
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("API key is missing. Please set the GROQ_API_KEY environment variable.")
        self.client = Groq(api_key=api_key)
        self.model_name = model_name

    def _response(self, message):
        return self.client.chat.completions.create(
            model=self.model_name,
            messages=message,
            temperature=0,
            max_tokens=4096,
            stream=True,
            stop=None,
        )
    def response_stream(self, message):        
        for chunk in self._response(message):
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

class Message:
    """Manages chat messages within the Streamlit UI."""
    system_prompt = "You are a professional AI. Please generate responses in English to all user inputs."

    def __init__(self):
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "system", "content": self.system_prompt}]

    def add(self, role: str, content: str):
        st.session_state.messages.append({"role": role, "content": content})

    def display_chat_history(self):
        for message in st.session_state.messages:
            if message["role"] == "system":
                continue
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    #  Streamlit chat message UI
    def display_stream(self, generator):
        with st.chat_message("assistant"):
            return st.write_stream(generator)
        

def main():
    user_input = st.chat_input("Enter message to AI models...")
    selected_model = "llama3-8b-8192"
    message = Message()
    st.title("Groq LLM Chatbot")
    st.sidebar.success(f"Model: {selected_model}")
    if user_input:
        llm = GroqAPI(selected_model)
        message.add("user", user_input)
        message.display_chat_history()
        response = message.display_stream(llm.response_stream(st.session_state.messages))
        message.add("assistant", response)

if __name__ == "__main__":
    main()
