# Backend - FastAPI + Socket.IO

## API Structure

### API Endpoints

### Authentication Endpoints

- POST /api/v1/auths/signup - User registration
- POST /api/v1/auths/signin - User login
- POST /api/v1/auths/signout - User logout
- GET /api/v1/auths/ - Get current user session
- POST /api/v1/auths/update/password - Update user password
- POST /api/v1/auths/update/profile - Update user profile
- GET /api/v1/auths/api_key - Get API keys
- POST /api/v1/auths/api_key - Create API key
- DELETE /api/v1/auths/api_key - Delete API key

### User Management

- GET /api/v1/users/ - List all users
- GET /api/v1/users/{user_id} - Get user by ID
- POST /api/v1/users/update/role - Update user role
- DELETE /api/v1/users/{user_id} - Delete user
- POST /api/v1/auths/add - Add new user (admin only)

### Chat Management

#### Chat Endpoints

- GET /api/v1/chats/ - Get all chats
- GET /api/v1/chats/{chat_id} - Get chat by ID
- POST /api/v1/chats/ - Create new chat
- PUT /api/v1/chats/{chat_id} - Update chat
- DELETE /api/v1/chats/{chat_id} - Delete chat
- POST /api/v1/chats/{chat_id}/title - Generate chat title
- POST /api/v1/chats/{chat_id}/pin - Pin chat
- POST /api/v1/chats/{chat_id}/unpin - Unpin chat

#### Message Endpoints

- GET /api/v1/chats/{chat_id}/messages - Get messages for a chat
- POST /api/v1/chats/{chat_id}/messages - Add message to chat
- DELETE /api/v1/chats/{chat_id}/messages/{message_id} - Delete message
- PUT /api/v1/chats/{chat_id}/messages/{message_id} - Update message

### Model Management

#### Ollama Model Endpoints

- GET /ollama/api/tags - Get Ollama models
- POST /ollama/api/pull - Pull Ollama model
- DELETE /ollama/api/delete - Delete Ollama model
- POST /ollama/api/generate - Generate with Ollama
- POST /ollama/api/chat - Chat with Ollama
