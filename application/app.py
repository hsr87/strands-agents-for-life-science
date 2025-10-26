import streamlit as st
import chat
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("streamlit")

# Page configuration
st.set_page_config(
    page_title='Life Science Research AI Assistant',
    page_icon='🧬',
    layout="centered",
    initial_sidebar_state="auto",
    menu_items=None
)

with st.sidebar:
    st.title("🧬 Life Science Research AI Assistant")

    st.markdown(
        """
        Welcome to the **Strands Agents & Amazon Bedrock AgentCore** Workshop Web Demo!
        ---

        For detailed code, please visit [Github](https://github.com/hsr87/strands-agents-for-life-science).
        """
    )

    st.markdown("---")

    # Model selection
    modelName = st.selectbox(
        '🤖 Model Selection',
        ('Claude 3.7 Sonnet', 'Claude 3.5 Sonnet', 'Claude 3.5 Haiku'),
        index=0
    )

    # Extended thinking (reasoning mode)
    select_reasoning = st.checkbox(
        '🧠 Enable Extended Thinking (Claude 3.7 Sonnet only)',
        value=False
    )
    reasoningMode = 'Enable' if select_reasoning and modelName == 'Claude 3.7 Sonnet' else 'Disable'
    logger.info(f"reasoningMode: {reasoningMode}")

    chat.update(modelName, reasoningMode)

    st.markdown("---")

    # Clear conversation button
    clear_button = st.button("🔄 Reset Conversation", key="clear")

# Main title
st.title('🧬 Life Science Research AI Assistant')

# Clear conversation if button clicked
if clear_button is True:
    chat.initiate()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.greetings = False

# Display chat messages from history
def display_chat_messages():
    """Display message history"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

display_chat_messages()

# Greet user
if not st.session_state.greetings:
    with st.chat_message("assistant"):
        intro = """
        Hello! I'm the **Life Science Research AI Assistant**.

        I can help you with questions like:

        **📚 External Database Search Examples:**
        - "Find the latest research papers on HER2 protein"

        **💾 Internal Database Query Examples:**
        - "What tables are available in the database?"

        **🧬 Protein Design Examples:**
        - "Optimize the following antibody sequence: EVQLVETGGGLVQPGGSLRLSCAASGFTLNSYGISWVRQAPGKGPEWVS - optimize for improved stability and binding affinity"

        How can I help you today?
        """
        st.markdown(intro)
        st.session_state.messages.append({"role": "assistant", "content": intro})
        st.session_state.greetings = True

# Reset conversation if clear button clicked
if clear_button or "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.greetings = False
    st.rerun()
    chat.clear_chat_history()

# Chat input
if prompt := st.chat_input("Enter your question..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    prompt = prompt.replace('"', "").replace("'", "")
    logger.info(f"prompt: {prompt}")

    # Generate and display assistant response
    with st.chat_message("assistant"):
        response = chat.run_multi_agent_system(prompt, "Enable", st)

    # Add assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": response})
