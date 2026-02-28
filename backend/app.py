from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

import uuid

# Set Google Cloud credentials from environment
if os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
    logger.info(f"Using credentials from: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')}")
else:
    logger.warning("GOOGLE_APPLICATION_CREDENTIALS not set")

try:
    from text_extractor import main  # Your analysis function
    logger.info("Text extractor loaded successfully")
except Exception as e:
    logger.error(f"Failed to load text_extractor: {e}")
    main = None

try:
    from detection import EnhancedFakeInfoDetector  # Import your detector class
    logger.info("Detection module loaded successfully")
except Exception as e:
    logger.error(f"Failed to load detection module: {e}")
    EnhancedFakeInfoDetector = None

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if GEMINI_API_KEY:
    logger.info("GEMINI_API_KEY is set")
else:
    logger.warning("GEMINI_API_KEY is not set")

# from firestore import log_to_firestore, get_history  # You need to implement these
# from bigquery import log_to_bigquery  # You need to implement this

app = Flask(__name__)

logger.info("Flask app created")

# Configure CORS to allow requests from your frontend
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://frontend-truthscope123.web.app",
            "https://frontend-truthscope123.firebaseapp.com",
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:5000"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Explicit CORS headers on every response (backup for preflight issues)
@app.after_request
def add_cors_headers(response):
    origin = request.headers.get('Origin', '')
    allowed_origins = [
        "https://frontend-truthscope123.web.app",
        "https://frontend-truthscope123.firebaseapp.com",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5000"
    ]
    if origin in allowed_origins:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

logger.info("CORS configured")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
logger.info(f"Upload folder created: {UPLOAD_FOLDER}")

# Initialize detector lazily
detector = None

def get_detector():
    global detector
    if detector is None and GEMINI_API_KEY and EnhancedFakeInfoDetector:
        try:
            logger.info("Initializing detector...")
            detector = EnhancedFakeInfoDetector(GEMINI_API_KEY)
            logger.info("Detector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize detector: {e}")
    return detector

@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint for Cloud Run"""
    logger.info("Health check endpoint called")
    return jsonify({
        "status": "healthy",
        "service": "Misinformation Detection API v2",
        "gemini_api_configured": bool(GEMINI_API_KEY),
        "detector_available": get_detector() is not None
    }), 200

@app.route("/analyze-document", methods=["POST"])
def analyze_document():
    detector = get_detector()
    if not main:
        return jsonify({"error": "Text extractor not available"}), 500
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    extracted = main(file_path)
    doc_text = extracted.get("document_text", "")
    misinfo_result = None
    if detector and doc_text.strip():
        misinfo_result = detector.analyze_text(doc_text)
    result = {
        "id": str(int(time.time() * 1000)),
        "type": "document",
        "file": file.filename,
        "verdict": "pending",
        "extracted": extracted,
        "misinformation_analysis": misinfo_result,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    os.remove(file_path)
    return jsonify(result)


@app.route('/analyze-misinformation/detailed', methods=['POST'])
def analyze_misinformation_detailed():
    detector = get_detector()
    if detector is None:
        return jsonify({'error': 'Detector not initialized. Please check GEMINI_API_KEY configuration.'}), 500
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    text = data.get('text')
    scrape_urls = data.get('scrape_urls', True)
    if not text or not text.strip():
        return jsonify({'error': 'Text cannot be empty'}), 400
    try:
        results = detector.analyze_text(text, scrape_urls)
        return jsonify({
            'status': 'success',
            'results': results,
            'analysis_type': 'comprehensive'
        })
    except Exception as e:
        logger.error(f"Error in analyze_misinformation_detailed: {e}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route("/analyze-image", methods=["POST"])
def analyze_image():
    detector = get_detector()
    if not main:
        return jsonify({"error": "Text extractor not available"}), 500
    
    logger.info(f"Request files: {request.files}")

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    extracted = main(file_path)
    # Try to get text from extraction result
    image_text = extracted.get("image_text", "")
    misinfo_result = None
    if detector and image_text.strip():
        misinfo_result = detector.analyze_text(image_text)
    result = {
        "id": str(int(time.time() * 1000)),
        "type": "image",
        "input": file.filename,
        "verdict": "pending",
        "extracted": extracted,
        "misinformation_analysis": misinfo_result,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    os.remove(file_path)
    return jsonify(result)

@app.route("/analyze-audio", methods=["POST"])
def analyze_audio():
    detector = get_detector()
    if not main:
        return jsonify({"error": "Text extractor not available"}), 500
    
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"

    file_path = os.path.join(UPLOAD_FOLDER,filename)
    file.save(file_path)

    # ✅ Process audio
    extracted = main(file_path)
    transcript = extracted.get("audio_transcript", "")
    misinfo_result = None
    if detector and transcript.strip():
        misinfo_result = detector.analyze_text(transcript)
    result = {
        "id": str(int(time.time() * 1000)),
        "type": "audio",
        "file": file.filename,
        "verdict": "pending",
        "extracted": extracted,
        "misinformation_analysis": misinfo_result,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    os.remove(file_path)
    return jsonify(result)


@app.route("/analyze-video", methods=["POST"])
def analyze_video():
    detector = get_detector()
    if not main:
        return jsonify({"error": "Text extractor not available"}), 500
    
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    try:
        extracted = main(file_path)  # your unified processing
        # Try to get transcript from extraction result
        transcript = extracted.get("video_audio_transcript", "")
        misinfo_result = None
        if detector and transcript.strip():
            misinfo_result = detector.analyze_text(transcript)
        result = {
            "id": str(int(time.time() * 1000)),
            "status": "success",
            "type": "video",
            "file": file.filename,
            "verdict": "pending",
            "extracted": extracted,
            "misinformation_analysis": misinfo_result,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
    except Exception as e:
        result = {
            "status": "error",
            "message": str(e)
        }
    finally:
        os.remove(file_path)  # clean up
    return jsonify(result)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "running"})

@app.route("/metrics", methods=["GET"])
def metrics():
    import psutil
    return jsonify({
        "backend_metrics": {
            "uptime": time.time(),
            "memory_usage": psutil.virtual_memory()._asdict(),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        },
        "microservice_metrics": {}  # Fill if you have other microservices
    })

@app.route("/history", methods=["GET"])
def history():
    # logs = get_history()  # Implement Firestore history retrieval
    logs = []  # Placeholder
    return jsonify({"status": "success", "count": len(logs), "logs": logs})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    # Disable debug mode for production
    debug_mode = os.environ.get("FLASK_ENV") != "production"
    logger.info(f"Starting Flask app on port {port}, debug={debug_mode}")
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
