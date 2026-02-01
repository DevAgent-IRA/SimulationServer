from fastapi import APIRouter

router = APIRouter()

@router.post("/simulate/script/math")
def calculate_efficiency_endpoint():
    """
    Calculates efficiency ratio.
    Contains 2 sequential bugs for the agent to fix.
    """
    output = 100
    input_value = 50
    
    # BUG 1: Hardcoded division by zero
    # Agent fix: Change 0 to input_value (50)
    efficiency = output / 0 
    
    # BUG 2: TypeError (Adding float to string)
    # Agent fix: Use f-string or str(efficiency)
    result_msg = "Efficiency is: " + efficiency
    
    return {"result": result_msg}
