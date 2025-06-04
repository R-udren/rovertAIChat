# rovertChat Backend

This is the backend API service for rovertChat, a self-hosted AI chat platform built with FastAPI and Python.

## 🚀 Features

- **FastAPI Framework**: High-performance async web framework
- **PostgreSQL Database**: Robust data persistence with SQLAlchemy ORM
- **JWT Authentication**: Secure user authentication with refresh tokens
- **Role-Based Access Control**: Admin, User, and Guest roles
- **Ollama Integration**: Direct integration with local LLM models
- **User Management**: Complete user lifecycle management
- **Model Management**: Admin controls for Ollama model deployment

## 🛠️ Tech Stack

- **Python 3.9+**
- **FastAPI**: Modern web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **PostgreSQL**: Primary database
- **Pydantic**: Data validation using Python type annotations
- **JWT**: JSON Web Tokens for authentication
- **UV**: Fast Python package installer and resolver
- **Docker**: Containerization support

## 📁 Project Structure

```
backend/
├── src/
│   ├── main.py              # Application entry point
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection and session management
│   ├── models/              # SQLAlchemy database models
│   │   ├── __init__.py
│   │   ├── user.py          # User model
│   │   ├── chat.py          # Chat and message models
│   │   └── settings.py      # User settings model
│   ├── schemas/             # Pydantic schemas for request/response
│   │   ├── __init__.py
│   │   ├── user.py          # User schemas
│   │   ├── chat.py          # Chat schemas
│   │   └── auth.py          # Authentication schemas
│   ├── routers/             # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── users.py         # User management endpoints
│   │   ├── chat.py          # Chat endpoints
│   │   ├── ollama.py        # Ollama integration endpoints
│   │   └── admin.py         # Admin-only endpoints
│   ├── services/            # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py  # Authentication logic
│   │   ├── user_service.py  # User management logic
│   │   ├── chat_service.py  # Chat functionality
│   │   └── ollama_service.py # Ollama API integration
│   └── utils/               # Utility functions
│       ├── __init__.py
│       ├── security.py      # Password hashing, JWT handling
│       └── dependencies.py  # FastAPI dependencies
├── tests/                   # Test suite
├── logs/                    # Application logs
├── .env.dev                 # Development environment variables
├── pyproject.toml           # Project dependencies and metadata
├── Dockerfile               # Docker container configuration
└── README.md                # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- PostgreSQL database
- UV package manager (recommended)

### Installation

1. **Clone the repository** (if not already done):

   ```bash
   git clone https://github.com/R-udren/rovertAIChat.git
   cd rovertAIChat/backend
   ```

2. **Install UV** (if not already installed):

   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Windows (PowerShell)
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

3. **Install dependencies**:

   ```bash
   uv sync
   ```

4. **Set up environment variables**:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your configuration:

   ```bash
   # Database
   DATABASE_URL=postgresql://username:password@localhost:5432/rovertchat

   # JWT Configuration
   JWT_SECRET_KEY=your-super-secret-jwt-key-here
   JWT_REFRESH_SECRET_KEY=your-super-secret-refresh-key-here
   JWT_ALGORITHM=HS256
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
   JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

   # CORS
   FRONTEND_ORIGINS=["http://localhost:3000", "https://localhost"]

   # Ollama
   OLLAMA_BASE_URL=http://host.docker.internal:11434
   ```

5. **Set up the database**:

   ```bash
   # Start PostgreSQL (using Docker)
   docker run -d --name postgres \
     -e POSTGRES_PASSWORD=your_password \
     -e POSTGRES_DB=rovertchat \
     -p 5432:5432 postgres:17-alpine
   ```

6. **Start the development server**:
   ```bash
   fastapi run src/main.py
   ```

The API will be available at `http://localhost:8000`

## 🔧 Configuration

### Environment Variables

| Variable                          | Description                   | Default                  |
| --------------------------------- | ----------------------------- | ------------------------ |
| `DATABASE_URL`                    | PostgreSQL connection string  | Required                 |
| `JWT_SECRET_KEY`                  | Secret key for JWT tokens     | Required                 |
| `JWT_REFRESH_SECRET_KEY`          | Secret key for refresh tokens | Required                 |
| `JWT_ALGORITHM`                   | JWT algorithm                 | `HS256`                  |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiry           | `30`                     |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS`   | Refresh token expiry          | `7`                      |
| `FRONTEND_ORIGINS`                | Allowed CORS origins          | `[]`                     |
| `OLLAMA_BASE_URL`                 | Ollama API endpoint           | `http://localhost:11434` |
| `LOG_LEVEL`                       | Logging level                 | `INFO`                   |

## 📚 API Documentation

Once the server is running, you can access:

- **Interactive API docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative API docs (ReDoc)**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Main Endpoints

#### Authentication

- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - User logout

#### Users

- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update user profile
- `GET /users/me/settings` - Get user settings
- `PUT /users/me/settings` - Update user settings

#### Chat

- `GET /chat/conversations` - List user conversations
- `POST /chat/conversations` - Create new conversation
- `GET /chat/conversations/{id}/messages` - Get conversation messages
- `POST /chat/conversations/{id}/messages` - Send message
- `DELETE /chat/conversations/{id}` - Delete conversation

#### Ollama Integration

- `GET /ollama/tags` - List available models
- `POST /ollama/chat` - Chat with Ollama model
- `POST /ollama/pull` - Pull new model (admin only)
- `DELETE /ollama/delete` - Delete model (admin only)

## 🐳 Docker

### Build the image:

```bash
docker build -t rovertchat-backend .
```

### Run with Docker Compose:

```bash
# From the project root
docker-compose up backend
```

## 🔒 Security

- **Password Hashing**: Using bcrypt for secure password storage
- **JWT Tokens**: Stateless authentication with access and refresh tokens
- **CORS Protection**: Configurable cross-origin request handling
- **Input Validation**: Pydantic schemas for request validation
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection

## 📝 Development

## 🚀 Production Deployment

### Environment Setup

1. Set production environment variables
2. Use a production-grade PostgreSQL instance
3. Configure proper logging
4. Set up reverse proxy (nginx)
5. Use HTTPS certificates

### Performance Optimization

- Enable database connection pooling
- Configure appropriate worker processes
- Set up caching where appropriate
- Monitor performance metrics

## 🛠️ Troubleshooting

### Common Issues

**Database Connection Errors**:

- Verify PostgreSQL is running
- Check DATABASE_URL format
- Ensure database exists

**JWT Token Issues**:

- Verify JWT_SECRET_KEY is set
- Check token expiration settings
- Ensure clock synchronization

**Ollama Connection Problems**:

- Verify Ollama is running
- Check OLLAMA_BASE_URL setting
- Test network connectivity

### Logging

Logs are written to `logs/` directory:

- `app.log` - Application logs

Adjust log level in environment:

```bash
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
```
