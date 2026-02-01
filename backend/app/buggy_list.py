from fastapi import APIRouter

router = APIRouter()

@router.post("/simulate/script/list")
def get_priority_task_endpoint():
    """
    Returns the 5th task from the list as priority.
    """
    tasks = ["Buy Milk", "Walk Dog", "Code"]
    
    # BUG: Hardcoded index 4 (5th item) without checking length
    # Agent fix: Check length or use index 0
    return {"task": tasks[4]}
