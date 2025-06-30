# %%
# Cell 1: Environment Setup and Client Initialization
# --------------------------------------------------
# Core Python Imports
# - `Optional`: for functions that may return None when the input isn't a calendar event.
# - `datetime`: to obtain the current date/time, grounding relative date expressions like "next Tuesday".
# - `os`: to read environment variables, particularly the OpenAI API key.
# - `logging`: to instrument the code with structured logs (INFO, DEBUG, WARNING).
from typing import Optional
from datetime import datetime
import os
import logging

# Third-Party Imports
# - `pydantic.BaseModel` and `pydantic.Field`: to define strongly-typed schemas for LLM inputs/outputs.
# - `OpenAI`: the official OpenAI Python client to make chat-completion calls.
from pydantic import BaseModel, Field
from openai import OpenAI

# ------------------------------------------------------------------
# Logging Configuration
# ------------------------------------------------------------------
# Sets up a root logger to emit timestamps, log level, and messages.
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more granular logs
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# OpenAI Client Initialization
# ------------------------------------------------------------------
# Grabs the `OPENAI_API_KEY` from environment; fails fast if not present.
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# Specify the desired LLM model name.
model = "gpt-4o"


# %%
# Cell 2: Define Structured Data Models for Each LLM Call
# --------------------------------------------------------
# Using Pydantic ensures:
#  1) Type safety: we know exactly the types returned from the LLM.
#  2) Documentation: each field has a description for clarity.
#  3) Validation: if the LLM returns unexpected shapes/types, Pydantic will raise.

class EventExtraction(BaseModel):
    """
    Model for the FIRST LLM call:
    - Determines if the user text describes a calendar event.
    - Provides a cleaned-up `description` for downstream parsing.
    - Supplies an `is_calendar_event` flag and `confidence_score`.
    """
    description: str = Field(
        description="LLM's cleaned description of the event or relevant snippet"
    )
    is_calendar_event: bool = Field(
        description="Whether this text should be scheduled in a calendar"
    )
    confidence_score: float = Field(
        description="LLM's self-reported confidence (0.0 to 1.0)"
    )


class EventDetails(BaseModel):
    """
    Model for the SECOND LLM call:
    - Parses `description` into structured details:
      * Event name
      * Exact ISO8601 date/time
      * Duration in minutes
      * Participants list
    """
    name: str = Field(
        description="Title or summary of the event (e.g., 'Team Meeting')"
    )
    date: str = Field(
        description=(
            "ISO 8601–formatted date/time string (e.g., 2025-07-08T14:00:00)"
        )
    )
    duration_minutes: int = Field(
        description="Planned duration of the event, in minutes"
    )
    participants: list[str] = Field(
        description="Names or identifiers of attendees"
    )


class EventConfirmation(BaseModel):
    """
    Model for the THIRD LLM call:
    - Generates a natural confirmation message for the user.
    - Optionally returns a calendar invite link.
    """
    confirmation_message: str = Field(
        description="User-facing confirmation text"
    )
    calendar_link: Optional[str] = Field(
        description="URL to add the event to a calendar, if generated"
    )


# %%
# Cell 3: LLM Invocation Functions
# ---------------------------------
# Each function wraps a single chat call, encapsulating:
#  1) Prompt construction (system + user messages)
#  2) Date context injection (to resolve relative phrases)
#  3) Response parsing into the Pydantic model
#  4) Logging of key events and values


def extract_event_info(user_input: str) -> EventExtraction:
    """
    Stage 1: Gatekeeper

    - Logs entry and raw user input.
    - Prepends a system message with today's date context.
    - Asks the LLM to decide if input is a calendar event.
    - Returns an EventExtraction model with cleaned description,
      boolean flag, and confidence score.
    """
    logger.info("[Stage 1] Starting event extraction analysis")
    logger.debug(f"User input for extraction: '{user_input}'")

    # Build relative date context
    today = datetime.now()
    date_context = f"Today is {today.strftime('%A, %B %d, %Y')}."

    # LLM call
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": f"{date_context} Analyze if the text describes a calendar event."},
            {"role": "user", "content": user_input},
        ],
        response_format=EventExtraction,
    )
    result = completion.choices[0].message.parsed

    # Log core outputs
    logger.info(
        f"[Stage 1] Extraction result - is_event: {result.is_calendar_event}, "
        f"confidence: {result.confidence_score:.2f}"
    )
    return result


def parse_event_details(description: str) -> EventDetails:
    """
    Stage 2: Detail Parser

    - Receives a cleaned `description` from Stage 1.
    - Adds date context for relative date resolution.
    - Requests structured extraction of:
      name, date, duration, participants.
    - Returns an EventDetails instance.
    """
    logger.info("[Stage 2] Starting event details parsing")
    logger.debug(f"Description input for parsing: '{description}'")

    today = datetime.now()
    date_context = f"Today is {today.strftime('%A, %B %d, %Y')}."

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    f"{date_context} Extract detailed event information. "
                    "When dates reference 'next Tuesday', resolve relative to today."
                ),
            },
            {"role": "user", "content": description},
        ],
        response_format=EventDetails,
    )
    result = completion.choices[0].message.parsed

    # Log extracted fields
    logger.info(
        f"[Stage 2] Parsed details - Name: {result.name}, Date: {result.date}, "
        f"Duration: {result.duration_minutes} minutes"
    )
    logger.debug(f"Participants: {result.participants}")
    return result


def generate_confirmation(event_details: EventDetails) -> EventConfirmation:
    """
    Stage 3: Confirmation Generator

    - Takes the fully structured EventDetails model.
    - Sends it to the LLM with instructions to craft a
      friendly confirmation message, signed by 'Susie'.
    - Returns an EventConfirmation model with:
      * Human-readable message
      * Optional calendar link
    """
    logger.info("[Stage 3] Generating confirmation message")
    logger.debug(f"Event details for confirmation: {event_details.model_dump()}")

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "Generate a concise, friendly confirmation message for the event, ending with '— Susie'",
            },
            {"role": "user", "content": str(event_details.model_dump())},
        ],
        response_format=EventConfirmation,
    )
    result = completion.choices[0].message.parsed

    logger.info("[Stage 3] Confirmation generated successfully")
    logger.debug(f"Confirmation message: {result.confirmation_message}")
    return result


# %%
# Cell 4: Orchestrator Function with Gate Check and Logging
# ----------------------------------------------------------
# - Coordinates all three stages
# - Implements a confidence gate (>= 0.7) to bail out early for non-events
# - Captures key transitions in the flow

def process_calendar_request(user_input: str) -> Optional[EventConfirmation]:
    """
    Orchestrator for the prompt chain:
    1. Stage 1: extract_event_info → gate check
    2. Stage 2: parse_event_details (if gate passed)
    3. Stage 3: generate_confirmation
    4. Return final confirmation, or None if gate fails
    """
    logger.info("[Orchestrator] Processing calendar request")
    logger.debug(f"Raw user input: '{user_input}'")

    # Stage 1: gate check
    initial = extract_event_info(user_input)
    if not initial.is_calendar_event or initial.confidence_score < 0.7:
        logger.warning(
            f"[Orchestrator] Gate failed - is_event={initial.is_calendar_event}, "
            f"confidence={initial.confidence_score:.2f}. Aborting."
        )
        return None

    logger.info("[Orchestrator] Gate passed. Continuing to Stage 2")

    # Stage 2: detailed parsing
    details = parse_event_details(initial.description)

    # Stage 3: confirmation message
    confirmation = generate_confirmation(details)

    logger.info("[Orchestrator] Calendar request completed successfully")
    return confirmation


# %%
# Cell 5: Example Usage and Testing
# ----------------------------------
# Demonstrates both a:
#  - Valid event extraction + confirmation flow
#  - Invalid input early-exit scenario
if __name__ == "__main__":
    # Valid event example
    user_input = (
        "Let's schedule a 1h team meeting next Tuesday at 2pm with Alice and Bob "
        "to discuss the project roadmap."
    )
    result = process_calendar_request(user_input)
    if result:
        print("[Result] Confirmation:", result.confirmation_message)
        if result.calendar_link:
            print("[Result] Calendar Link:", result.calendar_link)
    else:
        print("[Result] Input not recognized as a calendar event.")

    # Invalid (non-event) example
    user_input = (
        "Can you send an email to Alice and Bob to discuss the project roadmap?"
    )
    result = process_calendar_request(user_input)
    if result:
        print("[Result] Confirmation:", result.confirmation_message)
    else:
        print("[Result] Input not recognized as a calendar event.")