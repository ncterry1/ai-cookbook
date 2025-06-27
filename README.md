
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

# 3. Workflow Patterns (“Augmented LLM” in Action)
Dave builds three higher-order orchestrations by combining the above primitives:

## A. Prompt Chaining (05_prompt_chaining.py)
### Goal: Break a multifaceted user request into a clear sequence of LLM calls, each responsible for a narrow sub-task.
### Flow:

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

## B. Routing (06_routing.py)
### Goal: Dynamically choose different handlers based on intent (e.g., new vs. modify).
### Flow:
- Single entry function processes the raw user message.
- LLM call with a tiny schema: { request_type: "new"|"modify"|"unknown", confidence }.
   * if request_type == "new" → call handle_new_event(...)
   * elif "modify" → call handle_modify_event(...)
   * else → send “Sorry, I can’t handle that.”
* Key point

* Keeps your code modular: add new branches (cancellations, inquiries, etc.) by adding new LLM schemas + handlers.

## C. Parallelization (07_parallelization.py)
### Goal: Reduce latency for independent checks by firing them concurrently.
### When to use
- Safety/guardrail validations: e.g., “is it a calendar request?” and “does it attempt prompt injection?”
- These checks don’t depend on each other’s output.
### Implementation
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


# Installation instructions
## This is a broad overview on setting up a system to use python, vscode, jupyter, openai and other parts. These are just for initial setup of the system. There are many more actions to add/know

### Here’s the complete, step-by-step setup guide for your ai-cookbook project on Windows—from installing Python all the way through VS Code, Jupyter, OpenAI, and interactive workflows. I’ve clearly marked when you should be outside or inside your virtual environment (.venv).

# 1. Install Python 3.11 (Outside any venv)
Open an elevated PowerShell (“Run as Administrator”).

### Update WinGet sources:
powershell
> winget source update
> Install Python system-wide:

powershell
> winget install --id Python.Python.3.11 --exact --scope machine

### Verify (in a new Git CMD or PowerShell):
powershell
* python --version   # ⇒ Python 3.11.x  
* pip --version      # ⇒ pip 23.x.x
### Upgrade pip & friends:
powershell
- python -m pip install --upgrade pip setuptools wheel
All done outside any virtual environment.

# 2. Create & Activate Your Project’s venv
Your repo path:
makefile
- C:\Users\ncterry\Documents\git\ai-cookbook
### Open Git CMD (or PowerShell) and cd there:
cmd
> cd /d C:\Users\ncterry\Documents\git\ai-cookbook

### Create the venv:
cmd
> python -m venv .venv

### Activate it:
cmd
> .\.venv\Scripts\activate
You’ll now see (.venv) at your prompt.
From here on, you’re inside the venv until you run deactivate.

# 3. Install Core Python Libraries (Inside venv)
cmd
> pip install \
  openai \
  python-dotenv \
  requests \
  langchain \
  pydantic \
  aiohttp \
  jupyter \
  ipykernel
Then freeze for reproducibility:

cmd
> pip freeze > requirements.txt

# 4. VS Code Extensions & Interpreter
Open VS Code in your project:
cmd
> code .

### Install extensions in VSCode (Ctrl + Shift + X):
* Python (ms-python.python)
* Pylance (ms-python.vscode-pylance)
* Jupyter (ms-tools-ai.jupyter)
* GitLens (eamodio.gitlens)
* GitHub Pull Requests & Issues (GitHub.vscode-pull-request-github)
* GitHub Copilot (GitHub.copilot.vscode)
* Docker (ms-azuretools.vscode-docker) (optional)
* Remote – SSH (ms-vscode-remote.remote-ssh) (optional)

Select the Interpreter
- Ctrl + Shift + P → Python: Select Interpreter → choose
makefile
- C:\Users\ncterry\Documents\git\ai-cookbook\.venv\Scripts\python.exe

# 5. Workspace Settings (.vscode/settings.json)
Create or overwrite:
makefile
- C:\Users\ncterry\Documents\git\ai-cookbook\.vscode\settings.json
with:
(jsonc)

{
  // === Interpreter & auto-activate ===
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe",
  "python.terminal.activateEnvironment": true,

  // === Format on save & Black ===
  "editor.formatOnSave": true,
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  },
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "88"],

  // === Organize imports (isort) on save ===
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },

  // === Linting ===
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.flake8Args": [
    "--max-line-length=88",
    "--ignore=E203"
  ],

  // === Type checking ===
  "python.linting.mypyEnabled": true,
  "python.linting.mypyArgs": [
    "--ignore-missing-imports"
  ]
}
After saving, Reload Window (Ctrl + Shift + P → Developer: Reload Window).

# 6. Environment Variables & Initialization
Create .env at project root:
bash
> C:\Users\ncterry\Documents\git\ai-cookbook\.env

Populate with only your key:
ini
* OPENAI_API_KEY=sk-XXXXXXXXXXXXXXXXXXXXXXXX
Ensure .env is in your .gitignore.

In every Python file that calls the API (e.g. src/main.py):
python
- from dotenv import load_dotenv
- load_dotenv()
- from openai import OpenAI
- client = OpenAI()  # picks up OPENAI_API_KEY

# 7. Jupyter Notebook Integration (Inside venv)
Register your venv as a Jupyter kernel (once):
cmd
python -m ipykernel install --user --name ai-cookbook --display-name "Python (ai-cookbook)"
Reload VS Code (Ctrl + Shift + P → Developer: Reload Window).

### Create your notebook, example in \TESTING\analysis.ipynb.
Select the kernel (top-right of the notebook editor):
Click the kernel name → Python environments… → choose “Python (ai-cookbook)” or “.venv (Python 3.11.x)”.

### Run a cell:
You can establish a cell in just a .py file by adding '# %%' then all python code in the file will be that cell until you insert the next # %% (more shown below)
Cells show as gray blocks labeled In [ ]:.

In an .ipynb file, Click inside, type code (e.g. import sys; print(sys.executable)), then Run Cell ▶️ or press Shift + Enter.

Confirm the output path is your .venv\Scripts\python.exe.

8. Interactive .py Execution (Inside venv)
To run sections of a .py file with checkmarks in the right panel:
Open 1-basic.py (or any script) in the editor.

Annotate with cell markers:
python
- # %%
- import openai
- print("Cell 1")

- # %%
- response = client.chat.completions.create(...)
- print(response)
Open the Interactive window:

Run Cell gutter icons appear next to # %%.
Click ▶️ on a cell or run Run Current File in Interactive Window from the top-right menu.
See green checkmarks for executed cells and output in the Interactive pane.
Ensure the Interactive window’s kernel is your .venv\Scripts\python.exe.

9. Obtaining & Managing Your OpenAI API Key (Outside venv)
* Visit https://platform.openai.com/ → log in.
* Under Billing, add a payment method.
* Under API Keys, click Create new secret key, copy sk-… into your .env.
* Use the dashboard’s usage limits to cap your spend.

10. Cost Estimation & Example Usage
* Model	Prompt/1K	Completion/1K
* gpt-3.5-turbo	$0.0015	$0.002
* gpt-4 (8K context)	$0.03	$0.06

Light-use example: 500 short Q&As (~15 tokens each)
text
* 500 × (~0.015K × $0.002 avg) ≈ $0.013/month

venv Quick–Recap
Outside venv: Python & winget install, VS Code launch, API key provisioning.

Inside venv:
> pip install …
> ipykernel install
> pip freeze

Exit venv:
cmd
> deactivate

You’re now fully set up—VS Code, Python, Jupyter notebooks, interactive scripting, OpenAI API access, linting, formatting, Git/Copilot, and cost controls. 