# The Forge 🔥

**AI-Powered Startup Development Platform**

Transform your ideas into structured startup plans with our AI assistant. Whether you're a subject matter expert who sees automation opportunities, or a developer ready to implement innovative concepts - collaborate, contribute, and earn equity for your expertise.

## 🚀 Features

### For Ideators
- **AI-Powered Ideation**: Share your vision and domain expertise
- **Structured Development**: AI develops comprehensive business plans from conversations
- **8 Core Considerations**: Automatic development of essential business areas
- **Collaboration Tools**: Connect with implementers who can bring ideas to life

### For Developers
- **Ready-to-Implement Ideas**: Find structured startup concepts in the marketplace
- **Collaboration Platform**: Use tools like Replit to build alongside ideators
- **Equity Opportunities**: Earn equity through contribution and expertise
- **Team Formation**: Join existing projects or start new collaborations

### Core Business Considerations
1. **Problem Definition** - Clearly define the problem you're solving
2. **Target Market** - Identify your ideal customers and market size
3. **Solution Approach** - Outline your proposed solution and key features
4. **Competitive Analysis** - Analyze competitors and competitive advantages
5. **Business Model** - Define how you'll make money and serve customers
6. **Technical Feasibility** - Assess technical requirements and challenges
7. **Team Structure** - Define roles needed and team composition
8. **Growth Strategy** - Plan for customer acquisition and business scaling

## 🛠️ Installation

### Prerequisites
- Python 3.11 or higher
- OpenAI API key (for AI functionality)

### Setup
1. **Clone the repository**
   ```bash
   git clone https://github.com/ANSH-RIYAL/Apocrypha.git
   cd Apocrypha
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   Or using uv (recommended):
   ```bash
   uv sync
   ```

3. **Set up environment variables**
   ```bash
   export OPENAI_API_KEY="your_openai_api_key_here"
   export SESSION_SECRET="your_session_secret_here"
   ```

4. **Initialize the database**
   ```bash
   python3 database_setup.py
   ```

## 🚀 Running the Application

### Development Mode
```bash
python3 main.py
```
or
```bash
python3 app.py
```

The application will be available at `http://localhost:5000`

### Production Mode
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📁 Project Structure

```
Apocrypha/
├── app.py                 # Main Flask application
├── main.py               # Application entry point
├── data_manager.py       # JSON-based data management
├── openai_service.py     # OpenAI GPT-4o integration
├── database_setup.py     # Database initialization
├── pyproject.toml        # Project dependencies
├── requirements.txt      # Python dependencies
├── data/                 # JSON database files
│   ├── config.json       # Application configuration
│   ├── sessions/         # User session data
│   ├── ideas/           # Submitted ideas
│   ├── users/           # User profiles
│   └── comments/        # Idea comments
├── templates/           # HTML templates
│   ├── base.html        # Base template
│   ├── index.html       # Landing page
│   ├── forge.html       # Main ideation interface
│   ├── marketplace.html # Ideas marketplace
│   └── idea_detail.html # Individual idea view
└── static/              # Static assets
    ├── css/             # Stylesheets
    └── js/              # JavaScript files
```

## 🔧 Configuration

The application uses a JSON-based configuration system located in `data/config.json`:

- **Considerations**: Define the 8 core business considerations
- **Submission Requirements**: Minimum criteria for idea submission
- **Database Settings**: File storage and backup configurations

## 🤖 AI Integration

The Forge uses OpenAI's GPT-4o model to:
- Generate responses during ideation sessions
- **Auto-fill consideration panels** based on conversations with structured data extraction
- Provide equity distribution suggestions
- Offer business guidance and feedback
- **Track completion status** using boolean flags for each consideration
- **Maintain conversation context** with sliding window memory management

### Enhanced Auto-Filling System
- **Structured Data Format**: Considerations now use a hierarchical structure with `content`, `previous_value`, `metadata`, and `is_complete` fields
- **Smart Extraction**: AI responses are parsed to extract consideration updates in a structured format
- **Response Cleaning**: Consideration update sections are automatically removed from user-facing responses
- **Backward Compatibility**: Supports both new structured format and legacy string-based considerations
- **Completion Tracking**: Boolean completion status determined at update time based on content quality

### API Requirements
- OpenAI API key with GPT-4o access
- Internet connection for API calls

## 💾 Data Management

The application uses a local JSON-based database system:
- **Sessions**: Store user conversation history and consideration progress
- **Ideas**: Public marketplace submissions with full business plans
- **Users**: User profiles and collaboration data
- **Comments**: Community feedback on submitted ideas

All data is stored locally in the `data/` directory and automatically backed up.

### Enhanced Session Management
- **Comprehensive Logging**: Detailed logging throughout the application for debugging
- **Error Handling**: Robust error handling with detailed tracebacks
- **Session Persistence**: Automatic session creation and management
- **Consideration Tracking**: Real-time updates to consideration completion status

## 🌐 API Endpoints

### Core Routes
- `GET /` - Landing page
- `GET /forge` - Main ideation interface
- `GET /marketplace` - Public ideas marketplace
- `GET /idea/<idea_id>` - Individual idea detail page

### API Endpoints
- `POST /api/chat` - Chat with AI assistant
- `POST /api/update_consideration` - Update consideration content
- `POST /api/submit_idea` - Submit idea to marketplace
- `POST /api/add_comment` - Add comment to idea
- `GET /api/session_status` - Get session completion status

## 🎨 UI/UX Features

- **Light Theme**: Clean, accessible design for non-technical users
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Live consideration panel updates
- **Progress Tracking**: Visual completion indicators
- **Collaboration Tools**: Built-in commenting and sharing

## 🔒 Security

- Session-based authentication
- Input validation and sanitization
- CORS protection
- Secure API key handling

## 🚀 Deployment

### Local Development
```bash
python3 main.py
```

### Production (using Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key
- `SESSION_SECRET`: Secret key for session management
- `PORT`: Port number (default: 5000)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation in `replit.md`
- Review the commit summary in `COMMIT_SUMMARY.md`

## 🔄 Recent Updates

The Forge was transformed from the original "Agentic Startup Factory" with:
- Complete rebrand and light theme
- JSON-based data management
- Enhanced collaboration features
- Improved UI/UX design
- Comprehensive business consideration framework

### Latest Enhancements
- **Consideration Auto-Filling System**: AI automatically extracts and updates consideration content from conversations
- **Structured Data Management**: New hierarchical consideration format with metadata support
- **Boolean Completion Tracking**: Improved completion status tracking with boolean flags
- **Enhanced Debugging**: Comprehensive logging infrastructure throughout the application
- **Format Enforcement**: AI responses use plain text without formatting for better readability
- **HPC Cluster Support**: Standalone script for high-performance computing experiments
- **Local Development Setup**: Environment variable configuration for local development

---

**Built with ❤️ for the startup community** 