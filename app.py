# app.py
from flask import Flask, render_template, request, jsonify, session
from game_engine import Game
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24))

# Store games in memory (for demonstration - in production use Redis or a database)
games = {}

@app.route('/')
def index():
    # Create a unique session ID for each player
    session_id = session.get('session_id', os.urandom(16).hex())
    session['session_id'] = session_id
    
    # Create a new game instance if one doesn't exist
    if session_id not in games:
        games[session_id] = Game()
    
    return render_template('index.html')

@app.route('/command', methods=['POST'])
async def process_command():
    try:
        session_id = session.get('session_id')
        if not session_id or session_id not in games:
            return jsonify({'error': 'Session expired'}), 400
        
        game = games[session_id]
        command = request.json.get('command', '').strip()
        
        if not command:
            return jsonify({'error': 'Empty command'}), 400
            
        if command.startswith('talk to'):
            response = await game._talk_to(command[8:].strip())
        else:
            response = game.process_command(command)
        
        location_info = game._look()
        
        return jsonify({
            'response': response,
            'location': location_info,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

# Add a health check endpoint
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True)
