from fastapi import APIRouter, BackgroundTasks
from .logger import logger
from .alerts import send_email_alert, notify_agent
import time
import threading
import uuid
import sys

router = APIRouter()

# Global state for memory leak simulation
memory_hog = []

# --- HANDLED ERRORS (~40%) ---

@router.post("/simulate/memory_leak")
def simulate_memory_leak(background_tasks: BackgroundTasks):
    """
    Simulates a memory leak (Handled Exception).
    """
    logger.warning("incident_simulated", type="memory_leak", status="started")
    
    def leak():
        for _ in range(10):
            memory_hog.append(" " * 10 * 1024 * 1024) 
            time.sleep(1)
        
        try:
            raise MemoryError("Out of memory: Kill process or sacrifice child")
        except Exception as e:
            logger.exception(e)
            
        send_email_alert("High Memory Usage Detected", "Memory usage has crossed critical threshold.")
        notify_agent(severity="high", error_message="Memory usage spike detected.", incident_type="memory_leak")

    background_tasks.add_task(leak)
    return {"message": "Memory leak simulation started"}

@router.post("/simulate/memory_reset")
def reset_memory():
    global memory_hog
    memory_hog = []
    logger.info("memory_reset", status="cleared")
    return {"message": "Memory cleared"}

@router.post("/simulate/timeout")
def simulate_timeout(duration: int = 30):
    """
    Simulates an API timeout (Handled Exception).
    """
    logger.warning("incident_simulated", type="api_timeout", duration=duration)
    
    time.sleep(duration)
    
    try:
        raise TimeoutError(f"Request timed out after {duration}s")
    except Exception as e:
        logger.exception(e)
    
    notify_agent(severity="medium", error_message=f"Endpoint took {duration}s to respond.", incident_type="api_timeout")
    return {"message": f"Finished sleeping for {duration}s"}

@router.post("/simulate/disk_full")
def simulate_disk_full():
    """
    Simulates disk full (Handled Exception).
    """
    logger.warning("incident_simulated", type="disk_full", status="simulated")
    
    try:
        raise OSError(28, "No space left on device", "/data")
    except Exception as e:
        logger.exception(e)
    
    send_email_alert("Disk Full Warning", "Disk usage at 99.9% on /data")
    notify_agent(severity="critical", error_message="Disk usage critical.", incident_type="disk_full")
    
    return {"message": "Disk full incident simulated", "metrics": {"disk_usage": 99.9}}

@router.post("/simulate/division_by_zero")
def simulate_division_by_zero():
    """
    Simulates division by zero (Handled Exception).
    """
    try:
        result = 1 / 0
        return {"result": result}
    except Exception as e:
        logger.exception(e)
        notify_agent(severity="high", error_message=str(e), incident_type="division_by_zero")
        return {"error": "Division by zero simulated"}

@router.post("/simulate/db_error")
def simulate_db_error(duration: int = 30):
    """
    Simulates DB error (Handled Exception).
    """
    from .database import DB_FILE
    import os
    
    logger.warning("incident_simulated", type="db_connection_error", duration=duration)
    
    original_path = DB_FILE
    broken_path = DB_FILE + ".broken"
    
    try:
        if os.path.exists(original_path):
            os.rename(original_path, broken_path)
            logger.info("db_broken", status="file_renamed")
            
            def restore():
                time.sleep(duration)
                if os.path.exists(broken_path):
                    os.rename(broken_path, original_path)
                    logger.info("db_restored", status="file_restored")
            
            threading.Thread(target=restore).start()
            notify_agent(severity="critical", error_message="Database unreachable.", incident_type="db_connection_error")
            return {"message": f"DB error simulated for {duration}s"}
        else:
            return {"message": "DB file not found, maybe already broken?"}
    except Exception as e:
        logger.exception(e)
        return {"error": str(e)}


# --- UNHANDLED ERRORS (~60%) ---

@router.post("/simulate/unhandled/index_error")
def simulate_index_error():
    """
    Trigger an unhandled IndexError.
    """
    logger.info("triggering_unhandled_error", type="IndexError")
    my_list = [1, 2, 3]
    return my_list[10]  # Crash

@router.post("/simulate/unhandled/key_error")
def simulate_key_error():
    """
    Trigger an unhandled KeyError.
    """
    logger.info("triggering_unhandled_error", type="KeyError")
    my_dict = {"a": 1}
    return my_dict["b"]  # Crash

@router.post("/simulate/unhandled/type_error")
def simulate_type_error():
    """
    Trigger an unhandled TypeError.
    """
    logger.info("triggering_unhandled_error", type="TypeError")
    return 1 + "2"  # Crash

@router.post("/simulate/unhandled/recursion_error")
def simulate_recursion_error():
    """
    Trigger an unhandled RecursionError.
    """
    logger.info("triggering_unhandled_error", type="RecursionError")
    def recursive():
        return recursive()
    return recursive()  # Crash

@router.post("/simulate/unhandled/syntax_error")
def simulate_syntax_error():
    """
    Trigger an unhandled SyntaxError (via eval).
    """
    logger.info("triggering_unhandled_error", type="SyntaxError")
    eval("x =")  # Crash


# --- FIXABLE LOGIC BUGS (FOR AGENT TO SOLVE) ---

@router.post("/simulate/bug/attribute_error")
def simulate_attribute_error():
    """
    Bug: Typo in method name.
    """
    logger.info("triggering_bug", type="AttributeError")
    my_list = []
    # FIX: Should be .append()
    my_list.appendd("item") 
    return {"message": "Should fail before this"}

@router.post("/simulate/bug/name_error")
def simulate_name_error():
    """
    Bug: Variable name mismatch.
    """
    logger.info("triggering_bug", type="NameError")
    user_name = "Alice"
    # FIX: Should be user_name
    return {"user": username} 

@router.post("/simulate/bug/value_error")
def simulate_value_error():
    """
    Bug: Invalid type cast logic.
    """
    logger.info("triggering_bug", type="ValueError")
    value = "not_a_number"
    # FIX: Should validate input or catch error
    return {"number": int(value)}

@router.post("/simulate/bug/file_not_found")
def simulate_file_not_found():
    """
    Bug: Hardcoded wrong path.
    """
    logger.info("triggering_bug", type="FileNotFoundError")
    # FIX: Path should be valid or handled
    with open("/tmp/non_existent_config.json", "r") as f:
        return f.read()


@router.post("/simulate/traffic_gen")
def simulate_traffic_gen(duration: int = 60, background_tasks: BackgroundTasks = None):
    """
    Generates continuous traffic.
    """
    import random
    
    logger.info("traffic_gen_started", duration=duration, ratio="4:1")
    
    def generate_traffic():
        end_time = time.time() + duration
        
        while time.time() < end_time:
            is_success = random.random() < 0.8
            request_id = str(uuid.uuid4())
            
            if is_success:
                action = random.choice(["get_todos", "create_todo", "update_todo"])
                logger.debug(
                    "request_finished", 
                    method="GET" if action == "get_todos" else "POST",
                    path="/todos",
                    status_code=200,
                    process_time=random.uniform(0.01, 0.1), 
                    request_id=request_id,
                    action=action
                )
            else:
                # Simulate errors
                error_type = random.choice(["timeout", "db_error", "500_internal"])
                status_code = 504 if error_type == "timeout" else 500
                
                path = "/todos" if error_type == "db_error" else "/simulate/timeout"

                # Log generic error to mimic application failure
                # Note: traffic generator specific 'incidents' are still logged here manually
                # as they are 'simulated client side' observations.
                logger.error(
                    error_type,
                    details={
                        "method": "POST",
                        "path": path,
                        "status_code": status_code,
                        "process_time": random.uniform(0.1, 2.0),
                        "request_id": request_id
                    }
                )
            
            time.sleep(random.uniform(0.1, 0.5))

        logger.info("traffic_gen_finished", duration=duration)

    if background_tasks:
        background_tasks.add_task(generate_traffic)
    else:
        threading.Thread(target=generate_traffic).start()
        
    return {"message": f"Traffic generation started for {duration}s"}
