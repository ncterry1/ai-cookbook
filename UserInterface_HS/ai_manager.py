# ai_manager.py
"""
Module for mapping AI modes to their handlers and invoking them dynamically.

EXPORTS:
  • AVAILABLE_MODES: dict mapping mode names to module paths
  • call_ai_function: loads the module for a given mode and calls its run(prompt)
"""

import importlib

# ==========
# MODE DISPATCH CONFIGURATION
# ==========
# Map friendly mode names to the ai_functions module that provides run()
AVAILABLE_MODES = {
    "Q&A":           "ai_functions.qa",
    "Data Analysis": "ai_functions.data_analysis",
}

# ==========
# CALL AI FUNCTION
# ==========
def call_ai_function(mode: str, prompt: str) -> str:
    """
    Dynamically imports the module for the given mode and calls its run(prompt).
    Returns the AI-generated response or an error message.
    """
    module_path = AVAILABLE_MODES.get(mode)
    if not module_path:
        return f"Invalid mode: {mode}"
    try:
        module = importlib.import_module(module_path)
    except ImportError as err:
        return f"Error importing {module_path}: {err}"
    if not hasattr(module, "run"):
        return f"Module '{module_path}' missing run(prompt) function"
    try:
        return module.run(prompt)
    except Exception as err:
        return f"Error during AI function execution: {err}"
