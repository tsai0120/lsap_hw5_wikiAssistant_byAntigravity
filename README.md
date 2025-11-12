# Wiki Assistant

A Wikipedia-powered chat assistant that uses AI to answer questions by searching and analyzing Wikipedia content. The application consists of a FastAPI backend for Wikipedia data processing and a Streamlit frontend for interactive chat.

## Features

- 🔍 **Intelligent Wikipedia Search**: Automatically finds relevant Wikipedia pages based on your queries
- 🤖 **AI-Powered Responses**: Uses Google's Gemini AI with DSPy framework for intelligent responses
- 📚 **Semantic Search**: Employs sentence transformers to find the most relevant content chunks
- 💬 **Chat Interface**: Interactive Streamlit-based chat interface with conversation history
- ⚡ **Fast API Backend**: Efficient Wikipedia scraping and text processing

## Architecture

The application is split into two main components:

- **Backend** (`/backend`): FastAPI server that handles Wikipedia scraping, text chunking, and semantic search
- **Frontend** (`/frontend`): Streamlit chat interface that interacts with the backend and uses DSPy for AI responses

## Prerequisites

- Python 3.13 or higher
- [Poetry](https://python-poetry.org/) for dependency management
- [Task](https://taskfile.dev/) (optional, for easier command execution)
- Google Gemini API key

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd wiki-assistant
```

### 2. Install Poetry

If you don't have Poetry installed:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 3. Install Task (Optional)

If you want to use the Taskfile for easier command execution:

**macOS:**
```bash
brew install go-task
```

**Other platforms:** See [Task installation guide](https://taskfile.dev/installation/)

### 4. Set Up the Backend

```bash
cd backend
task install
```

### 5. Set Up the Frontend

```bash
cd ../frontend
task install
```

### 6. Configure Environment Variables

Create a `.env` file in the `frontend` directory:

```bash
cd frontend
touch .env
```

Add your Gemini API key to the `.env` file:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

To get a Gemini API key:
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key

## Running the Application

You need to run both the backend and frontend servers.

### Option 1: Using Task (Recommended)

**Terminal 1 - Start Backend:**
```bash
cd backend
task serve
```

**Terminal 2 - Start Frontend:**
```bash
cd frontend
task serve
```

## Accessing the Application

Once both servers are running:

- **Frontend (Chat Interface)**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (FastAPI auto-generated)

## Usage

1. Open your browser and navigate to http://localhost:8501
2. Type your question in the chat input
3. The assistant will:
   - Search for relevant Wikipedia pages
   - Extract and analyze relevant content
   - Provide an AI-generated response based on Wikipedia information
4. Continue the conversation with follow-up questions

## Project Structure

```
wiki-assistant/
├── backend/
│   ├── server.py          # FastAPI application
│   ├── utils.py           # Wikipedia scraping and text processing utilities
│   ├── pyproject.toml     # Backend dependencies
│   └── taskfile.yml       # Backend task definitions
├── frontend/
│   ├── chat.py            # Streamlit chat interface
│   ├── agent.py           # DSPy agent with ReAct reasoning
│   ├── pyproject.toml     # Frontend dependencies
│   ├── taskfile.yml       # Frontend task definitions
│   └── .env               # Environment variables (create this)
└── README.md
```

