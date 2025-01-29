# OpenAI Chat Completion API Integration

By Muthu Ramaswamy

This Python-based API service acts as a middleman between the client and OpenAI's Chat Completion API. The service:
- Handles incoming data
- Makes requests to OpenAI's API to generate completions
- Logs the request and response data in an SQLite database
- Returns the completion to the client

## Features:
- **POST Endpoint**: `/openai-completion`
- **Rate Limiting**: 5 requests per minute per client
- **Error Handling**: Gracefully handles missing fields, invalid input, rate limiting, and OpenAI errors.

## Setup Instructions

### Prerequisites:
- Python 3.8 or higher
- [OpenAI API Key](https://platform.openai.com/account/api-keys)

### 1. Clone the repository
```bash
git clone <repository_url>
cd <repository_folder>
```

### 2. Install dependencies
```bash
python -m venv venv
source venv/bin/activate   # For macOS/Linux
venv\Scripts\activate      # For Windows
pip install -r requirements.txt
```

### 3. Set up environment variables
Create a `.env` file and add the following:
```env
SECRET_KEY=your_secret_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. Initialize the database
Run the following to initialize the SQLite database:
```bash
flask shell
>>> from models import init_db
>>> init_db()
>>> exit()
```

### 5. Run the application
```bash
python main.py
```

---

## API Usage

### Endpoint: `/openai-completion` (POST)

#### Request Headers:
- `Content-Type`: `application/json`

#### Request Body:
```json
{
    "prompt": "What is the capital of France?"
}
```

#### Response:
```json
{
    "prompt_received": "What is the capital of France?",
    "completion": "The capital of France is Paris."
}
```

### Error Simulation:
To simulate an error, send the following headers:

- **Simulate OpenAI Error**: 
  - `Simulate-Error: OpenAIError`
  - Simulates an OpenAI API error.
  
- **Simulate Database Error**: 
  - `Simulate-Error: DatabaseError`
  - Simulates a server/database error.

---

## Rate Limiting
- Each client can make a maximum of **5 requests per minute**.
- If the rate limit is exceeded, the server will respond with:
```json
{
    "error": "Rate limit exceeded. Please try again later."
}
```

## Testing

### Example cURL Requests:

#### Valid Request:
Without User-ID as header (a random UUID will be generated):
```bash
curl -X POST http://localhost:8080/openai-completion \
-H "Content-Type: application/json" \
-d '{"prompt": "What is the capital of France?"}'
```

With User-ID as header:
```bash
curl -X POST http://localhost:8080/openai-completion \
-H "Content-Type: application/json" \
-H "User-ID: Person-A"
-d '{"prompt": "What is the capital of France?"}'
```

#### Simulate OpenAI Error:
```bash
curl -X POST http://localhost:8080/openai-completion \
-H "Content-Type: application/json" \
-H "Simulate-Error: OpenAIError" \
-d '{"prompt": "Simulate OpenAI error"}'
```

---

## Error Handling

### 400 Errors:
Bad Request Error.
For example:
- Missing `prompt` field in the request body.
- Invalid JSON format.

### 500 Errors:
Unexpected server error.
For example:
- OpenAI API error.
- Database error.

### 429 Errors:
- Rate limit exceeded.

---


## Test Cases (Represented as cURL, pasted into Postman)

## Non-Edge Cases (Normal Cases)

### Test 1: Valid Request
**Description**: Test a valid request with a 'prompt' field in the JSON payload.  
**Expected Response**: Status Code 200, JSON containing 'prompt_received' and 'completion'.  
**cURL**:
```bash
curl -X POST http://localhost:8080/openai-completion \
-H "Content-Type: application/json" \
-d '{"prompt": "What is the capital of France?"}'
```

### Test 2: Missing 'prompt' Field
**Description**: Test a request with no 'prompt' field in the JSON payload.  
**Expected Response**: Status Code 400, JSON response: {"error": "Missing 'prompt' field in request"}  
**cURL**:
```bash
curl -X POST http://localhost:8080/openai-completion \
-H "Content-Type: application/json" \
-d '{}'
```

### Test 3: Empty Prompt
**Description**: Test a request where the 'prompt' field is empty.  
**Expected Response**: Status Code 200, JSON containing 'completion'.  
**cURL**:
```bash
curl -X POST http://localhost:8080/openai-completion \
-H "Content-Type: application/json" \
-d '{"prompt": ""}'
```

### Test 4: Invalid JSON Request
**Description**: Test a request with invalid JSON format (missing closing brace).  
**Expected Response**: Status Code 400, JSON response: {"error": "Request must be JSON"}  
**cURL**:
```bash
curl -X POST http://localhost:8080/openai-completion \
-H "Content-Type: application/json" \
-d '{"prompt": "What is the capital of France?"'
```

### Test 5: Non-JSON Content-Type
**Description**: Test a request with a content type of 'application/x-www-form-urlencoded'.  
**Expected Response**: Status Code 400, JSON response: {"error": "Request must be JSON"}  
**cURL**:
```bash
curl -X POST http://localhost:8080/openai-completion \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "prompt=What is the capital of France?"
```

---

## Edge Cases

### Test 6: Very Long Prompt
**Description**: Test a request with a very long 'prompt' field (10,000 characters).  
**Expected Response**: Status Code 200 or potentially 400/500 depending on OpenAI's behavior.  
**cURL**:
```bash
curl -X POST http://localhost:8080/openai-completion \
-H "Content-Type: application/json" \
-d '{"prompt": "'"$(head -c 10000 < /dev/urandom | base64)"'"}'
```

### Test 7: Rate Limiting
**Description**: Test rate limiting by sending multiple requests quickly (After waiting for a minute for the limit to clear).  
**Expected Response (all within a minute)**: First 5 requests: Status Code 200, 6th request: Status Code 429.  
**cURL**:
```bash
curl -X POST http://localhost:8080/openai-completion \
-H "Content-Type: application/json" \
-d '{"prompt": "What is the capital of France?"}'

curl -X POST http://localhost:8080/openai-completion \
-H "Content-Type: application/json" \
-d '{"prompt": "What is the capital of France?"}'

curl -X POST http://localhost:8080/openai-completion \
-H "Content-Type: application/json" \
-d '{"prompt": "What is the capital of France?"}'

curl -X POST http://localhost:8080/openai-completion \
-H "Content-Type: application/json" \
-d '{"prompt": "What is the capital of France?"}'

curl -X POST http://localhost:8080/openai-completion \
-H "Content-Type: application/json" \
-d '{"prompt": "What is the capital of France?"}'

curl -X POST http://localhost:8080/openai-completion \
-H "Content-Type: application/json" \
-d '{"prompt": "What is the capital of France?"}'
```

### Test 8: Unexpected OpenAI API Error
**Description**: Simulate an OpenAI API error by adding a custom header.  
**Expected Response**: Status Code 500, JSON response: {"error": "OpenAI API error: Simulated OpenAI API error"}  
**cURL**:
```bash
curl -X POST http://localhost:8080/openai-completion \
-H "Content-Type: application/json" \
-H "Simulate-Error: OpenAIError" \
-d '{"prompt": "trigger-error"}'
```

### Test 9: Unexpected Server Error
**Description**: Simulate a server error (e.g., database error).  
**Expected Response**: Status Code 500, JSON response: {"error": "An unexpected error occurred: Simulated database error"}  
**cURL**:
```bash
curl -X POST http://localhost:8080/openai-completion \
-H "Content-Type: application/json" \
-H "Simulate-Error: DatabaseError" \
-d '{"prompt": "simulate-server-error"}'
```

### Test 10: Null Prompt
**Description**: Test a request where the 'prompt' field is set to 'null'.  
**Expected Response**: Status Code 400, JSON response: {"error": "Missing 'prompt' field in request"}  
**cURL**:
```bash
curl -X POST http://localhost:8080/openai-completion \
-H "Content-Type: application/json" \
-d '{"prompt": null}'
```
---
