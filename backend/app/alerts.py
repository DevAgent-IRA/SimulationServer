from .logger import logger
import requests
import os

def send_email_alert(subject: str, body: str):
    """
    Simulates sending an email alert.
    """
    # In a real app, this would use SMTP or an email API (SendGrid, SES)
    logger.info("email_alert_sent", subject=subject, body=body, type="alert")

import datetime

def notify_agent(severity: str, error_message: str, incident_type: str = "raw_error"):
    """
    Simulates notifying the AI agent with a specific payload format.
    Only sends the last 20 lines of the error message.
    """
    # Split by lines and keep only the last 20
    error_lines = error_message.splitlines()
    error_msg = "\n".join(error_lines[-20:])
    print("asdf", error_msg)
    payload = {
        "type": incident_type,
        "severity": severity.upper(),
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "error": error_msg
    }

    logger.debug("agent_notification", payload=payload, type="incident_trigger")
    
    # Use default URL if not provided to ensure we simulate the POST request
    # Priority: Environment Variable -> Default Localhost
    target_url = os.getenv("AGENT_URL") or "https://ira-agent-dfij4ukyrq-uc.a.run.app/analyze-incident"
    
    try:
        response = requests.post(target_url, json=payload, timeout=5)
        logger.info("agent_webhook_payload_sent", status_code=response.status_code, url=target_url)
    except Exception as e:
        # We catch the error because the webhook might not exist, but we attempted the POST
        logger.warning("agent_webhook_failed", error=str(e), url=target_url)
