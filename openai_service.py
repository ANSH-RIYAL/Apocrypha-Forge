import os
import json
import logging
from openai import OpenAI

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
        if not self.client:
            return "I'm sorry, but the AI assistant is not currently available. Please check that the OpenAI API key is properly configured."
        
        try:
            # Build context from session data
            context = self._build_context(session_data, consideration_categories)
            
            # Create system prompt for ASF
            system_prompt = f"""You are the Agentic Startup Factory (ASF), an AI assistant that helps ideators refine startup ideas through structured considerations. You guide users through 8 core consideration categories to develop comprehensive startup concepts.

Your role is to:
1. Ask insightful questions to help develop ideas
2. Provide constructive feedback and suggestions
3. Guide users toward completing all 8 considerations
4. Maintain focus on practical, actionable advice
5. Encourage ethical business practices and community collaboration
6. Suggest when considerations need more detail (minimum 100 words each)

Current session context:
{context}

Be conversational, supportive, and focus on helping the user develop a strong startup concept. If they ask about a specific consideration, provide targeted guidance for that area.
"""
            
            # Get chat history for context
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add recent chat history if available
            if session_data and 'chat_history' in session_data:
                recent_messages = session_data['chat_history'][-10:]  # Last 10 messages
                for msg in recent_messages:
                    messages.append({"role": "user", "content": msg.get('user_message', '')})
                    messages.append({"role": "assistant", "content": msg.get('ai_response', '')})
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=800,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"OpenAI API error: {str(e)}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again in a moment."
    
    def _build_context(self, session_data, consideration_categories):
        """Build context string from session data"""
        if not session_data:
            return "New session - no previous considerations completed."
        
        context_parts = []
        
        # Add completion status
        considerations = session_data.get('considerations', {})
        completed_count = sum(1 for content in considerations.values() if len(content.strip()) >= 100)
        context_parts.append(f"Completed considerations: {completed_count}/8")
        
        # Add brief summary of each completed consideration
        for cat in consideration_categories:
            cat_id = cat['id']
            content = considerations.get(cat_id, '').strip()
            if content:
                summary = content[:150] + "..." if len(content) > 150 else content
                context_parts.append(f"{cat['title']}: {summary}")
            else:
                context_parts.append(f"{cat['title']}: Not started")
        
        return "\n".join(context_parts)
    
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
