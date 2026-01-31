from .logger import logger
import requests

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
    
    if agent_url:
        try:
            response = requests.post(agent_url, json=payload, timeout=5)
            logger.info("agent_webhook_payload_sent", status_code=response.status_code)
        except Exception as e:
            logger.debug("agent_webhook_failed", error=str(e))
