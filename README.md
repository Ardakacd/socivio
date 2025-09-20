# Socivio - AI-Powered Social Media Assistant

Socivio is an AI-powered social media management platform that helps businesses manage their Instagram, TikTok, and X (Twitter) accounts efficiently. It uses CrewAI to generate intelligent comment replies, provide engagement insights, and automate social media tasks.

## 🚀 Features

### ✅ Core Features (MVP Complete)

- **🔐 User Authentication**: JWT-based authentication system
- **📱 Instagram Business Integration**: OAuth connection to Instagram Business API
- **📊 Post Analytics**: Fetch and display post performance metrics
- **💬 Comment Management**: View and manage comments across posts
- **🤖 AI-Powered Replies**: CrewAI generates contextual comment replies in multiple languages
- **📈 Engagement Insights**: Analytics dashboard with performance metrics
- **🎨 Modern UI**: Responsive design with Tailwind CSS and shadcn/ui components

### 🔄 Workflow

1. **Connect Accounts**: Link Instagram Business accounts via OAuth
2. **Sync Content**: Automatically fetch posts and comments
3. **AI Analysis**: CrewAI analyzes comments and generates appropriate replies
4. **Review & Approve**: Users can edit and approve AI-generated replies before sending
5. **Track Performance**: Monitor engagement metrics and get AI-powered insights

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: Database ORM with PostgreSQL
- **CrewAI**: AI agent framework for intelligent reply generation
- **Celery**: Background task processing
- **Redis**: Caching and task queue
- **Alembic**: Database migrations

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: Modern React components
- **React Query**: Data fetching and caching
- **Recharts**: Data visualization

### Infrastructure
- **Docker**: Containerization
- **PostgreSQL**: Primary database
- **Redis**: Caching and task queue

## 📁 Project Structure

```
socivio/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core functionality (auth, config)
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── db/             # Database configuration
│   ├── alembic/            # Database migrations
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile
├── frontend/               # Next.js frontend
│   ├── app/                # App router pages
│   ├── components/         # React components
│   ├── lib/                # Utilities and API client
│   ├── types/              # TypeScript types
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml      # Docker services
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Instagram Business Account
- OpenAI API Key (for CrewAI)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd socivio
```

### 2. Set Up Environment Variables

```bash
cp env.example .env
```

Edit `.env` with your credentials:

```env
# Instagram Business API
INSTAGRAM_CLIENT_ID=your-instagram-client-id
INSTAGRAM_CLIENT_SECRET=your-instagram-client-secret

# OpenAI API Key (for CrewAI)
OPENAI_API_KEY=your-openai-api-key

# Other variables are pre-configured for Docker
```

### 3. Start with Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 5. Database Setup

The database will be automatically created when you start the services. To run migrations manually:

```bash
docker-compose exec backend alembic upgrade head
```

## 🔧 Development Setup

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 📋 API Endpoints

### Authentication
- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `GET /api/auth/instagram/connect` - Get Instagram OAuth URL
- `GET /api/auth/instagram/callback` - Handle Instagram OAuth callback

### Posts
- `GET /api/posts/{account_id}` - Get posts for account
- `POST /api/posts/{account_id}/sync` - Sync posts from Instagram
- `GET /api/posts/{account_id}/analytics` - Get post analytics

### Comments & Replies
- `GET /api/comments/` - Get comments
- `POST /api/comments/{comment_id}/generate-reply` - Generate AI reply
- `POST /api/comments/{comment_id}/approve-reply` - Approve and send reply

### Insights
- `GET /api/insights/{account_id}/overview` - Get account overview
- `GET /api/insights/dashboard-summary` - Get dashboard summary

## 🤖 AI Features

### CrewAI Integration

Socivio uses CrewAI to power its AI features:

1. **Reply Generation**: Analyzes comment context and generates appropriate responses
2. **Sentiment Analysis**: Determines comment sentiment to inform reply strategy
3. **Multi-language Support**: Generates replies in multiple languages
4. **Business Context**: Considers business type and brand voice
5. **Performance Insights**: Analyzes engagement patterns and provides recommendations

### Supported Tones
- Friendly
- Professional
- Casual
- Helpful
- Enthusiastic

### Supported Languages
- English
- Spanish
- French
- German
- Portuguese
- And more...

## 🔐 Security

- JWT-based authentication
- Secure password hashing with bcrypt
- Environment variable configuration
- CORS protection
- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy ORM

## 📊 Monitoring & Analytics

### Dashboard Features
- Engagement rate tracking
- Post performance metrics
- Comment response rates
- Content type analysis
- Trending insights
- AI-powered recommendations

### Metrics Tracked
- Likes, comments, shares
- Engagement rates
- Response times
- Content performance
- Follower growth
- Peak activity times

## 🚀 Deployment

### Production Deployment

1. **Set up production environment variables**
2. **Configure database and Redis**
3. **Build and deploy with Docker**

```bash
# Production build
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Configuration

For production, update the following:
- Change `SECRET_KEY` to a secure random string
- Set `DEBUG=False`
- Configure proper CORS origins
- Use managed database services
- Set up SSL/TLS certificates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support, please contact us at support@socivio.com or open an issue on GitHub.

## 🗺️ Roadmap

### Phase 2 (Upcoming)
- TikTok integration
- X (Twitter) integration
- Advanced analytics
- Team collaboration features
- Mobile app
- Automated posting
- Content calendar
- A/B testing for replies

### Phase 3 (Future)
- Multi-language dashboard
- Advanced AI insights
- Custom AI training
- White-label solution
- Enterprise features

---

Built with ❤️ by the Socivio team
