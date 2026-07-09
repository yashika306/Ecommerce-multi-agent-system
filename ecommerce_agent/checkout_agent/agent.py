from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext

from ..order_summary_agent.agent import order_summary_agent


def save_shipping_address(address: str, tool_context: ToolContext) -> dict:
    """Saves the user's shipping address to session state so later agents
    (like order_summary_agent) can read it.

    Args:
        address: The user's full shipping address as provided in conversation.
        tool_context: Injected automatically by ADK — gives access to the
            current conversation's session state (unique per user session).

    Returns:
        dict: Confirmation that the address was saved.
    """
    tool_context.state["shipping_address"] = address
    return {"status": "success", "message": "Shipping address saved."}


# checkout_agent is a SUB-AGENT of catalog_agent (not a tool) — once control
# transfers here, this agent talks directly to the user until it's done,
# then hands off to its own sub-agent (order_summary_agent).
checkout_agent = LlmAgent(
    name="checkout_agent",
    model="gemini-2.5-flash",
    description=(
        "Collects the user's shipping address to complete an order, "
        "then hands off to the order summary agent."
    ),
    instruction="""
Goal: Collect the user's shipping address.

Workflow:
1. Ask the user for their shipping address.
2. Use the save_shipping_address tool to save it to session state.
3. Once you have captured the shipping address, ask the user if they'd like
   to view their order summary.
4. If the tool returns status "error", tell the user clearly what was wrong and ask them to provide it again — do NOT proceed until it's saved successfully.
5. Once confirmed, transfer control to order_summary_agent.
""",
    tools=[save_shipping_address],
    sub_agents=[order_summary_agent],
)
