import chainlit as cl

from langchain_core.messages import AIMessageChunk

from src.chatbot.input import BASE_INPUTS
from src.chatbot.workflow import graph

@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Medicines for Diabetes",
            message="What are some Medicines for Diabetes?",
            icon="https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/740-pill.svg/1200px-740-pill.svg.png",
            ),
        cl.Starter(
            label="Exercises for diabetics",
            message="Please suggest some appropriate exercises for diabetics with heart conditions.",
            icon="https://www.svgrepo.com/show/427306/fitness-workout-healthy.svg",
            ),
        cl.Starter(
            label="Diabetes Management Plan",
            message="Can you provide a comprehensive weekly plan for a newly diagnosed type 2 diabetic who is also overweight, has high blood pressure, and a family history of kidney disease? Include dietary recommendations, exercise routines, blood sugar monitoring schedule, potential medications, and lifestyle changes. Also, explain how this plan might need to be adjusted as the patient ages or if complications arise.",
            icon="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRtc4e90qSf97_dpcWCXKHDGI4wuUnmLnnmWg&s",
            )
        ]
    
@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("graph", graph)

@cl.on_message
async def on_message(message: cl.Message):
    
    graph = cl.user_session.get("graph")
    
    # Create an initial state
    inputs = BASE_INPUTS.copy()
    inputs["query"] = str(message.content)
    
    first = True
    final_answer = ""
    
    # Create a Chainlit message that we'll update
    chainlit_message = cl.Message(content="")
    
    # Stream the results
    async for message, update in graph.astream(inputs, stream_mode=["messages", "updates"]):
        if message == "messages":
            chunk = update[0]
            metadata = update[1]
            if first:
                await chainlit_message.send()
                chainlit_message.content += "Answer Generation Agent's Initial Answer: \n\n"
                first = False
            
            chainlit_message.content += chunk.content if metadata.get('langgraph_node') != 'grader' else ""
            final_answer += chunk.content if metadata.get('langgraph_node') != 'grader' else ""
            await chainlit_message.update()
        
        elif message == "updates": 
            # update is a dictionary here
            retrieved_context = (
                    update.get('search_vector_db', {}).get('db_context') or
                    update.get('search_kg_db', {}).get('kg_context') or
                    update.get('websearch', {}).get('websearch_context')
            )
            
            if not retrieved_context:
                continue
            
            vector_db = True if update.get('search_vector_db') else False
            kg_db = True if update.get('search_kg_db') else False
            websearch = True if update.get('websearch') else False
            
            if vector_db:
                context_elements = [
                    cl.Text(name="Vector DB Retriever Agent", display = "side", content=retrieved_context)
                ]
                await cl.Message(content="Vector DB Retriever Agent", elements=context_elements).send()
            
            elif kg_db:
                context_elements = [
                    cl.Text(name="KG DB Retriever Agent", display = "side", content=retrieved_context)
                ]
                await cl.Message(content="KG DB Retriever Agent", elements=context_elements).send()
            
            elif websearch:
                context_elements = [
                    cl.Text(name="Websearch Agent", display = "side", content=retrieved_context)
                ]
                await cl.Message(content="Websearch Agent", elements=context_elements).send()
            
            source_elements = [
                cl.Pdf(name="Diabetes Treatment_ Insulin", display="inline", path="src/pdfs/Diabetes Treatment_ Insulin.pdf")
            ]
            
            await cl.Message(content="Diabetes Treatment_ Insulin", elements=source_elements).send()
            
    await cl.Message(content=f"Final Chosen Answer: \n\n{final_answer}").send()