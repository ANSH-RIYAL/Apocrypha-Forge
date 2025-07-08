#!/usr/bin/env python3
"""
Database setup script for The Forge
Creates the initial JSON file structure and sample data
"""

import os
import json
from datetime import datetime

def create_directory_structure():
    """Create the necessary directory structure for JSON database"""
    directories = [
        'data',
        'data/sessions',
        'data/ideas',
        'data/users',
        'data/comments'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        
        # Create .gitkeep files to ensure directories are tracked
        gitkeep_path = os.path.join(directory, '.gitkeep')
        if not os.path.exists(gitkeep_path):
            with open(gitkeep_path, 'w') as f:
                f.write('')

def create_sample_data():
    """Create sample data structure files"""
    
    # Sample session structure
    sample_session = {
        "session_id": "sample_session_123",
        "created_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
        "considerations": {
            "problem_definition": "",
            "target_market": "",
            "solution_approach": "",
            "competitive_analysis": "",
            "business_model": "",
            "technical_feasibility": "",
            "team_structure": "",
            "growth_strategy": ""
        },
        "chat_history": [
            {
                "timestamp": datetime.now().isoformat(),
                "sender": "assistant",
                "message": "Welcome to The Forge! Let's develop your startup idea together."
            }
        ],
        "metadata": {
            "ip_address": "127.0.0.1",
            "user_agent": "sample"
        }
    }
    
    # Sample idea structure
    sample_idea = {
        "idea_id": "idea_123",
        "session_id": "sample_session_123",
        "title": "AI-Powered Task Management",
        "description": "An intelligent task management system that uses AI to prioritize and organize work",
        "submitted_at": datetime.now().isoformat(),
        "considerations": {
            "problem_definition": "Knowledge workers struggle with task prioritization and time management...",
            "target_market": "Professionals and teams in knowledge-intensive industries...",
            "solution_approach": "AI-powered task management with smart prioritization...",
            "competitive_analysis": "Competing with tools like Todoist, Asana, but with AI differentiation...",
            "business_model": "Freemium SaaS model with premium AI features...",
            "technical_feasibility": "Requires NLP, machine learning, and web development expertise...",
            "team_structure": "Need AI engineer, full-stack developer, product manager...",
            "growth_strategy": "Content marketing, integration partnerships, viral features..."
        },
        "status": "published",
        "views": 0,
        "implementations": []
    }
    
    # Sample user structure
    sample_user = {
        "user_id": "user_123",
        "type": "ideator",  # or "implementer", "hybrid"
        "profile": {
            "name": "John Doe",
            "expertise": ["Business Strategy", "Market Analysis"],
            "bio": "Business strategist with 10 years experience in tech startups",
            "skills": ["Strategic Planning", "Market Research", "Business Development"]
        },
        "contributions": {
            "ideas_created": 1,
            "implementations_completed": 0,
            "equity_earned": 0,
            "collaboration_score": 85
        },
        "created_at": datetime.now().isoformat()
    }
    
    # Sample comment structure
    sample_comment = {
        "comment_id": "comment_123",
        "idea_id": "idea_123",
        "author": "Jane Smith",
        "content": "Great idea! I'd love to help implement the AI components.",
        "timestamp": datetime.now().isoformat(),
        "author_type": "implementer",
        "contact_info": "jane@email.com"
    }
    
    # Write sample files
    samples = [
        ('data/sessions/sample_session.json', sample_session),
        ('data/ideas/sample_idea.json', sample_idea),
        ('data/users/sample_user.json', sample_user),
        ('data/comments/sample_comment.json', sample_comment)
    ]
    
    for filepath, data in samples:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

def create_config_file():
    """Create configuration file for database settings"""
    config = {
        "database": {
            "type": "json_file",
            "base_path": "data",
            "auto_backup": True,
            "max_file_size_mb": 10
        },
        "considerations": [
            {
                "id": "problem_definition",
                "title": "Problem Definition",
                "description": "Clearly define the problem you're solving and why it matters"
            },
            {
                "id": "target_market",
                "title": "Target Market",
                "description": "Identify your ideal customers and market size"
            },
            {
                "id": "solution_approach",
                "title": "Solution Approach",
                "description": "Outline your proposed solution and its key features"
            },
            {
                "id": "competitive_analysis",
                "title": "Competitive Analysis",
                "description": "Analyze competitors and your competitive advantage"
            },
            {
                "id": "business_model",
                "title": "Business Model",
                "description": "Define how you'll make money and serve customers"
            },
            {
                "id": "technical_feasibility",
                "title": "Technical Feasibility",
                "description": "Assess technical requirements and implementation challenges"
            },
            {
                "id": "team_structure",
                "title": "Team Structure",
                "description": "Define roles needed and team composition"
            },
            {
                "id": "growth_strategy",
                "title": "Growth Strategy",
                "description": "Plan for customer acquisition and business scaling"
            }
        ],
        "submission_requirements": {
            "min_completed_considerations": 6,
            "min_words_per_consideration": 100
        }
    }
    
    with open('data/config.json', 'w') as f:
        json.dump(config, f, indent=2)

def main():
    """Main setup function"""
    print("Setting up The Forge JSON database structure...")
    
    create_directory_structure()
    print("✓ Directory structure created")
    
    create_sample_data()
    print("✓ Sample data created")
    
    create_config_file()
    print("✓ Configuration file created")
    
    print("\nDatabase setup complete! Structure:")
    print("data/")
    print("├── sessions/     # User session data")
    print("├── ideas/        # Published ideas")
    print("├── users/        # User profiles")
    print("├── comments/     # Idea comments")
    print("└── config.json   # Configuration")

if __name__ == "__main__":
    main()