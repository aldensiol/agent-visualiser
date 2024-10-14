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
            icon="https://www.svgrepo.com/show/109551/pill.svg",
            ),
        cl.Starter(
            label="Exercises for diabetics",
            message="Please suggest some appropriate exercises for diabetics with heart conditions.",
            icon="https://cdni.iconscout.com/illustration/premium/thumb/exercise-illustration-download-in-svg-png-gif-file-formats--dumbbells-fitness-exercises-with-biceps-workout-doing-artistry-pack-people-illustrations-5295079.png",
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
    await chainlit_message.send()
    
    # Stream the results
    async for msg, metadata in graph.astream(inputs, stream_mode="messages"):
        
        print(f"METADATA: {metadata}")
        print("=====" * 20)
        
        if isinstance(msg, AIMessageChunk):
            if first:
                chainlit_message.content += "Initial Answer: \n\n"
                first = False
            
            chainlit_message.content += msg.content if metadata.get('langgraph_node') != 'grader' else ""
            final_answer += msg.content if metadata.get('langgraph_node') != 'grader' else ""
            await chainlit_message.update()

    await cl.Message(content=f"Final Chosen Answer: \n\n{final_answer}").send()