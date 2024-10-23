# src/ui/app.py
import streamlit as st
import asyncio
from datetime import datetime
from typing import Optional
from ..agent.enhanced_agent import EnhancedComputerAgent
from ..tools.results import ToolResult
from .components.chat import render_chat_message
from .components.workflow_sidebar import render_workflow_sidebar
from ..utils.logger import logger

# Page configuration
st.set_page_config(
    page_title="Mac Computer Control",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
with open("src/ui/styles/main.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = EnhancedComputerAgent()
if "current_workflow" not in st.session_state:
    st.session_state.current_workflow = None

async def process_message(
    message: str,
    workflow_id: Optional[str] = None
) -> None:
    """Process a message and update the chat"""
    try:
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now()
        })
        
        # Get agent response
        with st.spinner("Processing..."):
            response = await st.session_state.agent.process_message(
                message,
                workflow_id=workflow_id
            )
        
        # Add assistant response
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now()
        })
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        st.error(f"An error occurred: {str(e)}")

def main():
    st.title("Mac Computer Control")
    
    # Sidebar
    render_workflow_sidebar(
        workflow_manager=st.session_state.agent.workflow_manager,
        on_run_workflow=lambda wid: asyncio.run(
            process_message("", workflow_id=wid)
        )
    )
    
    # Main chat area
    chat_container = st.container()
    
    with chat_container:
        # Display messages
        for message in st.session_state.messages:
            render_chat_message(message)
        
        # Chat input
        if prompt := st.chat_input("What would you like me to do?"):
            asyncio.run(process_message(prompt))

if __name__ == "__main__":
    main()