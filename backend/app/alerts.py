from .logger import logger
import requests
import os

def send_email_alert(subject: str, body: str):
    """
    Simulates sending an email alert.
    """
    # In a real app, this would use SMTP or an email API (SendGrid, SES)
    logger.info("email_alert_sent", subject=subject, body=body, type="alert")

def notify_agent(payload: dict, agent_url: str = None):
    """
    Simulates notifying the AI agent. 
    If agent_url is provided, it tries to POST to it. 
    Otherwise checks AGENT_URL env var.
    """
    logger.debug("agent_notification", payload=payload, type="incident_trigger")
    
    # Use default URL if not provided to ensure we simulate the POST request
    # Use default URL if not provided to ensure we simulate the POST request
    # Priority: Function argument -> Environment Variable -> Default Localhost
    target_url = agent_url or os.getenv("AGENT_URL") or "https://ira-agent-dfij4ukyrq-uc.a.run.app/analyze-incident"
    
    try:
        response = requests.post(target_url, json=payload, timeout=5)
        logger.info("agent_webhook_payload_sent", status_code=response.status_code, url=target_url)
    except Exception as e:
        # We catch the error because the webhook might not exist, but we attempted the POST
        logger.warning("agent_webhook_failed", error=str(e), url=target_url)
