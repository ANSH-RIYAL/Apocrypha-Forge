from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import logging
from datetime import datetime, timedelta
import uuid
from openai_service import OpenAIService
from data_manager import DataManager

# Configure detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "apocrypha_forge_secret_key")

# Add CORS support if needed
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Initialize services
openai_service = OpenAIService()
data_manager = DataManager()

# Get considerations from config
CONSIDERATION_CATEGORIES = data_manager.config['considerations']

@app.route('/')
def index():
    """Main landing page introducing the Forge platform"""
    return render_template('index.html')

@app.route('/forge')
def forge():
    """Main ASF interface for ideation and chat"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    # Load existing session data
    session_data = data_manager.load_session(session['session_id'])
    
    return render_template('forge.html', 
                         considerations=CONSIDERATION_CATEGORIES,
                         session_data=session_data)

@app.route('/marketplace')
def marketplace():
    """Public ideas marketplace"""
    ideas = data_manager.get_public_ideas()
    return render_template('marketplace.html', ideas=ideas)

@app.route('/idea/<idea_id>')
def idea_detail(idea_id):
    """Individual idea detail page"""
    idea = data_manager.get_idea(idea_id)
    if not idea:
        return redirect(url_for('marketplace'))
    
    comments = data_manager.get_comments(idea_id)
    return render_template('idea_detail.html', idea=idea, comments=comments)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat interactions with OpenAI"""
    logger.info("=== CHAT API CALL START ===")
    try:
        data = request.get_json()
        message = data.get('message', '')
        session_id = session.get('session_id')
        
        logger.info(f"Received message: {message[:100]}...")
        logger.info(f"Session ID: {session_id}")
        logger.info(f"Request data keys: {list(data.keys()) if data else 'None'}")
        
        if not session_id:
            logger.error("No session ID found in session")
            return jsonify({'error': 'No session found'}), 400
        
        # Load session context
        logger.info("Loading session data...")
        session_data = data_manager.load_session(session_id)
        logger.info(f"Session data loaded: {list(session_data.keys()) if session_data else 'None'}")
        
        # Get AI response
        logger.info("Calling OpenAI service...")
        ai_result = openai_service.get_asf_response(message, session_data, CONSIDERATION_CATEGORIES)
        logger.info(f"OpenAI response received, length: {len(ai_result.get('response', ''))}")
        
        # Extract response and consideration updates
        response = ai_result.get('response', '')
        consideration_updates = ai_result.get('consideration_updates', {})
        
        # Apply consideration updates to session
        if consideration_updates:
            logger.info(f"Applying {len(consideration_updates)} consideration updates...")
            for consideration_id, content in consideration_updates.items():
                logger.info(f"Updating consideration {consideration_id}: {content[:50]}...")
                data_manager.update_consideration(session_id, consideration_id, content)
        
        # Update session with new message
        logger.info("Adding message to session...")
        data_manager.add_message(session_id, message, response)
        logger.info("Message added to session successfully")
        
        logger.info("=== CHAT API CALL END ===")
        return jsonify({
            'response': response,
            'session_id': session_id,
            'consideration_updates': consideration_updates
        })
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error traceback: ", exc_info=True)
        return jsonify({'error': 'Failed to process message'}), 500

@app.route('/api/update_consideration', methods=['POST'])
def update_consideration():
    """Update consideration content"""
    try:
        data = request.get_json()
        session_id = session.get('session_id')
        consideration_id = data.get('consideration_id')
        content = data.get('content', '')
        
        if not session_id or not consideration_id:
            return jsonify({'error': 'Missing required data'}), 400
        
        # Update consideration
        data_manager.update_consideration(session_id, consideration_id, content)
        
        # Get updated session data
        session_data = data_manager.load_session(session_id)
        
        return jsonify({
            'success': True,
            'completion_status': data_manager.get_completion_status(session_data)
        })
        
    except Exception as e:
        logging.error(f"Update consideration error: {str(e)}")
        return jsonify({'error': 'Failed to update consideration'}), 500

@app.route('/api/submit_idea', methods=['POST'])
def submit_idea():
    """Submit completed idea to public marketplace"""
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'error': 'No session found'}), 400
        
        session_data = data_manager.load_session(session_id)
        completion_status = data_manager.get_completion_status(session_data)
        
        # Check if idea meets minimum criteria
        if completion_status['completed_count'] < 6:
            return jsonify({
                'error': 'Idea must have at least 6 completed considerations to submit'
            }), 400
        
        # Submit to marketplace
        idea_id = data_manager.submit_to_marketplace(session_id, session_data)
        
        return jsonify({
            'success': True,
            'idea_id': idea_id,
            'message': 'Idea submitted successfully! It will be available for public review.'
        })
        
    except Exception as e:
        logging.error(f"Submit idea error: {str(e)}")
        return jsonify({'error': 'Failed to submit idea'}), 500

@app.route('/api/add_comment', methods=['POST'])
def add_comment():
    """Add comment to an idea"""
    try:
        data = request.get_json()
        idea_id = data.get('idea_id')
        comment = data.get('comment', '').strip()
        author = data.get('author', 'Anonymous').strip()
        
        if not idea_id or not comment:
            return jsonify({'error': 'Missing required data'}), 400
        
        comment_id = data_manager.add_comment(idea_id, comment, author)
        
        return jsonify({
            'success': True,
            'comment_id': comment_id
        })
        
    except Exception as e:
        logging.error(f"Add comment error: {str(e)}")
        return jsonify({'error': 'Failed to add comment'}), 500

@app.route('/api/session_status')
def session_status():
    """Get current session status"""
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'error': 'No session found'}), 400
        
        session_data = data_manager.load_session(session_id)
        completion_status = data_manager.get_completion_status(session_data)
        
        return jsonify({
            'session_id': session_id,
            'completion_status': completion_status,
            'can_submit': completion_status['completed_count'] >= 6
        })
        
    except Exception as e:
        logging.error(f"Session status error: {str(e)}")
        return jsonify({'error': 'Failed to get session status'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
