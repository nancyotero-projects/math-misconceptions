import json
import openai
import pandas as pd
from exp_lib import generate_prompt_test_batch, get_gpt4_diagnosis

# Test OpenAI connection
print("Testing OpenAI connection...")
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}],
    temperature=0.2,
    max_tokens=10
)
print("OpenAI connection successful!")

# Test data loading
print("Testing data loading...")
with open('data/data.json', 'r') as f:
    data = json.load(f)
print("Data loading successful!")
