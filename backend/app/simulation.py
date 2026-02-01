import traceback
from fastapi import APIRouter

from .alerts import notify_agent
from .logger import logger

router = APIRouter()


@router.post("/simulate/division_by_zero")
def simulate_division_by_zero():
    """
    Simulates division by zero (Handled Exception).
    """
    try:
        numerator = 1
        denominator = 0
        if denominator == 0:
            result = None
            logger.warning("Division by zero avoided")
        else:
            result = numerator / denominator
        return {"result": result}
    except Exception as e:
        logger.exception(e)
        full_traceback = traceback.format_exc()
        notify_agent(
            severity="high",
            error_message=full_traceback,
            incident_type="division_by_zero",
        )
        return {"error": "Division by zero simulated"}
