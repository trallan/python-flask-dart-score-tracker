from flask import Blueprint, render_template, session, redirect

adminPanel_bp = Blueprint('adminPanel', __name__)

@adminPanel_bp.route("/adminpanel")
def adminPanel():
    if session.get('user_role') != 'admin':
        return "Unauthorized", 403
    
    return render_template("adminPanel.html")