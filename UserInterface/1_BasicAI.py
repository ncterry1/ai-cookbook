# %% 
# Step 0: Imports and Client Initialization
# --------------------------------------------------------------
# SUMMARY:
# This script uses the OpenAI API to extract structured event 
# details from plain text. It defines a custom response format 
# using Pydantic (`CalendarEvent`) to capture the event name, 
# date, and participants. The model processes a user message 
# about an event and returns the data in a structured format, 
# which is then accessed like a Python object.
# --------------------------------------------------------------
# --------------------------------------------------------------
import os
from openai import OpenAI  # Main OpenAI library to interact with the API
from pydantic import BaseModel  # Used to define and validate the expected structured output

# Create an OpenAI client instance using the API key from your environment variables
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# %% 
# Step 1: Define the response format using Pydantic
# -------------------------------------------------------------- 
# You define a Pydantic class like this:
class CalendarEvent(BaseModel):
    name: str  # The name/title of the event
    date: str  # The date the event will occur
    participants: list[str]  # A list of participants attending the event

'''
This Pydantic model defines what the expected structure of the AI response should be.
By using Pydantic, we can automatically validate and parse the data returned by the AI.

Think of this as the "blueprint" or "template" for what the AI should give us back.

In this case, we’re telling the AI:
“Please return an event with a name, a date, and a list of participants.”
'''

# %% 
# Step 2: Make an API request using structured output
# -------------------------------------------------------------- 
completion = client.beta.chat.completions.parse(
    model="gpt-4o",  # Use OpenAI's GPT-4o model for response generation
    messages=[
        {"role": "system", "content": "Extract the event information."},
        {"role": "user", "content": "Alice and Bob are going to a science fair on Friday."},
    ],
    # You pass this class to response_format=CalendarEvent.
    # The SDK then:
    # Uses the structure of the Pydantic model to generate a JSON schema (a machine-readable format that describes how the data should look).
    # Sends this schema internally as part of the request to the OpenAI API using a special  OpenAI-supported technique for structured tool/function calling.
    # Tells the model: "Here’s the format I expect your answer to match."
    
    response_format=CalendarEvent,  # Use CalendarEvent class to define response structure
    #The model tries to fill in values that match your schema:
    #    name: "Science Fair"
    #    date: "Friday" or something similar
    #    participants: ["Alice", "Bob"]
)

'''
We're calling the OpenAI API with a small chat-like prompt exchange:
- The system message gives context or instruction to the AI.
- The user message provides the actual input text with the information we want to extract.

By specifying `response_format=CalendarEvent`, we're telling the model:
"Don't just respond with plain text — structure your answer to match this specific format."

This means the model will try to map the content into the `name`, `date`, and `participants` fields of the CalendarEvent model.
'''

# %%
# Step 3: Parse the structured response
# When the response comes back, the SDK automatically parses that response into your CalendarEvent class instance, so you can access it like: 
        # event.name
        # event.date
        # event.participants
event = completion.choices[0].message.parsed
'''
The `.parsed` attribute contains the AI's response as a validated `CalendarEvent` object.

At this point, `event` behaves like a Python object and you can easily access its fields.
'''

# %% 
# View the name of the event
event.name # 'Science Fair'

# %% 
# View the date of the event
event.date  # 'Friday'

# %% 
# View the participants in the event
event.participants  # ['Alice', 'Bob']

# %%
event # CalendarEvent(name='Science Fair', date='Friday', participants=['Alice', 'Bob'])

