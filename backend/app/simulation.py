from fastapi import APIRouter, BackgroundTasks
from .logger import logger
from .alerts import send_email_alert, notify_agent
import time
import threading
import uuid


router = APIRouter()

# Global state for memory leak simulation
memory_hog = []

@router.post("/simulate/memory_leak")
def simulate_memory_leak(background_tasks: BackgroundTasks):
    """
    Simulates a memory leak by appending data to a global list.
    """
    logger.warning("incident_simulated", type="memory_leak", status="started")
    
    # Simulate gradual leak
    def leak():
        for _ in range(10):
            # Append 10MB strings
            memory_hog.append(" " * 10 * 1024 * 1024) 
            logger.info("memory_usage_increasing", current_size_mb=len(memory_hog) * 10)
            time.sleep(1)
        
        send_email_alert("High Memory Usage Detected", "Memory usage has crossed critical threshold.")
        notify_agent({"incident": "memory_leak", "severity": "high", "details": "Memory usage spike detected."})

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
    Simulates an API timeout by sleeping.
    """
    logger.warning("incident_simulated", type="api_timeout", duration=duration)
    
    time.sleep(duration)
    
    # This might not be reached if the client times out, but we log it anyway
    logger.error("api_timeout_occurred", duration=duration)
    notify_agent({"incident": "api_timeout", "severity": "medium", "details": f"Endpoint took {duration}s to respond."})
    return {"message": f"Finished sleeping for {duration}s"}

@router.post("/simulate/disk_full")
def simulate_disk_full():
    """
    Simulates disk full metric.
    """
    logger.warning("incident_simulated", type="disk_full", status="simulated")
    
    # Log a metric-like entry
    logger.error("disk_usage_critical", disk_usage_percent=99.9, mount="/data")
    
    send_email_alert("Disk Full Warning", "Disk usage at 99.9% on /data")
    notify_agent({"incident": "disk_full", "severity": "critical", "details": "Disk usage critical."})
    
    return {"message": "Disk full incident simulated", "metrics": {"disk_usage": 99.9}}

@router.post("/simulate/db_error")
def simulate_db_error(duration: int = 30):
    """
    Simulates a database connection error by renaming the DB file.
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
            
            # Schedule restoration
            def restore():
                time.sleep(duration)
                if os.path.exists(broken_path):
                    os.rename(broken_path, original_path)
                    logger.info("db_restored", status="file_restored")
            
            threading.Thread(target=restore).start()
            
            notify_agent({"incident": "db_connection_error", "severity": "critical", "details": "Database unreachable."})
            return {"message": f"DB error simulated for {duration}s"}
        else:
            return {"message": "DB file not found, maybe already broken?"}
    except Exception as e:
        logger.error("simulation_failed", error=str(e))
        return {"error": str(e)}


@router.post("/simulate/traffic_gen")
def simulate_traffic_gen(duration: int = 60, background_tasks: BackgroundTasks = None):
    """
    Generates continuous traffic for a specified duration.
    Ratio: 4 Success : 1 Error.
    """
    import random
    
    logger.info("traffic_gen_started", duration=duration, ratio="4:1")
    
    def generate_traffic():
        end_time = time.time() + duration
        
        while time.time() < end_time:
            # 4:1 ratio means 80% success, 20% error
            is_success = random.random() < 0.8
            
            request_id = str(uuid.uuid4())
            
            if is_success:
                # Simulate successful Todo operations
                action = random.choice(["get_todos", "create_todo", "update_todo"])
                logger.info(
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
                
                # Assign meaningful paths based on error type
                if error_type == "db_error":
                    path = "/todos"
                elif error_type == "timeout":
                    path = "/simulate/timeout"
                else:
                    path = "/simulate/disk_full"

                logger.error(
                    "request_failed",
                    method="POST",
                    path=path,
                    status_code=status_code,
                    error=error_type,
                    process_time=random.uniform(0.1, 2.0),
                    request_id=request_id
                )
            
            # Sleep to prevent flooding logs too fast
            time.sleep(random.uniform(0.1, 0.5))

        logger.info("traffic_gen_finished", duration=duration)

    if background_tasks:
        background_tasks.add_task(generate_traffic)
    else:
        # Fallback if called directly or without background tasks dependency injection working intuitively
        threading.Thread(target=generate_traffic).start()
        
    return {"message": f"Traffic generation started for {duration}s"}

