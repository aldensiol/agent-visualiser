import chainlit as cl

from src.chatbot.agents import AgentGraph

@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Explain what AI Agents are",
            message="Explain what AI Agents are like I'm five years old.",
            icon="src/icons/agent.svg",
            ),
        cl.Starter(
            label="GraphRag over VectorRag",
            message="In what scenarios is GraphRag better than VectorRag?",
            icon="src/icons/exercise.svg",
            ),
        cl.Starter(
            label="Exercises for diabetics",
            message="Please suggest some appropriate exercises for diabetics with heart conditions.",
            icon="src/icons/nodes.svg",
            )
        ]
    
@cl.on_chat_start
async def on_chat_start():
    # Set Agent Chain Here
    cl.user_session.set("graph", AgentGraph)

@cl.on_message
async def on_message(message: cl.Message):
    chain = cl.user_session.get("graph")
    res = await chain.ainvoke(
        question=message.content, callbacks=[cl.LangchainCallbackHandler()]
    )

    await cl.Message(content=res).send()