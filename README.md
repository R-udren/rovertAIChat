# rovertChat ( ͡° ͜ʖ ͡°)

**rovertChat** is a feature-poor, self-hosted AI platform that prioritizes privacy and user experience. It seamlessly integrates with LLM runners like Ollama and supports OpenAI-compatible APIs, giving you complete control over your AI interactions.

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

To Be Determined...

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
