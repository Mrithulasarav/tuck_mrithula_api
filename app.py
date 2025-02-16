from flask import Flask, request, jsonify
import json
import logging
import os
from dotenv import load_dotenv

# Loading environment variables from .env file
load_dotenv()

# Initializing Flask app
app = Flask(__name__)

# Configuring logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
MARKDOWN_FILE = os.getenv("MARKDOWN_FILE", "markdown_storage.txt")
GPT_OUTPUT_FILE = os.getenv("GPT_OUTPUT_FILE", "gpt_output.json")

# Loading the initial JSON data
def load_initial_markdown():
    try:
        with open(GPT_OUTPUT_FILE, "r") as file:
            data = json.load(file)
        return data["gptOutput"]
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        logger.error(f"Error loading initial markdown: {e}")
        return ""

# Loading persistent markdown from file if it exists
def load_persistent_markdown():
    try:
        with open(MARKDOWN_FILE, "r") as file:
            return file.read()
    except FileNotFoundError:
        logger.warning(f"Persistent markdown file '{MARKDOWN_FILE}' not found. Starting with initial markdown.")
        return ""
    except Exception as e:
        logger.error(f"Error loading persistent markdown: {e}")
        return ""

# Saving updated markdown to file
def save_markdown(markdown):
    try:
        with open(MARKDOWN_FILE, "w") as file:
            file.write(markdown)
        logger.info("Markdown saved successfully.")
    except Exception as e:
        logger.error(f"Error saving markdown: {e}")

# Initializing markdown
markdown = load_persistent_markdown() or load_initial_markdown()

# GET endpoint to return the current markdown
@app.route("/markdown", methods=["GET"])
def get_markdown():
    return jsonify({"markdown": markdown})

# POST endpoint to update the markdown
@app.route("/markdown", methods=["POST"])
def update_markdown():
    global markdown
    new_sentence = request.json.get("sentence", "").strip()

    # Validating input
    if not new_sentence:
        logger.warning("POST request received with empty sentence.")
        return jsonify({"error": "No sentence provided"}), 400

    # Updating markdown
    markdown += f"\n{new_sentence}"
    save_markdown(markdown)

    logger.info(f"Markdown updated with new sentence: {new_sentence}")
    return jsonify({"message": "Markdown updated successfully", "markdown": markdown})

# Error handler for 404
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

# Error handler for 500
@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    # Run the app
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")