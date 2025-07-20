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
st.set_page_config(page_title="مساعد قهوة مقهى اللؤلؤة", layout="centered")
st.title("مساعد قهوة مقهى اللؤلؤة ☕")

# Chat History Display Function
def display_chat_history(app_instance, config_dict):
    """Displays messages from the LangGraph history for the current fixed session."""
    
    with st.chat_message("assistant"):
        st.markdown("<div dir='rtl'>أهلاً بك في مقهى اللؤلؤة! أنا مساعدك الشخصي هنا. كيف يمكنني مساعدتك اليوم؟ تفضل بطلبك أو اسأل عن قائمتنا!</div>", unsafe_allow_html=True)
    
    history = app_instance.get_state(config_dict)
    
    # Check if there are no messages in history
    if not history:
        return
    
    messages = history.values.get('messages', [])
    
    for msg in messages:
        if isinstance(msg, HumanMessage):
            with st.chat_message("user"):
                st.markdown(f"<div dir='rtl'>{msg.content}</div>", unsafe_allow_html=True)
        elif isinstance(msg, AIMessage):
            # Displays only the final AI messages that do not contain tool calls,
            # indicating a complete response from the assistant for that turn.
            if not msg.tool_calls:
                with st.chat_message("assistant"):
                    st.markdown(f"<div dir='rtl'>{msg.content}</div>", unsafe_allow_html=True)

# Stream Agent Response Function
def stream_response(graph_app, initial_state, config_for_run):
    """Streams the agent's response and updates status messages."""

    with st.status("الوكيل يفكر...", expanded=True) as status_container:

        for step in graph_app.stream(initial_state, config=config_for_run):
            # LangGraph step will have a single key representing the node that just ran
            node_name = list(step.keys())[0] 
            node_value = step[node_name]
            
            # Update status message based on the current node
            if node_name == "Process_node":
                status_container.update(label="الوكيل يجهز رده أو يحدد الأداة... 🧠")
                
            elif node_name == "tools_node":
                tool_name = node_value['messages'][0].name
                
                # Refine these messages based on specific tool names
                if tool_name == "get_menu_items":
                    status_container.update(label="جاري البحث في قائمة المشروبات... 📋")
                elif tool_name == "get_item_details":
                    status_container.update(label="جاري استعراض تفاصيل المنتج... 🔍")
                elif tool_name == "place_order":
                    status_container.update(label="جاري تسجيل طلبك... ✍️")
                elif tool_name == "get_order_status":
                    status_container.update(label="جاري التحقق من حالة الطلب... 📊")
                elif tool_name == "cancel_order":
                    status_container.update(label=f"جاري إلغاء الطلب... ❌")
                else:
                    status_container.update(label=f"تنفيذ أداة: {tool_name}... 🛠️")
                    
            time.sleep(1)
        status_container.update(label="انتهيت... ✅")
        time.sleep(1)


# Main Application Logic
if __name__ == "__main__":
    
    # Display the chat history.
    display_chat_history(app, LANGGRAPH_CONFIG)

    # Get user input at the bottom of the chat interface
    if prompt := st.chat_input("كيف يمكنني مساعدتك؟"):
        # Display the user's message
        with st.chat_message("user"):
            st.markdown(f"<div dir='rtl'>{prompt}</div>", unsafe_allow_html=True)
        
        # Stream the assistant's response
        with st.chat_message("assistant"):
            # Prepare the initial state for the LangGraph agent run
            initial_state = {
                "messages": [HumanMessage(content=prompt)],
                "customer_id": FIXED_CUSTOMER_ID
            }
            stream_response(app, initial_state, LANGGRAPH_CONFIG)
        
        # Rerun the Streamlit app to update the chat history from LangGraph's memory
        st.rerun()