# Strands Agents & Amazon Bedrock AgentCore Workshop
## AI Agent Development for Life Sciences and Healthcare

This workshop provides hands-on experience building AI Agents for life science research using AWS's new open-source framework **Strands Agents** and **Amazon Bedrock AgentCore** service.

---

## Workshop Overview

### Learning Objectives
- Understand and utilize the Strands Agents framework fundamentals
- Integrate external/internal databases through MCP (Model Context Protocol)
- Build multi-agent systems using Agent-as-Tool pattern
- Deploy to production with Amazon Bedrock AgentCore

### Key Technology Stack
- **Strands Agents**: AWS open-source AI Agent framework
- **Amazon Bedrock**: Claude 3.7 Sonnet model
- **MCP (Model Context Protocol)**: Standardized data integration protocol
- **AWS HealthOmics**: Protein design workflow
- **Amazon Bedrock AgentCore**: Serverless agent deployment platform

---

## Workshop Structure

### 📚 Hands-on Notebooks (notebook/)

#### [00. Environment Setup](notebook/00_setup_environment.ipynb)
- Install required packages and configure environment
- AWS account setup and permission verification
- Enable Bedrock model access

#### [01. External Database Integration via MCP](notebook/01_external_dbs.ipynb)
**Learning Content:**
- MCP server configuration and client integration
- Understanding and implementing Agent-as-Tool pattern
- Multi-agent orchestration

**Integrated Databases:**
- **ArXiv**: Search academic papers and preprints
- **ChEMBL**: Chemical compound and biological activity data
- **PubMed**: Biomedical literature search
- **ClinicalTrials.gov**: Clinical trial information lookup

#### [02. Internal Database Integration](notebook/02_internal_dbs.ipynb)
**Learning Content:**
- Natural language database queries using Text-to-SQL technology
- PostgreSQL internal clinical/genomic data analysis
- Automatic schema exploration and query generation

**Datasets:**
- `chemotherapy_survival`: Patient survival data after chemotherapy
- `clinical_genomic`: Lung cancer patient clinical-genomic integrated data (50+ columns)

**Key Features:**
- Query data using natural language without complex SQL
- Survival analysis, gene expression comparison, mutation analysis

#### [03. Hybrid Tool Integration](notebook/03_hybrid_tools.ipynb)
**Learning Content:**
- Amazon Bedrock Knowledge Base integration
- Unified search across internal documents and external databases
- RAG (Retrieval-Augmented Generation) pattern implementation

**Use Cases:**
- Collect research evidence on HER2 biomarkers
- Integrated search across internal knowledge base + PubMed

#### [04. Protein Design with AWS HealthOmics](notebook/04_protein_design_strands.ipynb)
**Learning Content:**
- Trigger AWS HealthOmics workflows
- Execute protein sequence optimization tasks
- Monitor workflow status and analyze results

**Key Features:**
- Directed evolution algorithm-based protein optimization
- Custom parameter settings (parallel chains, optimization steps)
- Real-time workflow monitoring

#### [05. Production Deployment with Amazon Bedrock AgentCore](notebook/05_production_agentcore.ipynb)
**Learning Content:**
- Implement comprehensive agent integrating all tools
- Operate scalable agents in serverless environment

**Integrated Features:**
- External databases (ArXiv, ChEMBL, PubMed, ClinicalTrials)
- Internal databases (PostgreSQL clinical/genomic data)
- Protein design (AWS HealthOmics)
- Knowledge Base (RAG)

---

## 🌐 Web Application (application/)

After completing the workshop, a fully functional web-based demo application is provided. Built on Streamlit, you can experience all hands-on features through a web interface.

**Key Features:**
- Interactive AI Agent interface
- Real-time research query responses
- Multi-source integrated search

---

## Prerequisites

### AWS Account and Permissions
- AWS account (Event Engine or personal account)
- Permissions for the following services:
  - Amazon Bedrock (Claude 3.7 Sonnet model access)
  - Amazon S3
  - Amazon RDS/Aurora (PostgreSQL)
  - AWS HealthOmics
  - Amazon Bedrock AgentCore

### SageMaker Studio Notebook or Local Environment
- Python 3.9 or higher
- Jupyter Notebook or JupyterLab
- AWS CLI configuration

### Required AWS Resource Deployment
The following CloudFormation stacks must be deployed in advance for workshop exercises:
1. **Networking Infrastructure**: VPC, subnets, etc.
2. **Amazon Aurora PostgreSQL**: Clinical/genomic database
3. **Amazon Bedrock Knowledge Base**: Internal document repository
4. **Protein Design Stack** (`stacks/protein_design_stack.yaml`): AWS HealthOmics workflow

---

## Quick Start

### 1. Environment Setup
```bash
# Clone repository
git clone <repository-url>
cd strands-agents-for-life-science

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install basic packages
pip install boto3 jupyter
```

### 2. Run Jupyter Notebook
```bash
jupyter notebook
```

### 3. Exercise Order
1. `notebook/00_setup_environment.ipynb` - Environment verification and setup
2. `notebook/01_external_dbs.ipynb` - External DB integration
3. `notebook/02_internal_dbs.ipynb` - Internal DB integration
4. `notebook/03_hybrid_tools.ipynb` - Hybrid tools
5. `notebook/04_protein_design_strands.ipynb` - Protein design tool usage
6. `notebook/05_production_agentcore.ipynb` - Production deployment

---

## Key Concepts

### Agent-as-Tool Pattern
A pattern where specialized agents are converted into tools for an orchestrator agent to utilize. Each agent is specialized in a specific domain (e.g., ArXiv search, ChEMBL compound lookup), and the main agent appropriately selects them to answer complex research questions.

### Text-to-SQL
Technology that automatically converts natural language questions into SQL queries. Researchers can query data with natural language questions like "What is the survival rate of EGFR mutation patients?" without knowing complex database schemas.

### MCP (Model Context Protocol)
An open protocol that enables AI agents to communicate with various data sources and tools in a standardized way. Uses stdin/stdout-based JSON-RPC messaging.

---

## Use Cases

### Drug Development
- Target Discovery: Track latest research trends on PubMed/ArXiv
- Lead Discovery: Search candidate compounds in ChEMBL
- Lead Optimization: Optimize protein structures with HealthOmics
- Clinical Strategy: Analyze similar clinical trials from ClinicalTrials.gov

### Precision Medicine
- Personalized Treatment: Analyze similar patient cohorts from internal clinical database
- Biomarker Discovery: Analyze correlations between gene expression data and survival rates
- Literature-based Decision Making: Automatically collect and summarize latest research evidence

### Research Acceleration
- Automated Literature Review: Search multiple databases simultaneously
- Integrated Data Analysis: Combine external public data + internal clinical data
- Hypothesis Generation: AI-based pattern discovery and research direction suggestions

---

## Project Structure

```
strands-agents-for-life-science/
├── notebook/                          # Hands-on notebooks
│   ├── 00_setup_environment.ipynb
│   ├── 01_external_dbs.ipynb
│   ├── 02_internal_dbs.ipynb
│   ├── 03_hybrid_tools.ipynb
│   ├── 04_protein_design_strands.ipynb
│   ├── 05_production_agentcore.ipynb
│   ├── documents/                     # Documents for Knowledge Base
│   ├── images/                        # Notebook images
│   ├── stacks/                        # CloudFormation templates
│   └── utils/                         # Helper functions
├── application/                       # Web demo application
│   ├── app.py                         # Streamlit main app
│   ├── mcp_server_*.py               # MCP server implementation
│   ├── pages/                         # Web pages
│   ├── requirements.txt
│   └── README.md
└── README.md                          # This file
```

---

## Troubleshooting

### Bedrock Model Access Error
**Symptom**: "Access denied to model" error occurs
**Solution**: Go to AWS Console > Bedrock > Model access and enable Claude 3.7 Sonnet model

### RDS Connection Failure
**Symptom**: PostgreSQL connection timeout error
**Solution**:
- Check port 5432 inbound rule in Security Group
- Verify RDS endpoint is configured correctly
- Check VPC settings and notebook environment network

### MCP Server Start Failure
**Symptom**: MCP client connection error
**Solution**:
- Check Python version (3.9 or higher required)
- Reinstall required packages: `pip install mcp arxiv chembl-webresource-client`

---

## References

- [Strands Agents Official Documentation](https://strandsagents.com/)
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [AWS HealthOmics Documentation](https://docs.aws.amazon.com/omics/)

---

## License

This project is distributed under the MIT-0 license. Feel free to use, modify, and distribute.

---

## Contributions and Feedback

For questions or suggestions, please reach out through GitHub Issues.

**Enjoy the workshop and welcome to the world of life science AI Agent development!** 🧬🤖
