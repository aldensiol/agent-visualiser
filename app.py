import chainlit as cl

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
    
# @cl.on_chat_start
# async def on_chat_start():
#     # Set Agent Chain Here
#     cl.user_session.set("graph", AgentGraph)

@cl.on_message
async def on_message(message: cl.Message):
    chain = cl.user_session.get("graph")
    res = await chain.ainvoke(
        question=message.content, callbacks=[cl.LangchainCallbackHandler()]
    )

    await cl.Message(content=res).send()