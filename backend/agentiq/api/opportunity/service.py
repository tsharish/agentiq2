from typing import Annotated

from .models import Stage
from .data import opportunities


def get_opportunity_by_name(name: Annotated[str, "Opportunity Name"]):
    """Returns opportunity details including opportunity ID based on the opportunity name"""
    name_lower = name.lower()

    return [
        opportunity for opportunity in opportunities if name_lower in opportunity["name"].lower()
    ]


def create_opportunity(
    name: Annotated[str, "Opportunity Name"],
    customer_id: Annotated[int, "Customer ID"],
    amount: Annotated[float, "Amount"],
):
    """Creates an opportunity record given the opportunity name, customer ID and amount"""
    id = max((opportunity["id"] for opportunity in opportunities), default=0) + 1
    opportunities.append(
        {
            "id": id,
            "name": name,
            "customer_id": customer_id,
            "amount": amount,
            "stage": Stage.open,
        }
    )
    return f"Opportunity {name} successfully created with ID {id}"


def close_opportunity(
    opportunity_id: Annotated[int, "ID of the opportunity"],
    stage: Annotated[str, "Opportunity Stage"] = None,
):
    """Closes an opportunity given the opportunity ID and stage"""
    if stage is None:
        return "Please ask the user to specify the stage as either 'Closed Won' or 'Closed Lost'."

    if stage not in [Stage.closed_won, Stage.closed_lost]:
        return "Invalid stage. Please specify the stage as either 'Closed Won' or 'Closed Lost'."

    opportunity = next(
        (opportunity for opportunity in opportunities if opportunity["id"] == opportunity_id), None
    )
    if not opportunity:
        return f"Opportunity with ID {opportunity_id} not found."

    if opportunity["stage"] != Stage.open:
        return f"Opportunity is already closed."

    opportunity["stage"] = stage
    return f"Opportunity {opportunity["name"]} successfully closed with stage {stage}"


def edit_opportunity(
    opportunity_id: Annotated[int, "ID of the opportunity"],
    name: Annotated[str, "New Opportunity Name"],
    customer_id: Annotated[int, "New Customer ID"],
    amount: Annotated[float, "New Amount"],
):
    """Edits an opportunity record given the opportunity ID and new details of the opportunity"""
    opportunity = next(
        (opportunity for opportunity in opportunities if opportunity["id"] == opportunity_id), None
    )
    if not opportunity:
        return f"Opportunity with ID {opportunity_id} not found"

    opportunity["name"] = name if name else opportunity["name"]
    opportunity["customer_id"] = customer_id if customer_id else opportunity["customer_id"]
    opportunity["amount"] = amount if amount else opportunity["amount"]

    return f"Opportunity {name} successfully updated"


def delete_opportunity(opportunity_id: Annotated[int, "ID of the opportunity to be deleted"]):
    """Deletes an opportunity record given the opportunity ID"""
    opportunity = next(
        (opportunity for opportunity in opportunities if opportunity["id"] == opportunity_id), None
    )

    if not opportunity:
        return f"Opportunity with ID {opportunity_id} not found"

    opportunities.remove(opportunity)
    return f"Opportunity with ID {opportunity_id} successfully deleted"
