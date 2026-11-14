from langchain_ollama import ChatOllama
from agent_planner import planner
from agent_data import get_data_from_steps
from agent_analyst import analyze_data

llama_model = ChatOllama(model="llama3.2:latest", temperature=0)
coder_model = ChatOllama(model="qwen2.5-coder", temperature=0)

question = "Which supplier has the highest defect rate in Raw Materials?"
print('agent is running...')
print('planning analysis...')
plan = planner(llama_model, question)
print('get data from database...')
sql_data = get_data_from_steps(coder_model, plan)
print('starting analyze...')
agent_analysis_result = analyze_data(llama_model, question, plan.model_dump(), sql_data)

print(agent_analysis_result)