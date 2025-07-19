from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt.tool_node import ToolNode
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate
import sqlite3
from state import AgentState
from config import llm
from tools import (
    get_menu_items,
    get_item_details,
    place_order,
    get_order_status,
    cancel_order
)
from db_utils import (
    initialize_database,
    DATABASE_FILE
)


# Initialize database tables
initialize_database()

tools = [get_menu_items, 
         get_item_details, 
         place_order,
         get_order_status, 
         cancel_order]


def Process(state: AgentState) -> AgentState:
    messages = state['messages']
    customer_id = state['customer_id'] # Get the customer_id from the state

    # Define the prompt template *inside* the function to access customer_id dynamically
    dynamic_prompt_template = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(
                f"""أنت مساعد قهوة ودود ومطلع في مقهى راقٍ. مهمتك هي التفاعل مع العملاء، 
                تقديم التوصيات، أخذ طلباتهم بدقة، والرد على استفساراتهم حول القائمة أو حالة الطلبات.
                
                معرف العميل الحالي هو: {customer_id}. استخدم هذا المعرف عند الحاجة إليه، 
                خاصة عند استخدام الأدوات التي تتطلب `customer_session_id` مثل `place_order`.

                عند أخذ الطلبات، كن مفيدًا في جمع التفاصيل. يمكن للعملاء تخصيص طلباتهم. 
                فيما يلي بعض التخصيصات الشائعة التي يمكنك الاستفسار عنها أو توقعها:
                - نوع الحليب: حليب عادي، حليب قليل الدسم، حليب لوز، حليب صويا، حليب جوز الهند، حليب شوفان.
                - درجة التحلية: بدون سكر، سكر قليل، سكر عادي، سكر إضافي.
                - درجة الحرارة: ساخن جداً، ساخن، دافئ، بارد، بارد جداً.
                - الحجم: صغير، متوسط، كبير.
                - إضافات: كريمة مخفوقة، صوص كراميل، فانيليا، قرفة.

                استخدم الأدوات المتاحة لك بحكمة للإجابة على الأسئلة أو تنفيذ الإجراءات.
                إذا لم تتمكن من تلبية الطلب باستخدام الأدوات، أجب بأدب.
                """
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    
    # Chain the dynamic prompt with the LLM and bound tools
    agent_chain = dynamic_prompt_template | llm.bind_tools(tools=tools)

    # Invoke the chain and passing the messages. 
    response = agent_chain.invoke({'messages': messages})
    
    return {
        'messages': response 
    }

def should_continue(state: AgentState) -> AgentState:
    last_message = state['messages'][-1]
    
    if last_message.tool_calls:
        return "need_tool"
    return "end"

def create_agent():
    
    # Create graph
    graph = StateGraph(AgentState)
    
    # Create nodes
    graph.add_node("Process_node", Process)
    graph.add_node("tools_node", ToolNode(tools=tools))
    
    # Set entry point
    graph.set_entry_point("Process_node")
    
    # Create edges
    graph.add_conditional_edges(
        "Process_node",
        should_continue,
        {
            "need_tool":"tools_node",
            "end":END
        }   
    )
    graph.add_edge("tools_node", "Process_node")
    
    # Create connection and memory
    sqlite_conn = sqlite3.connect(DATABASE_FILE, check_same_thread = False)
    memory = SqliteSaver(conn = sqlite_conn)
    
    # compile the graph
    return graph.compile(checkpointer=memory)

