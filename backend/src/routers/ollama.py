import os
from datetime import datetime

import aiohttp
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.auth.service import get_current_active_admin, get_current_active_user
from src.core.logger import app_logger
from src.database import get_db
from src.models.chat_models import Chat, Message, Model
from src.models.user import User
from src.schemas.chat import (
    ModelName,
    OllamaChatRequest,
    OllamaModelsWithCapabilitiesResponse,
    OllamaShowResponse,
)

# Router for Ollama API integration
router = APIRouter(prefix="/ollama", tags=["ollama"])

# Base URL for local Ollama instance
OLLAMA_API_BASE_URL = os.getenv("OLLAMA_API_BASE_URL", "http://localhost:11434")
app_logger.info(f"Using Ollama API base URL: {OLLAMA_API_BASE_URL}")


@router.get("/version")
async def get_ollama_version():
    """
    Retrieve the version of the Ollama API.
    Returns: {"version": "0.8.0"}
    """
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{OLLAMA_API_BASE_URL}/api/version") as resp:
                resp.raise_for_status()
                return await resp.json()
        except aiohttp.ClientError as e:
            raise HTTPException(status_code=502, detail=str(e))


@router.get("/tags", response_model=OllamaModelsWithCapabilitiesResponse)
async def get_ollama_tags_with_capabilities(
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve available Ollama model tags with their capabilities.
    """
    app_logger.info(f"User {current_user.id} requested Ollama tags with capabilities")
    try:
        async with aiohttp.ClientSession() as session:
            app_logger.info(
                f"Fetching Ollama tags from API: {OLLAMA_API_BASE_URL}/api/tags"
            )

            # First, get the tags/models list
            async with session.get(f"{OLLAMA_API_BASE_URL}/api/tags") as resp:
                resp.raise_for_status()
                tags_data = await resp.json()

            # Now fetch capabilities for each model
            models_with_capabilities = []
            for model in tags_data.get("models", []):
                model_name = model["name"]
                app_logger.info(f"Fetching capabilities for model: {model_name}")

                try:
                    # Get model show info to extract capabilities
                    async with session.post(
                        f"{OLLAMA_API_BASE_URL}/api/show", json={"name": model_name}
                    ) as show_resp:
                        show_resp.raise_for_status()
                        show_data = await show_resp.json()

                        # Extract capabilities
                        capabilities = show_data.get("capabilities", [])

                        # Create enhanced model object
                        enhanced_model = {
                            "name": model["name"],
                            "model": model["model"],
                            "modified_at": model["modified_at"],
                            "size": model["size"],
                            "digest": model["digest"],
                            "details": model["details"],
                            "capabilities": capabilities,
                        }
                        models_with_capabilities.append(enhanced_model)

                except Exception as model_error:
                    app_logger.warning(
                        f"Failed to fetch capabilities for model {model_name}: {str(model_error)}"
                    )
                    # Add model without capabilities if show fails
                    enhanced_model = {
                        "name": model["name"],
                        "model": model["model"],
                        "modified_at": model["modified_at"],
                        "size": model["size"],
                        "digest": model["digest"],
                        "details": model["details"],
                        "capabilities": [],
                    }
                    models_with_capabilities.append(enhanced_model)

            return {"models": models_with_capabilities}

    except aiohttp.ClientError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        app_logger.error(
            f"Unexpected error fetching Ollama tags with capabilities: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/show", response_model=OllamaShowResponse)
async def show_ollama_model(
    model: ModelName, current_user: User = Depends(get_current_active_user)
):
    """
    Show information about Ollama model.
    """
    app_logger.info(
        f"User {current_user.id} requested Ollama model details for {model.model}"
    )
    payload = model.model_dump(mode="json")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{OLLAMA_API_BASE_URL}/api/show", json=payload
            ) as resp:
                resp.raise_for_status()
                return await resp.json()
        except aiohttp.ClientError as e:
            app_logger.error(
                f"Error fetching Ollama model details: {str(e)}", exc_info=True
            )
            raise HTTPException(status_code=502, detail=str(e))
        except Exception as e:
            app_logger.error(
                f"Unexpected error fetching Ollama models: {str(e)}", exc_info=True
            )
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {str(e)}"
            )


@router.post("/pull")
async def pull_ollama_model(
    model: ModelName, admin_user: User = Depends(get_current_active_admin)
):
    """
    Pull an Ollama model by name.
    Expects JSON body: { "model": "model_name" }
    """

    if not admin_user.is_admin():
        raise HTTPException(
            status_code=403, detail="You do not have permission to perform this action."
        )

    payload = model.model_dump(mode="json")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{OLLAMA_API_BASE_URL}/api/pull", json=payload
            ) as resp:
                resp.raise_for_status()
                return await resp.text()
        except aiohttp.ClientError as e:
            raise HTTPException(status_code=502, detail=str(e))


@router.delete("/delete")
async def delete_ollama_model(
    model: ModelName,
    admin_user: User = Depends(get_current_active_admin),
):
    """
    Delete an Ollama model by name.
    Expects JSON body: { "model": "model_name" }
    """
    if not admin_user.is_admin():
        raise HTTPException(
            status_code=403, detail="You do not have permission to perform this action."
        )

    payload = model.model_dump(mode="json")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.delete(
                f"{OLLAMA_API_BASE_URL}/api/delete", json=payload
            ) as resp:
                resp.raise_for_status()
                return {"message": "Model deleted successfully"}
        except aiohttp.ClientError as e:
            raise HTTPException(status_code=502, detail=str(e))


@router.post("/chat")
async def chat_ollama(
    chat_request: OllamaChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Asynchronously get chat responses from an Ollama model.
    """
    try:
        # Verify chat belongs to the user
        chat = (
            db.query(Chat)
            .filter(Chat.id == chat_request.chatId, Chat.user_id == current_user.id)
            .first()
        )

        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        # Save the user message to the database
        latest_user_message = next(
            (msg for msg in reversed(chat_request.messages) if msg.role == "user"), None
        )

        if latest_user_message:
            user_db_message = Message(
                chat_id=chat_request.chatId,
                role="user",
                content=latest_user_message.content,
                images=latest_user_message.images,  # Store base64 images
            )
            db.add(user_db_message)
            db.commit()
            db.refresh(user_db_message)  # Make request to Ollama
        payload = chat_request.model_dump(mode="json")

        # Use aiohttp session to make request to Ollama
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{OLLAMA_API_BASE_URL}/api/chat",
                json=payload,
            ) as response:
                if response.status >= 400:
                    response_text = await response.text()
                    app_logger.error(
                        f"Ollama API error: {response.status}, {response_text}"
                    )
                    return {
                        "error": f"Ollama API error: {response.status}",
                        "details": response_text,
                    }

                response_data = await response.json()
        app_logger.info(f"Chat response: {response_data}")  # Snitching ai responses :)

        # Save the assistant message to the database
        if (
            "message" in response_data
            and response_data.get("message", {}).get("role") == "assistant"
        ):
            # Look up model from the database based on name
            model = db.query(Model).filter(Model.name == chat_request.model).first()
            model_id = model.id if model else None

            assistant_db_message = Message(
                chat_id=chat_request.chatId,
                role="assistant",
                content=response_data["message"]["content"],
                model_id=model_id,
                tokens_used=response_data.get("eval_count", 0),
                extended_metadata={
                    "prompt_eval_count": response_data.get("prompt_eval_count", 0),
                    "eval_count": response_data.get("eval_count", 0),
                    "eval_duration": response_data.get("eval_duration", 0),
                },
            )
            db.add(assistant_db_message)

            # Update the chat's updated_at timestamp
            setattr(chat, "updated_at", datetime.now())

            # Auto-generate chat title from first user message if it's still "New Chat"
            message_count = db.query(Message).filter(Message.chat_id == chat.id).count()
            if (
                str(chat.title) == "New Chat" and message_count <= 2
            ):  # First user message + assistant response
                # Get the user message (first message)
                user_message = (
                    latest_user_message.content if latest_user_message else ""
                )
                # Create a title from the first ~30 characters of user message
                if user_message:
                    new_title = user_message[:30].strip()
                    if len(user_message) > 30:
                        new_title += "..."
                    setattr(chat, "title", new_title)
                    app_logger.info(
                        f"Auto-generated title for chat {chat.id}: {new_title}"
                    )

            db.commit()
            db.refresh(assistant_db_message)

            # Set the ID in the response
            response_data["id"] = str(assistant_db_message.id)

            # Include updated chat data in response
            response_data["chat"] = {"id": str(chat.id), "title": chat.title}
        else:
            app_logger.error(f"Unexpected response format from Ollama: {response_data}")
            if "error" in response_data:
                return {
                    "error": "Ollama API error",
                    "details": response_data.get("error"),
                }
            return {"error": "Invalid response format from Ollama model"}

        return response_data

    except aiohttp.ClientError as e:
        app_logger.error(f"Error connecting to Ollama API: {str(e)}")
        raise HTTPException(
            status_code=502, detail=f"Error connecting to Ollama API: {str(e)}"
        )
    except Exception as e:
        app_logger.error(f"Unexpected error in chat_ollama: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
