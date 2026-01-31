import json
import base64
import requests

# Your endpoint
ALERT_ENDPOINT = "https://ira-agent-dfij4ukyrq-uc.a.run.app/analyze-incident"

def handle_incident(event, context):
    """
    Triggered by Pub/Sub when a log with type=incident appears.
    """
    print("cloud function triggered with event", event)
    # Decode the Pub/Sub message
    message = base64.b64decode(event['data']).decode('utf-8')
    log_entry = json.loads(message)

    # Extract the incident payload
    incident = log_entry.get("jsonPayload", {})
    print("triggered incident", incident)
    # Send POST request to your endpoint
    try:
        response = requests.post(ALERT_ENDPOINT, json=incident)
        print(f"Sent incident: {incident} Status: {response.status_code}")
    except Exception as e:
        print(f"Failed to send incident: {incident} Error: {e}")
