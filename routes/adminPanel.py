from flask import Blueprint, render_template, session, redirect, abort
from models.models import Match, User

adminPanel_bp = Blueprint('adminPanel', __name__)

@adminPanel_bp.route("/adminpanel")
def adminPanel():
    if session.get('user_role') != 'admin':
        abort(404)
    
    matches = Match.query.all()
    users = User.query.all()
    return render_template("adminPanel.html", matches=matches, users=users)