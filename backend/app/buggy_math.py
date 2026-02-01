from fastapi import APIRouter

router = APIRouter()

@router.post("/simulate/script/math")
def calculate_efficiency_endpoint():
    """
    Calculates efficiency ratio.
    """
    output = 100
    input_value = 50
    
    # BUG: Hardcoded division by zero
    # The agent should notice this and fix it (e.g., use 'input_value')
    efficiency = output / 0 
    return {"result": efficiency}
