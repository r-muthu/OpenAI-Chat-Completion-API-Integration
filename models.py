# Import necessary libraries
import sqlite3  # For interacting with the SQLite database
from datetime import datetime  # For working with timestamps

# Function to initialize the database and create the table if it doesn't exist
def init_db():
    # Connect to the SQLite database (it will be created if it doesn't exist)
    conn = sqlite3.connect('openai_logs.db')
    c = conn.cursor()

    # Create a table named 'logs' if it doesn't already exist
    c.execute('''CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique ID for each log
                    user_id TEXT NOT NULL,  -- Unique user ID to track different users
                    prompt TEXT NOT NULL,  -- The user prompt (required)
                    completion TEXT NOT NULL,  -- The AI's generated completion (required)
                    timestamp TEXT NOT NULL  -- The timestamp of when the interaction occurred (required)
                )''')

    # Commit the changes to the database and close the connection
    conn.commit()
    conn.close()

# Function to log the interaction (prompt and completion) into the database
def log_interaction(user_id, prompt, completion):
    # Connect to the SQLite database
    conn = sqlite3.connect('openai_logs.db')
    c = conn.cursor()

    # Get the current timestamp in the format YYYY-MM-DD HH:MM:SS
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Insert the prompt, completion, and timestamp into the 'logs' table
    c.execute('''INSERT INTO logs (user_id, prompt, completion, timestamp)
                 VALUES (?, ?, ?, ?)''', (user_id, prompt, completion, timestamp))

    # Commit the changes to the database and close the connection
    conn.commit()
    conn.close()