from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
import os
from IPython.display import Image,display
from langgraph.graph import START,END,StateGraph, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, RemoveMessage
from groq import  Groq
from google import genai
import base64
from google.genai import types
from src.credentials import creds

from langgraph.graph.message import add_messages
from typing import Literal
from typing_extensions import  TypedDict
from dotenv import load_dotenv

load_dotenv()


llm_gemini = ChatGoogleGenerativeAI(api_key=os.getenv("GOOGLE_API_KEY"),
                                model="gemini-2.0-flash",
                                credentials=creds)


class OverAllState(TypedDict):
    query: str
    base64_image: str
    llama_response: str
    gemini_response: str
    answer:str




answer_writing_system_message = [SystemMessage(
    content="""You are an AI assistant that summarizes farm image analysis results clearly for farmers and agricultural users.

Based on the given inputs, generate a **brief, user-friendly summary** of the likely crop condition, pest/disease detection, or recommendation.

Constraints:
- Keep the response **to the point**.
- Avoid scientific jargon; use **simple, agricultural-friendly language**.
- Include suggestions like **home remedies, crop treatments, fertilizer recommendations, or preventive measures**.
- Answer the user's question properly, including sub-parts if any.
"""
)]



# Example HumanMessage with the actual analysis outputs as input
analysis_results = """gemini_output: {gemini_response}, llama_output: {llama_response}"""



def process_image_llama(state: OverAllState):
    client = Groq(api_key=os.getenv("GROQ_API_KEY")) 
    query = state["query"]
    base64_image = state["base64_image"]


    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"{query}."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }
    ]

    chat_completion = client.chat.completions.create(
        messages=messages,
        model="llama-3.2-11b-vision-preview",
    )

    # Correct variable name used for response extraction.
    response = chat_completion.choices[0].message.content

    return {"llama_response": response}

    


def process_image_gemini(state: OverAllState):
    """Processes an image with Google Gemini Vision model."""
    query = state["query"]
    base64_image = state["base64_image"]
    # Decode base64 string to bytes
    image_bytes = base64.b64decode(base64_image)

    # Call Gemini Vision API
    client = genai.Client(credentials=creds)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            f"{query}",
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
        ],
    )

    return {"gemini_response": response.text}




def build_answer(state: OverAllState):


    llm_groq = ChatGroq(
        model="llama-guard-3-8b",
        temperature=0,
        max_tokens=None,
        api_key=os.getenv("GROQ_API_KEY")
    )

    llm_gemini = ChatGoogleGenerativeAI(api_key=os.getenv("GOOGLE_API_KEY"),
                            model="gemini-2.0-flash", credentials=creds)

    # response = llm_groq.invoke(answer_writing_instruction.format(gemini_response=state["gemini_response"],
    #                                                                llama_response= state["llama_response"]))
    response = llm_gemini.invoke(answer_writing_system_message+[HumanMessage(content=analysis_results.format(gemini_response=state["gemini_response"],
                                                                                                                llama_response= state["llama_response"]))])

    return {"answer":response.content}






# Build a simple graph with one node.
builder = StateGraph(OverAllState)

builder.add_node("process image llama", process_image_llama)
builder.add_node("process image gemini",process_image_gemini)
builder.add_node("build answer", build_answer)


builder.add_edge(START, "process image llama")
builder.add_edge(START, "process image gemini")
builder.add_edge("process image llama", "build answer")
builder.add_edge("process image gemini", "build answer")
builder.add_edge("build answer", END)


memory = MemorySaver()
vision_graph = builder.compile(checkpointer=memory)
vision_graph













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
    isImageUploaded : Literal[True,False]
    base64_image:str



def call_chat_model(state: State):
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
    response = llm_gemini.invoke(farmer_bot+state.get("messages")+new_mmsg)
    
    # Wrap the LLM response as an AIMessage.
    ai_message = AIMessage(content=response.content)
    
    # Update the state's messages: append both the human message and the AI response.
    updated_messages = state.get("messages") + add_messages(human_message,ai_message)
    
    # Return the latest AI message; for downstream nodes, you might return the full updated list
    return {"messages": updated_messages }


def call_image_model(state:State):
    # """Deals with any kind of vision logic"""

    # Wrap the human input in a HumanMessage.
    human_message = HumanMessage(content=state.get("query"))
    summary_mssg = state.get("summary","")
    if summary_mssg:
        mmsg_history = f"Summary of conversation from earlier: {summary_mssg}"+"Latest Chat History up until now: \n\n"
    else:
        mmsg_history = "Chat History up until now: \n\n"

    for mssg in state["messages"]:
        if isinstance(mssg, SystemMessage):
            mmsg_history += f"System: {mssg.content.strip()}\n\n"
        elif isinstance(mssg, HumanMessage):
            mmsg_history += f"Human: {mssg.content.strip()}\n\n"
        elif isinstance(mssg, AIMessage):
            mmsg_history += f"AI: {mssg.content.strip()}\n\n"

    user_query = f"User's current query: {state['query']}"

    config = {'configurable': {'thread_id': '1'}}
    vision_graph.invoke({"base64_image":state["base64_image"],"query": mmsg_history+user_query},config)
    response = vision_graph.get_state(config).values["answer"]
    
    # Wrap the LLM response as an AIMessage.
    ai_message = AIMessage(content=response)


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
    response = llm_gemini.invoke(messages)

    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"summary": response.content, "messages": delete_messages}


def handle_input(state:State):
    """Checks if image is the input"""
    if (state["isImageUploaded"]):
        return "image model"
    return "chat model"


def should_trim(state:State):
    """Returns the next node to be executed"""

    messages = state.get("messages")

    if len(messages)> 6:
        return "summarize_convo"
    
    return END



workflow = StateGraph(State)
workflow.add_node("image model", call_image_model)  
workflow.add_node("chat model",call_chat_model)
workflow.add_node("summarize_convo", summarize_convo)



workflow.add_conditional_edges(START, handle_input, ["chat model", "image model"])
workflow.add_conditional_edges("chat model", should_trim, ["summarize_convo",END])
workflow.add_conditional_edges("image model", should_trim, ["summarize_convo",END])
workflow.add_edge("summarize_convo", END)



memory = MemorySaver()
chat_graph = workflow.compile(checkpointer=memory)
chat_graph