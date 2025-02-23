"""
Slack Events Webhook Handler

This module provides a Flask endpoint to handle Slack Events API requests,
including event subscription verification and event processing.
"""

import os
import json
import logging
from flask import Flask, request, jsonify

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_url_verification(event_data):
    """
    Handle Slack URL verification challenge.
    
    Args:
        event_data (dict): Incoming event data from Slack
    
    Returns:
        dict: Challenge response
    """
    challenge = event_data.get('challenge')
    logger.info("Received URL verification challenge")
    return {"challenge": challenge}

def handle_app_mention(event):
    """
    Handle events where the bot is mentioned.
    
    Args:
        event (dict): Slack event data
    
    Returns:
        dict: Response message
    """
    logger.info(f"Bot mentioned in channel {event.get('channel')}")
    user = event.get('user')
    
    # Basic response logic
    return {
        "text": f"Hola <@{user}>! Gracias por mencionarme. ¿En qué puedo ayudarte?"
    }

def handle_message(event):
    """
    Handle incoming messages.
    
    Args:
        event (dict): Slack event data
    
    Returns:
        dict or None: Response message or None
    """
    # Ignore bot messages to prevent potential loops
    if event.get('bot_id'):
        return None

    logger.info(f"Message received in channel {event.get('channel')}")
    
    text = event.get('text', '')
    user = event.get('user')
    
    # Example: Simple echo
    return {
        "text": f"Recibí tu mensaje: {text}"
    }

# Initialize Flask app
app = Flask(__name__)

@app.route("/", methods=["POST"])
def slack_events():
    """
    Endpoint for Slack Events API
    
    Note: Request verification is handled by ngrok using --verify-webhook=slack
    
    Handles:
    1. URL Verification Challenge
    2. Event Processing
    """
    # Parse incoming request data
    event_data = request.json

    # Handle URL verification challenge
    if event_data and event_data.get('type') == 'url_verification':
        return jsonify(handle_url_verification(event_data))

    # Process other Slack events
    if 'event' in event_data:
        event_type = event_data['event'].get('type')
        
        if event_type == 'app_mention':
            response = handle_app_mention(event_data['event'])
        elif event_type == 'message':
            response = handle_message(event_data['event'])
        else:
            logger.info(f"Unhandled event type: {event_type}")
            return jsonify({"status": "ok"})
        
        return jsonify(response) if response else jsonify({"status": "ok"})

    return jsonify({"error": "No event found"}), 400

def start_webhook_server(port=3000):
    """
    Start the Flask webhook server.
    
    Args:
        port (int, optional): Port to run the server. Defaults to 3000.
    """
    app.run(host='0.0.0.0', port=port, debug=True)

if __name__ == '__main__':
    start_webhook_server()
