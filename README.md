# Smart AI Chatbot

A full-stack AI chatbot application built with **Python Flask, SQLite, Google Gemini API, HTML, CSS, and JavaScript**. The application provides an interactive ChatGPT-like experience with user authentication, AI-powered conversations, and persistent chat history.

## Features

* AI-powered chatbot using Google Gemini
* User registration and login
* Secure password hashing
* Session-based authentication
* Persistent chat history using SQLite
* View previous conversations
* Clear chat history
* Context-aware conversations using recent chat history
* Responsive and simple web interface
* Flask REST API backend
* CORS support for frontend-backend communication

## Tech Stack

### Frontend

* HTML5
* CSS3
* JavaScript

### Backend

* Python
* Flask
* Flask-CORS
* SQLite
* Werkzeug
* Google Gemini API

### AI Model

* Google Gemini `gemini-2.5-flash`

### Database

* SQLite

## Project Structure

```text
Smart-Ai-Chatbot/
│
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── chatbot.db
│
├── fronted/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── .gitignore
└── README.md
```

## How It Works

The application follows a simple full-stack architecture:

```text
User
  │
  ▼
Frontend
HTML + CSS + JavaScript
  │
  ▼
Flask REST API
  │
  ├── User Authentication
  ├── Chat Management
  ├── Chat History
  │
  ▼
SQLite Database
  │
  ▼
Google Gemini API
  │
  ▼
AI Response
  │
  ▼
Frontend
```

## API Endpoints

### Authentication

| Method | Endpoint      | Description          |
| ------ | ------------- | -------------------- |
| POST   | `/api/signup` | Create a new account |
| POST   | `/api/login`  | Login user           |
| POST   | `/api/logout` | Logout user          |
| GET    | `/api/me`     | Check login status   |

### Chat

| Method | Endpoint             | Description               |
| ------ | -------------------- | ------------------------- |
| POST   | `/api/chat`          | Send a message to the AI  |
| GET    | `/api/history`       | Retrieve chat history     |
| POST   | `/api/history/clear` | Clear user's chat history |

## Requirements

Make sure you have the following installed:

* Python 3.10 or higher
* pip
* A Google Gemini API key
* A modern web browser

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Gauravk-maker/Smart-Ai-Chatbot.git
```

```bash
cd Smart-Ai-Chatbot
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

For macOS/Linux:

```bash
source venv/bin/activate
```

### 3. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

The backend dependencies include Flask, Flask-CORS, Google Generative AI, and Werkzeug.

## Configure Gemini API

Create a Google Gemini API key and set it as an environment variable.

### Windows PowerShell

```powershell
$env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
$env:FLASK_SECRET_KEY="YOUR_SECRET_KEY"
```

### Windows CMD

```cmd
set GEMINI_API_KEY=YOUR_GEMINI_API_KEY
set FLASK_SECRET_KEY=YOUR_SECRET_KEY
```

Do not upload your API key to GitHub.

## Run the Backend

From the `backend` directory:

```bash
python app.py
```

The Flask server will run at:

```text
http://127.0.0.1:5000
```

You can test the backend by opening:

```text
http://127.0.0.1:5000/
```

You should receive a response indicating that the AI chatbot backend is running successfully.

## Run the Frontend

The frontend is located in:

```text
fronted/
```

It contains:

```text
index.html
script.js
style.css
```

You can open `index.html` in your browser, or preferably use the **Live Server** extension in VS Code.

Make sure the Flask backend is running before using the chatbot.

## Database

The application uses SQLite to store:

* User accounts
* Password hashes
* Chat messages
* Message roles
* Chat timestamps

The database is automatically initialized when the Flask application starts.

## Security

The project includes several basic security measures:

* Passwords are stored using password hashing rather than plain text.
* User sessions are used for authentication.
* Chat history is associated with individual users.
* API credentials are loaded through environment variables.

For production deployment, the default Flask secret key should be replaced with a strong randomly generated secret.

## Example Workflow

1. Open the chatbot frontend.
2. Create a new account.
3. Login using your credentials.
4. Enter a question in the chat interface.
5. The frontend sends the message to the Flask API.
6. Flask authenticates the user.
7. The message is saved in SQLite.
8. The message is sent to Google Gemini.
9. Gemini generates an AI response.
10. The response is returned to the frontend.
11. The AI response is saved in the chat history.



## Author

**Gaurav Kumar**

B.Tech CSE | AI/ML Enthusiast

GitHub: [Gauravk-maker](https://github.com/Gauravk-maker)

## License

This project is intended for educational and personal development purposes.

