# ==========================================================
# ==========================================================
# =========================================================
# %%
import json
import os

from openai import OpenAI
from pydantic import BaseModel, Field
# ==========================================================
# ==========================================================
# =========================================================
# %%-
# SECTION: Initialize the OpenAI Client
# --------------------------------------------------------------
# This sets up the OpenAI API client by retrieving the API key from
# an environment variable called 'OPENAI_API_KEY'. You must export this
# variable in your terminal or system settings before running the script.
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

"""
Reference: https://platform.openai.com/docs/guides/function-calling
This script demonstrates how to:
- Register a function (or "tool") with the OpenAI model
- Let the model decide if and when to use it
- Handle its output and re-inject that data into the conversation
- Request a structured final response using Pydantic models
"""
# ==========================================================
# ==========================================================
# =========================================================
# %%
# SECTION: Define the Mock Knowledge Base Retrieval Tool
# --------------------------------------------------------------
# This function simulates accessing a knowledge base (KB).
# For simplicity, it just loads and returns the full content
# of a local JSON file named "kb.json". No actual searching or
# ranking is performed—this is for demonstration purposes only.
def search_kb(question: str):
    """
    Simulated knowledge base query function.
    
    Args:
        question (str): The user's query about the KB.
    
    Returns:
        dict: The entire contents of the local 'kb.json' file.
    """
    with open("kb.json", "r") as f:
        return json.load(f)
# ==========================================================
# ==========================================================
# =========================================================
# %%
# SECTION: Register Tools with the Model
# --------------------------------------------------------------
# Tools allow the model to extend its capabilities by calling
# predefined functions. Here, we register a single function,
# `search_kb`, with the name, input schema, and description.
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_kb",  # Must match the actual Python function name
            "description": "Get the answer to the user's question from the knowledge base.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},  # Input is a string-based question
                },
                "required": ["question"],  # This argument is mandatory
                "additionalProperties": False,  # Prevent sending unexpected parameters
            },
            "strict": True,  # The model must match the input schema exactly
        },
    }
]
print(tools)
#[{'type': 'function', 'function': {'name': 'search_kb', 'description': "Get the answer to the user's question from the knowledge base.", 'parameters': {'type': 'object', 'properties': {'question': {'type': 'string'}}, 'required': ['question'], 'additionalProperties': False}, 'strict': True}}]
# ==========================================================
# ==========================================================
# =========================================================
# %%
# # SECTION: Compose Initial Chat Messages
# --------------------------------------------------------------
# These messages define the conversation context and user query.
# The system message shapes the model’s tone and capabilities,
# while the user message triggers the request.
system_prompt = (
    "You are a helpful assistant that answers questions "
    "from the knowledge base about our e-commerce store."
)

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "What is the return policy?"},  # Initial query
]
print(system_prompt)
#You are a helpful assistant that answers questions from the knowledge base about our e-commerce store.

print(messages)
# [{'role': 'system', 'content': 'You are a helpful assistant that answers questions from the knowledge base about our e-commerce store.'}, {'role': 'user', 'content': 'What is the return policy?'}]
# ==========================================================
# ==========================================================
# =========================================================
# %%
# SECTION: First API Call — Let Model Decide on Function Use
# --------------------------------------------------------------
# This first call gives the model access to both the prompt and
# the registered tools. It may choose to invoke a function rather
# than respond directly. We inspect the response for tool calls.

completion = client.chat.completions.create(
    model="gpt-4o",
    messages=messages, 
    tools=tools, 
)

# Optional debug: Dump the full response, including tool call details
completion.model_dump()
print(completion)
# ChatCompletion(id='chatcmpl-BoBYFCSEku4Ali94gL1HAvFTJEJGy', choices=[Choice(finish_reason='tool_calls', index=0, logprobs=None, message=ChatCompletionMessage(content=None, refusal=None, role='assistant', annotations=[], audio=None, function_call=None, tool_calls=[ChatCompletionMessageToolCall(id='call_BQKT0XykFzzJPGaDfAAmgNxe', function=Function(arguments='{"question":"return policy"}', name='search_kb'), type='function')]))], created=1751300503, model='gpt-4o-2024-08-06', object='chat.completion', service_tier='default', system_fingerprint='fp_07871e2ad8', usage=CompletionUsage(completion_tokens=16, prompt_tokens=74, total_tokens=90, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0)))
# ==========================================================
# ==========================================================
# =========================================================
# %%
# # SECTION: Handle and Execute Tool Calls Returned by the Model
# --------------------------------------------------------------
# If the model chose to call one of the tools, we must:
# 1. Parse the arguments it supplied,
# 2. Execute the function in Python,
# 3. Feed the result back into the conversation.
def call_function(name, args):
    """
    Dispatcher for calling tools based on their name.
    Currently only supports the 'search_kb' tool.
    
    Args:
        name (str): The name of the function to call.
        args (dict): The arguments passed by the model.
    
    Returns:
        dict: The result of the tool function.
    """
    if name == "search_kb":
        return search_kb(**args)

# Iterate through each tool call and execute it
for tool_call in completion.choices[0].message.tool_calls:
    # Extract function name and argument values from the model output
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)

    # Preserve the original assistant message (with the tool_call)
    messages.append(completion.choices[0].message)

    # Execute the tool function using the parsed arguments
    result = call_function(name, args)

    # Inject the result into the message history using a special role
    messages.append(
        {
            "role": "tool",
            "tool_call_id": tool_call.id,  # Must match the original tool call
            "content": json.dumps(result),  # Send result as a JSON-formatted string
        }
    )
# ==========================================================
# ==========================================================
# =========================================================
# %%
# SECTION: Define Structured Output Schema for Final Answer
# --------------------------------------------------------------
# Pydantic model used to define the expected format of the final
# assistant response. This helps validate and structure the output.
class KBResponse(BaseModel):
    answer: str = Field(description="The answer to the user's question.")
    source: int = Field(description="The record id of the answer.")
# ==========================================================
# ==========================================================
# =========================================================
# %%
# SECTION: Second API Call — Get Final Structured Answer
# --------------------------------------------------------------
# Now that the model has the full tool output in context,
# we call it again to generate a structured final answer
# based on that tool-provided data.
completion_2 = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=messages,
    tools=tools,
    response_format=KBResponse,  # Ask for structured output
)
# ==========================================================
# ==========================================================
# =========================================================
# %%
# SECTION: Extract Final Answer from Structured Output
# --------------------------------------------------------------
# Parse the returned data into fields that we can use directly
# for display, logging, or further logic.
final_response = completion_2.choices[0].message.parsed
print(final_response.answer)  # Human-readable answer
print(final_response.source)  # ID of the knowledge base record used
# ==========================================================
# ==========================================================
# =========================================================
# %%
# SECTION: Example of an Unrelated Question (No Tool Call)
# --------------------------------------------------------------
# This test demonstrates how the model behaves when the
# user asks something outside the tool’s purpose.
# The model should simply answer in text and not call any function.
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "What is the weather in Tokyo?"},  # Unrelated query
]
# THIS DOES NOT WORK - (Intended to not work)
# THE the kernel as been restarted. So It does not have weather data/functions 
#"'I currently cannot provide real-time weather updates. To find the current weather in Tokyo, I recommend checking a reliable weather website or using a weather app.'"
# Because the query isn't relevant to the KB, the model should answer directly
completion_3 = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=messages,
    tools=tools
)

# Extract the natural-language response from the model
completion_3.choices[0].message.content

# Items can be returned within 30 days of purchase with original receipt. Refunds will be processed to the original payment method within 5-7 business days.
# 1
