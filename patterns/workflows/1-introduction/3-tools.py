
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
print(client) # Just to see: <openai.OpenAI object at 0x0000027317725E10>
# ==========================================================
# ==========================================================
# ==========================================================
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
    print("response = ", response)
    print("data = ", data)
    return data["current"]  

# ==========================================================
# ==========================================================
# ==========================================================
# %%
# SECTION: Register Tools with the LLM
# -------------------------------------------------------------- 
"""
Here's what's happening in the “tools” block:
- We define a single entry of type "function."
- The SDK will serialize this into the API call so that GPT-4o knows:
    “Hey, you can call a tool named get_weather with these parameters.”
- The JSON Schema ensures the model only sends well-formed args.
"""
'''
description
Purpose: Let the model know “Here's a function you might call if you need live weather data.”
Description & schema:
Tell the model how to call it (name, args, types).
Do not tell the model when or why—that's up to its understanding of the conversation.
'''
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
print("tools = ", tools) # this simply prints the structure to the screen when we run it. Just visuals
# ==========================================================
# ==========================================================
# %%
# SECTION: Build Initial Chat Messages (Prompt Design)
# --------------------------------------------------------------
'''
---System message---
Sets the LLM’s persona, tone, and high-level goal.
E.g. “Be helpful, fact-focused, and concise.”

This shapes every subsequent decision the model makes—when to answer in text vs. when to call a function, how verbose to be, even how politely to phrase things.

---User message---
Carries the actual user request (“What’s the weather…?”).
Without this, the model has no prompt telling it what you want.
'''
system_prompt = "You are a helpful weather assistant." 

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user",   "content": "What's the weather like in Paris today?"},
]
print("messages = ", messages)
# ==========================================================
# ==========================================================
"""
# ==========================================================
At this point:
- The LLM processes the user question.
- Under the hood, it decides: “I need real-time weather data, so I'll call get_weather.”
- The response object may contain a `tool_calls` list instead of plain text.
"""
'''
You are not providing any latitude or longitude yourself. All you’ve given the model is:
A user question: “What’s the weather like in Paris today?”

A tools definition telling it:
“If you need real weather data, you can call get_weather(latitude, longitude).”
and it realizes:

“To call this function I must supply numeric values for latitude and longitude.”
Because you asked about “Paris,” the model internally retrieves (from its training data) the approximate coordinates of Paris—48.8566 N, 2.3522 E—and emits them in the tool_calls block:
'''
# ==========================================================
# ==========================================================
# ==========================================================
# %%
# SECTION: First LLM Call — Model May Invoke Our Tool
# --------------------------------------------------------------
completion = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,   # We hand over our “tools” definition here
)
# ==========================================================
# ==========================================================
# ==========================================================
# %%
# SECTION: Inspect What the Model Returned
# --------------------------------------------------------------
# .model_dump() shows you raw model output, including any tool call instructions
print("completion = ", completion)
print(completion.model_dump())  
'''
{'id': 'chatcmpl-BmmjILOu82AkPl3wjCGQXG7riSxw1', 
'choices': [{'finish_reason': 'tool_calls', 'index': 0, 'logprobs': None, 'message': 
{'content': None, 'refusal': None, 'role': 'assistant', 'annotations': [], 
'audio': None, 
'function_call': None, 
'tool_calls': [{'id': 'call_AgAqgAH6BIv5CFyotMtUvOWS', 'function': 
{'arguments': '{"latitude":48.8566,"longitude":2.3522}', 'name': 'get_weather'}, 'type': 'function'}]}}], 
'created': 1750966760, 
'model': 'gpt-4o-2024-08-06', 
'object': 'chat.completion', 
'service_tier': 'default', 
'system_fingerprint': 'fp_07871e2ad8', 
'usage': {'completion_tokens': 24, 'prompt_tokens': 66, 'total_tokens': 90, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 0, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}}
'''
# ==========================================================
# ==========================================================
# ==========================================================
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
# ==========================================================
# For each tool_call the model asked for, we:
#  1. Parse its arguments
#  2. Execute our Python function to get real data
#  3. Append a new "tool" message with the results
# NCT - 'completion' is the results that came back
# ==========================================================
# ==========================================================
# ==========================================================
'''
When you register 'get_weather' in the tools list, we're telling the LLM:

“Here's a function you can call if you need real weather data—its name is get_weather(lat, lon) and here's how to call it.”

But the LLM itself doesn't execute HTTP requests.
You send the tools definition to the LLM

completion = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,   # <-- you hand over the schema for get_weather
)
At this point, the LLM simply knows “I could call that function if I want data.
The LLM decides to call the tool
It inspects your user question (“What's the weather in Paris?”)
It “thinks,” “I need accurate data → call get_weather with these coords.”
It returns a structured response (tool_calls) telling you: (json)
{
  "tool_calls": [
    {
      "function": { "name": "get_weather", "arguments": "{\"latitude\":48.8566,\"longitude\":2.3522}" }
    }
  ]
}
Your Python code picks up that instruction
for tool_call in completion.choices[0].message.tool_calls:
    name = tool_call.function.name               # "get_weather"
    args = json.loads(tool_call.function.arguments)
    result = call_function(name, args)   

Here is where you (your code) actually invoke the function.
Under the hood, call_function("get_weather", args) calls your get_weather() implementation, which does the HTTP request to open-meteo.com.
You feed the real data back into the conversation

messages.append({
  "role": "tool",
  "tool_call_id": tool_call.id,
  "content": json.dumps(result)
})
Now the LLM sees:
“Here's the live weather data you asked for—go ahead and compose the final answer.”
'''
# ==========================================================
# ==========================================================
# ==========================================================
# %%
for tool_call in completion.choices[0].message.tool_calls: 
    
    # 1️ Extract the function name the model wants to call.
    #    Example: tool_call.function.name == 'get_weather'
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments) 
    messages.append(completion.choices[0].message) 
    result = call_function(name, args) 
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": json.dumps(result),
    })
    print("name = ", name)
    print("args = ", args)
    print("messages = ", messages)
    print("result = ", result)
    print("messages = ", messages)
    '''
name =  get_weather

args =  {'latitude': 48.8566, 'longitude': 2.3522}

messages =  [{'role': 'system', 'content': 'You are a helpful weather assistant.'}, {'role': 'user', 'content': "What's the weather like in Paris today?"}, ChatCompletionMessage(content=None, refusal=None, role='assistant', annotations=[], audio=None, function_call=None, tool_calls=[ChatCompletionMessageToolCall(id='call_6eTHcBl6VVHKyyOkVPzDej94', function=Function(arguments='{"latitude":48.8566,"longitude":2.3522}', name='get_weather'), type='function')]), {'role': 'tool', 'tool_call_id': 'call_6eTHcBl6VVHKyyOkVPzDej94', 'content': '{"time": "2025-06-27T16:15", "interval": 900, "temperature_2m": 29.5, "wind_speed_10m": 10.3}'}]

result =  {'time': '2025-06-27T16:15', 'interval': 900, 'temperature_2m': 29.5, 'wind_speed_10m': 10.3}

messages =  [{'role': 'system', 'content': 'You are a helpful weather assistant.'}, {'role': 'user', 'content': "What's the weather like in Paris today?"}, ChatCompletionMessage(content=None, refusal=None, role='assistant', annotations=[], audio=None, function_call=None, tool_calls=[ChatCompletionMessageToolCall(id='call_6eTHcBl6VVHKyyOkVPzDej94', function=Function(arguments='{"latitude":48.8566,"longitude":2.3522}', name='get_weather'), type='function')]), {'role': 'tool', 'tool_call_id': 'call_6eTHcBl6VVHKyyOkVPzDej94', 'content': '{"time": "2025-06-27T16:15", "interval": 900, "temperature_2m": 29.5, "wind_speed_10m": 10.3}'}]

    '''
    # Full code in for loop ^^^  Notes vvv
    # ----------------------------
    # 2️ Extract and parse the JSON-encoded arguments string.
    #    tool_call.function.arguments is a string:
    #      '{"latitude":48.8566,"longitude":2.3522"}'
    #    json.loads turns it into a Python dict:
    #      {'latitude': 48.8566, 'longitude': 2.3522}
    # At this point:
    #   name == 'get_weather'
    #   args == {'latitude': 48.8566, 'longitude': 2.3522}
    #args = json.loads(tool_call.function.arguments)

    # -------------------------------------------------------
    # 3️ Preserve the original assistant message (with its tool_call)
    #    so the model “remembers” that it asked for this function.
    #
    #    The message we re-append looks like:
    #    {
    #      'role': 'assistant',
    #      'content': None,
    #      'tool_calls': [...],
    #      # plus other metadata fields
    #    }
    # Preserve the original model message as context
    #messages.append(completion.choices[0].message)

    # --------------------------------------------
    # 4️ Execute the actual Python function to fetch real data.
    #    We route based on `name`; for 'get_weather' we call our helper.
    #    e.g. result might be: {'temperature_2m': 20.1, 'wind_speed_10m': 5.3}
    # Execute our external API fetch - we created 'call_function'
    #result = call_function(name, args)

    # Now we need to send that result *back* into the conversation
    # so the LLM can see "Here’s the real weather data you requested."

    # --------------------------------------------
    # 5️ Create a new message of role "tool" that holds the data.
    #    - tool_call_id must match the original call’s `id`
    #    - content must be a JSON-encoded string of our result dict
    #
    #    This message looks like:
    #    {
    #      "role": "tool",
    #      "tool_call_id": "call_AgAqgAH6BIv5CFyotMtUvOWS",
    #      "content": "{\"temperature_2m\":20.1,\"wind_speed_10m\":5.3}"
    #    }
    # Feed the result back into the conversation as a “tool” message
    #messages.append({
    #    "role": "tool",
    #    "tool_call_id": tool_call.id,
    #    "content": json.dumps(result),
    #})
    # After this iteration, `messages` contains:
    # 1) All the original system/user history,
    # 2) The assistant’s function_call message,
    # 3) Your new tool result message,
    # ready for the next LLM call to generate a final answer.
# ==========================================================
'''
Why each step matters:
Extract name: Lets your code know which local function to run.

Parse arguments: Converts the model-proposed arguments from text into Python types.

Re-append the assistant message:
Keeps the context so the model sees “I asked you to run this function here.”

Call your function: Fetches live data from the real API.

Append the tool result:
Feeds that data back into the conversation under a "tool" role so that on your next LLM call, GPT-4o can incorporate the actual weather values into its response.

This loop is the glue that bridges the LLM's decision to “call a function” with your Python code actually executing it and returning the data
'''
# ==========================================================
# ==========================================================
# ==========================================================
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


# ==========================================================
# ==========================================================
# ==========================================================

# %%
# SECTION: Second LLM Call — Combine Data + LLM for Final Output
'''
So we are essentially running the LLM twice: Plan --> Execute
1) First call - let the model decide whether it needs to call our get-weather tool and with what args
So first, we dont get back text, We get back that 'tool_calls' block
that says: “I want to call get_weather(latitude=48.8566, longitude=2.3522).”
Why not one call?
We need the model to tell us which function to run (if any) before we fetch data from the api
So we run the function, parse the args, call get-weather, get actual weather data, then
append that data back into the chat history as a 'tool' message
2) Second call - now that the model has both its own request and the real world data
you ask it AGAIN: "Given all of this, please produce the final user-facing answer
in the structured WeatherResponse format."
So we will get back a Pydantic-parsed object (final_response) containing:
temperature(raw number) and
response (a natrual language summary like It's 18 degrees C and sunny in Paris today.) 
'''
# --------------------------------------------------------------
completion_2 = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=messages,          # All prior messages + tool results
    tools=tools,                # Tools still available if needed again
    response_format=WeatherResponse,  # Parse into our Pydantic model
)

print("completion_2 = ", completion_2)
"""
This tells the SDK:
- Here's the conversation so far (including the fetched weather data).
- Give me a final answer, structured according to WeatherResponse.
"""
"""
completion_2 =  ParsedChatCompletion[WeatherResponse](id='chatcmpl-Bn6FcogOLsHaXMa4FhGYbPHa0RNZv', choices=[ParsedChoice[WeatherResponse](finish_reason='stop', index=0, logprobs=None, message=ParsedChatCompletionMessage[WeatherResponse](content='{"temperature":29.5,"response":"The current temperature in Paris is 29.5°C. It\'s quite warm today, with a light breeze around 10.3 km/h."}', refusal=None, role='assistant', annotations=[], audio=None, function_call=None, tool_calls=None, parsed=WeatherResponse(temperature=29.5, response="The current temperature in Paris is 29.5°C. It's quite warm today, with a light breeze around 10.3 km/h.")))], created=1751041800, model='gpt-4o-2024-08-06', object='chat.completion', service_tier='default', system_fingerprint='fp_07871e2ad8', usage=CompletionUsage(completion_tokens=44, prompt_tokens=211, total_tokens=255, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0)))

"""

# ==========================================================
# ==========================================================
# ==========================================================

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
# ==========================================================
# ==========================================================
# ==========================================================

# %%
