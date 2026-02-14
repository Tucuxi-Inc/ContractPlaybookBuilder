"""
Contract Playbook Builder - Main Flask Application

A web application that generates professional contract playbooks from uploaded agreements.
"""
import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename

import config
from utils.document_parser import parse_document, allowed_file
from utils.playbook_generator import analyze_contract_chunked
from utils.excel_writer import generate_playbook_excel

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = config.MAX_FILE_SIZE_MB * 1024 * 1024

# In-memory storage for progress tracking
processing_status = {}


@app.route("/")
def index():
    """Render the main upload page."""
    return render_template("index.html")


@app.route("/api/config", methods=["GET"])
def get_config():
    """Return current provider/model config and available options."""
    # Determine which key is configured (mask it)
    provider = config.AI_PROVIDER
    has_key = False
    if provider == "anthropic":
        has_key = bool(config.ANTHROPIC_API_KEY)
        current_model = config.ANTHROPIC_MODEL
    elif provider == "openai":
        has_key = bool(config.OPENAI_API_KEY)
        current_model = config.OPENAI_MODEL
    elif provider == "google":
        has_key = bool(config.GOOGLE_API_KEY)
        current_model = config.GOOGLE_MODEL
    else:
        current_model = ""

    return jsonify({
        "provider": provider,
        "model": current_model,
        "has_key": has_key,
        "providers": {
            pid: {"name": p["name"], "models": p["models"]}
            for pid, p in config.AVAILABLE_PROVIDERS.items()
        }
    })


@app.route("/api/config", methods=["POST"])
def save_config():
    """Save provider, model, and API key to .env and reload config."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    provider = data.get("provider", "").strip()
    model = data.get("model", "").strip()
    api_key = data.get("api_key", "").strip()

    if provider not in config.AVAILABLE_PROVIDERS:
        return jsonify({"error": f"Invalid provider: {provider}"}), 400

    provider_info = config.AVAILABLE_PROVIDERS[provider]

    # Check if key is already configured for this provider
    existing_key = getattr(config, provider_info["key_env"], "")
    if not api_key and not existing_key:
        return jsonify({"error": "API key is required"}), 400

    valid_models = [m["id"] for m in provider_info["models"]]
    if model and model not in valid_models:
        return jsonify({"error": f"Invalid model: {model}"}), 400

    if not model:
        model = valid_models[0]

    # Read existing .env or start fresh
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    env_lines = []
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            env_lines = f.readlines()

    # Build a dict of keys to set
    updates = {
        "AI_PROVIDER": provider,
        provider_info["model_env"]: model,
    }
    if api_key:
        updates[provider_info["key_env"]] = api_key

    # Update or append each key
    for key, value in updates.items():
        found = False
        for i, line in enumerate(env_lines):
            stripped = line.strip()
            # Match both active and commented-out lines
            if stripped.startswith(f"{key}=") or stripped.startswith(f"# {key}="):
                env_lines[i] = f"{key}={value}\n"
                found = True
                break
        if not found:
            env_lines.append(f"{key}={value}\n")

    with open(env_path, "w") as f:
        f.writelines(env_lines)

    # Also set in os.environ so reload picks them up
    for key, value in updates.items():
        os.environ[key] = value

    config.reload_config()

    return jsonify({
        "status": "saved",
        "provider": provider,
        "model": model
    })


@app.route("/api/upload", methods=["POST"])
def upload_file():
    """
    Handle file upload and start playbook generation.

    Returns JSON with job_id for progress tracking.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename, config.ALLOWED_EXTENSIONS):
        return jsonify({
            "error": f"File type not supported. Allowed types: {', '.join(config.ALLOWED_EXTENSIONS)}"
        }), 400

    # Check for API key
    if not config.ANTHROPIC_API_KEY and not config.OPENAI_API_KEY and not config.GOOGLE_API_KEY:
        return jsonify({
            "error": "API key not configured. Please configure your AI provider in Settings."
        }), 500

    # Generate unique job ID
    job_id = str(uuid.uuid4())

    # Save uploaded file
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved_filename = f"{timestamp}_{job_id}_{filename}"
    file_path = os.path.join(config.UPLOAD_FOLDER, saved_filename)
    file.save(file_path)

    # Get options from request
    agreement_type = request.form.get("agreement_type", "General Agreement")
    user_role = request.form.get("user_role", "Customer")
    risk_tolerance = request.form.get("risk_tolerance", "Moderate")

    # Initialize status
    processing_status[job_id] = {
        "status": "processing",
        "progress": 0,
        "message": "Uploading file...",
        "file_path": file_path,
        "original_filename": filename,
        "agreement_type": agreement_type,
        "user_role": user_role,
        "risk_tolerance": risk_tolerance,
        "output_path": None,
        "error": None
    }

    return jsonify({
        "job_id": job_id,
        "message": "File uploaded successfully. Processing started."
    })


@app.route("/api/process/<job_id>", methods=["POST"])
def process_file(job_id):
    """
    Process the uploaded file and generate the playbook.
    """
    if job_id not in processing_status:
        return jsonify({"error": "Job not found"}), 404

    job = processing_status[job_id]

    if job["status"] == "completed":
        return jsonify({"status": "completed", "message": "Already processed"})

    if job["status"] == "error":
        return jsonify({"status": "error", "error": job["error"]})

    try:
        # Update progress callback
        def update_progress(progress, message):
            processing_status[job_id]["progress"] = progress
            processing_status[job_id]["message"] = message

        # Step 1: Parse document
        update_progress(10, "Parsing document...")
        doc_data = parse_document(job["file_path"])

        if not doc_data.get("text"):
            raise ValueError("Could not extract text from the document. Please ensure it's not a scanned image.")

        # Step 2: Analyze with AI
        update_progress(20, "Analyzing contract with AI...")
        playbook_data = analyze_contract_chunked(
            contract_text=doc_data["text"],
            agreement_type=job["agreement_type"],
            user_role=job["user_role"],
            risk_tolerance=job["risk_tolerance"],
            progress_callback=lambda p, m: update_progress(20 + int(p * 0.6), m)
        )

        # Step 3: Generate Excel
        update_progress(85, "Generating Excel playbook...")
        output_filename = f"Playbook_{job['original_filename'].rsplit('.', 1)[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        output_path = os.path.join(config.OUTPUT_FOLDER, output_filename)
        generate_playbook_excel(playbook_data, output_path)

        # Update status
        processing_status[job_id]["status"] = "completed"
        processing_status[job_id]["progress"] = 100
        processing_status[job_id]["message"] = "Playbook generated successfully!"
        processing_status[job_id]["output_path"] = output_path
        processing_status[job_id]["output_filename"] = output_filename

        # Clean up uploaded file
        try:
            os.remove(job["file_path"])
        except Exception:
            pass

        return jsonify({
            "status": "completed",
            "message": "Playbook generated successfully!",
            "download_url": f"/api/download/{job_id}"
        })

    except Exception as e:
        processing_status[job_id]["status"] = "error"
        processing_status[job_id]["error"] = str(e)
        processing_status[job_id]["message"] = f"Error: {str(e)}"

        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@app.route("/api/status/<job_id>")
def get_status(job_id):
    """Get the processing status for a job."""
    if job_id not in processing_status:
        return jsonify({"error": "Job not found"}), 404

    job = processing_status[job_id]
    return jsonify({
        "status": job["status"],
        "progress": job["progress"],
        "message": job["message"],
        "error": job.get("error"),
        "download_url": f"/api/download/{job_id}" if job["status"] == "completed" else None
    })


@app.route("/api/download/<job_id>")
def download_file(job_id):
    """Download the generated playbook."""
    if job_id not in processing_status:
        return jsonify({"error": "Job not found"}), 404

    job = processing_status[job_id]

    if job["status"] != "completed":
        return jsonify({"error": "Playbook not ready"}), 400

    if not job.get("output_path") or not os.path.exists(job["output_path"]):
        return jsonify({"error": "Output file not found"}), 404

    return send_file(
        job["output_path"],
        as_attachment=True,
        download_name=job.get("output_filename", "Playbook.xlsx"),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@app.route("/api/health")
def health_check():
    """Health check endpoint."""
    api_configured = bool(config.ANTHROPIC_API_KEY) or bool(config.OPENAI_API_KEY) or bool(config.GOOGLE_API_KEY)
    return jsonify({
        "status": "healthy",
        "api_key_configured": api_configured,
        "provider": config.AI_PROVIDER
    })


if __name__ == "__main__":
    print(f"\n{'='*60}")
    print("Contract Playbook Builder")
    print(f"{'='*60}")
    print(f"Starting server on http://localhost:{config.PORT}")

    if config.AI_PROVIDER == "anthropic" and config.ANTHROPIC_API_KEY:
        print(f"AI Provider: Anthropic Claude ({config.ANTHROPIC_MODEL})")
    elif config.AI_PROVIDER == "openai" and config.OPENAI_API_KEY:
        print(f"AI Provider: OpenAI ({config.OPENAI_MODEL})")
    elif config.AI_PROVIDER == "google" and config.GOOGLE_API_KEY:
        print(f"AI Provider: Google Gemini ({config.GOOGLE_MODEL})")
    else:
        print("AI Provider: NOT CONFIGURED")
        print("Open http://localhost:{} to configure via the setup screen.".format(config.PORT))
    print(f"{'='*60}\n")

    app.run(host="0.0.0.0", port=config.PORT, debug=config.DEBUG)
