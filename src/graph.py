from langchain_core.messages import SystemMessage,HumanMessage, RemoveMessage, AIMessage
from langgraph.graph import StateGraph, START,END,MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

llm = ChatGoogleGenerativeAI(api_key=os.getenv("GOOGLE_API_KEY"),
                            model="gemini-2.0-flash")

farmer_bot = [SystemMessage(
    content=(
        "You are an AI assistant designed to help farmers with their agricultural needs. "
        "Your primary responsibilities include answering queries related to farming practices, "
        "providing crop recommendations based on conditions or inputs, suggesting solutions to "
        "common farming problems, and supporting any other agriculture-related questions. "
        "Respond in a clear, practical, and farmer-friendly manner."
    )
)]



class State(MessagesState):
    query:str
    summary: str



def call_model(state: State):
    # Extract the human query (currently stored as a plain string)
    human_query = state.get("query")
    
    # Wrap the human input in a HumanMessage.
    human_message = HumanMessage(content=human_query)
    
    # Build the messages list.
    if state.get("summary"):
        sys_msg = f"Summary of conversation from earlier: {state.get('summary')}"
        # Prepend the summary as a system message
        new_mmsg = [SystemMessage(content=sys_msg), human_message]
    else:
        new_mmsg = [human_message]
    
    # Now, call your LLM with these messages.
    response = llm.invoke(farmer_bot+state.get("messages")+new_mmsg)
    
    # Wrap the LLM response as an AIMessage.
    ai_message = AIMessage(content=response.content)
    
    # Update the state's messages: append both the human message and the AI response.
    updated_messages = state.get("messages") + add_messages(human_message,ai_message)
    
    # Return the latest AI message; for downstream nodes, you might return the full updated list
    return {"messages": updated_messages }


def summarize_convo(state:State):

    summary = state.get("summary")

    if summary:
        summary_mmsg = {
            f"This is the summary of the convo until now: {summary}.\n\n"
            "Extend the summary by taking into account the new messages above."
        }

    else:
        summary_mmsg = "Create a summary of the conversation above"

    messages = state.get("messages") + [HumanMessage(content=summary_mmsg)]
    response = llm.invoke(messages)

    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"summary": response.content, "messages": delete_messages}


def should_trim(state:State):
    """Returns the next node to be executed"""

    messages = state.get("messages")

    if len(messages)> 6:
        return "summarize_convo"
    
    return END

workflow = StateGraph(State)
workflow.add_node("conversation",call_model)
workflow.add_node("summarize_convo", summarize_convo)

workflow.add_edge(START, "conversation")
workflow.add_conditional_edges("conversation", should_trim)
workflow.add_edge("summarize_convo", END)

memory = MemorySaver()
chat_graph = workflow.compile(checkpointer=memory)
chat_graph


