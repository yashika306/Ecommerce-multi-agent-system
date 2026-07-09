from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext

from .catalog_agent.agent import catalog_agent
from pydantic import ValidationError
from .models import UserInfo

def save_user_info(name: str, email: str, mobile: str, tool_context: ToolContext) -> dict:
    """Saves the user's basic profile information to session state, so that
    every other agent later in the chain (catalog, checkout, order summary)
    can read it without asking the user again.

    Args:
        name: The user's full name.
        email: The user's email address.
        mobile: The user's mobile number.
        tool_context: Injected automatically by ADK. Gives access to the
            CURRENT conversation's session state only — if 100 different
            users are chatting with this app at once, each one's data stays
            isolated to their own session, never mixed with anyone else's.

    Returns:
        dict: Confirmation that the user's info was saved.
    """
    try:
        validated = UserInfo(name=name, email=email, mobile=mobile)
    except ValidationError as e:
        return {
            "status": "error",
            "message": "; ".join(err["msg"] for err in e.errors()),
        }

    tool_context.state["name"] = validated.name
    tool_context.state["email"] = validated.email
    tool_context.state["mobile"] = validated.mobile
    return {"status": "success", "message": f"Saved info for {validated.name}."}

# This is the ROOT agent. It owns the custom tool (save_user_info) and
# delegates to catalog_agent as a SUB-AGENT (not a tool) — meaning once
# control transfers to catalog_agent, catalog_agent talks directly to the
# user; control does NOT automatically bounce back to this root agent.
ecommerce_agent = LlmAgent(
    name="ecommerce_agent",
    model="gemini-2.5-flash-lite",
    description=(
        "Root e-commerce agent. Greets the user, collects their profile "
        "info, and routes them to the right sub-agent based on intent."
    ),
    instruction="""
You are an e-commerce agent who helps users with their shopping experience:
finding products, checkout, and tracking their orders.

Workflow:
1. Greet the user and give a brief introduction about yourself and what
   you can help with (finding products, checkout, tracking orders).
2. Start gathering the user's details: ask for their name, email, and
   mobile number.
3. Once you have this information, use the save_user_info tool to save it.
4. Ask the user: are they looking to make a new purchase, or track an
   existing order?
5. If the tool returns status "error", tell the user clearly what was wrong and ask them to provide it again — do NOT proceed until it's saved successfully.
6. Based on the user's intent, route the request to the correct sub-agent.
   For a new purchase, transfer to catalog_agent.
""",
    tools=[save_user_info],
    sub_agents=[catalog_agent],
)

# ADK's `adk web` / `adk run` looks for a variable named `root_agent`.
root_agent = ecommerce_agent