# HCP CRM - AI-First Healthcare Professional CRM System

An intelligent CRM system for managing healthcare professional (HCP) interactions with AI-powered assistance.

## Overview

HCP CRM is a modern web application designed to streamline the logging, tracking, and management of interactions with healthcare professionals. It features:

- **AI-Powered Form Filling**: Describe interactions in natural language, and the AI automatically extracts and fills in structured data
- **Real-time Chat Interface**: Communicate with an AI assistant for intelligent interaction management
- **Comprehensive Interaction Logging**: Track meetings, calls, emails, conferences, and sample distributions
- **Search & Analytics**: Find interactions quickly with powerful search capabilities
- **PostgreSQL Database**: Reliable data storage with async support

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 16 with SQLAlchemy ORM
- **AI/LLM**: Groq API with LangChain
- **Async Support**: AsyncPG for async database operations
- **API Style**: RESTful with Server-Sent Events (SSE) for streaming

### Frontend
- **Framework**: React 18 with TypeScript
- **State Management**: Redux Toolkit
- **Styling**: CSS with CSS Variables
- **UI Components**: Custom components (TextField, Select, Button, etc.)
- **Build Tool**: Vite

### DevOps
- **Containerization**: Docker & Docker Compose
- **Services**: Backend API, React Frontend, PostgreSQL Database

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Groq API key (get it from [console.groq.com](https://console.groq.com))

### Setup

1. **Clone and navigate to project**
   ```bash
   cd /home/digicoffer/AIVOA
   ```

2. **Configure environment variables**
   - `.env` file is already configured with Docker settings
   - Update `GROQ_API_KEY` in `.env` with your API key

3. **Start all services**
   ```bash
   docker compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Stopping Services
```bash
docker compose down
```

### Restarting Backend Only
```bash
docker compose restart backend
```

## Project Structure

```
AIVOA/
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   ├── ai/               # AI agent and tools
│   │   ├── db/               # Database models and sessions
│   │   ├── services/         # Business logic
│   │   ├── repositories/     # Data access layer
│   │   ├── schemas/          # Pydantic schemas
│   │   └── main.py           # FastAPI app
│   ├── scripts/              # Database seeding
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── features/         # Feature modules (interactions, assistant)
│   │   ├── components/       # Reusable UI components
│   │   ├── api/              # API client
│   │   ├── app/              # Redux store and hooks
│   │   ├── styles/           # Global styles
│   │   └── App.tsx           # Root component
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml        # Multi-container orchestration
└── .env                       # Environment configuration
```

## Key Features

### 1. AI-Powered Interaction Logging
- Natural language processing for interaction description
- Automatic field extraction (HCP name, interaction type, channel, sentiment, products)
- Support for relative dates ("today", "yesterday", "tomorrow")
- Intelligent sentiment analysis

### 2. Chat Interface
- Real-time streaming responses from AI
- Tool execution feedback
- Interaction history tracking
- Clear chat history functionality

### 3. Interaction Management
- Create, read, update, delete operations
- Status tracking (DRAFT, LOGGED)
- Source tracking (FORM, AI_ASSISTANT)
- Follow-up actions and AI summaries

### 4. Healthcare Professional Database
- Auto-create HCPs when first mentioned
- HCP autocomplete in forms
- Interaction history per HCP

## Development

### Backend Development
```bash
# Enter backend directory
cd backend

# Install dependencies (if not in container)
pip install -r requirements.txt

# Run tests
pytest

# Format code
black app/
```

### Frontend Development
```bash
# Enter frontend directory
cd frontend

# Install dependencies (if not in container)
npm install

# Development with hot reload
npm run dev

# Build for production
npm run build
```

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for the interactive Swagger UI documentation.

### Key Endpoints

**Interactions**
- `GET /api/interactions` - List all interactions
- `POST /api/interactions` - Create new interaction
- `GET /api/interactions/{id}` - Get interaction details
- `PUT /api/interactions/{id}` - Update interaction
- `DELETE /api/interactions/{id}` - Delete interaction
- `POST /api/interactions/{id}/confirm` - Confirm and log interaction

**HCPs**
- `GET /api/hcps` - List all HCPs
- `GET /api/hcps/{id}` - Get HCP details
- `GET /api/hcps/{id}/interactions` - Get HCP's interactions

**Assistant**
- `POST /api/assistant/chat` - Send message to AI assistant (Server-Sent Events)

## Configuration

### Environment Variables

**Backend** (`.env`)
```
DATABASE_URL=postgresql+asyncpg://hcp_crm:password@postgres:5432/hcp_crm_db
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=llama-3.1-8b-instant
ENVIRONMENT=development
DEBUG=false
```

**Frontend** (via docker-compose)
```
VITE_API_URL=http://localhost:8000
```

## Database

The application uses PostgreSQL 16 Alpine. Database initialization is automatic on first run:
- Tables are created automatically via SQLAlchemy ORM
- Sample data (5 HCPs and 5 interactions) are seeded on initialization
- Database volume persists between container restarts

## AI Agent

The AI agent is powered by Groq and can perform the following actions:

1. **log_interaction** - Create new HCP interaction from description
2. **edit_interaction** - Update existing interaction
3. **search_interactions** - Find interactions by keyword or HCP
4. **summarize_interaction** - Add AI-generated summary
5. **suggest_followups** - Add follow-up actions to interaction

## Known Issues & Solutions

### Issue: Form not auto-filling from AI
**Solution**: Ensure Groq API key is valid and the AI response includes proper tool_call tags

### Issue: Timezone errors when saving interactions
**Solution**: Backend automatically converts timezone-aware datetimes to naive format for database compatibility

### Issue: Scroll not working in UI sections
**Solution**: CSS overflow properties are properly configured with overflow-y: auto for scrollable sections

## Contributing

When making changes:
1. Backend changes require restarting the backend: `docker compose restart backend`
2. Frontend changes auto-reload via Vite hot module replacement
3. Test your changes in the browser before committing

## Troubleshooting

### Backend not starting
```bash
# Check logs
docker compose logs backend --tail=50

# Restart everything
docker compose down -v
docker compose up -d
```

### Frontend not loading
- Clear browser cache (Ctrl+Shift+Delete)
- Check if port 5173 is available
- Verify VITE_API_URL is correct

### Database connection issues
- Verify PostgreSQL container is healthy: `docker compose ps`
- Check DATABASE_URL in .env
- Ensure postgres_data volume exists

## License

This project is part of the AIVOA initiative.

## Support

For issues or questions, refer to the API documentation at `http://localhost:8000/docs` or check the backend logs for detailed error messages.
