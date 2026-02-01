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
    if len(my_list) > 10:
        return my_list[10]  # Crash
    else:
        return {"error": "List index out of range"}

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


# --- FIXABLE LOGIC BUGS (REALISTIC FEATURES) ---

@router.post("/simulate/bug/attribute_error")
def feature_add_to_cart():
    """
    Feature: Add item to shopping cart.
    Bug: AttributeError (Typo in method name).
    """
    logger.info("accessing_feature", feature="shopping_cart", action="add")
    cart = ["apple", "orange"]
    # FIX: Change 'appendd' to 'append'
    cart.appendd("banana") 
    return {"status": "success", "cart": cart}

@router.post("/simulate/bug/name_error")
def feature_get_user_profile():
    """
    Feature: User Profile.
    Bug: NameError (Variable name mismatch).
    """
    logger.info("accessing_feature", feature="user_profile", action="get")
    user_name = "Alice"
    email = "alice@example.com"
    # FIX: Change 'username' to 'user_name'
    return {"user": username, "email": email} 

@router.post("/simulate/bug/value_error")
def feature_process_payment():
    """
    Feature: Process payment amount.
    Bug: ValueError (Invalid type cast).
    """
    logger.info("accessing_feature", feature="payment", action="process")
    amount_str = "$50" # Received from input
    # FIX: Strip '$' before converting: int(amount_str.replace('$', ''))
    amount = int(amount_str)
    return {"status": "processed", "amount": amount}

@router.post("/simulate/bug/file_not_found")
def feature_load_config():
    """
    Feature: Load Application Config.
    Bug: FileNotFoundError (Wrong path).
    """
    logger.info("accessing_feature", feature="config", action="load")
    # FIX: Handle missing file or point to a real file (e.g., match standard config)
    # For simulation, getting this to work might mean mocking the return or creating the file.
    with open("config/app_settings.json", "r") as f:
        return {"config": f.read()}

@router.post("/simulate/bug/unbound_local")
def feature_increment_counter():
    """
    Feature: Visit Counter.
    Bug: UnboundLocalError (Scope issue).
    """
    logger.info("accessing_feature", feature="counter", action="increment")
    count = 100
    def update_count():
        # FIX: Add 'nonlocal count'
        count += 1
        return count
    new_count = update_count()
    return {"visits": new_count}

@router.post("/simulate/bug/module_not_found")
def feature_load_plugin():
    """
    Feature: Load Export Plugin.
    Bug: ModuleNotFoundError.
    """
    logger.info("accessing_feature", feature="plugins", action="load_export")
    # FIX: Remove bad import or mock it
    import pdf_export_plugin 
    return {"status": "plugin_loaded", "plugin": "pdf_export"}

@router.post("/simulate/bug/json_decode")
def feature_parse_webhook():
    """
    Feature: Parse Webhook Payload.
    Bug: JSONDecodeError.
    """
    import json
    logger.info("accessing_feature", feature="webhook", action="parse")
    # Simulating a payload execution
    raw_payload = "{'event': 'order_created'}" # Single quotes are invalid JSON
    # FIX: Use double quotes: '{"event": "order_created"}'
    data = json.loads(raw_payload)
    return {"parsed": True, "data": data}

@router.post("/simulate/bug/permission_error")
def feature_read_system_stats():
    """
    Feature: System Health Stats.
    Bug: PermissionError.
    """
    logger.info("accessing_feature", feature="system_stats", action="read")
    # FIX: Read a user-accessible file (e.g., /proc/loadavg on Linux or just a mock)
    # /etc/shadow is root only
    with open("/etc/shadow", "r") as f:
        return {"stats": f.read()}


# --- ADDITIONAL UNHANDLED ERRORS ---

@router.post("/simulate/unhandled/not_implemented")
def simulate_not_implemented():
    """
    Trigger NotImplementedError.
    """
    logger.info("triggering_unhandled_error", type="NotImplementedError")
    raise NotImplementedError("This feature is coming soon")

@router.post("/simulate/unhandled/assertion")
def simulate_assertion():
    """
    Trigger AssertionError.
    """
    logger.info("triggering_unhandled_error", type="AssertionError")
    assert 1 == 2, "Math is broken"

@router.post("/simulate/unhandled/import_error")
def simulate_import_error():
    """
    Trigger ImportError.
    """
    logger.info("triggering_unhandled_error", type="ImportError")
    raise ImportError("Failed to import required module 'antigravity'")

@router.post("/simulate/unhandled/unicode")
def simulate_unicode_error():
    """
    Trigger UnicodeDecodeError.
    """
    logger.info("triggering_unhandled_error", type="UnicodeDecodeError")
    b'\x80'.decode("utf-8")

@router.post("/simulate/unhandled/floating_point")
def simulate_floating_point():
    """
    Trigger FloatingPointError.
    """
    # Note: Python usually handles floats graciously, forcing an error for sim
    logger.info("triggering_unhandled_error", type="FloatingPointError")
    import math
    math.exp(1000) # Overflow -> usually OverflowError, close enough


# --- ADDITIONAL HANDLED INCIDENTS ---

@router.post("/simulate/connection_refused")
def simulate_connection_refused():
    """
    Simulates ConnectionRefusedError (Handled).
    """
    import socket
    logger.warning("incident_simulated", type="connection_refused")
    try:
        s = socket.socket()
        s.connect(("127.0.0.1", 9999)) # Port 9999 likely closed
    except Exception as e:
        logger.exception(e)
    return {"message": "Connection refused simulated"}

@router.post("/simulate/service_unavailable")
def simulate_service_unavailable():
    """
    Simulates 503 Service Unavailable behavior (Handled).
    """
    from fastapi import HTTPException
    logger.warning("incident_simulated", type="service_unavailable")
    try:
        raise HTTPException(status_code=503, detail="Upstream service down")
    except Exception as e:
        logger.exception(e)
        raise e # Re-raise to actually return 503

@router.post("/simulate/auth_failure")
def simulate_auth_failure():
    """
    Simulates 401 Auth Failure logic error (Handled).
    """
    logger.warning("incident_simulated", type="auth_failure")
    try:
        raise PermissionError("Invalid API Key provided")
    except Exception as e:
        logger.exception(e)
    return {"error": "Authentication failed"}

@router.post("/simulate/read_timeout")
def simulate_read_timeout():
    """
    Simulates Read Timeout (Handled).
    """
    logger.warning("incident_simulated", type="read_timeout")
    try:
        raise TimeoutError("Read operation timed out after 5000ms")
    except Exception as e:
        logger.exception(e)
    return {"error": "Read timeout"}

@router.post("/simulate/cache_explosion")
def simulate_cache_explosion():
    """
    Simulates Cache Explosion (Handled).
    """
    logger.warning("incident_simulated", type="cache_explosion")
    try:
        # Simulate generating too many keys
        raise MemoryError("Redis cache full: 1000000 keys eviction failed")
    except Exception as e:
        logger.exception(e)
    return {"error": "Cache overflow"}


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
