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
            system_prompt = f"""FORMATTING RULE: Use ONLY plain text. NO bold, NO asterisks, NO markdown, NO special formatting. Just regular text.

You are the Agentic Startup Factory (ASF), an AI assistant that helps ideators refine startup ideas through structured considerations. You guide users through 8 core consideration categories to develop comprehensive startup concepts.

Your role is to:
1. Ask insightful questions to help develop ideas
2. Provide constructive feedback and suggestions
3. Guide users toward completing all 8 considerations
4. Maintain focus on practical, actionable advice
5. Encourage ethical business practices and community collaboration
6. Suggest when considerations need more detail (minimum 100 words each)
7. AUTO-FILL consideration content based on the conversation
8. Ask about remaining incomplete considerations

CRITICAL: Use plain text only. No bold formatting, no asterisks, no markdown, no special characters. Just regular text.

RESPONSE LENGTH: Keep responses concise and focused. Aim for 2-3 sentences per point. Avoid lengthy explanations unless specifically requested.

MANDATORY: After your conversational response, you MUST include consideration updates in this exact format:

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

Be conversational, supportive, and focus on helping the user develop a strong startup concept. Use plain text without any formatting. Keep responses concise and easy to read. Always ask about remaining incomplete considerations to guide the user toward completing all 8 areas. ALWAYS include consideration updates section at the end of your response.
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
            
            # If no consideration updates found, generate them based on context
            if not consideration_updates:
                logger.info("No consideration updates found, generating fallback updates")
                consideration_updates = self._generate_fallback_updates(user_message, session_data, consideration_categories)
                logger.info(f"Generated fallback updates: {consideration_updates}")
            
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
        
        # Handle both old string format and new dict format for completion count
        completed_count = 0
        for content in considerations.values():
            if isinstance(content, dict):
                content_text = content.get('content', '').strip()
            else:
                content_text = content.strip()
            if len(content_text.split()) >= 100:
                completed_count += 1
        logger.info(f"Completed considerations: {completed_count}/8")
        context_parts.append(f"Completed considerations: {completed_count}/8")
        
        # Add brief summary of each completed consideration
        for cat in consideration_categories:
            cat_id = cat['id']
            consideration_data = considerations.get(cat_id, '')
            
            # Handle both old string format and new dict format
            if isinstance(consideration_data, dict):
                content = consideration_data.get('content', '').strip()
                is_complete = consideration_data.get('is_complete', False)
            else:
                content = consideration_data.strip()
                is_complete = len(content.split()) >= 100
            
            logger.info(f"Consideration '{cat['title']}': {len(content)} characters, complete: {is_complete}")
            
            if content:
                summary = content[:150] + "..." if len(content) > 150 else content
                status = "COMPLETE" if is_complete else "INCOMPLETE"
                context_parts.append(f"{cat['title']}: {status} - {summary}")
                logger.info(f"  - Has content: {summary[:50]}...")
            else:
                context_parts.append(f"{cat['title']}: NOT STARTED")
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
        
        # Look for consideration updates section and remove it
        start_marker = "=== CONSIDERATION UPDATES ==="
        end_marker = "=== END CONSIDERATION UPDATES ==="
        
        start_idx = ai_response.find(start_marker)
        if start_idx != -1:
            end_idx = ai_response.find(end_marker, start_idx)
            if end_idx != -1:
                # Remove the entire section including markers
                cleaned_response = ai_response[:start_idx].strip() + ai_response[end_idx + len(end_marker):].strip()
                logger.info(f"Removed consideration updates section, cleaned length: {len(cleaned_response)}")
                logger.info("=== RESPONSE CLEANING END ===")
                return cleaned_response
        
        logger.info("No consideration updates section found, keeping original response")
        logger.info("=== RESPONSE CLEANING END ===")
        return ai_response
    
    def _generate_fallback_updates(self, user_message, session_data, consideration_categories):
        """Generate fallback consideration updates when AI doesn't provide them"""
        logger.info("=== GENERATING FALLBACK UPDATES ===")
        
        # Get current considerations
        current_considerations = session_data.get('considerations', {}) if session_data else {}
        
        # Determine which considerations might need updates based on user message
        potential_updates = {}
        
        # Simple keyword-based mapping
        message_lower = user_message.lower()
        
        # Track how many updates we've generated
        updates_generated = 0
        max_updates = 3  # Try to fill 2-3 considerations
        
        if any(word in message_lower for word in ['problem', 'issue', 'challenge']):
            if 'problem_definition' not in current_considerations or not self._has_content(current_considerations.get('problem_definition')):
                potential_updates['problem_definition'] = f"Based on the conversation, the problem involves {user_message[:100]}..."
                updates_generated += 1
        
        if any(word in message_lower for word in ['market', 'customer', 'user', 'target']):
            if 'target_market' not in current_considerations or not self._has_content(current_considerations.get('target_market')):
                potential_updates['target_market'] = f"Target market analysis based on: {user_message[:100]}..."
                updates_generated += 1
        
        if any(word in message_lower for word in ['solution', 'approach', 'how', 'method']):
            if 'solution_approach' not in current_considerations or not self._has_content(current_considerations.get('solution_approach')):
                potential_updates['solution_approach'] = f"Solution approach considering: {user_message[:100]}..."
                updates_generated += 1
        
        if any(word in message_lower for word in ['competitor', 'competition', 'competitive']):
            if 'competitive_analysis' not in current_considerations or not self._has_content(current_considerations.get('competitive_analysis')):
                potential_updates['competitive_analysis'] = f"Competitive analysis based on: {user_message[:100]}..."
                updates_generated += 1
        
        if any(word in message_lower for word in ['business', 'revenue', 'money', 'model']):
            if 'business_model' not in current_considerations or not self._has_content(current_considerations.get('business_model')):
                potential_updates['business_model'] = f"Business model considerations: {user_message[:100]}..."
                updates_generated += 1
        
        if any(word in message_lower for word in ['technical', 'technology', 'feasibility', 'tech']):
            if 'technical_feasibility' not in current_considerations or not self._has_content(current_considerations.get('technical_feasibility')):
                potential_updates['technical_feasibility'] = f"Technical feasibility analysis: {user_message[:100]}..."
                updates_generated += 1
        
        if any(word in message_lower for word in ['team', 'people', 'hire', 'role']):
            if 'team_structure' not in current_considerations or not self._has_content(current_considerations.get('team_structure')):
                potential_updates['team_structure'] = f"Team structure considerations: {user_message[:100]}..."
                updates_generated += 1
        
        if any(word in message_lower for word in ['growth', 'scale', 'expand', 'strategy']):
            if 'growth_strategy' not in current_considerations or not self._has_content(current_considerations.get('growth_strategy')):
                potential_updates['growth_strategy'] = f"Growth strategy based on: {user_message[:100]}..."
                updates_generated += 1
        
        # If we haven't generated enough updates, fill some empty considerations
        if updates_generated < max_updates:
            # Get all consideration categories
            all_considerations = [cat['id'] for cat in consideration_categories]
            
            # Find empty considerations
            empty_considerations = []
            for consideration_id in all_considerations:
                if consideration_id not in current_considerations or not self._has_content(current_considerations.get(consideration_id)):
                    empty_considerations.append(consideration_id)
            
            # Fill up to max_updates total
            for consideration_id in empty_considerations:
                if updates_generated >= max_updates:
                    break
                if consideration_id not in potential_updates:
                    potential_updates[consideration_id] = f"Basic {consideration_id.replace('_', ' ')} considerations based on the startup idea..."
                    updates_generated += 1
        
        logger.info(f"Generated {len(potential_updates)} fallback updates")
        logger.info("=== FALLBACK UPDATES END ===")
        return potential_updates
    
    def _has_content(self, consideration_data):
        """Check if consideration has meaningful content"""
        if isinstance(consideration_data, dict):
            content = consideration_data.get('content', '')
        else:
            content = consideration_data or ''
        return len(content.strip()) > 50  # At least 50 characters
    
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
