# Apocrypha Forge - Project Reference Document

## Project Overview
**Name**: Apocrypha Forge (The Forge)  
**Focus**: Agentic Startup Factory (ASF) - AI-powered startup ideation platform  
**Goal**: Help 30-40 people develop 50-60 structured startup ideas for developer pickup  

## Current Architecture Analysis

### Existing Implementation (Already Built)
- **Flask Web Application**: Fully functional with proper structure
- **OpenAI Integration**: GPT-4o powered chat assistant
- **Data Management**: JSON-based file storage system
- **User Interface**: Bootstrap dark theme with responsive design
- **Core Features**: 
  - Real-time chat with ASF agent
  - 8 structured considerations system
  - Auto-save functionality
  - Progress tracking
  - Public marketplace for idea sharing
  - Community commenting system

### File Structure
```
/
├── app.py                 # Main Flask routes and logic
├── main.py               # Application entry point
├── openai_service.py     # AI integration service
├── data_manager.py       # File-based data management
├── templates/            # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── forge.html
│   ├── marketplace.html
│   └── idea_detail.html
├── static/
│   ├── css/custom.css
│   └── js/
│       ├── forge.js
│       └── marketplace.js
└── data/
    ├── sessions/         # User session data
    └── ideas/           # Submitted public ideas
```

## ASF Core Considerations Structure

### 8 Standard Considerations (Implemented)
1. **Problem Definition** - Core problem and why it matters
2. **Target Market** - Audience identification and market size
3. **Solution Approach** - Proposed solution methodology
4. **Competitive Analysis** - Existing solutions and advantages
5. **Business Model** - Revenue generation strategy
6. **Technical Feasibility** - Implementation requirements
7. **Team Structure** - Required roles and composition
8. **Growth Strategy** - Go-to-market and scaling plan

### Completion Criteria
- **Minimum for Submission**: 6 out of 8 considerations
- **Word Requirement**: 100+ words per consideration
- **Public Review Period**: 7 days after submission

## User Flow Design

### 1. Individual Ideation Process
```
User Access → Forge Interface → AI Chat + Considerations Sidebar
          ↓
Real-time Chat with ASF → Auto-save Progress → Visual Progress Tracking
          ↓
Complete 6+ Considerations → Submit to Marketplace → Community Review
```

### 2. Marketplace System
```
Public Ideas Board → Filter/Search → Idea Detail Page → Comments → Collaboration
```

### 3. AI Interaction Flow
```
User Input → Context Building → OpenAI GPT-4o → Structured Response → Session Update
```

## Technical Implementation Details

### Data Persistence Strategy
- **Session Data**: JSON files in `data/sessions/`
- **Public Ideas**: JSON files in `data/ideas/`
- **Future Migration**: S3 buckets for scalability
- **Auto-save**: 2-second debounced saving

### AI Integration
- **Model**: GPT-4o (latest OpenAI model)
- **Context Management**: Last 10 chat messages + consideration status
- **Response Format**: Conversational guidance with structured prompts
- **Error Handling**: Graceful fallbacks and user-friendly messages

### Frontend Architecture
- **Framework**: Vanilla JavaScript with ES6 classes
- **UI Library**: Bootstrap 5 with dark theme
- **Real-time Updates**: Fetch API for async operations
- **Progress Tracking**: Visual progress bars and status indicators

## User Experience Design

### Forge Interface Layout
```
[Progress Bar Header - Sticky]
[Main Content Area]
├── [Chat Interface - 8 columns]
│   ├── Chat History
│   ├── Typing Indicators
│   └── Message Input
└── [Considerations Sidebar - 4 columns]
    ├── Accordion-style panels
    ├── Word count tracking
    ├── Auto-save indicators
    └── Completion status
```

### Key UX Features
- **Auto-save**: Prevents data loss with debounced saving
- **Progress Visualization**: Clear completion status
- **Mobile Responsive**: Works on all devices
- **Accessibility**: Proper ARIA labels and keyboard navigation

## Community Features

### Marketplace System
- **Public Visibility**: 7-day review period
- **Search & Filter**: By status, date, engagement
- **Comment System**: Community feedback and collaboration
- **View Tracking**: Basic analytics for idea popularity

### Collaboration Framework
- **Open Ideas**: Public viewing of completed considerations
- **Community Feedback**: Structured comment system
- **Collaboration Signals**: Interest indication for team formation

## Scaling Considerations

### Current Limitations (Acceptable for Beta)
- **File-based Storage**: Simple but not enterprise-scale
- **No User Authentication**: Anonymous sessions work for now
- **Basic Analytics**: Simple view/comment tracking
- **Manual Moderation**: No automated content filtering

### Future Enhancements (Post-MVP)
- **Database Migration**: PostgreSQL for production
- **User Authentication**: Email-based accounts
- **Advanced Analytics**: Detailed engagement metrics
- **Team Formation**: Automated role matching
- **Equity Calculation**: AI-powered equity suggestions

## Development Priorities

### Phase 1: Core ASF Implementation ✅ (DONE)
- ✅ Flask application structure
- ✅ OpenAI integration
- ✅ 8 considerations system
- ✅ Chat interface
- ✅ Auto-save functionality
- ✅ Progress tracking

### Phase 2: Marketplace System ✅ (DONE)
- ✅ Public idea submission
- ✅ Community viewing
- ✅ Comment system
- ✅ Search and filtering

### Phase 3: Website Refocus (CURRENT)
- 🔄 Streamline homepage for ASF focus
- 🔄 Update content to emphasize Forge
- 🔄 Remove cluttered information
- 🔄 Clear value proposition

### Phase 4: User Onboarding (NEXT)
- 📋 Simple tutorial flow
- 📋 Example considerations
- 📋 Better first-time experience

## Key Design Decisions

### Technology Choices
- **Flask over Django**: Lighter weight for MVP
- **JSON over Database**: Simpler deployment and backup
- **Bootstrap over Custom CSS**: Faster development with professional look
- **Vanilla JS over React**: Reduces complexity and build requirements

### User Experience Choices
- **Anonymous Sessions**: Lower barrier to entry
- **Auto-save**: Prevents frustration from lost work
- **Minimum 6/8 Considerations**: Ensures quality without being overwhelming
- **7-day Review Period**: Balances exposure with freshness

## Success Metrics

### Primary Goals
- **30-40 Active Users**: Initial user base target
- **50-60 Completed Ideas**: Quality idea generation
- **Developer Pickup**: Ideas selected for development

### Secondary Metrics
- **Session Completion Rate**: % of users who complete 6+ considerations
- **Community Engagement**: Comments per idea
- **Idea Quality**: Feedback scores and developer interest

## User Preferences & Context

### Communication Style
- **Language**: Simple, everyday language (non-technical)
- **Tone**: Supportive and encouraging
- **Approach**: Focus on practical outcomes

### Technical Preferences
- **Python**: Basic Flask patterns (as in original repo)
- **No Complex Frameworks**: Keep it simple and maintainable
- **File-based Storage**: JSON for simplicity
- **Bootstrap Styling**: Use provided dark theme

## Implementation Notes

### Current Status
- **Fully Functional**: Core ASF system is complete and working
- **Needs Refocus**: Website content needs streamlining
- **Ready for Users**: Technical implementation is solid

### Next Steps
1. Refactor homepage to focus on Forge
2. Update navigation and content structure
3. Add user onboarding flow
4. Test with initial user group
5. Iterate based on feedback

---

*Last Updated: July 8, 2025*  
*Context: Refocusing Apocrypha website to emphasize Forge (ASF) functionality*