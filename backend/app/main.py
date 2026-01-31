from fastapi import FastAPI, Request, HTTPException
from .simulation import router as simulation_router
from .logger import logger
from .database import get_db_connection
from .alerts import notify_agent
import time
import uuid
from pydantic import BaseModel

class TodoItem(BaseModel):
    title: str
    completed: bool = False

app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    logger.info("request_started", method=request.method, path=request.url.path, request_id=request_id)
    
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(
            "request_finished",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            process_time=process_time,
            request_id=request_id
        )
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            "request_failed",
            details={
                "method": request.method,
                "path": request.url.path,
                "error": str(e),
                "process_time": process_time,
                "request_id": request_id
            }
        )
        notify_agent({
            "incident": "unhandled_exception",
            "severity": "critical",
            "details": {
                "method": request.method,
                "path": request.url.path,
                "error": str(e)
            }
        })
        raise e

app.include_router(simulation_router)

@app.get("/todos")
def get_todos():
    try:
        conn = get_db_connection()
        todos = conn.execute("SELECT * FROM todos").fetchall()
        conn.close()
        return [{"id": row["id"], "title": row["title"], "completed": bool(row["completed"])} for row in todos]
    except Exception as e:
        logger.error("db_query_failed", details={"error": str(e)})
        raise HTTPException(status_code=500, detail="Database Error")

@app.post("/todos")
def create_todo(item: TodoItem):
    try:
        conn = get_db_connection()
        cursor = conn.execute("INSERT INTO todos (title, completed) VALUES (?, ?)", (item.title, item.completed))
        conn.commit()
        todo_id = cursor.lastrowid
        conn.close()
        logger.info("todo_created", id=todo_id, title=item.title)
        return {"id": todo_id, "title": item.title, "completed": item.completed}
    except Exception as e:
        logger.error("db_insert_failed", details={"error": str(e)})
        raise HTTPException(status_code=500, detail="Database Error")

@app.get("/")
def read_root():
    logger.info("root_accessed")
    return {"message": "Incident Response Simulation Backend"}

@app.get("/metrics")
def metrics():
    """
    Mock metrics endpoint.
    """
    return {
        "memory_usage_mb": 512,
        "cpu_usage_percent": 15,
        "disk_usage_percent": 45
    }

