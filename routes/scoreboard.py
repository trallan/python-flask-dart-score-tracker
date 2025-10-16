from flask import Blueprint, render_template, session, redirect
from models.models import User

scoreboard_bp = Blueprint('scoreboard', __name__)

@scoreboard_bp.route("/scoreboard")
def scoreboard():
    users = User.query.all()

    # Calculate score and match count for each user
    user_stats = []
    for user in users:
        wins = len(user.won_matches)
        losses = len(user.lost_matches)
        total_matches = wins + losses
        score = wins  # Or whatever logic you want

        user_stats.append({
            'username': user.username,
            'score': score * 12,
            'matches': total_matches,
        })

    # Sort by score descending
    user_stats.sort(key=lambda x: x['score'], reverse=True)

    # Assign ranks
    for i, user in enumerate(user_stats, start=1):
        user['rank'] = i

    return render_template('scoreboard.html', user_stats=user_stats)
