Production-Ready Multi-Intent Rule-Based Chatbot 🤖

A terminal chatbot in pure Python that routes user input across multiple conversation flows
using a dictionary-based dispatch map and nested session state.

| Task | Folder | Description |
|------|--------|-------------|
| Task 4 | [`task4-rule-based-chatbot`](./task4-rule-based-chatbot) | Multi-intent rule-based terminal chatbot with session state |

## Features
- **Text normalization**: lowercasing, punctuation stripping, whitespace collapsing
- **Multi-intent detection**: greeting, name capture, help menu, order tracking, billing, time, thanks, goodbye
- **Whole-word matching** with regex `\b` boundaries (so "time" is never mistaken for the keyword "im")
- **Session state** (`SessionState`): user name, conversation history, active topic
- **Nested help trees**:
  - `help` → `order` → give an order ID (e.g. `ORD12345`) → status reply
  - `help` → `billing` → `refund` / `invoice` → separate replies
- **Graceful fallback** for unrecognized input; handles empty input and Ctrl+C

## Run
```bash
python3 chatbot.py
```

## Sample session
Full transcript in [`sample_output.txt`](./sample_output.txt). Excerpt:

```
Ebad: hi
Bot: Hi there! I'm ProgreeBot. What's your name?

Ebad: my name is Ebad
Bot: Nice to meet you, Ebad! Type 'help' anytime to see what I can do.

Ebad: billing
Bot: You're in the billing help tree. I can assist with:
  - 'refund' status
  - 'invoice' copies

Ebad: refund
Bot: Refunds are processed within 5-7 business days to your original payment method.

Ebad: blah blah xyz
Bot: Sorry, I didn't quite understand that. Type 'help' to see what I can do, or try rephrasing.
```

## How it works
1. `normalize_text()` cleans raw input
2. `detect_intent()` matches it against `INTENT_KEYWORDS` using word-boundary regex
3. `INTENT_HANDLERS` (dictionary) maps each intent to a handler function
4. `get_response()` applies nested state checks first (awaiting name, inside order tree), then routes
5. `run_chat()` is the terminal loop

## Files
```
chatbot.py            # chatbot + terminal loop
sample_output.txt     # real transcript
README.md
```

## Ideas for extension
Conversation logging to file, unit tests, more help trees, a Flask web front end.

## Requirements
- Python 3.7+
- No external libraries (standard library only)
