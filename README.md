# rovertChat ( ͡° ͜ʖ ͡°)

[![GitHub Repository](https://img.shields.io/badge/GitHub-rovertAIChat-blue?style=for-the-badge&logo=github)](https://github.com/R-udren/rovertAIChat)
[![Stars](https://img.shields.io/github/stars/R-udren/rovertAIChat?style=for-the-badge)](https://github.com/R-udren/rovertAIChat/stargazers)
[![License](https://img.shields.io/github/license/R-udren/rovertAIChat?style=for-the-badge)](https://github.com/R-udren/rovertAIChat/blob/main/LICENSE)
[![Issues](https://img.shields.io/github/issues/R-udren/rovertAIChat?style=for-the-badge)](https://github.com/R-udren/rovertAIChat/issues)

**rovertChat** is a powerful, self-hosted AI platform that prioritizes privacy and user experience. It seamlessly integrates with LLM runners like Ollama and supports OpenAI-compatible APIs, giving you complete control over your AI interactions.

## 🚀 Key Features

- **Self-hosted & Privacy-focused**: Keep your data on your own infrastructure
- **Real-time AI chat**: Smooth, responsive conversations with AI models
- **Model flexibility**: Connect to various LLM backends (Ollama, OpenAI API compatible services)
- **Multi-user support**: Role-based access control (guest, user, admin)
- **Complete chat history**: All conversations securely stored and easily accessible
- **Responsive design**: Works on desktop and mobile devices
- **Authentication**: JWT-based secure authentication system
- **User profiles**: Personalize your experience with custom settings and preferences
- **Markdown support**: Write and render Markdown in chat

## 🔧 Technical Stack

- **Backend**: Python with FastAPI for API endpoints and real-time communication via Socket.IO
- **Frontend**: Vue.js with Tailwind CSS 4 for a modern, responsive UI and Markdown support with Bun as the build tool
- **Database**: PostgreSQL/SQLite database for storing user auth, user profiles, chat history, and configurations

## 🛠️ Installation

### Prerequisites

Before getting started, ensure you have the following installed:

- **Docker & Docker Compose**: For containerized deployment
- **Git**: To clone the repository
- **Ollama** (optional): For local LLM hosting

### Quick Start with Docker 🐳

1. **Clone the repository**

   ```bash
   git clone https://github.com/R-udren/rovertAIChat.git
   cd rovertAIChat
   ```

2. **Set up environment variables**

   ```bash
   cp .env.example .env
   ```

3. **Configure your environment**
   Edit the `.env` file with your settings:

   ```bash
   # Database Configuration
   DATABASE_PASSWORD=your_secure_password

   # Domain Configuration
   DOMAIN=localhost  # or your domain name
   FRONTEND_ORIGINS=https://localhost  # or https://yourdomain.com
   VITE_API_BASE_URL=https://localhost  # or https://yourdomain.com

   # JWT Configuration (generate secure random strings)
   JWT_SECRET_KEY=your_super_secret_jwt_key_here
   JWT_REFRESH_SECRET_KEY=your_super_secret_refresh_key_here
   ```

4. **SSL Certificates Setup**

   For **local development**:

   ```bash
   # Create self-signed certificates for localhost
   mkdir -p frontend/certs
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout frontend/certs/privkey.pem \
     -out frontend/certs/fullchain.pem \
     -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
   ```

   For **production** with Let's Encrypt:

   ```bash
   # Use certbot to get real certificates
   sudo certbot certonly --standalone -d yourdomain.com

   # Copy certificates to the project
   sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem frontend/certs/
   sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem frontend/certs/
   sudo cp /etc/letsencrypt/live/yourdomain.com/cert.pem frontend/certs/
   sudo cp /etc/letsencrypt/live/yourdomain.com/chain.pem frontend/certs/
   ```

5. **Build and run the application**

   ```bash
   docker-compose up --build -d
   ```

6. **Access the application**
   - **Frontend**: https://localhost (or your domain)
   - **Backend API**: https://localhost/api/docs
   - **Database**: localhost:5432 (PostgreSQL)

### Local Development Setup 💻

If you prefer to run the services individually for development:

#### Backend Setup

1. **Install Python dependencies**

   ```bash
   cd backend
   pip install uv
   uv sync
   ```

2. **Set up the database**

   ```bash
   # Start PostgreSQL with Docker
   docker run -d --name postgres \
     -e POSTGRES_PASSWORD=your_password \
     -e POSTGRES_DB=postgres \
     -p 5432:5432 postgres:17-alpine
   ```

3. **Run the backend**
   ```bash
   uv run python src/main.py
   ```

#### Frontend Setup

1. **Install Bun** (if not already installed)

   ```bash
   # Windows (PowerShell)
   powershell -c "irm bun.sh/install.ps1 | iex"

   # macOS/Linux
   curl -fsSL https://bun.sh/install | bash
   ```

2. **Install dependencies and run**
   ```bash
   cd frontend
   bun install
   bun run dev
   ```

### Setting up Ollama Integration 🦙

To use local LLMs with Ollama:

1. **Install Ollama**

   ```bash
   # Windows/macOS/Linux
   # Visit https://ollama.ai and download the installer
   ```

2. **Pull some models**

   ```bash
   ollama pull llama3.2
   ollama pull mistral
   ollama pull codellama
   ```

3. **Configure the backend**
   The backend is already configured to connect to Ollama at `http://host.docker.internal:11434`

### Environment Variables Reference 📋

| Variable                 | Description               | Example                         |
| ------------------------ | ------------------------- | ------------------------------- |
| `DATABASE_PASSWORD`      | PostgreSQL password       | `your_secure_password`          |
| `DOMAIN`                 | Your domain name          | `localhost` or `yourdomain.com` |
| `FRONTEND_ORIGINS`       | CORS origins for frontend | `https://localhost`             |
| `VITE_API_BASE_URL`      | API base URL for frontend | `https://localhost`             |
| `JWT_SECRET_KEY`         | JWT signing key           | `your_super_secret_key`         |
| `JWT_REFRESH_SECRET_KEY` | JWT refresh token key     | `your_refresh_secret_key`       |

### Troubleshooting 🔧

**Common Issues:**

- **SSL Certificate errors**: Make sure your certificates are properly placed in `frontend/certs/`
- **Database connection issues**: Verify PostgreSQL is running and credentials are correct
- **Ollama not accessible**: Ensure Ollama is running on the host machine
- **CORS errors**: Check that `FRONTEND_ORIGINS` matches your domain

**Useful Commands:**

```bash
# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Rebuild after code changes
docker-compose up --build

# Stop all services
docker-compose down

# Reset database
docker-compose down -v && docker-compose up -d
```

## 🔐 Role-Based Access

rovertChat implements three user roles:

- **Guest**: Can interact with AI models in a very limited session
- **User**: Has persistent chat history and personalized settings
- **Admin**: Can upload and manage LLM models, configure system settings, and manage users

## 🌟 Upcoming Features

These features will be implemented in future releases:

- **Real-time Text-to-Speech and Speech-to-Text**: Voice interactions with AI
- **Advanced Markdown support**: Real-time rendering and code highlighting
- **Mermaid Diagramming**: Create and visualize diagrams directly in chat
- **Function Calling**: Execute external functions through chat commands
- **Image Generation**: Create images using text prompts

## 🖥️ Deployment Options

rovertChat is designed to be flexible in deployment:

- **Local development**: Run on your personal machine
- **Self-hosted server**: Deploy on your own server infrastructure
- **Docker containers**: Simple containerized deployment

## 🔒 Security Considerations

- **HTTPS**: SSL/TLS encryption is enabled by default
- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt for secure password storage
- **CORS Protection**: Configurable origin restrictions
- **Rate Limiting**: API rate limiting to prevent abuse
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries

## 📖 API Documentation

Once the backend is running, you can access the interactive API documentation:

- **Swagger UI**: `https://yourdomain.com/docs`
- **ReDoc**: `https://yourdomain.com/redoc`
- **OpenAPI Schema**: `https://yourdomain.com/openapi.json`

## 🧪 Testing

Run the test suite:

```bash
# Backend tests
cd backend
uv run pytest

# Frontend tests (when implemented)
cd frontend
bun test
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the [repository](https://github.com/R-udren/rovertAIChat)
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request on [GitHub](https://github.com/R-udren/rovertAIChat/pulls)

## 📝 Development Guidelines

- **Code Style**: Follow PEP 8 for Python, ESLint for JavaScript/Vue
- **Commit Messages**: Use conventional commit format
- **Testing**: Write tests for new features
- **Documentation**: Update documentation for API changes

## 🆘 Support

- **GitHub Repository**: [R-udren/rovertAIChat](https://github.com/R-udren/rovertAIChat)
- **Documentation**: Check this README and API docs
- **Issues**: [Report bugs and request features](https://github.com/R-udren/rovertAIChat/issues)
- **Discussions**: [Join community discussions](https://github.com/R-udren/rovertAIChat/discussions)

## 🙏 Acknowledgments

- **FastAPI**: For the excellent Python web framework
- **Vue.js**: For the reactive frontend framework
- **Ollama**: For making local LLM hosting accessible
- **PostgreSQL**: For reliable data storage
- **Tailwind CSS**: For beautiful, responsive styling

---

**Made with ❤️ for the self-hosting and privacy-conscious AI community**

_rovertChat - Where your AI conversations stay yours_ ( ͡° ͜ʖ ͡°)
