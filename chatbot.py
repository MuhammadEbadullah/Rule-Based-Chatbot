"""
Task 4: Production-Ready Multi-Intent Rule-Based Chatbot
------------------------------------------------------------
A terminal-based conversational agent that:
  - Normalizes user text (lowercasing, punctuation stripping)
  - Routes user intent using a dictionary-based dispatch map
  - Maintains session state (user name, conversation history, active topic)
  - Handles multiple "help trees" (support flows) with nested logic
  - Falls back gracefully on unrecognized input

Author: (add your name here)
"""

import re
import random
from datetime import datetime


# =========================================================
# SESSION STATE
# =========================================================
class SessionState:
    """Holds everything the bot needs to remember during a conversation."""

    def __init__(self):
        self.user_name = None
        self.history = []          # list of (user_input, bot_response) tuples
        self.active_topic = None   # tracks which "help tree" we're inside
        self.awaiting_name = False


# =========================================================
# TEXT NORMALIZATION
# =========================================================
def normalize_text(raw_text: str) -> str:
    """
    Clean and standardize user input for reliable intent matching.

    Steps:
    1. Lowercase everything
    2. Strip leading/trailing whitespace
    3. Remove punctuation (keep only letters, numbers, spaces)
    4. Collapse multiple spaces into one
    """
    text = raw_text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


# =========================================================
# INTENT DETECTION
# =========================================================
INTENT_KEYWORDS = {
    "greeting": ["hi", "hello", "hey", "salam", "assalam", "helo"],
    "goodbye": ["bye", "exit", "quit", "goodbye", "see you"],
    "ask_name": ["what is your name", "who are you", "your name"],
    "tell_name": ["my name is", "i am", "im", "call me"],
    "time": ["time", "what time", "current time"],
    "help": ["help", "support", "menu", "options"],
    "order_status": ["order", "track", "shipment", "delivery"],
    "billing": ["bill", "billing", "payment", "invoice", "refund"],
    "thanks": ["thanks", "thank you", "shukriya"],
}


def detect_intent(clean_text: str) -> str:
    """
    Match normalized text against known keyword sets using WHOLE-WORD /
    WHOLE-PHRASE boundaries (not naive substring matching).

    Why word boundaries matter:
        A naive `if kw in clean_text` check would wrongly match the
        keyword "im" (from "i'm Ali") inside the word "time", since
        "im" is literally a substring of "t-im-e". Wrapping each
        keyword in \\b...\\b ensures "im" only matches the standalone
        word "im", not a fragment buried inside another word.
    """
    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            pattern = r"\b" + re.escape(kw) + r"\b"
            if re.search(pattern, clean_text):
                return intent
    return "fallback"


# =========================================================
# INTENT HANDLERS (each returns a string response)
# =========================================================
def handle_greeting(state: SessionState, text: str) -> str:
    if state.user_name:
        return f"Hello again, {state.user_name}! How can I help you today?"
    state.awaiting_name = True
    return "Hi there! I'm ProgreeBot. What's your name?"


def handle_tell_name(state: SessionState, text: str) -> str:
    # Extract name after phrases like "my name is", "i am", "call me"
    match = re.search(r"(?:my name is|i am|im|call me)\s+(\w+)", text)
    if match:
        state.user_name = match.group(1).capitalize()
    else:
        # fallback: assume the last word is the name (e.g. user just typed "sara")
        words = text.split()
        state.user_name = words[-1].capitalize() if words else "Friend"
    state.awaiting_name = False
    return f"Nice to meet you, {state.user_name}! Type 'help' anytime to see what I can do."


def handle_ask_name(state: SessionState, text: str) -> str:
    return "I'm ProgreeBot, your friendly rule-based assistant."


def handle_time(state: SessionState, text: str) -> str:
    now = datetime.now().strftime("%I:%M %p")
    return f"The current time is {now}."


def handle_help(state: SessionState, text: str) -> str:
    state.active_topic = "help_menu"
    return (
        "Here's what I can help with:\n"
        "  1. order   - Track an order / delivery\n"
        "  2. billing - Payments, invoices, refunds\n"
        "  3. time    - Get the current time\n"
        "  4. bye     - End the conversation\n"
        "Just type a keyword to continue."
    )


def handle_order_status(state: SessionState, text: str) -> str:
    state.active_topic = "order"
    return (
        "Sure, I can help with order tracking. "
        "Please share your order ID (e.g. ORD12345), or type 'help' to go back."
    )


def handle_billing(state: SessionState, text: str) -> str:
    # Nested logic: if already inside the billing tree, refine the reply
    if state.active_topic == "billing":
        if re.search(r"\brefund\b", text):
            return ("Refunds are processed within 5-7 business days to your "
                    "original payment method. Type 'help' for the main menu.")
        if re.search(r"\binvoice\b", text):
            return ("Your invoice copy will be emailed to your registered "
                    "address. Type 'help' for the main menu.")
    state.active_topic = "billing"
    return (
        "You're in the billing help tree. I can assist with:\n"
        "  - 'refund' status\n"
        "  - 'invoice' copies\n"
        "Type your specific need, or 'help' to see the main menu."
    )


def handle_order_lookup(state: SessionState, text: str) -> str:
    order_id = re.search(r"\bord\d+\b", text).group().upper()
    state.active_topic = None
    return (f"Order {order_id} is currently IN TRANSIT and expected within "
            "2-3 days. Type 'help' for the main menu.")


def handle_thanks(state: SessionState, text: str) -> str:
    return random.choice([
        "You're welcome!",
        "Anytime! Happy to help.",
        "No problem at all."
    ])


def handle_goodbye(state: SessionState, text: str) -> str:
    name = state.user_name or "there"
    return f"Goodbye, {name}! Have a great day. (session ending)"


def handle_fallback(state: SessionState, text: str) -> str:
    return (
        "Sorry, I didn't quite understand that. "
        "Type 'help' to see what I can do, or try rephrasing."
    )


# =========================================================
# DISPATCH MAP -- connects intents to handler functions
# =========================================================
INTENT_HANDLERS = {
    "greeting": handle_greeting,
    "tell_name": handle_tell_name,
    "ask_name": handle_ask_name,
    "time": handle_time,
    "help": handle_help,
    "order_status": handle_order_status,
    "order_lookup": handle_order_lookup,
    "billing": handle_billing,
    "thanks": handle_thanks,
    "goodbye": handle_goodbye,
    "fallback": handle_fallback,
}


# =========================================================
# CORE RESPONSE ENGINE
# =========================================================
def get_response(state: SessionState, raw_text: str) -> str:
    """
    Full pipeline: normalize -> detect intent -> route -> respond.
    Also applies nested state logic (e.g. mid-conversation name capture).
    """
    clean_text = normalize_text(raw_text)

    # Nested state handling: if we're waiting for the user's name,
    # treat the next input as their name regardless of keyword match.
    if state.awaiting_name and "tell_name" not in clean_text:
        intent = "tell_name"
    elif state.active_topic == "order" and re.search(r"\bord\d+\b", clean_text):
        intent = "order_lookup"
    else:
        intent = detect_intent(clean_text)

    handler = INTENT_HANDLERS.get(intent, handle_fallback)
    response = handler(state, clean_text)

    state.history.append((raw_text, response))
    return response


# =========================================================
# TERMINAL CHAT LOOP
# =========================================================
def run_chat():
    """Main terminal loop for the chatbot."""
    state = SessionState()
    print("=" * 50)
    print(" ProgreeBot - Multi-Intent Rule-Based Assistant")
    print(" Type 'bye' anytime to exit.")
    print("=" * 50)

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBot: Session interrupted. Goodbye!")
            break

        if not user_input:
            print("Bot: Please type something.")
            continue

        response = get_response(state, user_input)
        print(f"Bot: {response}")

        if normalize_text(user_input) in INTENT_KEYWORDS["goodbye"] or \
           detect_intent(normalize_text(user_input)) == "goodbye":
            break


if __name__ == "__main__":
    run_chat()
