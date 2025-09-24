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
        if request.content_type != 'application/json':
            logger.warning(f"Unexpected content type: {request.content_type}")
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        payload = request.get_json()
        if not payload:
            return jsonify({'error': 'Invalid JSON payload'}), 400
        
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
        
        return jsonify({'status': 'received'}), 200
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
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
