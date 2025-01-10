# app.py
from flask import Flask, render_template, request, jsonify, session
from game_engine import Game
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    if 'game' not in session:
        session['game'] = Game()
    return render_template('index.html')

@app.route('/command', methods=['POST'])
async def process_command():
    command = request.json.get('command')
    game = session.get('game')
    
    if command.startswith('talk to'):
        response = await game._talk_to(command[8:].strip())
    else:
        response = game.process_command(command)
    
    return jsonify({
        'response': response,
        'location': game._look(),
    })

if __name__ == '__main__':
    app.run(debug=True)
