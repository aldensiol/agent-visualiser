# Streamlit-Agent-Visualiser: A Visual Learning Tool for Agentic Workflows

Welcome to the **Streamlit-Agent-Visualiser**! This project is designed as a visual and interactive tool to learn and explore the fascinating world of Retrieval-Augmented Generation (RAG) systems and Agentic workflows.

## 🌟 Project Overview

This chatbot serves as both a personal learning tool and an educational platform to ease the introduction to others about **Agentic workflows** and **RAG systems**. It is built using **Streamlit** to provide an intuitive interface with cool visualisations that illustrate how agents think, reason, and make decisions in real time.

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
- **Streamlit**: `pip install streamlit`
- **LangGraph**: `pip install langgraph`
- **LangChain**: `pip install langchain`
- **AWS SDK for Python (Boto3)**: `pip install boto3`
- **Neo4j Driver**: `pip install neo4j`
- **Relik**: [Relik Installation Guide](https://medium.com/neo4j/entity-linking-and-relationship-extraction-with-relik-in-llamaindex-ca18892c169f)

### Installation

1. **Clone the Repository**
    ```bash
    git clone https://github.com/your-username/streamlit-rag-chatbot.git
    cd streamlit-rag-chatbot

2. **Install Required Packages**
    ```
    pip install -r requirements.txt

3. **Run the Streamlit App**
    ```
    streamlit run streamlit_app.py

## 🌐 Project Structure
    ```
    streamlit-rag-chatbot/
    │
    ├── notebooks/                      # Jupyter Notebooks for exploratory analysis
    │   └── agentic_flow.ipynb          # Notebook for agentic flow exploration
    │
    ├── src/                            # Source code for the chatbot
    │   ├── chatbot/                    # Core chatbot logic
    │   │   ├── prompts/                # Prompts and agent logic
    │   │   │   ├── prompts.py          # Predefined prompts for the chatbot
    │   │   │   ├── __init__.py         
    │   │   ├── agents.py               # Agent management and decision making logic
    │   │   ├── utils.py                # Utility functions
    │   │
    │   ├── graph/                      # Graph-based components
    │   │   ├── __init__.py             
    │   │   ├── build_graph.py          # Script to build and initialize the knowledge graph
    │   │   ├── query_graph.py          # Query functions for interacting with the graph database
    │   │
    │   ├── ui/                         # User Interface components for Streamlit
    │   │   ├── __init__.py             
    │   │   ├── components.py           # Streamlit UI components and layout
    │
    ├── .env                            # Environment variables and API keys
    ├── .gitignore                      # Git ignore file
    ├── README.md                       # Project documentation
    ├── requirements.txt                # Python dependencies
    └── streamlit_app.py                # Main Streamlit application file

