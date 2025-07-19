# Coffee Shop Assistant ☕🧠

An intelligent, conversational assistant for coffee shop operations, powered by **LangGraph**. This agent helps users navigate the menu, place orders, and receive personalized suggestions—all through a multi-turn, context-aware chat interface. All chat history is persistently stored using a SQLite backend for seamless experiences across sessions.

---

## 🖼️ Application UI

The app features a clean, multilingual interface with real-time streaming chat, persistent session management, and interactive messaging components.

![Coffee Shop Assistant Application](<Coffee Shop Assistant App.png>)

---

## ✨ Overview

**Coffee Shop Assistant** is designed to simulate a helpful AI agent in a real café setting. It guides customers through menu options, answers questions about drinks and items, and supports conversational follow-up using contextual memory.

The app architecture leverages:

- **LangGraph** for stateful, multi-step conversations.
- **Streamlit** for the interactive UI.
- **SQLite** for persistent chat storage.
- **Gemini 2.5 Pro** for fast, intelligent responses.
- **Local database files** for coffee menu data and interactions.

---

## ⚙️ How It Works

The assistant follows a structured LangGraph flow:

1. **Initial Greeting**: Welcomes the user and presents a helpful introduction.
2. **Intent Recognition**: Parses user intent—whether it’s asking about drinks, placing an order, or general questions.
3. **Data Lookup**: Fetches responses from internal knowledge (e.g. `.db` file) using the relevant LangGraph tools.
4. **Response Generation**: Crafts a helpful reply based on the query and current conversation context.
5. **Persistence**: Logs every message into a persistent SQLite conversation history.

---

## 🧠 Graph Architecture

The architecture relies on a deterministic graph built with LangGraph that controls user interactions in clear, logical steps. It includes memory nodes, conditional branching, and fallback logic for unrecognized intents.

![Coffee Shop Assistant Graph](<Coffee Shop Assistant Graph.PNG>)

---

## 🚀 Key Features

- **Conversational Agent**: Handles Arabic or English customer queries with natural language responses.
- **Persistent Chat Memory**: Saves each session in a local SQLite database.
- **Interactive Streamlit UI**: Streamlined, user-friendly experience.
- **Menu Lookup**: Supports intelligent retrieval of menu items and their details.

---

## 🛠️ Tech Stack

- **Orchestration**: LangChain & LangGraph
- **LLM**: Google Gemini (`gemini-2.5-pro`)
- **Database**: SQLite (`coffee_shop.db`)
- **UI Framework**: Streamlit
- **Environment Management**: Python `venv` or Docker

---

## 📦 Setup & Installation

### Option 1: Run Locally (venv)

1. **Clone the Repository**
    ```bash
    git clone https://github.com/eslammohamedtolba/Coffee-Shop-Assistant.git
    cd Coffee-Shop-Assistant
    ```

2. **Create and Activate a Virtual Environment**
    ```bash
    # Create the environment
    python -m venv venv

    # Activate on Windows PowerShell
    .\venv\Scripts\Activate.ps1

    # On macOS/Linux
    source venv/bin/activate
    ```

3. **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4. **Add Environment Variables**
    - Create a `.env` file in the root directory and add:
      ```env
      GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
      ```

5. **Launch the App**
    ```bash
    streamlit run main.py
    ```

6. **Access the App**  
    Open `http://localhost:8501` in your browser and start chatting.

---

### Option 2: Run with Docker

1. **Ensure Docker is Running**

2. **Build the Docker Image**
    ```bash
    docker build -t coffee-shop-assistant .
    ```

3. **Run the Container**
    ```bash
    docker run -p 8501:8501 \
      -v "$(pwd)/coffee_shop.db:/app/coffee_shop.db" \
      -v "$(pwd)/.env:/app/.env" \
      coffee-shop-assistant
    ```

    **Explanation:**
    - `-p 8501:8501`: Maps Streamlit port
    - `-v "$(pwd)/coffee_shop.db:/app/coffee_shop.db"`: Mounts your local database
    - `-v "$(pwd)/.env:/app/.env"`: Injects your local API keys

4. **Access the Application**  
    Go to: `http://localhost:8501`

5. **Stop the Container**
    ```bash
    docker stop coffee-shop-assistant
    ```

6. **(Optional) Remove the Container**
    ```bash
    docker rm coffee-shop-assistant
    ```

---

## 🤝 Contributing

Feel free to fork this repo, open issues, or submit pull requests to enhance functionality, add features, or improve performance.
