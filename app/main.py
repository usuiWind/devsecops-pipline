from flask import Flask, jsonify
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    logger.info("Health check accessed")
    return jsonify({
        "status": "healthy",
        "service": "flask-api",
        "version": os.getenv("APP_VERSION", "1.0.0")
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)