from langgraph.graph import START, END, StateGraph

from src.chatbot.agents import VectorDBRetrievalAgent, KGDBRetrievalAgent, WebSearchAgent, AnswerGenerationAgent, AnswerGradingAgent, AnswerRefineAgent, decide_metrics_agent
from src.chatbot.state import GraphState
    
# retrieval agents
retrieve_db_agent = VectorDBRetrievalAgent().retrieve
retrieve_kg_agent = KGDBRetrievalAgent().retrieve
websearch_agent = WebSearchAgent().retrieve

# generation agents
generate_answer_agent = AnswerGenerationAgent().generate
grader_agent = AnswerGradingAgent().generate
refine_answer_agent = AnswerRefineAgent().generate
    
def get_full_graph():
    """
    Generates workflow with all Retrieval Nodes and Agents

    Returns:
       `CompiledGraph` : Compiles the state graph into a `CompiledGraph` object.
        The compiled graph implements the `Runnable` interface and can be invoked,
        streamed, batched, and run asynchronously.
    """
    builder = StateGraph(GraphState)

    builder.add_node("search_kg_db", retrieve_kg_agent)
    builder.add_node("search_vector_db", retrieve_db_agent)
    builder.add_node("generate_answer", generate_answer_agent)
    builder.add_node("grader", grader_agent)
    builder.add_node("websearch", websearch_agent)
    builder.add_node("refine_answer", refine_answer_agent)
    
    builder.add_edge(START, "search_vector_db")
    builder.add_edge(START, "search_kg_db")

    builder.add_edge(["search_kg_db", "search_vector_db"], "generate_answer")
    builder.add_edge("generate_answer", "grader")

    builder.add_conditional_edges(
        "grader",
        decide_metrics_agent,
        {
            "good": END,
            "not good enough": "websearch"
        }
    )
    
    builder.add_edge("websearch", "refine_answer")

    builder.add_edge("refine_answer", "grader")

    graph = builder.compile()
    
    return graph

def get_vector_graph():
    """
    Generates workflow with Vector DB Node and the rest of the Agents

    Returns:
       `CompiledGraph` : Compiles the state graph into a `CompiledGraph` object.
        The compiled graph implements the `Runnable` interface and can be invoked,
        streamed, batched, and run asynchronously.
    """
    builder = StateGraph(GraphState)
    
    builder.add_node("search_vector_db", retrieve_db_agent)
    builder.add_node("generate_answer", generate_answer_agent)
    builder.add_node("grader", grader_agent)
    builder.add_node("websearch", websearch_agent)
    builder.add_node("refine_answer", refine_answer_agent)
    
    builder.set_entry_point("search_vector_db")
    
    builder.add_edge("search_vector_db", "generate_answer")
    
    builder.add_edge("generate_answer", "grader")
    
    builder.add_conditional_edges(
        "grader",
        decide_metrics_agent,
        {
            "good": END,
            "not good enough": "websearch"
        }
    )
    
    builder.add_edge("websearch", "refine_answer")
    
    builder.add_edge("refine_answer", "grader")
    
    graph = builder.compile()
    
    return graph

def get_kg_graph():
    """
    Generates workflow with KG DB Node and the rest of the Agents

    Returns:
       `CompiledGraph` : Compiles the state graph into a `CompiledGraph` object.
        The compiled graph implements the `Runnable` interface and can be invoked,
        streamed, batched, and run asynchronously.
    """
    builder = StateGraph(GraphState)
    
    builder.add_node("search_kg_db", retrieve_kg_agent)
    builder.add_node("generate_answer", generate_answer_agent)
    builder.add_node("grader", grader_agent)
    builder.add_node("websearch", websearch_agent)
    builder.add_node("refine_answer", refine_answer_agent)
    
    builder.set_entry_point("search_kg_db")
    
    builder.add_edge("search_kg_db", "generate_answer")
    
    builder.add_edge("generate_answer", "grader")
    
    builder.add_conditional_edges(
        "grader",
        decide_metrics_agent,
        {
            "good": END,
            "not good enough": "websearch"
        }
    )
    
    builder.add_edge("websearch", "refine_answer")
    
    builder.add_edge("refine_answer", "grader")
    
    graph = builder.compile()
    
    return graph

full_graph = get_full_graph()
vector_graph = get_vector_graph()
kg_graph = get_kg_graph()