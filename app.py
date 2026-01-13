import streamlit as st
import os
import re
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

# Page configuration
st.set_page_config(
    page_title="Chatbot with History",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: flex-start;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 20%;
    }
    .assistant-message {
        background-color: #f5f5f5;
        margin-right: 20%;
    }
    .message-icon {
        font-size: 1.5rem;
        margin-right: 0.5rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        border-radius: 0.5rem;
        padding: 0.5rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #1565c0;
    }
    </style>
""", unsafe_allow_html=True)

# Load environment variables
load_dotenv("C:/Users/vineet.srivastava/venvGenAIStudy/.env")

# Initialize session state
if "store" not in st.session_state:
    st.session_state.store = {}

if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = "default"

if "session_counter" not in st.session_state:
    st.session_state.session_counter = 1

# Initialize LLM
@st.cache_resource
def initialize_llm():
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    return ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)

# Get session history function
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in st.session_state.store:
        st.session_state.store[session_id] = ChatMessageHistory()
    return st.session_state.store[session_id]

# Initialize LLM and wrapper
llm = initialize_llm()
with_message_history = RunnableWithMessageHistory(llm, get_session_history)

# Function to generate session name from question
def generate_session_name(question: str) -> str:
    """Generate a meaningful session name based on the first question."""
    try:
        prompt = f"""Based on the following question, generate a short, descriptive session name (2-4 words max) that captures the main topic or context. 
        
Question: {question}

Return ONLY the session name, nothing else. Make it lowercase with underscores instead of spaces.
Examples:
- "What is Python?" -> "python_question"
- "How do I cook pasta?" -> "cooking_pasta"
- "Explain machine learning" -> "machine_learning"
- "Tell me about the weather" -> "weather_inquiry"

Session name:"""
        
        response = llm.invoke([HumanMessage(content=prompt)])
        session_name = response.content.strip().lower()
        
        # Clean the session name: remove special characters, replace spaces with underscores
        session_name = re.sub(r'[^a-z0-9_]+', '_', session_name)
        session_name = re.sub(r'_+', '_', session_name)  # Replace multiple underscores with single
        session_name = session_name.strip('_')  # Remove leading/trailing underscores
        
        # Limit length
        if len(session_name) > 50:
            session_name = session_name[:50]
        
        # Fallback if empty or too short
        if not session_name or len(session_name) < 3:
            session_name = f"chat_{st.session_state.session_counter}"
            st.session_state.session_counter += 1
        
        return session_name
    except Exception as e:
        # Fallback to numbered session if generation fails
        session_name = f"session_{st.session_state.session_counter}"
        st.session_state.session_counter += 1
        return session_name

# Sidebar for session management
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Session management
    st.subheader("📝 Session Management")
    
    # Display current session
    st.info(f"**Current Session:** {st.session_state.current_session_id}")
    
    # Create new session
    if st.button("➕ New Chat", use_container_width=True):
        # Reset to default so next question will generate a name
        st.session_state.current_session_id = "default"
        st.rerun()
    
    # List existing sessions
    if st.session_state.store:
        st.subheader("📋 Existing Sessions")
        for session_id in st.session_state.store.keys():
            if st.button(f"💬 {session_id}", key=f"session_{session_id}", use_container_width=True):
                st.session_state.current_session_id = session_id
                st.rerun()
    
    # Clear current session
    if st.session_state.current_session_id in st.session_state.store:
        if st.button("🗑️ Clear Current Session", use_container_width=True):
            del st.session_state.store[st.session_state.current_session_id]
            st.session_state.current_session_id = "default"
            st.rerun()
    
    # Show info about auto-naming
    if st.session_state.current_session_id == "default":
        st.info("💡 **Tip:** Your first message will automatically create a named session based on your question!")
    
    st.divider()
    
    # Model info
    st.subheader("🤖 Model Info")
    st.info("**Model:** GPT-3.5 Turbo\n\n**Temperature:** 0.7")
    
    # Instructions
    st.subheader("ℹ️ Instructions")
    st.markdown("""
    1. Type your message in the input box
    2. Press Enter or click Send
    3. The chatbot remembers your conversation
    4. **Auto-naming:** Sessions are automatically named based on your first question
    5. Create new sessions for different topics
    """)

# Main content area
st.markdown('<p class="main-header">💬 Chatbot with History</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Powered by LangChain & OpenAI GPT-3.5 Turbo</p>', unsafe_allow_html=True)

# Display chat history
chat_container = st.container()

with chat_container:
    # Get current session history
    if st.session_state.current_session_id in st.session_state.store:
        history = st.session_state.store[st.session_state.current_session_id]
        messages = history.messages
        
        # Display all messages
        for message in messages:
            if isinstance(message, HumanMessage):
                with st.chat_message("user"):
                    st.write(message.content)
            elif isinstance(message, AIMessage):
                with st.chat_message("assistant"):
                    st.write(message.content)
    else:
        # Welcome message for new sessions
        with st.chat_message("assistant"):
            st.write("👋 Hello! I'm your AI assistant. I can remember our conversation. How can I help you today?")

# Chat input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Check if this is a new session (no messages yet)
    is_new_session = (
        st.session_state.current_session_id not in st.session_state.store or
        len(st.session_state.store.get(st.session_state.current_session_id, ChatMessageHistory()).messages) == 0
    )
    
    # Generate session name from first question if it's a new session
    if is_new_session and st.session_state.current_session_id == "default":
        with st.spinner("Creating session..."):
            generated_name = generate_session_name(user_input)
            # Check if name already exists, append number if needed
            original_name = generated_name
            counter = 1
            while generated_name in st.session_state.store:
                generated_name = f"{original_name}_{counter}"
                counter += 1
            st.session_state.current_session_id = generated_name
    
    # Display user message
    with st.chat_message("user"):
        st.write(user_input)
    
    # Get response from LLM
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                config = {"configurable": {"session_id": st.session_state.current_session_id}}
                response = with_message_history.invoke(
                    [HumanMessage(content=user_input)],
                    config=config
                )
                st.write(response.content)
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Please check your OpenAI API key in the .env file")
    
    # Rerun to update the chat display
    st.rerun()

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>Built with ❤️ using Streamlit, LangChain, and OpenAI</p>
    </div>
    """,
    unsafe_allow_html=True
)

