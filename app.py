from flask import Flask, render_template, request, session, redirect, jsonify, flash
from flask_session import Session
from models import db
from models.models import Match, User

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///scores.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

Session(app)
db.init_app(app)

@app.route('/addscore', methods=["GET", "POST"])
def add_score():
    if session.get('user_role') != 'admin':
        return "Unauthorized", 403
    
    if request.method == 'POST':
        score = request.form.get('score')
        winner_username = request.form.get('winner').lower()
        loser_username = request.form.get('loser').lower()

        winner = User.query.filter_by(username=winner_username).first()
        loser = User.query.filter_by(username=loser_username).first()

        if not winner:
            return "Winner not found", 400
        if not loser:
            return "Loser not found", 400
        
        new_match = Match(
            winner_id=winner.id,
            loser_id=loser.id,
            score=score
        )
        db.session.add(new_match)
        db.session.commit()

        return redirect('/')
    return render_template('addscore.html')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect('/login')
    
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

@app.route("/")
def index():
    return render_template("index.html", user_id=session.get('user_id'), user_name=session.get('user_name'), user_role=session.get('user_role'))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.username
            session['user_role'] = user.role
            return redirect('/')
        else:
            flash('Invalid username or password')
            return redirect('/login')
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/matches")
def matches():
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
     
    all_matches = Match.query.all()
    return jsonify([
        {
            'id': m.id,
            'score': m.score,
            'date': m.date.strftime("%Y-%m-%d %H:%M:%S"),
            'winner': m.winner.username if m.winner else None,
            'loser': m.loser.username if m.loser else None
        }
        for m in all_matches
    ])

if __name__ == '__main__':
    app.run(debug=True)
