# MediDash - Quick Medicine Delivery Platform

## 🚀 Overview

MediDash is a full-stack, quick-commerce platform for rapid medicine delivery that enables users to search, upload prescriptions, order medicines, and get them delivered within 30 minutes. The platform serves customers, pharmacists, and delivery partners with real-time tracking and secure prescription management.

## 🎯 Key Features

- **10-30 minute medicine delivery**
- **Secure prescription management via Cloudinary**
- **Real-time inventory & delivery tracking using WebSockets**
- **Dynamic pricing & emergency support**
- **Elderly-friendly and accessible UX**
- **Compliance with prescription validation**

## 🏗️ Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT with phone verification
- **Media Storage**: Cloudinary
- **Real-time**: Native WebSockets
- **Notifications**: OneSignal

### Frontend
- **Framework**: React + Vite + TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Context/Redux Toolkit
- **Real-time**: WebSocket client
- **Maps**: Google Maps API

## 📁 Project Structure

```
e-med/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configurations
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utilities
│   ├── requirements.txt
│   └── main.py
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── hooks/          # Custom hooks
│   │   ├── services/       # API services
│   │   ├── utils/          # Utilities
│   │   └── types/          # TypeScript types
│   ├── package.json
│   └── vite.config.ts
├── docs/                   # Documentation
├── tests/                  # Test files
├── PRD.md                  # Product Requirements Document
├── TASK_LIST.md           # Development task list
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Git

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd e-med
   ```

2. **Set up Python environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Set up database**
   ```bash
   # Create PostgreSQL database
   createdb medidash_db
   
   # Run migrations
   alembic upgrade head
   ```

5. **Start the backend server**
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd ../frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API endpoints
   ```

4. **Start the development server**
   ```bash
   npm run dev
   ```

## 📋 Development Phases

### Phase 1: Foundation (MVP) - Weeks 1-4
- [x] Project setup and documentation
- [ ] Backend authentication system
- [ ] Medicine catalog
- [ ] Basic order management
- [x] Frontend setup and basic UI

### Phase 2: Prescription & Security - Weeks 5-8
- [ ] Cloudinary integration
- [ ] Prescription management
- [ ] Enhanced security features
- [ ] Role-based access control

### Phase 3: Real-time Features - Weeks 9-12
- [ ] WebSocket implementation
- [ ] Live order tracking
- [ ] Push notifications
- [ ] Delivery optimization

### Phase 4: Advanced Features - Weeks 13-16
- [ ] Emergency delivery system
- [ ] Analytics dashboard
- [ ] Performance optimization
- [ ] Production deployment

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://user:password@localhost/medidash_db

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Cloudinary
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Twilio (for phone verification)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=your-twilio-number

# OneSignal (for push notifications)
ONESIGNAL_APP_ID=your-app-id
ONESIGNAL_REST_API_KEY=your-rest-api-key
```

#### Frontend (.env)
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WEBSOCKET_URL=ws://localhost:8000/ws
VITE_GOOGLE_MAPS_API_KEY=your-google-maps-api-key
```

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest
```

### Frontend Testing
```bash
cd frontend
npm test
```

### E2E Testing
```bash
npm run test:e2e
```

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🚀 Deployment

### Backend Deployment
```bash
# Production build
pip install -r requirements.txt
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend Deployment
```bash
# Build for production
npm run build

# Serve static files
npm run preview
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the [docs/](docs/) folder
- **Issues**: Create an issue in the repository
- **Discussions**: Use GitHub Discussions for questions

## 🎯 Roadmap

- [ ] AI-powered prescription OCR
- [ ] Multi-city expansion
- [ ] Insurance integration
- [ ] Mobile app development
- [ ] International markets

---

**Built with ❤️ for better healthcare delivery** 