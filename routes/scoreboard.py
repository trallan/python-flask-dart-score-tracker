from flask import Blueprint, render_template, session, redirect

scoreboard_bp = Blueprint('scoreboard', __name__)

@scoreboard_bp.route("/scoreboard")
def scoreboard():
    if 'user_id' not in session:
        return redirect('/login')
    
    return render_template("scoreboard.html")