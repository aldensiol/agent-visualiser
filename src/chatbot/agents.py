from abc import abstractmethod
from langchain_core.tools import StructuredTool
from typing_extensions import override

from src.chatbot.tools import DBRetrievalTool, KGRetrievalTool, WebSearchTool, AnswerGenerationTool, GradeAnswerTool, RefineAnswerTool
from src.chatbot.state import GraphState

class BaseAgent:
    def __init__(self, 
                 name: str = "Base Agent", 
                 tool: StructuredTool = None):
        self.name = name
        self.tool = tool
    
class BaseRetrievalAgent(BaseAgent):
    def __init__(self, name: str = "Base Retrieval Agent", tool: StructuredTool = None):
        super().__init__(name=name, tool=tool)
    
    @abstractmethod
    async def retrieve(self, query: str):
        pass
    
class BaseGenerationAgent(BaseAgent):
    def __init__(self, name: str = "Base Generation Agent", tool: StructuredTool = None):
        super().__init__(name=name, tool=tool)
        
    @abstractmethod
    async def generate(self, query: str):
        pass
    
class VectorDBRetrievalAgent(BaseRetrievalAgent):
    def __init__(self):
        super().__init__(name="Vector DB Retrieval Agent", 
                         tool=DBRetrievalTool().get_tool())
    
    @override
    async def retrieve(self, state: GraphState) -> GraphState:
        """
        Agent that retrieves context from a Vector DB

        Args:
            state (GraphState): The state of the graph

        Returns:
            GraphState: The updated state of the graph
        """
        print("------- Retrieving Context Via Vector DB -------")
        context = self.tool.invoke({"query": state["query"]})
        return {"db_context": context}
    
class KGDBRetrievalAgent(BaseRetrievalAgent):
    def __init__(self):
        super().__init__(name="KG DB Retrieval Agent",
                         tool=KGRetrievalTool().get_tool())
    
    @override
    async def retrieve(self, state: GraphState) -> GraphState:
        """
        Agent that retrieves context from a Knowledge Graph

        Args:
            query (str): The query to retrieve context

        Returns:
            dict: The retrieved context
        """
        print("------- Retrieving Context Via KG DB -------")
        query = state["query"]
        context = self.tool.invoke({"query": query})
        return {"kg_context": context}
    
class WebSearchAgent(BaseRetrievalAgent):
    def __init__(self):
        super().__init__(name="Web Search Agent",
                         tool=WebSearchTool().get_tool())
    
    @override
    async def retrieve(self, state: GraphState) -> GraphState:
        """
        Agent that retrieves context from the web

        Args:
            query (str): The query to retrieve context

        Returns:
            dict: The retrieved context
        """
        print("------- Retrieving Context Via Web Search -------")
        query = state["query"]
        context = await self.tool.invoke({"query": query})
        return {"websearch_context": context}
    
class AnswerGenerationAgent(BaseGenerationAgent):
    def __init__(self):
        super().__init__(name="Answer Generation Agent",
                         tool=AnswerGenerationTool().get_tool())
    
    @override
    async def generate(self, state: GraphState) -> GraphState:
        """
        Agent that generates an answer to the user query from the Retrieved Context

        Args:
            state (GraphState): The state of the graph

        Returns:
            state (GraphState): The updated state of the graph
        """
        query = state["query"]
        db_context = state["db_context"]
        kg_context = state["kg_context"]
        context = db_context + kg_context
        
        print("------- Generating Answer -------")
        response = await self.tool.ainvoke({"query": query, "context": context})
        print(f"Generated Answer: {response}")
        return {"answer": response}

class AnswerGradingAgent(BaseGenerationAgent):
    def __init__(self):
        super().__init__(name="Answer Grading Agent",
                         tool=GradeAnswerTool().get_tool())
    
    @override
    async def generate(self, state: GraphState) -> GraphState:
        """
        Agent that grades the answer generated by the Answer Generation Agent

        Args:
            state (GraphState): The state of the graph

        Returns:
            state (GraphState): The updated state of the graph
        """
        print("------- Grading Answer -------")
        query = state["query"]
        answer = state["answer"]
        result = self.tool.invoke({"query": query, "answer": answer})
        evaluation, reasoning = result['evaluation'], result['reasoning']
        
        relevance, completeness, coherence, correctness = evaluation["relevance"], evaluation["completeness"], evaluation["coherence"], evaluation["correctness"]
        reason_relevance, reason_completeness, reason_coherence, reason_correctness = reasoning["relevance"], reasoning["completeness"], reasoning["coherence"], reasoning["correctness"]
        
        metrics, reasons = state["metrics"], state["reasons"]
        metrics["relevance"], metrics["completeness"], metrics["coherence"], metrics["correctness"] = relevance, completeness, coherence, correctness
        reasons["relevance"], reasons["completeness"], reasons["coherence"], reasons["correctness"] = reason_relevance, reason_completeness, reason_coherence, reason_correctness
        
        return {
            "metrics": metrics,
            "reasons": reasons
        }
        
class AnswerRefineAgent(BaseGenerationAgent):
    def __init__(self):
        super().__init__(name="Answer Refine Agent",
                         tool=RefineAnswerTool().get_tool())
    
    @override
    async def generate(self, state: GraphState) -> GraphState:
        """
        Refines the initial answer using context retrieved from Websearch

        Args:
            query (str): The user query 
            answer (str): The initial answer generated
            Websearch (str): The context retrieved from the Websearch

        Returns:
            str: The refined answer
        """
        print("------- Refining Answer -------")
        query = state["query"]
        answer = state["answer"]
        websearch_context = state["websearch_context"]
        refined_answer = await self.tool.invoke({"query": query, "answer": answer, "websearch_context": websearch_context})
        return {"answer": refined_answer}
    
def decide_metrics_agent(state: GraphState) -> GraphState:
    """
    Checks the metrics of the answer generated and decides if they are good enough

    Args:
        state (GraphState): The state of the graph

    Returns:
        GraphState: The updated state of the graph
    """
    
    print("------- Deciding If Requires Extra Context from KG -------")
    metric_list = [state["metrics"]["relevance"], state["metrics"]["completeness"], state["metrics"]["coherence"], state["metrics"]["correctness"]]
    print(f"Metrics: {metric_list}")
    for metric in metric_list:
        if metric <= 7:
            "not good enough"
    return "good"