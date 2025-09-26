# Dart Score Tracker

A simple web application for tracking daily dart games between friends. Built with **Flask**, **SQLite**, and **HTML/CSS**, the app lets you record match results, view statistics, and manage player profiles.

## Features

- Register and log in with a secure password
- Record daily matches (winner, loser, score, and date)
- View a dynamic list of recent matches
- Track player stats: total games, wins, and losses
- Lightweight, fast, and easy to use
- JSON API for match data (fetched via JavaScript)
- Responsive design using Bootstrap (optional)

## Folder Structure
  ├── app.py # Main Flask app  
  ├── models/ # SQLAlchemy models  
  ├── templates/ # HTML (Jinja2) templates  
  ├── static/ # CSS/JS files  
  ├── instance/ # SQLite DB & config 
  ├── flask_session/ # Server-side session files (ignored)  
  ├── venv/ # Virtual environment (ignored)  
  ├── requirements.txt # Python dependencies  
  ├── README.md # You're reading it  

## Tech Stack

- **Python 3**
- **Flask** (Web Framework)
- **Flask-SQLAlchemy** (Database ORM)
- **SQLite** (Lightweight database)
- **Jinja2** (Template engine)
- **HTML + JS** (Frontend with fetch API)
- **Bootstrap** *(optional)*

## How to Run

### 1. Clone the repo
```bash
git clone https://github.com/trallan/python-flask-dart-score-tracker.git
cd dart-score-tracker
```
### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate      # On macOS/Linux
venv\Scripts\activate         # On Windows
```
### 3. Install dependencies
```bash
pip install -r requirements.txt
```
### 4. Run the app
```bash
python app.py or flask run
```

## Environment & Configuration

- Passwords are securely hashed using Werkzeug’s `generate_password_hash` and `check_password_hash`
- User authentication is managed through server-side sessions
- A `venv/` virtual environment is used for dependency isolation (not included in the repo)
- Application configuration and the SQLite database are stored in the `instance/` directory, which is excluded from version control for security
- All unnecessary or sensitive files and folders are ignored via `.gitignore`

## Future Features

- Player registration system
- User authentication is managed through server-side sessions
- Match history filters (by date, opponent, etc.)
- Leaderboard and win percentages
- Graphs/charts for performance over time



