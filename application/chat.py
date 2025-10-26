import info
import traceback
import uuid
import logging
import sys
import asyncio
import os
from botocore.config import Config
from strands import Agent, tool
from strands.models import BedrockModel
from strands.agent.conversation_manager import SlidingWindowConversationManager
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d | %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("chat")

model_name = "Claude 3.7 Sonnet"
model_type = "claude"
debug_mode = "Enable"
model_id = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
models = info.get_model_info(model_name)
reasoning_mode = 'Disable'

def update(modelName, reasoningMode):
    global model_name, model_id, model_type, reasoning_mode

    if model_name != modelName:
        model_name = modelName
        logger.info(f"model_name: {model_name}")

        models_info = info.get_model_info(model_name)
        model_id = models_info[0]["model_id"]
        model_type = models_info[0]["model_type"]

    if reasoningMode != reasoning_mode:
        reasoning_mode = reasoningMode
        logger.info(f"reasoning_mode: {reasoning_mode}")

def initiate():
    global userId
    userId = uuid.uuid4().hex
    logger.info(f"userId: {userId}")

#########################################################
# Strands Agent Model Configuration
#########################################################
def get_model():
    models_info = info.get_model_info(model_name)
    profile = models_info[0]

    if profile['model_type'] == 'nova':
        STOP_SEQUENCE = '"\n\n<thinking>", "\n<thinking>", " <thinking>"'
    elif profile['model_type'] == 'claude':
        STOP_SEQUENCE = "\n\nHuman:"

    if model_type == 'claude':
        maxOutputTokens = 64000
    else:
        maxOutputTokens = 5120

    maxReasoningOutputTokens = 64000
    thinking_budget = min(maxOutputTokens, maxReasoningOutputTokens-1000)

    if reasoning_mode == 'Enable':
        model = BedrockModel(
            boto_client_config=Config(
               read_timeout=900,
               connect_timeout=900,
               retries=dict(max_attempts=3, mode="adaptive"),
            ),
            model_id=model_id,
            max_tokens=64000,
            stop_sequences=[STOP_SEQUENCE],
            temperature=1,
            additional_request_fields={
                "thinking": {
                    "type": "enabled",
                    "budget_tokens": thinking_budget,
                }
            },
        )
    else:
        model = BedrockModel(
            boto_client_config=Config(
               read_timeout=900,
               connect_timeout=900,
               retries=dict(max_attempts=3, mode="adaptive"),
            ),
            model_id=model_id,
            max_tokens=maxOutputTokens,
            stop_sequences=[STOP_SEQUENCE],
            temperature=0.1,
            top_p=0.9,
            additional_request_fields={
                "thinking": {
                    "type": "disabled"
                }
            }
        )
    return model

conversation_manager = SlidingWindowConversationManager(
    window_size=10,
)

# MCP Clients for various databases
arxiv_mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(command="python", args=["mcp_server_arxiv.py"])
))

pubmed_mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(command="python", args=["mcp_server_pubmed.py"])
))

chembl_mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(command="python", args=["mcp_server_chembl.py"])
))

clinicaltrials_mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(command="python", args=["mcp_server_clinicaltrial.py"])
))

internal_db_mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(command="python", args=["mcp_server_internal_db.py"])
))

#########################################################
# Import Protein Design Tools
#########################################################
try:
    from utils.protein_design_tools import trigger_protein_optimization, monitor_protein_workflow
    PROTEIN_TOOLS_AVAILABLE = True
    logger.info("Protein design tools loaded successfully")

except ImportError as e:
    logger.warning(f"Protein design tools not available: {e}")
    PROTEIN_TOOLS_AVAILABLE = False

#########################################################
# Main Orchestrator Agent
#########################################################
def create_orchestrator_agent(
    history_mode,
    arxiv_client=None,
    pubmed_client=None,
    chembl_client=None,
    clinicaltrials_client=None,
    internal_db_client=None
):
    """
    Create orchestrator agent that integrates all capabilities:
    - External databases (ArXiv, PubMed, ChEMBL, ClinicalTrials)
    - Internal database (PostgreSQL)
    - Protein design tools (AWS HealthOmics)
    """

    system = """
    You are an integrated AI assistant for life science research. You provide the following capabilities:

    ## 1. External Database Search
    - **ArXiv**: Search academic papers and preprints
    - **PubMed**: Search biomedical literature
    - **ChEMBL**: Search chemical compounds and biological activity data
    - **ClinicalTrials.gov**: Search clinical trial information

    ## 2. Internal Database Analysis (Text2SQL)
    - Analyze clinical and genomic data stored in PostgreSQL database
    - Automatically convert natural language questions to SQL queries
    - Database schema:
      * chemotherapy_survival: Patient survival data after chemotherapy
      * clinical_genomic: Integrated clinical and genomic data for lung cancer patients

    ## 3. Protein Design
    - Optimize protein sequences through AWS HealthOmics workflows
    - Apply directed evolution algorithms
    - Monitor workflow execution

    ## Usage Guidelines:
    1. Select and use appropriate tools based on the question content
    2. For database-related questions, first check the schema before generating SQL
    3. Provide comprehensive answers by integrating multiple data sources
    4. Always clearly present sources and evidence
    """

    model = get_model()

    try:
        # Collect all tools
        tools = []

        # Add ArXiv tools
        if arxiv_client:
            arxiv_tools = arxiv_client.list_tools_sync()
            logger.info(f"arxiv_tools: {len(arxiv_tools)} tools loaded")
            tools.extend(arxiv_tools)

        # Add PubMed tools
        if pubmed_client:
            pubmed_tools = pubmed_client.list_tools_sync()
            logger.info(f"pubmed_tools: {len(pubmed_tools)} tools loaded")
            tools.extend(pubmed_tools)

        # Add ChEMBL tools
        if chembl_client:
            chembl_tools = chembl_client.list_tools_sync()
            logger.info(f"chembl_tools: {len(chembl_tools)} tools loaded")
            tools.extend(chembl_tools)

        # Add ClinicalTrials tools
        if clinicaltrials_client:
            clinicaltrials_tools = clinicaltrials_client.list_tools_sync()
            logger.info(f"clinicaltrials_tools: {len(clinicaltrials_tools)} tools loaded")
            tools.extend(clinicaltrials_tools)

        # Add Internal DB tools
        if internal_db_client:
            internal_db_tools = internal_db_client.list_tools_sync()
            logger.info(f"internal_db_tools: {len(internal_db_tools)} tools loaded")
            tools.extend(internal_db_tools)

        # Add Protein Design tools if available
        if PROTEIN_TOOLS_AVAILABLE:
            tools.extend([trigger_protein_optimization, monitor_protein_workflow])
            logger.info("protein_design_tools: 2 tools loaded")

        logger.info(f"Total tools available: {len(tools)}")

        # Create agent with conversation history if enabled
        if history_mode == "Enable":
            logger.info("history_mode: Enable")
            orchestrator = Agent(
                model=model,
                system_prompt=system,
                tools=tools,
                conversation_manager=conversation_manager
            )
        else:
            logger.info("history_mode: Disable")
            orchestrator = Agent(
                model=model,
                system_prompt=system,
                tools=tools
            )

        return orchestrator
    except Exception as e:
        logger.error(f"Error initializing orchestrator agent: {e}")
        logger.error(traceback.format_exc())
        # Return basic agent if error occurs
        return Agent(
            model=model,
            system_prompt=system,
            tools=tools if 'tools' in locals() else []
        )

def run_multi_agent_system(question, history_mode, st):
    """
    Run the integrated multi-agent system with all capabilities
    """
    message_placeholder = st.empty()
    full_response = ""

    async def process_streaming_response():
        nonlocal full_response
        try:
            # Open all MCP client sessions
            with arxiv_mcp_client as arxiv_client, \
                 pubmed_mcp_client as pubmed_client, \
                 chembl_mcp_client as chembl_client, \
                 clinicaltrials_mcp_client as clinicaltrials_client, \
                 internal_db_mcp_client as internal_db_client:

                # Create orchestrator with all active clients
                current_orchestrator = create_orchestrator_agent(
                    history_mode,
                    arxiv_client=arxiv_client,
                    pubmed_client=pubmed_client,
                    chembl_client=chembl_client,
                    clinicaltrials_client=clinicaltrials_client,
                    internal_db_client=internal_db_client
                )

                # Stream response
                agent_stream = current_orchestrator.stream_async(question)
                async for event in agent_stream:
                    if "data" in event:
                        full_response += event["data"]
                        message_placeholder.markdown(full_response)

        except Exception as e:
            logger.error(f"Error in streaming response: {e}")
            logger.error(traceback.format_exc())
            error_msg = "Sorry, an error occurred while generating the response."
            message_placeholder.markdown(error_msg)

    asyncio.run(process_streaming_response())

    return full_response

def clear_chat_history():
    """Clear conversation history"""
    global conversation_manager
    conversation_manager = SlidingWindowConversationManager(window_size=10)
    logger.info("Chat history cleared")
