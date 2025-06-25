# Introduction

This Cookbook contains examples and tutorials to help developers build AI systems, offering copy/paste code snippets that you can easily integrate into your own projects.

## About Me

Hi! I'm Dave, AI Engineer and founder of Datalumina®. On my [YouTube channel](https://www.youtube.com/@daveebbelaar?sub_confirmation=1), I share practical tutorials that teach developers how to build AI systems that actually work in the real world. Beyond these tutorials, I also help people start successful freelancing careers. Check out the links below to learn more!

### Explore More Resources

Whether you're a learner, a freelancer, or a business looking for AI expertise, we've got something for you:

1. **Learning Python for AI and Data Science?**  
   Join our **free community, Data Alchemy**, where you'll find resources, tutorials, and support  
   ▶︎ [Learn Python for AI](https://www.skool.com/data-alchemy)

Here’s a fully expanded walkthrough—covering motivation, each core building block, the three workflow patterns, and how all the repo scripts fit together. I’ve added more context, examples, and links between concepts so you can see how everything connects end-to-end.

0. Repository Structure & Table of Contents
Use this as your roadmap—you can jump straight to any script for hands-on code.

text
├── 01_basic_llm_call.py           # Raw ChatCompletion → free-form text  
├── 02_structured_output.py        # Pydantic models + parse() → strict JSON  
├── 03_tools_function_calling.py   # Define “tools” + function-calling schema  
├── 04_retrieval_tool.py           # KB/JSON search as a tool (simple RAG)  
├── 05_prompt_chaining.py          # Gate → extract → confirm sequence  
├── 06_routing.py                  # Branch: new-event vs. modify-event vs. reject  
├── 07_parallelization.py          # Async intent + safety checks in parallel  
└── README.md                      # Overview + link to Entropic blog post  

## 1. Motivation & Context
* Why avoid high-level frameworks?
** Frameworks (LangChain, Agents.js, etc.) hide the LLM API calls behind layers of abstraction.
** By coding directly in Python against the OpenAI (or any LLM) SDK, you learn:
*** How prompts really get sent, truncated, retried.
*** How to specify exact input/output schemas.
*** When and why to catch rate limits, retries, or partial failures.
* Real-world benefit
** Full transparency into every step → easier debugging, tuning, and compliance.
* Underlying theory
** Patterns drawn from Entropic’s “Building Effective Agents” blog post, which outlines the four building blocks and three workflow patterns.

## 2. Core Building Blocks
* These are the “primitives” you’ll reuse in every agent:
* Raw LLM Calls (01_basic_llm_call.py)
 **  Example: ask GPT-4 to “Write a limerick about Python.”
   ** Code sketch:

python
client = OpenAI(api_key=…)
resp = client.chat.completions.create(
  model="gpt-4",
  messages=[{"role":"system","content":"You are helpful."},
            {"role":"user","content":"Write me a limerick about Python"}]
)
print(resp.choices[0].message.content)

** Use when you just need human-readable text responses.

### Structured Output (02_structured_output.py)
* Define Pydantic-style classes for your expected output.
* Example CalendarEvent with fields name: str, date: date, participants: List[str].
* Use the Chat API’s beta_tools.chat.completions.parse() or function-calling to enforce JSON that fits your model.
* Benefit: your code downstream can safely assume correct types—no brittle regex parsing or manual JSON loads.

### Tool Integration / Function Calling (03_tools_function_calling.py)
* Wrap external logic (weather API, Google Calendar, database query) as “tools” by giving OpenAI:
  ** name: string identifier
  ** description: when/how the LLM should use it
  ** parameters schema: JSON object definition of args
* LLM will decide “Yes, call ‘get_weather’ with {lat:..., lon:...}.”
* Your code reads that instruction, invokes the actual function, then appends the real result back into the chat.
* Keeps “thinking” and “doing” separate—prevents hallucinating API calls.

### Retrieval as a Tool (04_retrieval_tool.py)
* Treat your knowledge base or vector store lookup exactly like any other tool.
* Define a search_kb(query: str) → List[Document] schema.
* Model decides when to call it, supplies the query (e.g. “return policy”), and you feed back the matching JSON snippets along with metadata (source IDs, etc.).
- Builds in retriever-augmented generation (RAG) without extra libraries.

## 3. Workflow Patterns (“Augmented LLM” in Action)
Dave builds three higher-order orchestrations by combining the above primitives:

# A. Prompt Chaining (05_prompt_chaining.py)
## Goal: Break a multifaceted user request into a clear sequence of LLM calls, each responsible for a narrow sub-task.
## Flow:

### Gate
- Ask: “Is this a calendar-event request?”
- Output: { is_event: bool, confidence: float }
- If false or below threshold, stop early—avoids wasted downstream calls.
### Extract Details
- Prompt: “Extract event name, date, duration, participants.”
- Output: your EventDetails data model.
### Generate Confirmation
- Prompt: “Write a confirmation email text + calendar link for this event.”
- Output: ConfirmationResponse(message: str, calendar_link: str).
###  Why it matters
* Each step has its own tailored prompt and data model → easier to debug and refine.
* Human-in-the-loop or conditional gating can be inserted between steps.

# B. Routing (06_routing.py)
### Goal: Dynamically choose different handlers based on intent (e.g., new vs. modify).
### Flow:
- Single entry function processes the raw user message.
- LLM call with a tiny schema: { request_type: "new"|"modify"|"unknown", confidence }.
   * if request_type == "new" → call handle_new_event(...)
   * elif "modify" → call handle_modify_event(...)
   * else → send “Sorry, I can’t handle that.”
* Key point

* Keeps your code modular: add new branches (cancellations, inquiries, etc.) by adding new LLM schemas + handlers.

# C. Parallelization (07_parallelization.py)
## Goal: Reduce latency for independent checks by firing them concurrently.
## When to use
- Safety/guardrail validations: e.g., “is it a calendar request?” and “does it attempt prompt injection?”
- These checks don’t depend on each other’s output.
## Implementation
- Use Python’s async/await with the OpenAI async client.
-  Kick off both LLM calls simultaneously, then await them together.
-  Aggregate results: if either fails (e.g. security check flags a risk), short-circuit the flow.

# 4. Putting It All Together
## Whiteboard first
### Draw your user flow: trigger, data extraction, decision points, API/tool calls, final response.

## Implement primitives
### Basic LLM calls, data models, tool schemas, retrieval function.

## Compose workflows
* Prompt chain for multi-step tasks.
* Routing for branching intents.
* Parallelization for concurrent checks.

## Orchestrate
* Single entrypoint script wires everything: maintains message history, loops through checks, invokes tools, aggregates, and returns the final answer.

## Extend
* Swap in real Google Calendar API.
* Hook up to a UI or messaging queue.
* Add more tools (email sender, database writer, monitoring webhook).

# 5. Next Steps & Jump-ins
## By timestamp
- Basic call: ~ 0:45
- Structured output: ~ 3:55
- Tools & function calling: ~ 8:40
- Retrieval: ~ 18:30
- Prompt chaining: ~ 26:00
- Routing: ~ 38:00
- Parallelization: ~ 42:00

## By script name
- Open 01_basic_llm_call.py to see the simplest API call.
- Inspect 05_prompt_chaining.py for the full gate/extract/confirm pipeline.
- Review 07_parallelization.py for an example of async safety checks.

## By action
* “Show me how to define Pydantic models for structured output.”
* “Walk me through the function-calling loop in 03_tools_function_calling.py.”
* “Explain how the routing logic picks ‘new’ vs. ‘modify.’”

