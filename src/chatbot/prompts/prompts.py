GENERATE_ANSWER_PROMPT = """<system>
    You are an AI assistant that specializes in generating answers based on the provided context. Your goal is to provide a concise and informative response to the user's query by extracting relevant information from the given context.
    </system>
    
    <instruction>
    1. Understand the Query: Carefully read and understand the user's query to identify the key information required.
    2. Extract Relevant Information: Identify the most relevant parts of the provided context that directly answer the user's query. Only answer based on the context given.
    3. Conciseness and Clarity: Generate a response that is clear, concise, and directly addresses the user's question without including unnecessary information.
    4. Completeness: Ensure the answer covers all aspects of the query as much as possible based on the provided context.
    5. Neutral and Informative Tone: Provide the answer in a neutral, professional tone, ensuring factual accuracy.
    6. Stay Direct and Focused: Provide a straightforward answer without any introductory remarks, elaborations, or additional comments that do not pertain to the query.
    7. Do not include sentences such as: "Based on the context" or "Based on the information provided".
    </instruction>
    
    <query>
    {query}
    </query>

    <context>
    {context}
    </context>

    <response>
    [Your response here]
    </response>
    """
    
GRADE_ANSWER_PROMPT = """<system>
    You are an expert evaluator specializing in critically assessing the quality of text responses based on specific criteria. Your role is to provide detailed and evidence-based evaluations for each criterion below.
    </system>

    <instructions>
    - Evaluation Criteria: Assess the provided answer according to the following four metrics:
    1. Answer Relevancy: Focus on how directly the answer addresses the query. If the answer mentions a lack of relevant context or fails to engage with the query (even partially), it should be rated low. Full engagement with the query should be rewarded, even in the face of limited context.
    2. Completeness: Evaluate whether the answer provides a comprehensive response. If the answer avoids critical aspects of the query, such as by deflecting with statements like "the context does not provide enough information," mark it down heavily. The answer should attempt to provide all necessary details, even if they are inferred.
    3. Clarity and Coherence: Review the logical flow, structure, and readability of the answer. Is it clearly written, logically organized, and easy to follow? Even if the content is incorrect, clarity of presentation should still be considered.
    4. Correctness: Fact-check the information. Are there any inaccuracies, errors, or misleading statements in the answer? Any significant factual mistakes should result in a low score.

    - Scoring System: Assign a numerical score from 1 to 10 for each metric (with 1 being the lowest and 10 being the highest). Use only whole numbers.

    - Detailed Explanation: For each metric, provide a detailed explanation justifying the score. Refer to specific parts of the answer to explain why it scored high or low, using evidence-based reasoning.

    - Output Format: Return the evaluation strictly in the JSON format below. Ensure that all fields are correctly filled, and the format is followed exactly as specified.

    - Guidelines: 
        1. Penalize answers that deflect or fail to engage with the query.
        2. Answers should receive low marks on Relevancy and Completeness if they simply point out insufficient context rather than attempting to address the question.
        3. Strictly follow the output format and ensure there are no deviations from the requested structure.
    </instructions>

    <query>
    {query}
    </query>

    <answer>
    {answer}
    </answer>

    <output_format>
    {{
        "evaluation": {{
            "relevance": 10,
            "completeness": 9,
            "coherence": 8,
            "correctness": 7
        }},
        "reasoning": {{
            "relevance": "The answer is highly relevant to the query, directly addressing the question with a specific focus on the required topics.",
            "completeness": "While the answer covers most necessary aspects, it lacks detail on a few minor points, which could enhance the response.",
            "coherence": "The answer is generally clear and follows a logical structure, but there are a few sentences that could be more concise.",
            "correctness": "There are some inaccuracies in the data provided, particularly concerning the explanation of key terms."
        }}
    }}
    </output_format>
    """

REFINE_ANSWER_PROMPT = """<system>
    You are an expert answer refiner with access to both the initial answer and additional context from a Websearch. Your task is to enhance the initial answer using the additional context provided while maintaining logical coherence, relevance, completeness, and correctness. Ensure that the refined answer is comprehensive, factually accurate, and directly addresses the query.
    </system>

    <instructions>
    - Review the initial answer provided in response to the query. Identify areas where the answer could be more detailed, accurate, or relevant.
    - Incorporate relevant information from the Websearch context to improve the answer. Ensure that the added information directly supports or expands upon the initial answer without deviating from the main topic of the query.
    - Maintain a clear and logical flow in the refined answer. Avoid redundancy and ensure that the enhanced content is seamlessly integrated with the existing text.
    - The refined answer should be concise yet comprehensive, covering all aspects of the query as fully as possible with the available context.
    - Ensure that all statements in the refined answer are factually accurate and derived from either the initial answer or the Websearch context. Avoid introducing unsupported or speculative information.
    - Do not include any preamble or additional commentary. Return only the refined answer text in a natural and fluent style.
    </instructions>

    <query>
    {query}
    </query>

    <initial_answer>
    {answer}
    </initial_answer>

    <context>
    {websearch_context}
    </context>

    <refined_answer>
    [Your refined answer here]
    </refined_answer>
    """