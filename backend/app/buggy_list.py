from fastapi import APIRouter

router = APIRouter()

@router.post("/simulate/script/list")
def get_priority_task_endpoint():
    """
    Processing a task list.
    Contains 2 sequential bugs for the agent to fix.
    """
    tasks = ["Buy Milk", "Walk Dog", "Code"]
    
    # BUG 1: IndexError (Accessing index 5, list has 3 items)
    # Agent fix: Change index to 0, 1, or 2
    priority_task = tasks[5]
    
    # BUG 2: AttributeError (List object has no attribute 'upper')
    # Agent fix: Apply .upper() to the string item, not the list itself (if logic changes)
    # OR more likely: trying to call a method that doesn't exist on the specific item if it wasn't a string, 
    # but here let's do: calling .split() on the list 'tasks'
    
    # Let's say we want to format the list as a string
    # This crashes because tasks is a list, not a string
    formatted = tasks.split(",") 
    
    return {"task": priority_task, "all": formatted}
