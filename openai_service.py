import os
import json
import logging
from openai import OpenAI

# Configure detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key:
            self.client = OpenAI(api_key=api_key)
            self.model = "gpt-4o"  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
        else:
            self.client = None
            self.model = None
    
    def get_asf_response(self, user_message, session_data, consideration_categories):
        """Generate ASF response based on user message and session context"""
        logger.info(f"=== ASF RESPONSE GENERATION START ===")
        logger.info(f"User message: {user_message[:100]}...")
        logger.info(f"Session data keys: {list(session_data.keys()) if session_data else 'None'}")
        logger.info(f"Consideration categories count: {len(consideration_categories)}")
        
        if not self.client:
            logger.error("OpenAI client not available - API key missing")
            return "I'm sorry, but the AI assistant is not currently available. Please check that the OpenAI API key is properly configured."
        
        try:
            # Build context from session data
            logger.info("Building context from session data...")
            context = self._build_context(session_data, consideration_categories)
            logger.info(f"Built context: {context[:200]}...")
            
            # Create system prompt for ASF with consideration auto-filling instructions
            system_prompt = f"""You are the Agentic Startup Factory (ASF), an AI assistant that helps ideators refine startup ideas through structured considerations. You guide users through 8 core consideration categories to develop comprehensive startup concepts.

Your role is to:
1. Ask insightful questions to help develop ideas
2. Provide constructive feedback and suggestions
3. Guide users toward completing all 8 considerations
4. Maintain focus on practical, actionable advice
5. Encourage ethical business practices and community collaboration
6. Suggest when considerations need more detail (minimum 100 words each)
7. AUTO-FILL consideration content based on the conversation

IMPORTANT: After your conversational response, you MUST include consideration updates in this exact format:

=== CONSIDERATION UPDATES ===
[consideration_id]: [content]
=== END CONSIDERATION UPDATES ===

For example:
=== CONSIDERATION UPDATES ===
problem_definition: Rural clinics face significant challenges with manual patient data management including inefficiencies, data loss risks, and limited accessibility. This creates barriers to quality healthcare delivery in underserved areas.
target_market: Primary target includes rural healthcare clinics, community health centers, and small medical practices in low-bandwidth regions across developing countries and remote areas.
=== END CONSIDERATION UPDATES ===

Current session context:
{context}

Be conversational, supportive, and focus on helping the user develop a strong startup concept. If they ask about a specific consideration, provide targeted guidance for that area.
"""
            logger.info(f"System prompt length: {len(system_prompt)} characters")
            
            # Get chat history for context
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add recent chat history if available
            if session_data and 'chat_history' in session_data:
                recent_messages = session_data['chat_history'][-10:]  # Last 10 messages
                logger.info(f"Adding {len(recent_messages)} recent messages to context")
                for msg in recent_messages:
                    messages.append({"role": "user", "content": msg.get('user_message', '')})
                    messages.append({"role": "assistant", "content": msg.get('ai_response', '')})
            else:
                logger.info("No chat history found in session data")
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            logger.info(f"Total messages for API call: {len(messages)}")
            
            # Log API call details
            logger.info(f"Making OpenAI API call with model: {self.model}")
            logger.info(f"Max tokens: 800, Temperature: 0.7")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=800,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            logger.info(f"API response received, length: {len(ai_response)} characters")
            logger.info(f"Response preview: {ai_response[:200]}...")
            
            # Extract consideration updates from response
            consideration_updates = self._extract_consideration_updates(ai_response)
            logger.info(f"Extracted consideration updates: {consideration_updates}")
            
            # Clean response by removing consideration update section
            clean_response = self._clean_response(ai_response)
            logger.info(f"Clean response length: {len(clean_response)} characters")
            
            logger.info(f"=== ASF RESPONSE GENERATION END ===")
            
            # Return both response and consideration updates
            return {
                'response': clean_response,
                'consideration_updates': consideration_updates
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            return {
                'response': "I apologize, but I'm having trouble processing your request right now. Please try again in a moment.",
                'consideration_updates': {}
            }
    
    def _build_context(self, session_data, consideration_categories):
        """Build context string from session data"""
        logger.info("=== BUILDING CONTEXT ===")
        
        if not session_data:
            logger.info("No session data - returning default context")
            return "New session - no previous considerations completed."
        
        context_parts = []
        
        # Add completion status
        considerations = session_data.get('considerations', {})
        logger.info(f"Considerations in session: {list(considerations.keys())}")
        
        completed_count = sum(1 for content in considerations.values() if len(content.strip()) >= 100)
        logger.info(f"Completed considerations: {completed_count}/8")
        context_parts.append(f"Completed considerations: {completed_count}/8")
        
        # Add brief summary of each completed consideration
        for cat in consideration_categories:
            cat_id = cat['id']
            content = considerations.get(cat_id, '').strip()
            logger.info(f"Consideration '{cat['title']}': {len(content)} characters")
            
            if content:
                summary = content[:150] + "..." if len(content) > 150 else content
                context_parts.append(f"{cat['title']}: {summary}")
                logger.info(f"  - Has content: {summary[:50]}...")
            else:
                context_parts.append(f"{cat['title']}: Not started")
                logger.info(f"  - No content yet")
        
        final_context = "\n".join(context_parts)
        logger.info(f"Final context length: {len(final_context)} characters")
        logger.info("=== CONTEXT BUILDING END ===")
        
        return final_context
    
    def _extract_consideration_updates(self, ai_response):
        """Extract consideration updates from AI response"""
        logger.info("=== EXTRACTING CONSIDERATION UPDATES ===")
        
        consideration_updates = {}
        
        try:
            # Look for consideration updates section
            start_marker = "=== CONSIDERATION UPDATES ==="
            end_marker = "=== END CONSIDERATION UPDATES ==="
            
            start_idx = ai_response.find(start_marker)
            end_idx = ai_response.find(end_marker)
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                # Extract the consideration updates section
                updates_section = ai_response[start_idx + len(start_marker):end_idx].strip()
                logger.info(f"Found consideration updates section: {updates_section[:200]}...")
                
                # Parse each line
                for line in updates_section.split('\n'):
                    line = line.strip()
                    if ':' in line:
                        consideration_id, content = line.split(':', 1)
                        consideration_id = consideration_id.strip()
                        content = content.strip()
                        
                        if consideration_id and content:
                            consideration_updates[consideration_id] = content
                            logger.info(f"Extracted: {consideration_id} -> {content[:50]}...")
            else:
                logger.info("No consideration updates section found in response")
                
        except Exception as e:
            logger.error(f"Error extracting consideration updates: {str(e)}")
        
        logger.info(f"Total consideration updates extracted: {len(consideration_updates)}")
        logger.info("=== CONSIDERATION EXTRACTION END ===")
        return consideration_updates
    
    def _clean_response(self, ai_response):
        """Remove consideration updates section from response"""
        logger.info("=== CLEANING RESPONSE ===")
        
        try:
            # Remove consideration updates section
            start_marker = "=== CONSIDERATION UPDATES ==="
            end_marker = "=== END CONSIDERATION UPDATES ==="
            
            start_idx = ai_response.find(start_marker)
            end_idx = ai_response.find(end_marker)
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                # Remove the entire section
                clean_response = ai_response[:start_idx].strip()
                logger.info(f"Removed consideration updates section, cleaned length: {len(clean_response)}")
            else:
                clean_response = ai_response
                logger.info("No consideration updates section found, keeping original response")
                
        except Exception as e:
            logger.error(f"Error cleaning response: {str(e)}")
            clean_response = ai_response
        
        logger.info("=== RESPONSE CLEANING END ===")
        return clean_response
    
    def generate_equity_suggestion(self, team_structure, contribution_data):
        """Generate equity split suggestions based on team structure and contributions"""
        if not self.client:
            return {"error": "AI assistant is not currently available. Please check that the OpenAI API key is properly configured."}
        
        try:
            prompt = f"""As an equity distribution advisor for startups, analyze the following team structure and contributions to suggest a fair equity split:

Team Structure: {team_structure}
Contribution Data: {contribution_data}

Provide a JSON response with:
1. Suggested equity percentages for each role/contributor
2. Reasoning for each allocation
3. Recommendations for vesting schedules
4. Considerations for future team additions

Focus on fairness, long-term sustainability, and alignment with startup best practices.
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logging.error(f"Equity suggestion error: {str(e)}")
            return {"error": "Unable to generate equity suggestions at this time"}
