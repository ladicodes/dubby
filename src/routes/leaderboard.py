from flask import Blueprint, request, jsonify
from src.models.leaderboard import db, LeaderboardEntry
from datetime import datetime

leaderboard_bp = Blueprint('leaderboard', __name__)

@leaderboard_bp.route('/leaderboard/<difficulty>', methods=['GET'])
def get_leaderboard(difficulty):
    """Get top scores for a specific difficulty"""
    if difficulty not in ['easy', 'hard']:
        return jsonify({'error': 'Invalid difficulty. Must be "easy" or "hard"'}), 400
    
    # Get top 10 scores for the difficulty, ordered by time (ascending)
    scores = LeaderboardEntry.query.filter_by(difficulty=difficulty)\
                                 .order_by(LeaderboardEntry.time.asc())\
                                 .limit(10)\
                                 .all()
    
    return jsonify({
        'difficulty': difficulty,
        'scores': [score.to_dict() for score in scores]
    })

@leaderboard_bp.route('/leaderboard', methods=['POST'])
def submit_score():
    """Submit a new score to the leaderboard"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    name = data.get('name', '').strip()
    difficulty = data.get('difficulty')
    time = data.get('time')
    
    # Validation
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    
    if len(name) > 50:
        return jsonify({'error': 'Name must be 50 characters or less'}), 400
    
    if difficulty not in ['easy', 'hard']:
        return jsonify({'error': 'Invalid difficulty. Must be "easy" or "hard"'}), 400
    
    if not isinstance(time, (int, float)) or time <= 0:
        return jsonify({'error': 'Time must be a positive number'}), 400
    
    # Create new entry
    new_entry = LeaderboardEntry(
        name=name,
        difficulty=difficulty,
        time=float(time),
        date=datetime.utcnow()
    )
    
    try:
        db.session.add(new_entry)
        db.session.commit()
        
        # Calculate rank
        rank = LeaderboardEntry.query.filter_by(difficulty=difficulty)\
                                   .filter(LeaderboardEntry.time < time)\
                                   .count() + 1
        
        return jsonify({
            'success': True,
            'message': 'Score added to leaderboard',
            'rank': rank,
            'entry': new_entry.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to save score'}), 500

@leaderboard_bp.route('/leaderboard/check/<difficulty>/<float:time>', methods=['GET'])
def check_qualification(difficulty, time):
    """Check if a time qualifies for the leaderboard"""
    if difficulty not in ['easy', 'hard']:
        return jsonify({'error': 'Invalid difficulty. Must be "easy" or "hard"'}), 400
    
    if time <= 0:
        return jsonify({'error': 'Time must be positive'}), 400
    
    # Count how many scores are better than this time
    better_scores = LeaderboardEntry.query.filter_by(difficulty=difficulty)\
                                         .filter(LeaderboardEntry.time < time)\
                                         .count()
    
    # Check total number of scores for this difficulty
    total_scores = LeaderboardEntry.query.filter_by(difficulty=difficulty).count()
    
    # Qualifies if it would be in top 10 or if there are less than 10 scores
    qualifies = better_scores < 10 or total_scores < 10
    rank = better_scores + 1
    
    return jsonify({
        'qualifies': qualifies,
        'rank': rank,
        'total_scores': total_scores
    })

