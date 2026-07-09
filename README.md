# E-Commerce Multi-Agent System (Google ADK)

A 4-agent system demonstrating **sub-agent delegation** and **session state** management in Google's Agent Development Kit (ADK) — built around a simulated e-commerce shopping flow.

## The Agent Chain

```
ecommerce_agent (root)
  └── catalog_agent (sub-agent)
        └── checkout_agent (sub-agent)
              └── order_summary_agent (sub-agent, final)
```

Each agent finishes its part of the job, then **transfers control** to the next agent in the chain — the user ends up talking to a different agent at each stage, without ever having to know that's happening.

| Agent | Job | Tool | Reads from state |
|---|---|---|---|
| `ecommerce_agent` | Greets user, collects name/email/mobile | `save_user_info` | — |
| `catalog_agent` | Shows product categories, builds cart | `save_cart` | — |
| `checkout_agent` | Collects shipping address | `save_shipping_address` | — |
| `order_summary_agent` | Generates final order summary | *(none)* | name, email, mobile, item, quantity, price, shipping_address |

## Key Concept: Sub-Agents vs. Tools

This project deliberately uses **sub-agents** (`sub_agents=[...]`), not tools (`AgentTool`), to connect these four agents. The difference matters:

- **Tool**: once the tool's logic finishes, control returns to the agent that called it. That agent still talks to the user.
- **Sub-agent**: once control transfers, the sub-agent talks directly to the user from then on. Control does **not** automatically bounce back to the parent.

That's why `ecommerce_agent` → `catalog_agent` → `checkout_agent` → `order_summary_agent` is a one-way chain of handoffs, each agent taking over the conversation fully once it receives control.

## Key Concept: Session State & `ToolContext`

Every custom tool in this project takes a `tool_context: ToolContext` parameter, injected automatically by ADK. This gives access to **session state** — a dictionary scoped to the current conversation only.

Why this matters: if this app were public and 100 different users were chatting with it simultaneously, `tool_context.state` for one user's conversation is completely isolated from everyone else's. Each session gets its own private state.

`order_summary_agent` demonstrates the **read side**: its instructions use `{name}`, `{item}`, `{shipping_address}`, etc. — ADK automatically substitutes these from session state before the LLM ever sees the prompt. The `{mobile?}` syntax (trailing `?`) marks a field as optional, in case it isn't present in state for some conditional-branching scenario.

## Project Structure

```
ecommerce_agent/
├── __init__.py
├── agent.py                          # root_agent: save_user_info tool + catalog_agent as sub-agent
├── .env                               # your GOOGLE_API_KEY goes here
├── catalog_agent/
│   ├── __init__.py
│   └── agent.py                       # save_cart tool + checkout_agent as sub-agent
├── checkout_agent/
│   ├── __init__.py
│   └── agent.py                       # save_shipping_address tool + order_summary_agent as sub-agent
└── order_summary_agent/
    ├── __init__.py
    └── agent.py                       # no tools, no sub-agents — reads state, generates summary
requirements.txt
README.md
```

## Setup

1. Get a free Gemini API key from [Google AI Studio](https://aistudio.google.com) → **Get API Key** → **Create API key**.
2. Paste it into `ecommerce_agent/.env`:
   ```
   GOOGLE_GENAI_USE_VERTEXAI=FALSE
   GOOGLE_API_KEY=your_actual_key_here
   ```
3. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Run

From the folder **containing** `ecommerce_agent/`:
```bash
adk web
```
Open the printed URL, select **ecommerce_agent** from the dropdown, and start chatting.

### Try this conversation:
1. "Hi" → agent introduces itself, asks for your name, email, mobile
2. Provide your details → transfers to `catalog_agent`
3. "I'm looking for a new purchase" → shown 3 categories
4. "Smartphones" → shown product list → "2 Pixel 9" → added to cart
5. "Yes, checkout" → transfers to `checkout_agent`, asks for shipping address
6. Provide an address → "Yes, show my order summary" → transfers to `order_summary_agent`
7. Final agent reads everything from session state and generates a friendly order summary

### Debugging tip
In the ADK web UI, go to **Sessions** → select your session → **State** to inspect exactly what's been saved at any point in the conversation — invaluable for understanding what each agent can (and can't) see.

## What's Next

This project uses instruction-driven sequential handoffs (each agent's instructions manually say "then transfer to X"). The next step in this series replaces this with ADK's **Workflow Agents** — specifically `SequentialAgent` — which enforces the execution order structurally instead of relying on the LLM to follow instructions correctly every time.
