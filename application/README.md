# Life Science Research AI Assistant

An integrated life science research platform utilizing **Strands Agents** and **Amazon Bedrock AgentCore**.

This application is a complete Streamlit web application example that integrates the features covered in AWS workshop notebooks (01-04).

Additional configuration such as DB setup (steps 2-4) is required for actual execution.

---

## Key Features

### 📚 1. External Database Search (Notebook 01)

Access external databases via MCP (Model Context Protocol):

- **ArXiv**: Search academic papers and preprints
- **PubMed**: Biomedical literature search
- **ChEMBL**: Chemical compound and biological activity data
- **ClinicalTrials.gov**: Clinical trial information

**Example Questions:**
```
"Find the latest research papers on HER2 protein"
"Tell me about the biological activity data of aspirin"
"Search for clinical trial information related to breast cancer"
```

### 💾 2. Internal Database Analysis (Notebook 02)

Analyze clinical and genomic data in PostgreSQL database using **Text2SQL** technology:

- **chemotherapy_survival**: Patient survival data after chemotherapy
- **clinical_genomic**: Lung cancer patient clinical and genomic integrated data

**Example Questions:**
```
"Tell me the average age of adenocarcinoma patients"
"Analyze the survival rate of patients with EGFR mutations"
"Compare LRIG1 gene expression levels between surviving and deceased patients after chemotherapy"
```

### 🔬 3. Hybrid Tool Integration (Notebook 03)

Integrated search across internal knowledge base (Amazon Bedrock Knowledge Base) and external data sources (PubMed):

**Example Questions:**
```
"Search for evidence on the effectiveness of HER2-targeted therapies in HER2-positive breast cancer from both internal knowledge base and PubMed"
```

### 🧪 4. Protein Design (Notebook 04)

Protein sequence optimization through AWS HealthOmics workflow:

- Apply directed evolution algorithm
- Execute and monitor workflow
- Analyze optimization results

**Example Questions:**
```
"Optimize this protein sequence: EVQLVETGGGLVQPGGSLRLSCAASGFTLN..."
"Run protein optimization with 20 parallel chains and 200 steps"
"Check the workflow execution status"
```

---

## Installation and Execution

### Prerequisites

1. **Python 3.9 or higher**
2. **AWS account and credential setup**
3. **Required AWS resources** (refer to workshop environment setup notebook 00):
   - Amazon RDS (PostgreSQL)
   - Amazon Bedrock access permissions
   - AWS HealthOmics workflow (for protein design feature)

### Installation

```bash
# Clone repository
git clone <repository-url>
cd application

# Install dependencies
pip install -r requirements.txt
```

### Environment Variable Setup

Set the following environment variables to use the internal database:

```bash
export DB_HOST="your-rds-endpoint"
export DB_PORT="5432"
export DB_NAME="agentdb"
export DB_USER="dbadmin"
export DB_PASSWORD="your-password"
```

Additional setup is required for the protein design feature (refer to notebook 04).

### Execution

```bash
# Run Streamlit app
streamlit run app.py
```

Access in browser at `http://localhost:8501`.

---

## Architecture

```
Life Science Research AI Assistant
│
├── Streamlit UI (app.py)
│   └── User Interface
│
├── Orchestrator Agent (chat.py)
│   ├── External DB Agents
│   │   ├── ArXiv MCP Client
│   │   ├── PubMed MCP Client
│   │   ├── ChEMBL MCP Client
│   │   └── ClinicalTrials MCP Client
│   │
│   ├── Internal DB Agent
│   │   └── PostgreSQL MCP Client
│   │
│   └── Protein Design Agent
│       └── AWS HealthOmics Tools
│
└── MCP Servers
    ├── mcp_server_arxiv.py
    ├── mcp_server_pubmed.py
    ├── mcp_server_chembl.py
    ├── mcp_server_clinicaltrial.py
    └── mcp_server_internal_db.py
```

### MCP (Model Context Protocol)

MCP is a protocol that enables AI agents to communicate with external tools and data sources:

- **MCP Server**: Independent process providing specific functionality
- **MCP Client**: Interface allowing agents to invoke server functionality
- **Communication Method**: stdin/stdout-based JSON-RPC

---

## Technology Stack

- **Strands Agents**: Open-source AI agent framework
- **Amazon Bedrock**: Provides foundation models like Claude 3.7 Sonnet
- **Amazon RDS (PostgreSQL)**: Store clinical and genomic data
- **AWS HealthOmics**: Execute life science workflows
- **Streamlit**: Web UI framework
- **MCP (Model Context Protocol)**: Tool integration protocol

---

## Usage Examples

### Comprehensive Analysis Request

```
Question: "Provide a comprehensive analysis of HER2-positive breast cancer"

AI Assistant's Tasks:
1. Search for latest research papers on ArXiv
2. Search biomedical literature on PubMed
3. Search HER2-related compound data on ChEMBL
4. Search related clinical trials on ClinicalTrials.gov
5. Analyze HER2-related patient data from internal DB
6. Generate comprehensive report by synthesizing all information
```

### Text2SQL Example

```
Question: "How many patients over 50 who are smokers have EGFR mutations?"

AI Assistant's Tasks:
1. Analyze schema (fetch_table_schema)
2. Generate SQL query:
   SELECT COUNT(*)
   FROM clinical_genomic
   WHERE Age_at_Histological_Diagnosis >= 50
     AND Smoking_status LIKE '%smoker%'
     AND EGFR_mutation_status LIKE '%Mutant%'
3. Execute query (execute_postgres_query)
4. Interpret results in natural language
```

---

## Limitations

- This application was created for **educational and demo purposes**
- Additional security and performance optimization are needed for **production environment** use
- External API rate limits may apply

---

## Troubleshooting

### MCP Server Connection Error

```bash
# Verify MCP server runs correctly
python application/mcp_server_arxiv.py
```

### Database Connection Error

```bash
# Check environment variables
echo $DB_HOST
echo $DB_PORT

# Verify RDS endpoint accessibility
psql -h $DB_HOST -U $DB_USER -d $DB_NAME
```

### Protein Design Feature Error

Verify that the CloudFormation stack (`protein-design-stack`) has been deployed successfully.

## References

- [Strands Agents Documentation](https://strandsagents.com/)
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [AWS HealthOmics Documentation](https://docs.aws.amazon.com/omics/)
- [MCP Protocol](https://modelcontextprotocol.io/)

## License

MIT-0 License
