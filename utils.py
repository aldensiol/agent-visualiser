import chainlit as cl
from typing import List, Tuple, Optional

def get_source_files(content: str) -> List[Tuple[str, str]]:
    lst = []
    if "diabetes_treatment__insulin" in content or ("diabetes" in content and "insulin" in content):
        lst.append(("Diabetes Treatment_ Insulin", "src/pdfs/Diabetes Treatment_ Insulin.pdf"))
    
    if "diabetes_medications" in content or "diabetes medications" in content:
        lst.append(("Diabetes Medications", "src/pdfs/Diabetes Medications.pdf"))
        
    if "diabetic_foot_ulcer__symptoms_and_treatment" in content or ("diabetic" in content and "foot" in content):
        lst.append(("Diabetic Foot Ulcer_ Symptoms and Treatment", "src/pdfs/Diabetic Foot Ulcer_ Symptoms and Treatment.pdf"))
    
    if "managing-pre-diabetes" in content or "managing pre-diabetes" in content:
        lst.append(("managing-pre-diabetes-(updated-on-27-jul-2021)c2bfc77474154c2abf623156a4b93002", "src/pdfs/managing-pre-diabetes-(updated-on-27-jul-2021)c2bfc77474154c2abf623156a4b93002.pdf"))
        
    return lst

def get_source_elements(content:str, display: str = "inline"):
    source_files = get_source_files(content)
    source_elements = [
        cl.Pdf(name=name, display=display, path=path)
        for name, path in source_files
    ]
    return source_elements

async def handle_messages(update, answer_message, refine_message, first_answer, first_grade, first_refine, final_answer):
    chunk, metadata = update
    node = metadata.get('langgraph_node')

    if node == 'generate_answer':
        await handle_answer(chunk, answer_message, first_answer, final_answer)
    elif node == 'grader':
        await handle_grader(first_grade)
    elif node == 'refine_answer':
        await handle_refine(chunk, refine_message, first_refine, final_answer)

async def handle_answer(chunk, answer_message, first_answer, final_answer):
    if first_answer[0]:
        await send_answer_header()
        await answer_message.send()
        first_answer[0] = False
    else:
        answer_message.content += chunk.content
        await answer_message.update()
        final_answer[0] += chunk.content

async def handle_grader(first_grade):
    if first_grade[0]:
        await send_grader_header()
        first_grade[0] = False

async def handle_refine(chunk, refine_message, first_refine, final_answer):
    if first_refine[0]:
        await send_refine_header()
        await refine_message.send()
        first_refine[0] = False
    else:
        refine_message.content += chunk.content
        await refine_message.update()
        final_answer[0] += chunk.content

async def handle_updates(update, final_answer):
    print(f"Update: {update}")
    print("=====================================" * 4)
    agent_type = get_agent_type(update)
    if agent_type == "Grader Agent":
        metrics = get_metrics(update)
        await send_agent_message(agent_type=agent_type, 
                                 retrieved_context=None, 
                                 metrics=metrics,
                                 final_answer=final_answer)
    elif agent_type:
        retrieved_context = get_retrieved_context(update)
        await send_agent_message(agent_type=agent_type, 
                                 retrieved_context=retrieved_context, 
                                 metrics=None)

def get_retrieved_context(update):
    return (update.get('search_vector_db', {}).get('db_context') or
            update.get('search_kg_db', {}).get('kg_context') or
            update.get('websearch', {}).get('websearch_context'))
    
def get_metrics(update):
    string = ""
    metrics = update.get('grader').get('metrics')
    reasons = update.get('grader').get('reasons')
    scores = []
    for metric, num in metrics.items():
        reason = reasons.get(metric, '').capitalize()
        string += f"**{metric.capitalize()}**: **{num}/10**\n{reason}\n\n"
        scores.append(num)
    return (string, scores)

def get_agent_type(update):
    if update.get('search_vector_db'): return "Vector DB Retriever Agent"
    if update.get('search_kg_db'): return "KG DB Retriever Agent"
    if update.get('websearch'): return "Websearch Agent"
    if update.get('grader'): return "Grader Agent"
    return None

async def send_agent_message(agent_type: str, retrieved_context: Optional[str], metrics: Optional[Tuple[str, List[int]]], final_answer: List[str] = [""]):
    if agent_type == "Grader Agent":
        grading_element = cl.Text(name="Evaluation", display="inline", content=metrics[0])
        await cl.Message(content="", elements=[grading_element]).send()
        
        # decision
        decision = "The answer is good enough."
        for score in metrics[1]:
            if score < 7:
                decision = "The answer is not good enough. Extra context from a Websearch is required."
                final_answer[0] = ""
                break
        
        grading_decision = cl.Text(name="Decision", display="inline", content=decision)
        await cl.Message(content="", elements=[grading_decision]).send()
        
    else:  # Vector DB Retriever Agent or KG DB Retriever Agent or Websearch Agent
        if retrieved_context:
            context_element = get_context_element(name=agent_type, display="side", content=retrieved_context)
            await cl.Message(content=agent_type, elements=context_element).send()
            
            source_elements = get_source_elements(retrieved_context) if agent_type != "Websearch Agent" else []
            # for elem in source_elements:
            #     await cl.Message(content=elem.name, elements=[elem]).send()
            await cl.Message(content="PDF Source Material", elements=source_elements).send()
        else:
            await cl.Message(content=f"No context available for {agent_type}").send()

async def send_answer_header():
    answer_elements = [cl.Text(name="Answer Generation Agent's Answer", display="inline", content=" ")]
    await cl.Message(content="", elements=answer_elements).send()

async def send_grader_header():
    grading_elements = [cl.Text(name="Grader Agent's Evaluation", display="inline", content=" ")]
    await cl.Message(content="", elements=grading_elements).send() 
    
async def send_refine_header():
    refine_elements = [cl.Text(name="Refine Answer Agent's Refined Answer", display="inline", content=" ")]
    await cl.Message(content="", elements=refine_elements).send()

def get_context_element(name: str, content: str, display: str = "side"):
    return [cl.Text(name=name, display=display, content=content)]
