#!/usr/bin/env python3

from flask import Flask, request, jsonify
import json
import logging
from datetime import datetime

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.route('/webhook', methods=['POST'])
def alertmanager_webhook():
    try:
        # Log complete request details
        logger.info("=" * 80)
        logger.info("WEBHOOK REQUEST RECEIVED")
        logger.info("=" * 80)

        # Log request headers
        logger.info("REQUEST HEADERS:")
        for header_name, header_value in request.headers.items():
            logger.info(f"  {header_name}: {header_value}")

        # Log request metadata
        logger.info(f"METHOD: {request.method}")
        logger.info(f"URL: {request.url}")
        logger.info(f"REMOTE_ADDR: {request.remote_addr}")
        logger.info(f"USER_AGENT: {request.headers.get('User-Agent', 'Not provided')}")
        logger.info(f"CONTENT_TYPE: {request.content_type}")
        logger.info(f"CONTENT_LENGTH: {request.content_length}")

        # Log raw request data
        raw_data = request.get_data(as_text=True)
        logger.info("RAW REQUEST BODY:")
        logger.info(raw_data)

        if request.content_type != 'application/json':
            logger.warning(f"Unexpected content type: {request.content_type}")
            return jsonify({'error': 'Content-Type must be application/json'}), 400

        payload = request.get_json()
        if not payload:
            logger.error("Failed to parse JSON payload")
            return jsonify({'error': 'Invalid JSON payload'}), 400

        # Log parsed JSON payload with pretty formatting
        logger.info("PARSED JSON PAYLOAD:")
        logger.info(json.dumps(payload, indent=2, default=str))

        logger.info(f"Received webhook with {len(payload.get('alerts', []))} alerts")
        
        for alert in payload.get('alerts', []):
            status = alert.get('status', 'unknown')
            alertname = alert.get('labels', {}).get('alertname', 'Unknown')
            instance = alert.get('labels', {}).get('instance', 'Unknown')
            
            logger.info(f"Alert: {alertname} - Status: {status} - Instance: {instance}")
            
            if status == 'firing':
                handle_firing_alert(alert)
            elif status == 'resolved':
                handle_resolved_alert(alert)
        
        logger.info("=" * 80)
        logger.info("WEBHOOK PROCESSING COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)

        return jsonify({'status': 'received'}), 200

    except Exception as e:
        logger.error("=" * 80)
        logger.error("WEBHOOK PROCESSING FAILED")
        logger.error(f"Error: {str(e)}")
        logger.error("=" * 80)
        return jsonify({'error': 'Internal server error'}), 500

def handle_firing_alert(alert):
    alertname = alert.get('labels', {}).get('alertname', 'Unknown')
    summary = alert.get('annotations', {}).get('summary', 'No summary')
    description = alert.get('annotations', {}).get('description', 'No description')
    
    logger.warning(f"FIRING ALERT: {alertname}")
    logger.warning(f"Summary: {summary}")
    logger.warning(f"Description: {description}")

def handle_resolved_alert(alert):
    alertname = alert.get('labels', {}).get('alertname', 'Unknown')
    logger.info(f"RESOLVED ALERT: {alertname}")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}), 200

if __name__ == '__main__':
    logger.info("Starting Alertmanager webhook receiver...")
    app.run(host='0.0.0.0', port=8080, debug=False)
