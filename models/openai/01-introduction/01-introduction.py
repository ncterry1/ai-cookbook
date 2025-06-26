
# In every Python file that uses the OpenAI SDK (e.g. src/main.py, src/agent.py, etc.), 
# add at the very top:
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load your .env into environment variables
load_dotenv()
# Set your OpenAI API key for this session
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

"""
   NCT - If we have the api key established in the .env file, 
then we can make it more simple and just do this: (I think)
--------------------------
from openai import OpenAI
# The OpenAI class will automatically use the OPENAI_API_KEY environment variable
client = OpenAI()
"""
