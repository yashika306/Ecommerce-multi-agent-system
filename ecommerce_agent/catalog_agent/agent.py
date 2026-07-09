from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext

from ..checkout_agent.agent import checkout_agent
from pydantic import ValidationError
from ..models import CartItem

def save_cart(category: str, item: str, quantity: int, price: float, tool_context: ToolContext) -> dict:
    """Saves the item the user wants to add to their cart to session state.

    Args:
        category: Product category (e.g. "Smartphones", "Laptops", "Headphones").
        item: The specific product name (e.g. "iPhone 16", "Pixel 9").
        quantity: How many units the user wants.
        price: The unit price of the item, in the store's currency.
        tool_context: Injected automatically by ADK — gives access to the
            current conversation's session state.

    Returns:
        dict: Confirmation that the cart item was saved.
    """
    try:
        validated = CartItem(category=category, item=item, quantity=quantity, price=price)
    except ValidationError as e:
        return {
            "status": "error",
            "message": "; ".join(err["msg"] for err in e.errors()),
        }

    tool_context.state["category"] = validated.category
    tool_context.state["item"] = validated.item
    tool_context.state["quantity"] = validated.quantity
    tool_context.state["price"] = validated.price
    return {"status": "success", "message": f"Added {validated.quantity} x {validated.item} to cart."}

    

# This is a DEMO catalog hardcoded into the instructions. In a real system,
# this would come from a CSV, product database, or a custom tool that
# queries your catalog service — swap that in later without changing the
# rest of the agent's logic.
catalog_agent = LlmAgent(
    name="catalog_agent",
    model="gemini-2.5-flash",
    description=(
        "Helps the user browse product categories and add items to their "
        "cart, then hands off to checkout."
    ),
    instruction="""
You help the user browse the product catalog and build their cart.

You have 3 categories of products:

1. Smartphones
   - iPhone 16 — ₹80,000
   - Pixel 9 — ₹70,000
   - Galaxy S24 — ₹75,000

2. Laptops
   - MacBook Air M3 — ₹1,15,000
   - Dell XPS 14 — ₹1,05,000
   - ThinkPad X1 Carbon — ₹1,20,000

3. Headphones
   - Sony WH-1000XM5 — ₹28,000
   - AirPods Pro 2 — ₹22,000
   - Bose QuietComfort — ₹25,000

Workflow:
1. Tell the user you have 3 categories: Smartphones, Laptops, and Headphones.
   Ask which category they'd like to browse.
2. List the items and prices in that category.
3. Ask which item (and how many) they'd like to add to their cart.
4. Use the save_cart tool to save the category, item, quantity, and price
   to session state.
5. Ask the user if they'd like to add more items or proceed to checkout.
6. If the tool returns status "error", tell the user clearly what was wrong and ask them to provide it again — do NOT proceed until it's saved successfully.
7. Once you've captured these details, transfer control to checkout_agent.
""",
    tools=[save_cart],
    sub_agents=[checkout_agent],
)