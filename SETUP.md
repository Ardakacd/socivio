# Socivio Setup Guide

## 🚀 Quick Start (Recommended)

### 1. Prerequisites
- Docker Desktop installed and running
- Instagram Business Account
- OpenAI API Key

### 2. Clone and Setup
```bash
git clone <your-repo>
cd socivio
cp env.example .env
```

### 3. Configure Environment
Edit `.env` file with your credentials:
```env
INSTAGRAM_CLIENT_ID=your-instagram-client-id
INSTAGRAM_CLIENT_SECRET=your-instagram-client-secret
OPENAI_API_KEY=your-openai-api-key
```

### 4. Start Application
```bash
# Use the startup script (recommended)
./scripts/start.sh

# Or manually with docker-compose
docker-compose up -d
```

### 5. Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔧 Development Setup

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp env.example .env
# Edit .env with your values
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Database Setup
```bash
# If using Docker (automatic)
docker-compose up -d postgres

# Manual setup
# 1. Install PostgreSQL
# 2. Create database 'socivio'
# 3. Run migrations
cd backend
alembic upgrade head
```

## 📱 Instagram Business API Setup

### 1. Create Facebook App
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app
3. Add Instagram Basic Display product

### 2. Configure OAuth
1. Set redirect URI: `http://localhost:8000/auth/instagram/callback`
2. Copy Client ID and Client Secret to `.env`

### 3. Test Connection
1. Start the application
2. Navigate to the dashboard
3. Click "Connect Instagram Account"

## 🤖 OpenAI API Setup

### 1. Get API Key
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to API Keys
4. Create a new secret key

### 2. Configure
Add your API key to `.env`:
```env
OPENAI_API_KEY=sk-your-api-key-here
```

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild services
docker-compose up -d --build

# Access backend container
docker-compose exec backend bash

# Access database
docker-compose exec postgres psql -U socivio_user -d socivio
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Kill processes on ports
sudo lsof -ti:3000 | xargs kill -9  # Frontend
sudo lsof -ti:8000 | xargs kill -9  # Backend
sudo lsof -ti:5432 | xargs kill -9  # PostgreSQL
```

#### 2. Database Connection Error
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Restart database
docker-compose restart postgres
```

#### 3. Instagram API Errors
- Verify your Instagram Business Account is properly set up
- Check that your app is in development mode
- Ensure redirect URI matches exactly

#### 4. OpenAI API Errors
- Verify your API key is correct
- Check your OpenAI account has sufficient credits
- Ensure you're using the correct model

### Logs and Debugging

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Check service status
docker-compose ps
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### API Testing
Use the interactive API documentation at http://localhost:8000/docs

## 🚀 Production Deployment

### Environment Variables
Set these for production:
```env
DEBUG=False
SECRET_KEY=your-super-secure-secret-key
DATABASE_URL=your-production-database-url
REDIS_URL=your-production-redis-url
CORS_ORIGINS=["https://yourdomain.com"]
```

### Docker Production
```bash
# Build for production
docker-compose -f docker-compose.prod.yml up -d
```

### Database Migrations
```bash
# Run migrations in production
docker-compose exec backend alembic upgrade head
```

## 📊 Monitoring

### Health Checks
- Backend: http://localhost:8000/health
- Database: Check docker-compose logs postgres

### Performance
- Use Docker stats: `docker stats`
- Monitor logs for errors
- Check API response times in browser dev tools

## 🔐 Security Considerations

### Development
- Never commit `.env` files
- Use strong passwords for database
- Keep API keys secure

### Production
- Use HTTPS
- Set secure CORS origins
- Use managed database services
- Regular security updates
- Monitor for suspicious activity

## 📞 Support

If you encounter issues:
1. Check this troubleshooting guide
2. Review the logs for error messages
3. Check the GitHub issues
4. Contact support at support@socivio.com
