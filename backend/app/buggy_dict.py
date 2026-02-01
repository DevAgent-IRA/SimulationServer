from fastapi import APIRouter

router = APIRouter()

@router.post("/simulate/script/dict")
def get_server_port_endpoint():
    """
    Retrieves the port number from config.
    """
    config = {"host": "localhost", "port": 8000}
    
    # BUG: Accessing 'port' key with wrong casing (Port)
    # Agent fix: Use 'port'
    return {"port": config["Port"]}
