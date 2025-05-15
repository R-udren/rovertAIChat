# rovertChat Database Schema

This document outlines the database schema for the rovertChat application, including tables, fields, and their relationships.

## Database Tables

### Users

| Column        | Type         | Description                 |
| ------------- | ------------ | --------------------------- |
| id            | UUID         | Primary key                 |
| username      | VARCHAR(100) | Unique username             |
| email         | VARCHAR(255) | User email address          |
| password_hash | VARCHAR(255) | Hashed password             |
| role          | ENUM         | 'guest', 'user', or 'admin' |
| created_at    | TIMESTAMP    | Account creation time       |
| last_login    | TIMESTAMP    | Last login time             |
| is_active     | BOOLEAN      | Account status              |

### ModelProviders

| Column     | Type         | Description                              |
| ---------- | ------------ | ---------------------------------------- |
| id         | UUID         | Primary key                              |
| name       | VARCHAR(100) | Provider name (e.g., 'Ollama', 'OpenAI') |
| api_url    | VARCHAR(255) | Base URL for API requests                |
| auth_type  | VARCHAR(50)  | Authentication method                    |
| created_by | UUID         | Admin who added this provider            |
| created_at | TIMESTAMP    | Creation time                            |
| is_active  | BOOLEAN      | Provider status                          |

### Models

| Column       | Type         | Description                   |
| ------------ | ------------ | ----------------------------- |
| id           | UUID         | Primary key                   |
| provider_id  | UUID         | Foreign key to ModelProviders |
| name         | VARCHAR(100) | Model name                    |
| display_name | VARCHAR(100) | User-friendly name            |
| description  | TEXT         | Model description             |
| config       | JSONB        | Model-specific configuration  |
| created_at   | TIMESTAMP    | When model was added          |
| updated_at   | TIMESTAMP    | Last update time              |
| is_active    | BOOLEAN      | Model availability            |

### Chats

| Column      | Type         | Description          |
| ----------- | ------------ | -------------------- |
| id          | UUID         | Primary key          |
| user_id     | UUID         | Foreign key to Users |
| title       | VARCHAR(255) | Chat title           |
| created_at  | TIMESTAMP    | Creation time        |
| updated_at  | TIMESTAMP    | Last activity time   |
| is_archived | BOOLEAN      | Archive status       |

### Messages

| Column      | Type        | Description                                   |
| ----------- | ----------- | --------------------------------------------- |
| id          | UUID        | Primary key                                   |
| chat_id     | UUID        | Foreign key to Chats                          |
| role        | VARCHAR(50) | 'user' or 'assistant'                         |
| content     | TEXT        | Message content                               |
| model_id    | UUID        | Foreign key to Models (which model responded) |
| created_at  | TIMESTAMP   | Message timestamp                             |
| tokens_used | INTEGER     | Token count for this message                  |
| metadata    | JSONB       | Additional message metadata                   |

### UserSettings

| Column           | Type         | Description                             |
| ---------------- | ------------ | --------------------------------------- |
| user_id          | UUID         | Primary key, Foreign key to Users       |
| default_model_id | UUID         | Preferred model (Foreign key to Models) |
| display_name     | VARCHAR(100) | Custom display name                     |
| avatar_url       | VARCHAR(255) | Profile picture URL                     |
| preferences      | JSONB        | Other user preferences                  |

### UserModelAccess

| Column     | Type      | Description              |
| ---------- | --------- | ------------------------ |
| id         | UUID      | Primary key              |
| user_id    | UUID      | Foreign key to Users     |
| model_id   | UUID      | Foreign key to Models    |
| granted_by | UUID      | Admin who granted access |
| granted_at | TIMESTAMP | When access was granted  |
| is_active  | BOOLEAN   | Access status            |

## Database Diagram (Mermaid)

```mermaid
erDiagram
    Users ||--o{ Chats : "creates"
    Users ||--|| UserSettings : "has"
    Users ||--o{ UserModelAccess : "has access to"
    Users ||--o{ ModelProviders : "creates"

    ModelProviders ||--o{ Models : "provides"

    Models ||--o{ Messages : "generates"
    Models ||--o{ UserModelAccess : "accessible to"

    Chats ||--o{ Messages : "contains"

    Users {
        UUID id PK
        string username
        string email
        string password_hash
        enum role
        timestamp created_at
        timestamp last_login
        boolean is_active
    }

    ModelProviders {
        UUID id PK
        string name
        string api_url
        string auth_type
        UUID created_by FK
        timestamp created_at
        boolean is_active
    }

    Models {
        UUID id PK
        UUID provider_id FK
        string name
        string display_name
        text description
        jsonb config
        timestamp created_at
        timestamp updated_at
        boolean is_active
    }

    Chats {
        UUID id PK
        UUID user_id FK
        string title
        timestamp created_at
        timestamp updated_at
        boolean is_archived
    }

    Messages {
        UUID id PK
        UUID chat_id FK
        string role
        text content
        UUID model_id FK
        timestamp created_at
        integer tokens_used
        jsonb metadata
    }

    UserSettings {
        UUID user_id PK,FK
        UUID default_model_id FK
        string display_name
        string avatar_url
        jsonb preferences
    }

    UserModelAccess {
        UUID id PK
        UUID user_id FK
        UUID model_id FK
        UUID granted_by FK
        timestamp granted_at
        boolean is_active
    }
```

## Key Database Features

1. **UUID Primary Keys**: For scalability and security
2. **Timestamps**: All relevant tables have creation and modification timestamps
3. **JSONB Fields**: For flexible storage of configuration and preferences
4. **Role-Based Access**: User roles and model access permissions
5. **Archiving**: Soft deletion for chats and messages
6. **Provider Flexibility**: Support for different LLM providers
7. **Token Tracking**: For usage monitoring and potential billing

## Indexes and Performance Considerations

- Index on `Users.username` and `Users.email` for fast lookups
- Index on `Messages.chat_id` for quick chat history retrieval
- Index on `Chats.user_id` for user's chat listing
- Index on `UserModelAccess.user_id` and `UserModelAccess.model_id` for permission checks

## Authentication

The system uses JWT-based authentication with password hashing for security.
