import chainlit as cl

from src.chatbot.input import BASE_INPUTS
from src.chatbot.workflow import graph
from utils import *

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
            label="Complex Diet & Exercise Plan",
            message="Design a 4-week exercise plan for a newly diagnosed type 2 diabetic who is overweight and has mild hypertension. Include a progressive exercise routine, balanced diet, blood sugar monitoring schedule, stress management techniques, and lifestyle modifications. Explain how each element helps manage diabetes, promotes weight loss, and improves heart health.",
            icon="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRtc4e90qSf97_dpcWCXKHDGI4wuUnmLnnmWg&s",
            )
        ]
    
@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("graph", graph)

@cl.on_message
async def on_message(message: cl.Message):
    graph = cl.user_session.get("graph")
    inputs = BASE_INPUTS.copy()
    inputs["query"] = str(message.content)
    
    first_answer, first_grade, first_refine = [True], [True], [True]
    final_answer = [""]
    answer_message = cl.Message(content="")
    refine_message = cl.Message(content="")
    
    async for msg_type, update in graph.astream(inputs, stream_mode=["messages", "updates"]):
        if msg_type == "messages":
            await handle_messages(update, answer_message, refine_message, first_answer, first_grade, first_refine, final_answer)
        elif msg_type == "updates":
            await handle_updates(update, final_answer)
    
    await cl.Message(content=f"Final Chosen Answer: \n\n{final_answer[0]}").send()