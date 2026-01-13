# Chatbot with History - LangChain Implementation

## Summary

This Code demonstrates how to build a chatbot with conversation history management using LangChain. It shows how to maintain context across multiple interactions, enabling the chatbot to remember previous messages within a conversation session. The implementation uses LangChain's `RunnableWithMessageHistory` to automatically manage chat histories for multiple independent conversation sessions.

## Features

- ✅ **Conversation History Management**: Automatically maintains chat history for each session
- ✅ **Multi-Session Support**: Handle multiple independent conversations simultaneously
- ✅ **Context Retention**: Chatbot remembers previous messages within the same session
- ✅ **Session Isolation**: Different sessions don't interfere with each other
- ✅ **Automatic History Handling**: No need to manually pass previous messages
- ✅ **Smart Session Naming**: Automatically generates meaningful session names based on the first question
- ✅ **OpenAI Integration**: Uses GPT-3.5-turbo for chat completions
- ✅ **Simple Configuration**: Easy-to-use session-based configuration

## Imports and Setup

### Required Libraries

```python
import os 
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
```

### Key Components

1. **Message Types**:
   - `HumanMessage`: Messages from the user
   - `AIMessage`: Messages from the AI assistant
   - `SystemMessage`: System-level instructions (optional)

2. **History Management**:
   - `ChatMessageHistory`: Stores conversation history for a session
   - `BaseChatMessageHistory`: Base class for chat history implementations
   - `RunnableWithMessageHistory`: Wrapper that automatically manages history

3. **LLM**:
   - `ChatOpenAI`: OpenAI's chat model interface

### Output Display 
[ChatbotDisplay.png]

### Environment Setup

```python
# Load environment variables
load_dotenv("path/to/your/.env")

# Set OpenAI API key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Initialize the LLM
llm = ChatOpenAI(model_name="gpt-3.5-turbo")
```

## Concept Explanation

### The Problem

In a basic chatbot implementation, each message is treated independently. The model doesn't remember previous interactions, making it impossible to have meaningful multi-turn conversations.

**Example without history:**
```python
# First message
response1 = llm.invoke([HumanMessage("My name is John")])

# Second message - model doesn't remember the first message
response2 = llm.invoke([HumanMessage("What is my name?")])
# ❌ Model doesn't know the name
```

### Manual History Management

One approach is to manually pass previous messages:

```python
response1 = llm.invoke([HumanMessage("My name is John")])

# Manually include previous messages
response2 = llm.invoke([
    HumanMessage("My name is John"),
    AIMessage(content=response1.content),
    HumanMessage("What is my name?")
])
```

**Problems with this approach:**
- ❌ Requires manually managing message history
- ❌ Error-prone (easy to forget previous messages)
- ❌ Doesn't scale for multiple sessions
- ❌ Difficult to maintain conversation state

### Solution: RunnableWithMessageHistory

LangChain's `RunnableWithMessageHistory` solves these problems by automatically managing conversation history.

#### How It Works

1. **Session Store**: A dictionary that holds multiple chat histories
   ```python
   store = {}  # Key: session_id, Value: ChatMessageHistory
   ```

2. **History Getter Function**: Retrieves or creates history for a session
   ```python
   def get_session_history(session_id: str) -> BaseChatMessageHistory:
       if session_id not in store:
           store[session_id] = ChatMessageHistory()
       return store[session_id]
   ```

3. **Wrapper**: Wraps the LLM to automatically manage history
   ```python
   with_message_history = RunnableWithMessageHistory(
       llm, 
       get_session_history
   )
   ```

4. **Configuration**: Each invocation includes a session ID
   ```python
   config = {"configurable": {"session_id": "chat1"}}
   response = with_message_history.invoke(
       [HumanMessage("Hello!")],
       config=config
   )
   ```

#### Workflow

1. **First Message in Session**:
   - User sends: `"My name is Vineet"`
   - System retrieves/creates history for session `"chat1"`
   - LLM processes the message
   - Response is stored in history
   - Response returned to user

2. **Subsequent Messages**:
   - User sends: `"Where do I work?"`
   - System retrieves history for session `"chat1"` (contains previous messages)
   - LLM processes current message WITH full history context
   - Response is stored in history
   - Response returned to user

3. **New Chat**:
   - User sends message with different session ID (`"chat2"`)
   - System creates new history for `"chat2"`
   - Previous session's history is not included
   - Each session maintains independent context

### Benefits

✅ **Automatic History Management**: No need to manually pass previous messages  
✅ **Multi-Session Support**: Handle multiple users/conversations simultaneously  
✅ **Smart Session Naming**: Automatically generates meaningful session names based on conversation context  
✅ **Clean API**: Simple configuration-based approach  
✅ **Scalable**: Easy to extend with persistent storage (database, Redis, etc.)  
✅ **Type-Safe**: Uses LangChain's type system for safety  

### Smart Session Auto-Naming (Streamlit App)

The Streamlit app includes an intelligent session naming feature that automatically generates descriptive session names from the first question:

**How it works:**
1. When a user starts a new session and asks their first question
2. The system uses the LLM to analyze the question and extract the main topic
3. A clean, descriptive session name is generated (e.g., "python_question", "cooking_pasta")
4. The session is created with this meaningful name
5. Users can easily identify and switch between different conversation topics

**Benefits:**
- 🎯 **Context-Aware**: Names reflect the actual conversation topic
- 📝 **Easy Organization**: Quickly identify sessions by their purpose
- 🔍 **Better UX**: No need to remember generic session IDs
- 🤖 **AI-Powered**: Uses GPT-3.5 to understand context and generate appropriate names

### Use Cases

- **Customer Support Chatbots**: Each customer has their own session
- **Multi-User Applications**: Different users have separate conversation contexts
- **Contextual Assistants**: Remember user preferences and previous interactions
- **Conversational AI**: Build natural, flowing conversations


## Streamlit Web Application

A clean, user-friendly web interface is available for interacting with the chatbot.

### Features

- 🎨 **Clean UI**: Modern, intuitive interface with custom styling
- 💬 **Real-time Chat**: Interactive chat interface with message history
- 📝 **Session Management**: Create, switch, and manage multiple conversation sessions
- 🤖 **Smart Auto-Naming**: Sessions are automatically named based on the first question's context
- 🔄 **Auto-refresh**: Automatic updates after each message
- ⚙️ **Sidebar Controls**: Easy access to session management and settings
- 📱 **Responsive Design**: Works on different screen sizes

### Running the Streamlit App

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Update the .env path** in `app.py`:
   ```python
   load_dotenv("path/to/your/.env")
   ```

3. **Run the app**:
   ```bash
   streamlit run app.py
   ```

4. **Access the app**:
   - The app will open automatically in your browser
   - Default URL: `http://localhost:8501`

### App Interface

#### Main Chat Area
- **Header**: Displays app title and model information
- **Chat Messages**: Shows conversation history with user and assistant messages
- **Input Field**: Type your message and press Enter or click Send

#### Sidebar Features
- **Session Management**:
  - Create new chats with the "➕ New Chat" button
  - Switch between existing sessions
  - Clear current session
  - View all active sessions with auto-generated names

- **Model Information**: Displays current model and settings
- **Instructions**: Quick guide on how to use the app

### Smart Session Auto-Naming

The app automatically generates meaningful session names based on the context of your first question. This makes it easy to identify and manage different conversation topics.

#### How It Works

1. **Start a New Chat**: When you click "➕ New Chat" or start with the default session
2. **Ask Your First Question**: Type your message in the chat input
3. **Auto-Naming**: The system analyzes your question and generates a descriptive session name
4. **Session Created**: Your session is now named and ready for conversation

#### Examples

| First Question | Generated Session Name |
|----------------|------------------------|
| "What is Python?" | `python_question` |
| "How do I cook pasta?" | `cooking_pasta` |
| "Explain machine learning" | `machine_learning` |
| "Tell me about the weather" | `weather_inquiry` |
| "Help me with my Python code" | `python_code_help` |

#### Features

- **Context-Aware**: Uses AI to understand the topic of your question
- **Clean Names**: Automatically formats names (lowercase, underscores, no special characters)
- **Duplicate Handling**: Automatically appends numbers if a name already exists
- **Fallback**: Uses numbered sessions if name generation fails

### Usage Tips

1. **Starting a Conversation**: Simply type your message in the input box - the session will be auto-named
2. **Creating New Chats**: Click "➕ New Chat" in the sidebar for a fresh conversation
3. **Switching Sessions**: Click on any session name in the sidebar to switch between conversations
4. **Clearing History**: Use "🗑️ Clear Current Session" to start fresh in the current session
5. **Session Names**: Session names are based on your first question, making it easy to find specific conversations

### Screenshots

The app includes:
- Clean, modern design with blue color scheme
- Distinct styling for user and assistant messages
- Intuitive sidebar navigation
- Real-time conversation display

## Requirements

- Python 3.8+
- langchain
- langchain-openai
- langchain-community
- python-dotenv
- OpenAI API key

## Installation

### For Notebook Usage

```bash
pip install langchain langchain-openai langchain-community python-dotenv
```

### For Streamlit App

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install streamlit langchain langchain-openai langchain-community python-dotenv openai
```

## Notes

- The session store is in-memory and will be lost when the application restarts
- For production, consider using persistent storage (Redis, PostgreSQL, etc.)
- Each session maintains its own independent conversation history
- The `config` parameter must include `"configurable": {"session_id": "..."}` for history to work
- **Auto-Naming**: Session names are automatically generated from the first question using AI, making it easy to identify conversation topics
- Session names are cleaned (lowercase, underscores) and limited to 50 characters for better readability

