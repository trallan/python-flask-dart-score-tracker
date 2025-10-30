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

@app.route('/editmatch/<int:match_id>', methods=['POST'])
def edit_match(match_id):
    if session.get('user_role') != 'admin':
        return "Unauthorized", 403

    match = Match.query.get_or_404(match_id)

    try:
        winner_id = int(request.form.get('winner'))
        loser_id = int(request.form.get('loser'))
    except (TypeError, ValueError):
        flash("Invalid winner or loser selection.", "danger")
        return redirect(url_for('adminPanel.adminPanel') + '#matchesPanel')

    score = request.form.get('score')

    # Get user objects
    winner_user = User.query.get(winner_id)
    loser_user = User.query.get(loser_id)

    if not winner_user or not loser_user:
        flash("Winner or loser not found.", "danger")
        return redirect(url_for('adminPanel.adminPanel') + '#matchesPanel')

    if winner_id == loser_id:
        flash("Winner and loser must be different users.", "danger")
        return redirect(url_for('adminPanel.adminPanel') + '#matchesPanel')

    match.winner_id = winner_id
    match.loser_id = loser_id
    match.score = score
    db.session.commit()

    flash(f"Match updated: {winner_user.username} vs {loser_user.username}", "success")
    return redirect(url_for('adminPanel.adminPanel') + '#matchesPanel')



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
        return redirect(url_for('adminPanel.adminPanel') + '#matchesPanel')

    db.session.delete(match)
    db.session.commit()
    flash("Match deleted successfully.", "success")
    return redirect(url_for('adminPanel.adminPanel') + '#matchesPanel')

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
        abort(404)

    user_session = session.get('user_role')
    users = User.query.all()
    
    if request.method == 'POST':  
        winner_username = request.form.get('winner').lower()
        loser_username = request.form.get('loser').lower()
        score = request.form.get('score')

        # Validate score format using regex
        if not re.fullmatch(r'(0|[1-9]\d*)-(0|[1-9]\d*)', score):
            return "Invalid score format. Use format 'X-Y' with numbers only, no spaces.", 400

        winner = User.query.filter_by(username=winner_username).first()
        loser = User.query.filter_by(username=loser_username).first()

        if not winner:
            flash("All fields are required.", "danger")
            return redirect(url_for('adminPanel.adminPanel'))
        if not loser:
            flash("All fields are required.", "danger")
            return redirect(url_for('adminPanel.adminPanel'))
        
        new_match = Match(
            winner_id=winner.id,
            loser_id=loser.id,
            score=score
        )
        db.session.add(new_match)
        db.session.commit()

        if user_session == 'moderator':
            return redirect('/')

        return redirect(url_for('adminPanel.adminPanel') + '#matchesPanel')
    if user_session == 'moderator':
            return render_template('addscore.html', users=users)
    return redirect(url_for('adminPanel.adminPanel') + '#matchesPanel')

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

    page = request.args.get('page', 1, type=int)
    per_page = 7

    # Query total count for pagination
    total_matches = Match.query.count()
    total_pages = (total_matches + per_page - 1) // per_page

    # Fetch only the rows needed for this page
    paginated_matches = (
        Match.query
        .order_by(Match.date.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return jsonify({
        "matches": [
            {
                'id': m.id,
                'score': m.score,
                'date': m.date.strftime("%Y-%m-%d %H:%M:%S"),
                'winner': m.winner.username if m.winner else None,
                'loser': m.loser.username if m.loser else None,
            } for m in paginated_matches
        ],
        "page": page,
        "total_pages": total_pages
    })



if __name__ == '__main__':
    app.run(debug=True)
