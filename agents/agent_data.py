from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama   
from pathlib import Path
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import pandas as pd
import json

load_dotenv()

def extract_data_from_sql(sql):
    # Connect to PostgreSQL
    DB_NAME = os.getenv("DB_NAME")
    DB_SCHEMA = os.getenv("DB_SCHEMA")
    DB_TABLE_NAME = os.getenv("DB_TABLE_NAME")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = int(os.getenv("DB_PORT", 5432))
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_USER = os.getenv("DB_USER")

    db_engine = create_engine(
        f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    
    df = pd.read_sql(sql, db_engine).to_dict(orient='records')
    db_engine.dispose()

    return df

def get_data_from_steps(model, plan):
    data_dictionary = Path("data_dictionary.md").read_text(encoding="utf-8")

    template = """
    You are a senior data analyst. 
    - You will be given the hypothesis and the steps to test it.
    - You will be given the database schema and the data dictionary based on {data_dictionary}.

    Rules:
    - You will only answer with the SQL query with PostgreSQL 
    - The scheme in PostgreSQL is "public" with one table called "procurement_kpi".
    - No other table exists in the database rather than the "procurement_kpi" table.
    - Always add "" around column names when selecting them to avoid any errors (Example: SELECT "column_name" FROM public.procurement_kpi).
    - Always use the correct column names based on the data dictionary provided in the data_dictionary.
    - Always use PostgreSQL syntax for the SQL query.
    - Output the SQL query only without any explanation or additional text
    - Select only the columns needed to answer the question, do not select all columns

    Step: {Step}
    feedback: {feedback}
    """

    prompt = ChatPromptTemplate.from_template(template)
   
    chain = prompt | model
    result_save = []

    for i, step in enumerate(plan.steps):
        # print(f"Step {i+1}: {step.goal} (Needs SQL: {step.needs_sql})")
        if step.needs_sql:
            
            result = chain.invoke({
                "data_dictionary": data_dictionary,
                # "hypothesis": plan.hypothesis,
                "Step": step.goal,
                "feedback": ""
                })
            
            feedback = ""

            clean_sql = result.content.replace('```', '').replace('sql', '').strip()  # Clean the SQL query since the result format is ```sql ....```
            print(f"query step {i+1}")

            ## Handle potential errors in SQL execution
            for attempt in range(3):  # Allow up to 3 attempts
                try:
                    df = extract_data_from_sql(clean_sql)
                    # print(f"result step {i+1}: {df}")
                    print(f"Data extracted successfully for step {i+1}.")
                    result_save.append({
                            'step': i+1,
                            'goal': step.goal,
                            'sql_result': df
                        })
                    break  # Exit the loop if successful
                except Exception as e:
                    feedback = f"Your last SQL query {result.content} error with this message: {e}, fix it based on hint provided in the error message and provide a new SQL query."
                    print(feedback)
                    if attempt < 2:  # If not the last attempt, ask for a new query
                        result = chain.invoke({
                            "data_dictionary": data_dictionary,
                            # "hypothesis": plan.hypothesis,
                            "Step": step.goal,
                            "feedback": feedback
                        })
                        
                        result_save.append({
                            'step': i+1,
                            'goal': step.goal,
                            'sql_result': df
                        })
                        print(f"query step {i+1} (attempt {attempt + 2}): {result.content}")
                    else:
                        print(f"Failed to extract data after 3 attempts for step {i+1}.")

    # keep the result in a json file
    with open("./agent_result/agent_data_results.json", "w", encoding="utf-8") as f:
        json.dump(result_save, f, ensure_ascii=False, indent=2, default=str)  # Use default=str to handle non-serializable objects like datetime
    
    return result_save


