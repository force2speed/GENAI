from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import uuid
from text_extractor import main  # Your analysis function
from detection import EnhancedFakeInfoDetector  # Import your detector class
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# from firestore import log_to_firestore, get_history  # You need to implement these
# from bigquery import log_to_bigquery  # You need to implement this

app = Flask(__name__)

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

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
detector = EnhancedFakeInfoDetector(GEMINI_API_KEY) if GEMINI_API_KEY else None
@app.route("/analyze-document", methods=["POST"])
def analyze_document():
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
    if detector is None:
        return jsonify({'error': 'Detector not initialized'}), 400
    data = request.get_json()
    text = data.get('text')
    scrape_urls = data.get('scrape_urls', True)
    if not text or not text.strip():
        return jsonify({'error': 'Text cannot be empty'}), 400
    results = detector.analyze_text(text, scrape_urls)
    return jsonify({
        'status': 'success',
        'results': results,
        'analysis_type': 'comprehensive'
    })

@app.route("/analyze-image", methods=["POST"])

def analyze_image():
    print(request.files)

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

@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "service": "Misinformation Detection API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "endpoints": {
            "analyze_text": "/analyze-text",
            "analyze_image": "/analyze-image",
            "analyze_audio": "/analyze-audio",
            "analyze_video": "/analyze-video",
            "health": "/health",
            "metrics": "/metrics"
        }
    })

@app.route("/history", methods=["GET"])
def history():
    # logs = get_history()  # Implement Firestore history retrieval
    logs = []  # Placeholder
    return jsonify({"status": "success", "count": len(logs), "logs": logs})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # Use 5000 or another free port
    app.run(host="0.0.0.0", port=port)
