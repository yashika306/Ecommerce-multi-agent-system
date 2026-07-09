from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext
from pydantic import ValidationError
from ..models import ShippingAddress

def save_shipping_address(address: str, tool_context: ToolContext) -> dict:
    try:
        validated = ShippingAddress(address=address)
    except ValidationError as e:
        return {
            "status": "error",
            "message": "; ".join(err["msg"] for err in e.errors()),
        }

    tool_context.state["shipping_address"] = validated.address
    return {"status": "success", "message": "Shipping address saved."}
# This is the FINAL agent in the sub-agent chain: no tools, no sub-agents.
# It only READS from session state (using the {key} templating syntax below)
# to generate a friendly, human-readable order summary — mirroring the
# order confirmation screen you'd see on Amazon/Flipkart after checkout.
order_summary_agent = LlmAgent(
    name="order_summary_agent",
    model="gemini-2.5-flash",
    description=(
        "Reads the complete order information from session state and "
        "generates a friendly, human-readable order summary for the user."
    ),
    instruction="""
Read the complete order information from session state:

Name: {name}
Email: {email}
Mobile: {mobile?}
Item: {item}
Quantity: {quantity}
Price: {price}
Shipping Address: {shipping_address}

Using this information, generate a friendly order summary, the way Amazon
or Flipkart would display an order confirmation after checkout — include
the item, quantity, total price, shipping address, and a thank-you note.

IMPORTANT RULE: Only use information that is present in session state above.
Never invent, guess, or hallucinate any detail that isn't explicitly given
to you here. If something is missing, say so plainly instead of making it up.

Note: {mobile?} uses the optional-state syntax (trailing "?") since a field
might not always be present in state — everything else here is required and
will always be present by the time this agent runs.
""",
    tools=[ save_shipping_address],
)
