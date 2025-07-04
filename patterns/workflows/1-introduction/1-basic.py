
# -------------------------------------------------------------
# This script sends a chat prompt to the OpenAI API asking for 
# a limerick about Python. It uses the GPT-4o model and prints 
# the model's response. Each section is isolated using `# %%` 
# to allow independent execution.
# ------------------------------------------------------------

# %% 
# Step 0: Load the operating system module to access environment variables
import os

# %% 
# Step 1: Import the OpenAI library
from openai import OpenAI

# %% 
# Step 2: Initialize the OpenAI client with your API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
'''
This uses your environment variable `OPENAI_API_KEY` to authenticate.
Make sure that your API key is set in your environment before running.
'''

# %% 
# Step 3: Make a basic chat completion request
completion = client.chat.completions.create(
    model="gpt-4o",  # Specify the model to use for generation
    messages=[
        {"role": "system", "content": "You're a helpful assistant."},  # Provides behavior/context
        {"role": "user", "content": "Write a limerick about the Python programming language."},  # User's actual prompt
    ],
)

'''
We’re sending a two-message chat:
- The "system" message gives the AI a persona or behavior.
- The "user" message asks for a specific task—in this case, a limerick.

The result is stored in the `completion` object.
'''

# %% 
# Step 4: Extract the generated response and print it
response = completion.choices[0].message.content
print(response)

'''
Run Confirmed!
Return Example:
    In Python, the code is quite clear,  
    Indentation’s the rule year to year.  
    With imports concise,  
    And syntax so nice,  
    It's a language to hold very dear. 
'''
