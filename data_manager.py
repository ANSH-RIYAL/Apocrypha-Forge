import os
import json
import logging
from datetime import datetime, timedelta
import uuid

# Configure detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self):
        self.sessions_dir = "data/sessions"
        self.ideas_dir = "data/ideas"
        self.users_dir = "data/users"
        self.comments_dir = "data/comments"
        self.config_file = "data/config.json"
        self._ensure_directories()
        self.config = self._load_config()
    
    def _ensure_directories(self):
        """Create data directories if they don't exist"""
        os.makedirs(self.sessions_dir, exist_ok=True)
        os.makedirs(self.ideas_dir, exist_ok=True)
        os.makedirs(self.users_dir, exist_ok=True)
        os.makedirs(self.comments_dir, exist_ok=True)
    
    def _load_config(self):
        """Load configuration from config.json"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logging.error(f"Error loading config: {e}")
        
        # Return default config if file doesn't exist or error occurred
        return {
            "considerations": [
                {"id": "problem_definition", "title": "Problem Definition", "description": "Clearly define the problem you're solving"},
                {"id": "target_market", "title": "Target Market", "description": "Identify your ideal customers"},
                {"id": "solution_approach", "title": "Solution Approach", "description": "Outline your proposed solution"},
                {"id": "competitive_analysis", "title": "Competitive Analysis", "description": "Analyze competitors"},
                {"id": "business_model", "title": "Business Model", "description": "Define how you'll make money"},
                {"id": "technical_feasibility", "title": "Technical Feasibility", "description": "Assess technical requirements"},
                {"id": "team_structure", "title": "Team Structure", "description": "Define roles needed"},
                {"id": "growth_strategy", "title": "Growth Strategy", "description": "Plan for scaling"}
            ],
            "submission_requirements": {
                "min_completed_considerations": 6,
                "min_words_per_consideration": 100
            }
        }
    
    def load_session(self, session_id):
        """Load session data from file"""
        logger.info(f"=== LOADING SESSION {session_id} ===")
        session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
        logger.info(f"Session file path: {session_file}")
        
        if os.path.exists(session_file):
            logger.info("Session file exists, loading...")
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                logger.info(f"Session loaded successfully: {list(session_data.keys())}")
                logger.info(f"Considerations: {list(session_data.get('considerations', {}).keys())}")
                logger.info(f"Chat history length: {len(session_data.get('chat_history', []))}")
                return session_data
            except Exception as e:
                logger.error(f"Error loading session {session_id}: {str(e)}")
        else:
            logger.info("Session file does not exist, creating new session")
        
        # Return new session structure
        new_session = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "considerations": {},
            "chat_history": [],
            "last_updated": datetime.now().isoformat()
        }
        logger.info(f"Created new session structure: {list(new_session.keys())}")
        logger.info("=== SESSION LOADING END ===")
        return new_session
    
    def save_session(self, session_id, session_data):
        """Save session data to file"""
        session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
        session_data["last_updated"] = datetime.now().isoformat()
        
        try:
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving session {session_id}: {str(e)}")
    
    def add_message(self, session_id, user_message, ai_response):
        """Add chat message to session"""
        session_data = self.load_session(session_id)
        
        message_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "ai_response": ai_response
        }
        
        session_data["chat_history"].append(message_entry)
        
        # Keep only last 50 messages to prevent file size issues
        if len(session_data["chat_history"]) > 50:
            session_data["chat_history"] = session_data["chat_history"][-50:]
        
        self.save_session(session_id, session_data)
    
    def update_consideration(self, session_id, consideration_id, content):
        """Update consideration content with previous value storage and metadata placeholder"""
        session_data = self.load_session(session_id)
        
        # Get current content (handle both old string format and new dict format)
        current_content = session_data["considerations"].get(consideration_id, '')
        if isinstance(current_content, dict):
            current_content = current_content.get('content', '')
        
        # Check if this update makes the consideration complete (100+ words)
        word_count = len(content.split())
        is_complete = word_count >= self.config['submission_requirements']['min_words_per_consideration']
        
        # Initialize or update the consideration structure
        if consideration_id not in session_data["considerations"]:
            # New consideration - initialize with new structure
            session_data["considerations"][consideration_id] = {
                'content': content,
                'previous_value': '',
                'metadata': {},
                'is_complete': is_complete
            }
        elif isinstance(session_data["considerations"][consideration_id], str):
            # Convert from old string format to new dict format
            session_data["considerations"][consideration_id] = {
                'content': current_content,
                'previous_value': '',
                'metadata': {},
                'is_complete': len(current_content.split()) >= self.config['submission_requirements']['min_words_per_consideration']
            }
            # Update with new content
            session_data["considerations"][consideration_id]['previous_value'] = current_content
            session_data["considerations"][consideration_id]['content'] = content
            session_data["considerations"][consideration_id]['is_complete'] = is_complete
        else:
            # Already in new dict format - update with new content, preserving previous value
            session_data["considerations"][consideration_id]['previous_value'] = current_content
            session_data["considerations"][consideration_id]['content'] = content
            session_data["considerations"][consideration_id]['is_complete'] = is_complete
        
        self.save_session(session_id, session_data)
    
    def get_consideration_content(self, consideration_data):
        """Get content from consideration data, handling both old and new formats"""
        if isinstance(consideration_data, dict):
            return consideration_data.get('content', '')
        else:
            return consideration_data
    
    def get_consideration_previous_value(self, consideration_data):
        """Get previous value from consideration data, handling both old and new formats"""
        if isinstance(consideration_data, dict):
            return consideration_data.get('previous_value', '')
        else:
            return ''
    
    def get_completion_status(self, session_data):
        """Get completion status for considerations"""
        if not session_data:
            return {
                "completed_count": 0, 
                "total_count": len(self.config['considerations']), 
                "can_submit": False
            }
        
        considerations = session_data.get("considerations", {})
        
        # Count completed considerations using boolean is_complete values
        completed_count = 0
        for consideration_id, content in considerations.items():
            if isinstance(content, dict):
                # New format: check is_complete field
                if content.get('is_complete', False):
                    completed_count += 1
            else:
                # Old format: calculate word count on demand
                content_text = content.strip()
                if len(content_text.split()) >= self.config['submission_requirements']['min_words_per_consideration']:
                    completed_count += 1
        
        min_completed = self.config['submission_requirements']['min_completed_considerations']
        
        return {
            "completed_count": completed_count,
            "total_count": len(self.config['considerations']),
            "can_submit": completed_count >= min_completed
        }
    
    def submit_to_marketplace(self, session_id, session_data):
        """Submit idea to public marketplace"""
        idea_id = str(uuid.uuid4())
        
        idea_data = {
            "id": idea_id,
            "session_id": session_id,
            "title": self._extract_title(session_data),
            "description": self._extract_description(session_data),
            "considerations": session_data.get("considerations", {}),
            "submitted_at": datetime.now().isoformat(),
            "review_until": (datetime.now() + timedelta(days=7)).isoformat(),
            "status": "under_review",
            "views": 0,
            "comments": []
        }
        
        idea_file = os.path.join(self.ideas_dir, f"{idea_id}.json")
        
        try:
            with open(idea_file, 'w') as f:
                json.dump(idea_data, f, indent=2)
            return idea_id
        except Exception as e:
            logging.error(f"Error submitting idea: {str(e)}")
            raise
    
    def get_public_ideas(self):
        """Get all public ideas for marketplace"""
        ideas = []
        
        try:
            for filename in os.listdir(self.ideas_dir):
                if filename.endswith('.json') and filename != '.gitkeep':
                    idea_file = os.path.join(self.ideas_dir, filename)
                    with open(idea_file, 'r') as f:
                        idea_data = json.load(f)
                        
                        # Add summary info for marketplace listing
                        idea_summary = {
                            "id": idea_data.get("id", idea_data.get("idea_id", filename.replace('.json', ''))),
                            "title": idea_data.get("title", "Untitled Idea"),
                            "description": (idea_data.get("description", "No description available")[:300] + "..." 
                                          if len(idea_data.get("description", "")) > 300 
                                          else idea_data.get("description", "No description available")),
                            "submitted_at": idea_data.get("submitted_at", datetime.now().isoformat()),
                            "review_until": idea_data.get("review_until", (datetime.now() + timedelta(days=7)).isoformat()),
                            "status": idea_data.get("status", "published"),
                            "views": idea_data.get("views", 0),
                            "comment_count": len(idea_data.get("comments", []))
                        }
                        ideas.append(idea_summary)
        except Exception as e:
            logging.error(f"Error loading public ideas: {str(e)}")
        
        # Sort by submission date (newest first)
        ideas.sort(key=lambda x: x["submitted_at"], reverse=True)
        return ideas
    
    def get_idea(self, idea_id):
        """Get specific idea by ID"""
        idea_file = os.path.join(self.ideas_dir, f"{idea_id}.json")
        
        if os.path.exists(idea_file):
            try:
                with open(idea_file, 'r') as f:
                    idea_data = json.load(f)
                    
                    # Increment view count
                    idea_data["views"] = idea_data.get("views", 0) + 1
                    
                    # Save updated view count
                    with open(idea_file, 'w') as f:
                        json.dump(idea_data, f, indent=2)
                    
                    return idea_data
            except Exception as e:
                logging.error(f"Error loading idea {idea_id}: {str(e)}")
        
        return None
    
    def add_comment(self, idea_id, comment, author):
        """Add comment to an idea"""
        idea_file = os.path.join(self.ideas_dir, f"{idea_id}.json")
        
        if not os.path.exists(idea_file):
            raise ValueError("Idea not found")
        
        try:
            with open(idea_file, 'r') as f:
                idea_data = json.load(f)
            
            comment_id = str(uuid.uuid4())
            comment_data = {
                "id": comment_id,
                "author": author,
                "content": comment,
                "timestamp": datetime.now().isoformat()
            }
            
            if "comments" not in idea_data:
                idea_data["comments"] = []
            
            idea_data["comments"].append(comment_data)
            
            with open(idea_file, 'w') as f:
                json.dump(idea_data, f, indent=2)
            
            return comment_id
            
        except Exception as e:
            logging.error(f"Error adding comment to idea {idea_id}: {str(e)}")
            raise
    
    def get_comments(self, idea_id):
        """Get comments for an idea"""
        idea_data = self.get_idea(idea_id)
        if idea_data:
            return idea_data.get("comments", [])
        return []
    
    def _extract_title(self, session_data):
        """Extract title from session data"""
        considerations = session_data.get("considerations", {})
        
        # Try to extract from problem definition
        problem_def = considerations.get("problem_definition", "")
        if problem_def:
            # Take first sentence as title
            title = problem_def.split('.')[0].strip()
            if len(title) > 100:
                title = title[:100] + "..."
            return title
        
        return "Untitled Startup Idea"
    
    def _extract_description(self, session_data):
        """Extract description from session data"""
        considerations = session_data.get("considerations", {})
        
        # Combine key considerations for description
        description_parts = []
        
        for key in ["problem_definition", "solution_approach", "target_market"]:
            content = considerations.get(key, "").strip()
            if content:
                description_parts.append(content)
        
        description = " ".join(description_parts)
        
        # Limit description length
        if len(description) > 500:
            description = description[:500] + "..."
        
        return description if description else "No description available."
