# Import necessary libraries
from dotenv import load_dotenv  # Loads environment variables from a .env file
import os  # For interacting with the operating system (environment variables)
import uuid #For unique user identification
from flask import Flask, request, jsonify  # For Flask web framework
from openai import OpenAI, OpenAIError, RateLimitError # For interacting with OpenAI's API
from models import log_interaction, init_db  # Import functions for interacting with the database
from flask_limiter import Limiter  # To limit the number of requests per minute
from flask_limiter.util import get_remote_address  # Helper to track requests by IP address

load_dotenv() # Load environment variables from the .env file

app = Flask(__name__) # Initialize the Flask web app

# Configure the Flask app with the secret key (used for session management or other security features)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

openai_api_key = os.getenv("OPENAI_API_KEY") # Set the OpenAI API key from the environment variable
client = OpenAI(api_key = openai_api_key) # Initialize the OpenAI client

init_db() # Initialize the SQLite database (creates the database and table if they don't exist)

limiter = Limiter(get_remote_address, app=app) # Initialize the rate limiter to track requests per IP address

# Limit the number of requests (5 requests per minute)
@app.before_request
@limiter.limit("5 per minute")
def rate_limit():
    pass  # Simply a placeholder; rate limiting is handled automatically by the limiter

# Define the POST endpoint that interacts with OpenAI API and handles user requests
@app.route('/openai-completion', methods=['POST'])
def openai_completion():
    # Check if the incoming request is in JSON format. If not, return an error
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json() # Parse the incoming JSON payload

    # Check if the 'prompt' field is present in the JSON payload. If not, return an error
    if 'prompt' not in data:
        return jsonify({"error": "Missing 'prompt' field in request"}), 400

    prompt = data['prompt'] # Extract the 'prompt' from the JSON payload

    # Return an error if 'prompt' is null/None
    if prompt == None:
        return jsonify({"error": "'prompt' field is empty"}), 400
    
    # Get or generate the user_id (session management)
    user_id = request.headers.get('User-ID', None)  # Check if the user ID is provided in the headers
    if not user_id:
        user_id = str(uuid.uuid4())  # Generate a unique user ID using UUID

    try:
        # Simulate different errors for testing by checking custom headers
        if request.headers.get("Simulate-Error") == "OpenAIError":
            raise OpenAIError("Simulated OpenAI API error") # Simulate an OpenAI API error
        elif request.headers.get("Simulate-Error") == "DatabaseError":
            raise Exception("Simulated database error") # Simulate a database error

        # Make a request to OpenAI's API to get a completion for the prompt
        response = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",  # Use GPT-4o-mini model for generating responses
            messages=[{"role": "user", "content": prompt}]  # Structure the input as a conversation
        )

        # Extract the completion text from the API response
        completion_text = response.choices[0].message.content

        # Log the interaction (both prompt and response) into the database
        log_interaction(user_id, prompt, completion_text)

        # Return the prompt and the generated completion in a JSON response
        return jsonify({
            "prompt_received": prompt,
            "completion": completion_text
        }), 200

    except RateLimitError:
        # Handle rate limit errors from OpenAI API
        return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429
    except OpenAIError as e:
        # Catch any OpenAI-specific errors (e.g., API errors)
        log_interaction(prompt, f'{str(e)}')  # Log the error
        return jsonify({"error": f"OpenAI API error: {str(e)}"}), 500
    except Exception as e:
        # Catch any other unexpected errors and log them
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

# Run the Flask app
if __name__ == "__main__":
    # The app will run on all network interfaces (0.0.0.0) on port 8080, with debug mode enabled
    app.run(host="0.0.0.0", port=8080, debug=True)
