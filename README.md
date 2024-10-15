# Agent-Visualiser: A Visual Learning Tool for Agentic Workflows

Welcome to the **Agent-Visualiser**! This project is designed as a visual and interactive tool to learn and explore the fascinating world of Retrieval-Augmented Generation (RAG) systems and Agentic workflows.

## 🌟 Project Overview

This chatbot serves as both a personal learning tool and an educational platform to ease the introduction to others about **Agentic workflows** and **RAG systems**. It is built using **Chainlit** to provide an intuitive interface with cool visualisations that illustrate how agents think, reason, and make decisions in real time.

![Alt text](/images/Iterative_Workflow.drawio.png "Iterative Workflow")

### Key Features

- **Visual Decision Making:** Real-time visualisation of agent decision-making processes.
- **Interactive Learning Tool:** Offers an interactive way to learn about RAG systems, graph databases, and their applications.
- **Dual Database Setup:** Combines a vector-based search engine with a knowledge graph database to provide diverse information retrieval capabilities.
- **Flow Engineering with LangGraph:** Utilises LangGraph for defining, visualising, and executing workflows. 

## 🔍 How It Works

1. **LangGraph Workflows:** The tool uses **LangGraph** to engineer and compile workflows. In my personal opinion, LangGraph strikes the right balance between autonomous agent decisions and deterministic outcomes, which makes it my ideal choice this project.
2. **Information Retrieval:** 
   - **Vector Database:** Implemented using AWS OpenSearch, allowing for efficient and scalable vector-based information retrieval.
   - **Graph Database:** Uses **Neo4j** as the knowledge graph database, populated using **Relik** for a lightweight and quick approach, without relying on large language models (LLMs). As such, the preprocessing of documents involved splitting coreference resolution, Named Entity Recognition (NER), Entity Linking (EL), and Relationship Extraction (RE) into it's own processes.

## 🚀 Getting Started

### Prerequisites

- **Python**: Make sure you have Python 3.10 or higher installed.
- **Chainlit**: `pip install chainlit`
- **LangGraph**: `pip install langgraph`
- **LangChain**: `pip install langchain`
- **AWS SDK for Python (Boto3)**: `pip install boto3`
- **Neo4j Driver**: `pip install neo4j`
- **Relik**: [Relik Installation Guide](https://medium.com/neo4j/entity-linking-and-relationship-extraction-with-relik-in-llamaindex-ca18892c169f)

### Installation

1. **Clone the Repository**
    ```bash
    git clone https://github.com/aldensiol/agent-visualiser
    cd agent-visualiser

2. **Install Required Packages**
    ```
    pip install -r requirements.txt

3. **Run the Streamlit App**
    ```
    chainlit run app.py -w

## 🌐 Project Structure
    STREAMLIT-AGENT/
    ├── notebooks/                           # Jupyter notebooks for different workflows
    │   ├── agentic_flow.ipynb               # Uses LangGraph to build an Agentic RAG System
    │   ├── graph_ingestion.ipynb            # Ingests documents into a knowledge graph
    │   └── zillis_ingestion.ipynb           # Ingests documents into a vector database (Zilliz/Milvus)
    ├── src/                                 
    │   ├── chatbot/                         # Chatbot logic and related scripts
    │   │   ├── prompts/                     # Contains prompt templates and initialisations
    │   │   │   ├── prompts.py               # Script for handling chatbot prompts
    │   │   ├── agents.py                    # Defines various agent behaviors
    │   │   ├── utils.py                     # Utility functions for the chatbot
    │   │   ├── workflow.py                  # Workflow management for the chatbot processes
    │   │   └── __init__.py                 
    │   │
    │   ├── data/                            # Data-related scripts and management
    │   │
    │   ├── graph/                           # Knowledge graph database management (Neo4j)
    │   │   ├── __init__.py                  
    │   │   ├── build_graph.py               # Script to build the knowledge graph
    │   │   └── query_graph.py               # Script to query the knowledge graph
    │   │
    │   ├── pdfs/                            # PDF handling or storage
    │   │
    │   ├── schema/                          # API Data Requests
    │   │   ├── __init__.py                 
    │   │   └── data.py                      # Pydantic handling
    │   │
    │   ├── services/                        # Service layer for backend functionality
    │   │   ├── __init__.py                 
    │   │   └── services.py                  # Core service implementations
    │   │
    │   ├── ui/                              # User interface components
    │   │   ├── __init__.py                  
    │   │   └── components.py                # UI components used in the Streamlit app
    │   │
    │   ├── utils/                           # Vector database management (Zilliz/Milvus)
    │   │   ├── __init__.py                  
    │   │   └── utils.py                     # Utility Functions for Document Parsing
    │   │
    │   ├── vector/                          # Vector database management (Zilliz/Milvus)
    │   │   ├── __init__.py                  
    │   │   ├── create_collection.py         # Script to create vector collections
    │   │   ├── create_index.py              # Script to create vector indices
    │   │   └── query_index.py               # Script to query vector indices
    │   │
    │   ├── __init__.py
    │   ├── app.py                           # API endpoints
    │   └── main.py                          # FastAPI Ports
    │
    ├── .gitignore                           
    ├── README.md                            # Project documentation and overview
    ├── requirements.txt                     # Python dependencies required for the project
    └── app.py                               # Main entry point for the Chainlit application
