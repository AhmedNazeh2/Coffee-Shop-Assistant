import streamlit as st
import time
from graph import create_agent
from langchain_core.messages import HumanMessage, AIMessage

# Fixed customer_id and thread_id for this single-session application
FIXED_CUSTOMER_ID = "single_coffee_customer"
LANGGRAPH_CONFIG = {
    "configurable": {
        "thread_id": FIXED_CUSTOMER_ID,
        "recursion_limit": 50
    }
}

# Initialize the LangGraph Agent
app = create_agent()

# --- Streamlit Page Setup ---
st.set_page_config(page_title="Coffee Shop Assistant", layout="centered")
st.title("Coffee Shop Assistant ☕")

# Chat History Display Function
def display_chat_history(app_instance, config_dict):
    """Displays messages from the LangGraph history for the current fixed session."""

    with st.chat_message("assistant"):
        st.markdown("Welcome to Coffee Shop I'm your personal assistant. How can I help you today? Feel free to place your order or ask about the menu!")

    history = app_instance.get_state(config_dict)

    # Check if there are no messages in history
    if not history:
        return

    messages = history.values.get('messages', [])

    for msg in messages:
        if isinstance(msg, HumanMessage):
            with st.chat_message("user"):
                st.markdown(f"{msg.content}")
        elif isinstance(msg, AIMessage):
            if not msg.tool_calls:
                with st.chat_message("assistant"):
                    st.markdown(f"{msg.content}")

# Stream Agent Response Function
def stream_response(graph_app, initial_state, config_for_run):
    """Streams the agent's response and updates status messages."""

    with st.status("The assistant is thinking...", expanded=True) as status_container:

        for step in graph_app.stream(initial_state, config=config_for_run):
            node_name = list(step.keys())[0]
            node_value = step[node_name]

            # Update status message based on the current node
            if node_name == "Process_node":
                status_container.update(label="The assistant is preparing a response or identifying a tool... 🧠")

            elif node_name == "tools_node":
                tool_name = node_value['messages'][0].name

                # Update based on tool name
                if tool_name == "get_menu_items":
                    status_container.update(label="Searching the drink menu... 📋")
                elif tool_name == "get_item_details":
                    status_container.update(label="Looking up item details... 🔍")
                elif tool_name == "place_order":
                    status_container.update(label="Registering your order... ✍️")
                elif tool_name == "get_order_status":
                    status_container.update(label="Checking your order status... 📊")
                elif tool_name == "cancel_order":
                    status_container.update(label=f"Cancelling the order... ❌")
                else:
                    status_container.update(label=f"Executing tool: {tool_name}... 🛠️")

            time.sleep(1)
        status_container.update(label="Done! ✅")
        time.sleep(1)

if __name__ == "__main__":

    display_chat_history(app, LANGGRAPH_CONFIG)

    # Get user input at the bottom of the chat interface
    if prompt := st.chat_input("How can I help you?"):
        with st.chat_message("user"):
            st.markdown(f"{prompt}")

        with st.chat_message("assistant"):
            # Prepare the initial state for the LangGraph agent run
            initial_state = {
                "messages": [HumanMessage(content=prompt)],
                "customer_id": FIXED_CUSTOMER_ID
            }
            stream_response(app, initial_state, LANGGRAPH_CONFIG)

        st.rerun()
