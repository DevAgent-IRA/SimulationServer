from fastapi import APIRouter

router = APIRouter()

@router.post("/simulate/script/dict")
def get_server_config_endpoint():
    """
    Retrieves server configuration.
    Contains 2 sequential bugs for the agent to fix.
    """
    config = {"host": "localhost", "port": 8080, "debug": True}
    
    # BUG 1: KeyError (Wrong casing)
    # Agent fix: Use "port"
    port = config["Port"]
    
    # BUG 2: TypeError (Unhashable type or bad concatenation)
    # Let's try to add the dict to a string
    # "Config summary: " + config -> TypeError
    summary = "Current Config: " + config
    
    return {"port": port, "summary": summary}
