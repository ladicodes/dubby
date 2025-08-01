from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class LeaderboardEntry(db.Model):
    __tablename__ = 'leaderboard'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(10), nullable=False)  # 'easy' or 'hard'
    time = db.Column(db.Float, nullable=False)  # time in seconds
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'difficulty': self.difficulty,
            'time': self.time,
            'date': self.date.isoformat() + 'Z'
        }
    
    def __repr__(self):
        return f'<LeaderboardEntry {self.name}: {self.time}s on {self.difficulty}>'

