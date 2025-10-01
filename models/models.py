from datetime import datetime, timezone
from models import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def wins(self):
        return Match.query.filter_by(winner_id=self.id).count()

    @property
    def losses(self):
        return Match.query.filter_by(loser_id=self.id).count()

    @property
    def games_played(self):
        return self.wins + self.losses

    def __repr__(self):
        return f"<User {self.username}>"

class Match(db.Model):
    __tablename__ = 'Matches'

    id = db.Column(db.Integer, primary_key=True)
    winner_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    loser_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=True)
    score = db.Column(db.String(10), nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    winner = db.relationship('User', foreign_keys=[winner_id], backref='won_matches')
    loser = db.relationship('User', foreign_keys=[loser_id], backref='lost_matches')

    def __repr__(self):
        return f"<Match {self.id}: {self.winner_id} vs {self.loser_id}, score={self.score}>"