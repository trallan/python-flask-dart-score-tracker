from flask import Flask, render_template, request, session, redirect, jsonify, flash, url_for, flash, abort
from routes import register_blueprints
from werkzeug.security import generate_password_hash
from flask_session import Session
from models import db
from models.models import Match, User
import re

app = Flask(__name__)
register_blueprints(app)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///scores.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 60 * 60 * 24 # Caches static files for 1 days

Session(app)
db.init_app(app)

@app.route('/edituser/<int:user_id>', methods=['POST'])
def edit_user(user_id):
    if session.get('user_role') != 'admin':
        return "Unauthorized", 403

    user = User.query.get_or_404(user_id)

    username = request.form.get('username')
    email = request.form.get('email')
    role = request.form.get('role')

    # Optional: check duplicates
    existing_user = User.query.filter(
        ((User.username == username) | (User.email == email)) & (User.id != user.id)
    ).first()
    if existing_user:
        flash("Username or email already exists.", "danger")
        return redirect(url_for('adminPanel.adminPanel'))

    # Update user
    user.username = username
    user.email = email
    user.role = role
    db.session.commit()

    flash(f"User '{username}' updated successfully!", "success")
    return redirect(url_for('adminPanel.adminPanel'))

@app.route("/delete_match/<int:match_id>", methods=["POST"])
def delete_match(match_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Only allow admins
    if session.get('user_role') != 'admin':
        abort(404)

    match = Match.query.get(match_id)
    if not match:
        flash("Match not found.", "warning")
        return redirect(url_for('adminPanel.adminPanel'))

    db.session.delete(match)
    db.session.commit()
    flash("Match deleted successfully.", "success")
    return redirect(url_for('adminPanel.adminPanel'))

@app.route('/deletuser/<int:user_id>', methods=["POST"])
def delete_user(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Only allow admins
    if session.get('user_role') != 'admin':
        abort(404)
    
    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "warning")
        return redirect(url_for('adminPanel.adminPanel'))

    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully.", "success")
    return redirect(url_for('adminPanel.adminPanel'))

@app.route('/adduser', methods=["POST"])
def add_user():
    if session.get('user_role') != 'admin':
        abort(404)
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        role = request.form.get('role')

        if not username or not password or not email or not role:
            flash("All fields are required.", "danger")
            return redirect(url_for('adminPanel.adminPanel'))
        
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Username or email already exists.", "danger")
            return redirect(url_for('adminPanel.adminPanel'))

        new_user = User(
            username=username,
            password_hash=generate_password_hash(password),
            email=email,
            role=role
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('adminPanel.adminPanel'))

    return redirect(url_for('adminPanel.adminPanel'))

@app.route('/addscore', methods=["GET", "POST"])
def add_score():
    if session.get('user_role') not in ['admin', 'moderator']:
        return "Unauthorized", 403
    
    if request.method == 'POST':
        score = request.form.get('score')
        winner_username = request.form.get('winner').lower()
        loser_username = request.form.get('loser').lower()

        # Validate score format using regex
        if not re.fullmatch(r'(0|[1-9]\d*)-(0|[1-9]\d*)', score):
            return "Invalid score format. Use format 'X-Y' with numbers only, no spaces.", 400

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
    if (user.wins + user.losses) > 0:
        user_win_rate = round((user.wins / (user.wins + user.losses)) * 100)
        return render_template('profile.html', user=user, user_win_rate=user_win_rate)
    else:
        user_win_rate = 0
        return render_template('profile.html', user=user, user_win_rate=user_win_rate)
    

@app.route("/")
def index():
    if 'user_id' not in session:
        return redirect('/login')
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
