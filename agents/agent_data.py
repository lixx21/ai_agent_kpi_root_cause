from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama   
from pathlib import Path
from pydantic import BaseModel, Field
from agent_planner import planner

context = Path("data_dictionary.md").read_text(encoding="utf-8")

template = """
You are a senior data analyst. 
- You will be given the hypothesis and the steps to test it.
- You will be given the database schema and the data dictionary based on {context}.

Rules:
- You will only answer with the SQL query with PostgreSQL syntax and the scheme in PostgreSQL is "public"
- Output the SQL query only without any explanation or additional text
- Select only the columns needed to answer the question, do not select all columns

Hypothesis: {hypothesis}
Step: {Step}
"""

prompt = ChatPromptTemplate.from_template(template)
model = ChatOllama(model="llama3.2:latest", temperature=0)
chain = prompt | model

plan = planner("How many orders are still Pending, and since when?")
print(plan.hypothesis)

for i, step in enumerate(plan.steps):
    # print(f"Step {i+1}: {step.goal} (Needs SQL: {step.needs_sql})")
    if step.needs_sql:
        result = chain.invoke({
            "context": context,
            "hypothesis": plan.hypothesis,
            "Step": step.goal
            })
        print(f"Step {i+1}: {step.goal}, SQL Query: {result.content}")