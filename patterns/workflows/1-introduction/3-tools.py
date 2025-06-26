
# %%
# Imports & Client Initialization
# --------------------------------------------------------------
import json                    # For serializing/deserializing JSON
import os                      # To read environment variables
import requests                # To call external REST APIs (our "tool")
from openai import OpenAI      # OpenAI SDK for calling the LLM
from pydantic import BaseModel, Field  # For defining structured output schemas

# Instantiate the OpenAI client, pulling your API key from the OPENAI_API_KEY env var
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# %%
# SECTION: Define “Tool” Function for External Data
# --------------------------------------------------------------
def get_weather(latitude: float, longitude: float) -> dict:
    """
    This function calls a public weather API (open-meteo.com) 
    to fetch current weather data for given coordinates.
    It's our custom 'tool' that the LLM can invoke via Function Calling.
    """
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}&longitude={longitude}"
        "&current=temperature_2m,wind_speed_10m"
    )
    response = requests.get(url)
    response.raise_for_status()  # Raise an error if the HTTP request failed
    data = response.json()
    # We return only the 'current' block; the rest (hourly, etc.) is dropped
    return data["current"]  


# %%
# SECTION: Register Tools with the LLM
# -------------------------------------------------------------- 
tools = [
    {
        "type": "function",           # Indicates this is a function the LLM may call
        "function": {
            "name": "get_weather",    # Must match our Python function name
            "description": "Get current temperature for provided coordinates in celsius.",
            "parameters": {          # JSON Schema to tell the model what args to pass
                "type": "object",
                "properties": {
                    "latitude":  {"type": "number"},
                    "longitude": {"type": "number"},
                },
                "required": ["latitude", "longitude"],
                "additionalProperties": False,
            },
            "strict": True,  # Reject any extra arguments not in the schema
        },
    }
]
"""
Here's what's happening in the “tools” block:
- We define a single entry of type "function."
- The SDK will serialize this into the API call so that GPT-4o knows:
    “Hey, you can call a tool named get_weather with these parameters.”
- The JSON Schema ensures the model only sends well-formed args.
"""


# %%
# SECTION: Build Initial Chat Messages (Prompt Design)
# --------------------------------------------------------------
system_prompt = "You are a helpful weather assistant." 
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user",   "content": "What's the weather like in Paris today?"},
]


# %%
# SECTION: First LLM Call — Model May Invoke Our Tool
# --------------------------------------------------------------
completion = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,   # We hand over our “tools” definition here
)
"""
At this point:
- The LLM processes the user question.
- Under the hood, it decides: “I need real-time weather data, so I'll call get_weather.”
- The response object may contain a `tool_calls` list instead of plain text.
"""


# %%
# SECTION: Inspect What the Model Returned
# --------------------------------------------------------------
# .model_dump() shows you raw model output, including any tool call instructions
print(completion.model_dump())  
'''
{'id': 'chatcmpl-BmmjILOu82AkPl3wjCGQXG7riSxw1', 
'choices': [{'finish_reason': 'tool_calls', 'index': 0, 'logprobs': None, 'message': {'content': None, 'refusal': None, 'role': 'assistant', 'annotations': [], 
'audio': None, 
'function_call': None, 
'tool_calls': [{'id': 'call_AgAqgAH6BIv5CFyotMtUvOWS', 'function': {'arguments': '{"latitude":48.8566,"longitude":2.3522}', 'name': 'get_weather'}, 'type': 'function'}]}}], 
'created': 1750966760, 
'model': 'gpt-4o-2024-08-06', 
'object': 'chat.completion', 
'service_tier': 'default', 
'system_fingerprint': 'fp_07871e2ad8', 
'usage': {'completion_tokens': 24, 'prompt_tokens': 66, 'total_tokens': 90, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 0, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}}
'''
# %%
# SECTION: Execute the Tool Calls Locally
# --------------------------------------------------------------
def call_function(name: str, args: dict) -> dict:
    """
    Router for executing the correct Python function based on the name.
    Right now, we only support get_weather.
    """
    if name == "get_weather":
        return get_weather(**args)
    raise ValueError(f"Unknown function: {name}")

# For each tool_call the model asked for, we:
#  1. Parse its arguments
#  2. Execute our Python function to get real data
#  3. Append a new "tool" message with the results
# NCT - 'completion' is the results that came back
for tool_call in completion.choices[0].message.tool_calls: 
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    
    # Preserve the original model message as context
    messages.append(completion.choices[0].message)
    
    # Execute our external API fetch
    result = call_function(name, args)
    
    # Feed the result back into the conversation as a “tool” message
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": json.dumps(result),
    })


# %%
# SECTION: Define Structured Output Schema for Final Response
# -------------------------------------------------------------- 
class WeatherResponse(BaseModel):
    temperature: float = Field(
        description="The current temperature in celsius for the given coordinates."
    )
    response: str = Field(
        description="A natural language summary of the weather for the user."
    )


# %%
# SECTION: Second LLM Call — Combine Data + LLM for Final Output
# --------------------------------------------------------------
completion_2 = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=messages,          # All prior messages + tool results
    tools=tools,                # Tools still available if needed again
    response_format=WeatherResponse,  # Parse into our Pydantic model
)
"""
This tells the SDK:
- Here's the conversation so far (including the fetched weather data).
- Give me a final answer, structured according to WeatherResponse.
"""


# %%
# SECTION: Extract & Use the Parsed Result
# -------------------------------------------------------------- 
final_response = completion_2.choices[0].message.parsed
print("Temperature (°C):", final_response.temperature)
print("Assistant says:", final_response.response)
'''
Temperature (°C): 25.5
Assistant says: The current temperature in Paris is 25.5°C with a wind speed of 10.7 m/s, making it a pleasant day in the city. Enjoy your visit!
'''