# from altair import Step
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama   
from pathlib import Path
from pydantic import BaseModel, Field
import json

class Step(BaseModel):
    goal: str = Field(description="What this step should find out")
    needs_sql: bool = Field(description="True if this step needs a database query")
    
class Plan(BaseModel):
    hypothesis: str = Field(description="One testable hypothesis")
    assumptions: list[str] = Field(description="Assumptions made, if any")
    reasoning: str = Field(description="Short explanation of the reasoning")
    steps: list[Step] = Field(description="Ordered analysis steps, one query per step")

def planner(question):
    context = Path("data_dictionary.md").read_text(encoding="utf-8")

    template = """
    You are a senior data analyst. You will be given a question about procurement KPIs.
    Your answer give an hypothesis based on the question and considering the context provided.
    If you need to make assumptions, please state them clearly.

    Context: {context}
    Question: {question}

    Answer: 
        - asnwer the question based on the context and provide a clear explanation of your reasoning. 
        - Give 1 hyptohesis and explain how you would test it (plan the analysis) step by step.
        - Keep each step small: one step = one query.
    """

    prompt = ChatPromptTemplate.from_template(template)

    model = ChatOllama(model="llama3.2:latest", temperature=0)
    structured_model = model.with_structured_output(Plan)   # forces the Plan shape

    chain = prompt | structured_model

    result = chain.invoke({
        "context": context,
        "question": question
        })
    
    path = Path("./agent_result/agent_planner_results.json")
    path.parent.mkdir(parents=True, exist_ok=True)   # creates the folder if missing
    
    with open("./agent_result/agent_planner_results.json", "w", encoding="utf-8") as f:
        json.dump(result.model_dump(), f, ensure_ascii=False, indent=2, default=str)  # Use default=str to handle non-serializable objects like datetime
    return result

