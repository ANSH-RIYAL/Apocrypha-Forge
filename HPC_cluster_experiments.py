#!/usr/bin/env python3
"""
HPC Cluster Experiments - Agentic LLM Setup
============================================

This script contains the complete agentic LLM methodology from The Forge project,
adapted to use a local DeepSeek reasoning model from HuggingFace.

Features:
- Complete agentic prompting setup
- Session management and context building
- Consideration-based startup development
- Local LLM integration with DeepSeek
- Standalone execution without web dependencies
"""

import os
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import warnings
warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ConsiderationCategory:
    """Data structure for consideration categories"""
    id: str
    title: str
    description: str

@dataclass
class ChatMessage:
    """Data structure for chat messages"""
    timestamp: str
    user_message: str
    ai_response: str

@dataclass
class SessionData:
    """Data structure for session data"""
    session_id: str
    created_at: str
    considerations: Dict[str, str]
    chat_history: List[ChatMessage]
    last_updated: str

class LocalLLMService:
    """Local LLM service using DeepSeek reasoning model"""
    
    def __init__(self, model_name: str = "deepseek-ai/deepseek-coder-6.7b-instruct"):
        """
        Initialize the local LLM service
        
        Args:
            model_name: HuggingFace model name for DeepSeek
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"Initializing DeepSeek model: {model_name}")
        logger.info(f"Using device: {self.device}")
        
        try:
            self._load_model()
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def _load_model(self):
        """Load the DeepSeek model and tokenizer"""
        logger.info("Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
        )
        
        # Set pad token if not present
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        logger.info("Loading model...")
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            trust_remote_code=True,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto" if self.device == "cuda" else None,
            low_cpu_mem_usage=True
        )
        
        logger.info("Model loaded successfully!")
    
    def generate_response(self, messages: List[Dict[str, str]], max_tokens: int = 800) -> str:
        """
        Generate response using the local model
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated response text
        """
        try:
            # Convert messages to DeepSeek format
            prompt = self._format_messages_for_deepseek(messages)
            
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=4096)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again in a moment."
    
    def _format_messages_for_deepseek(self, messages: List[Dict[str, str]]) -> str:
        """
        Format messages for DeepSeek model input
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Formatted prompt string
        """
        formatted_prompt = ""
        
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            if role == 'system':
                formatted_prompt += f"<|system|>\n{content}\n<|end|>\n"
            elif role == 'user':
                formatted_prompt += f"<|user|>\n{content}\n<|end|>\n"
            elif role == 'assistant':
                formatted_prompt += f"<|assistant|>\n{content}\n<|end|>\n"
        
        # Add assistant prefix for response generation
        formatted_prompt += "<|assistant|>\n"
        
        return formatted_prompt

class AgenticStartupFactory:
    """Agentic Startup Factory - Core agentic LLM implementation"""
    
    def __init__(self, llm_service: LocalLLMService):
        """
        Initialize the Agentic Startup Factory
        
        Args:
            llm_service: Local LLM service instance
        """
        self.llm_service = llm_service
        self.consideration_categories = self._get_consideration_categories()
        self.sessions: Dict[str, SessionData] = {}
    
    def _get_consideration_categories(self) -> List[ConsiderationCategory]:
        """Get the 8 core business consideration categories"""
        return [
            ConsiderationCategory(
                id="problem_definition",
                title="Problem Definition",
                description="Clearly define the problem you're solving and why it matters"
            ),
            ConsiderationCategory(
                id="target_market",
                title="Target Market",
                description="Identify your ideal customers and market size"
            ),
            ConsiderationCategory(
                id="solution_approach",
                title="Solution Approach",
                description="Outline your proposed solution and its key features"
            ),
            ConsiderationCategory(
                id="competitive_analysis",
                title="Competitive Analysis",
                description="Analyze competitors and your competitive advantage"
            ),
            ConsiderationCategory(
                id="business_model",
                title="Business Model",
                description="Define how you'll make money and serve customers"
            ),
            ConsiderationCategory(
                id="technical_feasibility",
                title="Technical Feasibility",
                description="Assess technical requirements and implementation challenges"
            ),
            ConsiderationCategory(
                id="team_structure",
                title="Team Structure",
                description="Define roles needed and team composition"
            ),
            ConsiderationCategory(
                id="growth_strategy",
                title="Growth Strategy",
                description="Plan for customer acquisition and business scaling"
            )
        ]
    
    def create_session(self) -> str:
        """
        Create a new session
        
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        
        session_data = SessionData(
            session_id=session_id,
            created_at=datetime.now().isoformat(),
            considerations={cat.id: "" for cat in self.consideration_categories},
            chat_history=[],
            last_updated=datetime.now().isoformat()
        )
        
        self.sessions[session_id] = session_data
        logger.info(f"Created new session: {session_id}")
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[SessionData]:
        """
        Get session data
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data or None if not found
        """
        return self.sessions.get(session_id)
    
    def _build_context(self, session_data: SessionData) -> str:
        """
        Build context string from session data for LLM prompts
        
        Args:
            session_data: Current session data
            
        Returns:
            Formatted context string
        """
        if not session_data:
            return "New session - no previous considerations completed."
        
        context_parts = []
        
        # Add completion status
        considerations = session_data.considerations
        completed_count = sum(1 for content in considerations.values() if len(content.strip()) >= 100)
        context_parts.append(f"Completed considerations: {completed_count}/8")
        
        # Add brief summary of each consideration
        for cat in self.consideration_categories:
            content = considerations.get(cat.id, '').strip()
            if content:
                summary = content[:150] + "..." if len(content) > 150 else content
                context_parts.append(f"{cat.title}: {summary}")
            else:
                context_parts.append(f"{cat.title}: Not started")
        
        return "\n".join(context_parts)
    
    def get_agentic_response(self, user_message: str, session_id: str) -> str:
        """
        Generate agentic response based on user message and session context
        
        Args:
            user_message: User's input message
            session_id: Session identifier
            
        Returns:
            AI response
        """
        session_data = self.get_session(session_id)
        if not session_data:
            return "Session not found. Please create a new session."
        
        try:
            # Build context from session data
            context = self._build_context(session_data)
            
            # Create system prompt for agentic behavior
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
            
            # Build message history
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add recent chat history (last 10 messages)
            recent_messages = session_data.chat_history[-10:]
            for msg in recent_messages:
                messages.append({"role": "user", "content": msg.user_message})
                messages.append({"role": "assistant", "content": msg.ai_response})
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Generate response using local LLM
            response = self.llm_service.generate_response(messages, max_tokens=800)
            
            # Update session with new message
            self._add_message(session_id, user_message, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating agentic response: {e}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again in a moment."
    
    def _add_message(self, session_id: str, user_message: str, ai_response: str):
        """
        Add message to session chat history
        
        Args:
            session_id: Session identifier
            user_message: User's message
            ai_response: AI's response
        """
        session_data = self.get_session(session_id)
        if not session_data:
            return
        
        message = ChatMessage(
            timestamp=datetime.now().isoformat(),
            user_message=user_message,
            ai_response=ai_response
        )
        
        session_data.chat_history.append(message)
        session_data.last_updated = datetime.now().isoformat()
        
        # Keep only last 50 messages to prevent memory issues
        if len(session_data.chat_history) > 50:
            session_data.chat_history = session_data.chat_history[-50:]
        
        logger.info(f"Added message to session {session_id}")
    
    def update_consideration(self, session_id: str, consideration_id: str, content: str) -> bool:
        """
        Update consideration content
        
        Args:
            session_id: Session identifier
            consideration_id: Consideration ID to update
            content: New content
            
        Returns:
            Success status
        """
        session_data = self.get_session(session_id)
        if not session_data:
            return False
        
        # Validate consideration ID
        valid_ids = [cat.id for cat in self.consideration_categories]
        if consideration_id not in valid_ids:
            return False
        
        session_data.considerations[consideration_id] = content
        session_data.last_updated = datetime.now().isoformat()
        
        logger.info(f"Updated consideration {consideration_id} in session {session_id}")
        return True
    
    def get_completion_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get completion status for session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Completion status dictionary
        """
        session_data = self.get_session(session_id)
        if not session_data:
            return {
                "completed_count": 0,
                "total_count": 8,
                "can_submit": False
            }
        
        considerations = session_data.considerations
        completed_count = sum(1 for content in considerations.values() if len(content.strip().split()) >= 100)
        
        return {
            "completed_count": completed_count,
            "total_count": 8,
            "can_submit": completed_count >= 6
        }
    
    def generate_equity_suggestion(self, team_structure: str, contribution_data: str) -> Dict[str, Any]:
        """
        Generate equity distribution suggestions
        
        Args:
            team_structure: Team structure description
            contribution_data: Contribution information
            
        Returns:
            Equity suggestion dictionary
        """
        try:
            prompt = f"""As an equity distribution advisor for startups, analyze the following team structure and contributions to suggest a fair equity split:

Team Structure: {team_structure}
Contribution Data: {contribution_data}

Provide a detailed response with:
1. Suggested equity percentages for each role/contributor
2. Reasoning for each allocation
3. Recommendations for vesting schedules
4. Considerations for future team additions

Focus on fairness, long-term sustainability, and alignment with startup best practices.
"""
            
            messages = [{"role": "user", "content": prompt}]
            response = self.llm_service.generate_response(messages, max_tokens=1000)
            
            return {
                "success": True,
                "suggestion": response,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating equity suggestion: {e}")
            return {
                "success": False,
                "error": "Unable to generate equity suggestions at this time",
                "timestamp": datetime.now().isoformat()
            }
    
    def extract_idea_summary(self, session_id: str) -> Dict[str, str]:
        """
        Extract idea summary from session data
        
        Args:
            session_id: Session identifier
            
        Returns:
            Idea summary dictionary
        """
        session_data = self.get_session(session_id)
        if not session_data:
            return {"title": "Untitled Idea", "description": "No description available"}
        
        considerations = session_data.considerations
        
        # Extract title from problem definition
        problem_def = considerations.get("problem_definition", "")
        title = "Untitled Startup Idea"
        if problem_def:
            title = problem_def.split('.')[0].strip()
            if len(title) > 100:
                title = title[:100] + "..."
        
        # Combine key considerations for description
        description_parts = []
        for key in ["problem_definition", "solution_approach", "target_market"]:
            content = considerations.get(key, "").strip()
            if content:
                description_parts.append(content)
        
        description = " ".join(description_parts)
        if len(description) > 500:
            description = description[:500] + "..."
        
        return {
            "title": title,
            "description": description if description else "No description available"
        }

class ExperimentRunner:
    """Main experiment runner for testing the agentic setup"""
    
    def __init__(self, model_name: str = "deepseek-ai/deepseek-coder-6.7b-instruct"):
        """
        Initialize the experiment runner
        
        Args:
            model_name: HuggingFace model name
        """
        logger.info("Initializing Experiment Runner...")
        self.llm_service = LocalLLMService(model_name)
        self.asf = AgenticStartupFactory(self.llm_service)
        logger.info("Experiment Runner initialized successfully!")
    
    def run_interactive_session(self):
        """Run an interactive session with the agentic LLM"""
        print("\n" + "="*60)
        print("🔥 THE FORGE - Agentic Startup Factory")
        print("="*60)
        print("Welcome to the Agentic LLM Experiment!")
        print("This system will help you develop a startup idea through 8 core considerations.")
        print("Type 'quit' to exit, 'status' to see progress, 'summary' for idea summary.")
        print("="*60)
        
        # Create new session
        session_id = self.asf.create_session()
        print(f"Session created: {session_id[:8]}...")
        
        while True:
            try:
                # Get user input
                user_input = input("\n🤔 You: ").strip()
                
                if user_input.lower() == 'quit':
                    print("👋 Goodbye! Your session data has been saved.")
                    break
                
                elif user_input.lower() == 'status':
                    status = self.asf.get_completion_status(session_id)
                    print(f"\n📊 Progress: {status['completed_count']}/{status['total_count']} considerations completed")
                    print(f"✅ Can submit: {status['can_submit']}")
                    continue
                
                elif user_input.lower() == 'summary':
                    summary = self.asf.extract_idea_summary(session_id)
                    print(f"\n📋 Idea Summary:")
                    print(f"Title: {summary['title']}")
                    print(f"Description: {summary['description']}")
                    continue
                
                elif not user_input:
                    continue
                
                # Generate agentic response
                print("🤖 ASF: ", end="", flush=True)
                response = self.asf.get_agentic_response(user_input, session_id)
                print(response)
                
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted. Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error in interactive session: {e}")
                print(f"❌ Error: {e}")
    
    def run_demo_conversation(self):
        """Run a demo conversation to showcase the agentic capabilities"""
        print("\n" + "="*60)
        print("🎭 DEMO MODE - Agentic Startup Factory")
        print("="*60)
        
        # Create session
        session_id = self.asf.create_session()
        
        # Demo conversation
        demo_messages = [
            "I have an idea for a mobile app that helps people find local restaurants",
            "I'm thinking it could use AI to recommend dishes based on user preferences",
            "What should I consider for the target market?",
            "How can I differentiate from apps like Yelp and Google Maps?",
            "What technical challenges should I expect?",
            "How should I structure the team for this project?"
        ]
        
        for i, message in enumerate(demo_messages, 1):
            print(f"\n--- Turn {i} ---")
            print(f"🤔 User: {message}")
            
            response = self.asf.get_agentic_response(message, session_id)
            print(f"🤖 ASF: {response}")
            
            # Show progress
            status = self.asf.get_completion_status(session_id)
            print(f"📊 Progress: {status['completed_count']}/{status['total_count']} considerations")
        
        # Show final summary
        print(f"\n--- Final Summary ---")
        summary = self.asf.extract_idea_summary(session_id)
        print(f"📋 Title: {summary['title']}")
        print(f"📋 Description: {summary['description']}")
        
        # Test equity suggestion
        print(f"\n--- Equity Suggestion ---")
        equity_result = self.asf.generate_equity_suggestion(
            "Founder (idea + initial development), CTO (technical leadership), Marketing Lead (go-to-market)",
            "Founder: 40%, CTO: 30%, Marketing: 20%, Reserved: 10%"
        )
        if equity_result['success']:
            print(f"💡 Equity Suggestion: {equity_result['suggestion'][:200]}...")
        else:
            print(f"❌ Equity suggestion failed: {equity_result['error']}")

def main():
    """Main function to run the experiment"""
    print("🚀 Starting HPC Cluster Experiments - Agentic LLM Setup")
    
    try:
        # Initialize experiment runner
        runner = ExperimentRunner()
        
        # Ask user for mode
        print("\nSelect mode:")
        print("1. Interactive session (chat with the AI)")
        print("2. Demo conversation (automated demo)")
        
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == "1":
            runner.run_interactive_session()
        elif choice == "2":
            runner.run_demo_conversation()
        else:
            print("Invalid choice. Running demo conversation...")
            runner.run_demo_conversation()
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"❌ Fatal error: {e}")
        print("Please check your model installation and try again.")

if __name__ == "__main__":
    main() 