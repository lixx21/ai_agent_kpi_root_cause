from langchain_core.prompts import ChatPromptTemplate
import json

def analyze_data(model, question, plan_data, sql_data):
    prompt = """
    You are a senior data analyst. 
    You will be given the question from user, hypothesis, assumption, reasoning, 
    steps and the data from our database. Please provide a clear analysis and answer 
    the question based on the data provided. Test wheteher the hypothesis is correct or not based on the data provided.
    If possible, test the data using statistical methods and provide a clear recommendation to the user based on the analysis.

    question: {question}
    hypothesis: {hypothesis}
    assumptions: {assumptions}
    reasoning: {reasoning}
    data: {data}

    Output rules: 
    - give the high level analysis answer to business stakeholders 
    - provide the data to support the answer
    """

    chat_prompt_template = ChatPromptTemplate.from_template(prompt)
    chain = chat_prompt_template | model

    analysis_result = chain.invoke({
        "question": question,
        "hypothesis": plan_data["hypothesis"],
        "assumptions": plan_data["assumptions"],
        "reasoning": plan_data["reasoning"],
        "data": sql_data  # Convert the data to a JSON string for better readability
    }).content

    json_output = {
        "question": question,
        "hypothesis": plan_data["hypothesis"],
        "assumptions": plan_data["assumptions"],
        "reasoning": plan_data["reasoning"],
        "data": sql_data,
        "analysis_result": analysis_result
    }

    with open("./agent_result/agent_analysis_results.json", "w", encoding="utf-8") as f:
        json.dump(json_output, f, ensure_ascii=False, indent=2, default=str)  # Use default=str to handle non-serializable objects like datetime

    return analysis_result