import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from src.auth.service import get_current_active_admin, get_current_active_user
from src.core.logger import app_logger
from src.database import get_db
from src.models.chat_models import Chat, Message, Model
from src.models.user import User

# Router for Ollama API integration
router = APIRouter(prefix="/ollama", tags=["ollama"])

# Base URL for local Ollama instance
OLLAMA_API_BASE_URL = os.getenv("OLLAMA_API_BASE_URL", "http://localhost:11434")
app_logger.info(f"Using Ollama API base URL: {OLLAMA_API_BASE_URL}")


@router.get("/version")
async def get_ollama_version():
    """
    Retrieve the version of the Ollama API.
    """
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{OLLAMA_API_BASE_URL}/api/version")
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=str(e))


@router.get("/tags")
async def get_ollama_tags(current_user: User = Depends(get_current_active_user)):
    """
    Retrieve available Ollama model tags.
    """
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{OLLAMA_API_BASE_URL}/api/tags")
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=str(e))


@router.post("/pull")
async def pull_ollama_model(
    request: Request, admin_user: User = Depends(get_current_active_admin)
):
    """
    Pull an Ollama model by name.
    Expects JSON body: { "model": "model_name" }
    """

    if not admin_user.is_admin:
        raise HTTPException(
            status_code=403, detail="You do not have permission to perform this action."
        )

    payload = await request.json()
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(f"{OLLAMA_API_BASE_URL}/api/pull", json=payload)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=str(e))


@router.delete("/delete")
async def delete_ollama_model(
    request: Request,
    admin_user: User = Depends(get_current_active_admin),
):
    """
    Delete an Ollama model by name.
    Expects JSON body: { "model": "model_name" }
    """
    if not admin_user.is_admin:
        raise HTTPException(
            status_code=403, detail="You do not have permission to perform this action."
        )

    payload = await request.json()
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.request(
                "DELETE", f"{OLLAMA_API_BASE_URL}/api/delete", json=payload
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=str(e))


@router.post("/generate")
async def generate_ollama(request: Request):
    """
    Stream generation from an Ollama model.
    Expects JSON with "model", "prompt", and optionally other parameters.
    """
    payload = await request.json()
    payload["stream"] = True

    async def generate_stream():
        async with httpx.AsyncClient(timeout=None) as client:
            try:
                async with client.stream(
                    "POST", f"{OLLAMA_API_BASE_URL}/api/generate", json=payload
                ) as resp:
                    resp.raise_for_status()
                    async for chunk in resp.aiter_raw():
                        if chunk:
                            yield chunk
            except httpx.HTTPError as e:
                yield f"[error] {str(e)}".encode()

    return StreamingResponse(generate_stream(), media_type="application/octet-stream")


class ChatMessage(BaseModel):
    role: str = Field(
        ..., description="Role of the message sender (e.g., 'user', 'assistant')"
    )
    content: str = Field(..., description="Content of the message")


class OllamaChatRequest(BaseModel):
    model: str = Field(..., description="Name of the Ollama model to use")
    messages: List[ChatMessage] = Field(
        ..., description="List of conversation messages"
    )
    stream: Optional[bool] = Field(False, description="Whether to stream the response")
    options: Optional[Dict[str, Any]] = Field(
        None, description="Additional model options"
    )
    chatId: UUID = Field(..., description="ID of the chat this message belongs to")


@router.post("/chat")
async def chat_ollama(
    request: OllamaChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Stream or get instant chat responses from an Ollama model.
    """
    # Verify chat belongs to the user
    chat = (
        db.query(Chat)
        .filter(Chat.id == request.chatId, Chat.user_id == current_user.id)
        .first()
    )

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Save the user message to the database
    latest_user_message = next(
        (msg for msg in reversed(request.messages) if msg.role == "user"), None
    )

    if latest_user_message:
        user_db_message = Message(
            chat_id=request.chatId,
            role="user",
            content=latest_user_message.content,
        )
        db.add(user_db_message)
        db.commit()
        db.refresh(user_db_message)

    # Make request to Ollama
    payload = request.model_dump(mode="json")
    app_logger.info(f"Chat request: {payload}")

    with httpx.Client(timeout=None) as client:
        response = client.post(
            f"{OLLAMA_API_BASE_URL}/api/chat",
            json=payload,
        )
        response_data = response.json()
        app_logger.info(f"Chat response: {response_data}")

    # Save the assistant message to the database
    if "message" in response_data and response_data["message"]["role"] == "assistant":
        # Look up model from the database based on name
        model = db.query(Model).filter(Model.name == request.model).first()

        assistant_db_message = Message(
            chat_id=request.chatId,
            role="assistant",
            content=response_data["message"]["content"],
            model_id=model.id if model else None,
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

        db.commit()
        db.refresh(assistant_db_message)

        # Set the ID in the response
        response_data["id"] = str(assistant_db_message.id)

    return response_data


@router.post("/chat/stream")
async def stream_chat_ollama(
    request: OllamaChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Stream chat responses from an Ollama model and save messages to database (POST method).
    """
    # Verify chat belongs to the user
    chat = (
        db.query(Chat)
        .filter(Chat.id == request.chatId, Chat.user_id == current_user.id)
        .first()
    )

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Save the user message to the database
    latest_user_message = next(
        (msg for msg in reversed(request.messages) if msg.role == "user"), None
    )

    if latest_user_message:
        user_db_message = Message(
            chat_id=request.chatId,
            role="user",
            content=latest_user_message.content,
        )
        db.add(user_db_message)
        db.commit()
        db.refresh(user_db_message)

    # Set up streaming
    payload = request.model_dump(mode="json")
    payload["stream"] = True
    app_logger.info(f"Stream chat request: {payload}")

    # Create a placeholder for the assistant's message
    assistant_db_message = Message(
        chat_id=request.chatId,
        role="assistant",
        content="",  # Will be updated as the stream progresses
    )
    db.add(assistant_db_message)
    db.commit()
    db.refresh(assistant_db_message)

    message_id = str(assistant_db_message.id)
    accumulated_content = []

    async def generate_stream():
        nonlocal accumulated_content

        async with httpx.AsyncClient(timeout=None) as client:
            try:
                async with client.stream(
                    "POST", f"{OLLAMA_API_BASE_URL}/api/chat", json=payload
                ) as resp:
                    resp.raise_for_status()

                    async for chunk in resp.aiter_text():
                        try:
                            chunk_data = json.loads(chunk)
                            content = chunk_data.get("message", {}).get("content", "")

                            if content:
                                accumulated_content.append(content)
                                yield f"data: {json.dumps({'id': message_id, 'content': content})}\n\n"

                            # Check if this is the final chunk (done=true)
                            if chunk_data.get("done", False):
                                # Update the database with the complete message
                                full_content = "".join(accumulated_content)
                                app_logger.info(
                                    f"Completed message: {full_content[:100]}..."
                                )

                                # Update the message in the database
                                db.query(Message).filter(
                                    Message.id == UUID(message_id)
                                ).update(
                                    {
                                        "content": full_content,
                                        "tokens_used": chunk_data.get("eval_count", 0),
                                        "extended_metadata": {
                                            "prompt_eval_count": chunk_data.get(
                                                "prompt_eval_count", 0
                                            ),
                                            "eval_count": chunk_data.get(
                                                "eval_count", 0
                                            ),
                                            "eval_duration": chunk_data.get(
                                                "eval_duration", 0
                                            ),
                                        },
                                    }
                                )
                                # Update chat timestamp
                                setattr(chat, "updated_at", datetime.now())
                                db.commit()

                                # Send the "done" event
                                yield f"data: {json.dumps({'done': True, 'id': message_id})}\n\n"
                        except json.JSONDecodeError:
                            app_logger.error(f"Failed to parse JSON chunk: {chunk}")
                            continue
                        except Exception as e:
                            app_logger.error(f"Error processing chunk: {str(e)}")
                            continue
            except httpx.HTTPError as e:
                error_msg = f"Error from Ollama API: {str(e)}"
                app_logger.error(error_msg)
                yield f"data: {json.dumps({'error': error_msg})}\n\n"
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                app_logger.error(error_msg)
                yield f"data: {json.dumps({'error': error_msg})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        },
    )


@router.get("/chat/stream")
async def stream_chat_ollama_get(
    payload: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Stream chat responses from an Ollama model and save messages to database (GET method).
    This endpoint is designed for EventSource/SSE connections from the frontend.
    """
    try:
        # Parse the payload from query param
        request_data = json.loads(payload)

        # Convert to our model
        request = OllamaChatRequest(
            model=request_data["model"],
            messages=[
                ChatMessage(role=msg["role"], content=msg["content"])
                for msg in request_data["messages"]
            ],
            chatId=request_data["chatId"],
            stream=True,
            options=request_data.get("options"),
        )

        # Verify chat belongs to the user
        chat = (
            db.query(Chat)
            .filter(Chat.id == request.chatId, Chat.user_id == current_user.id)
            .first()
        )

        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        # Save the user message to the database
        latest_user_message = next(
            (msg for msg in reversed(request.messages) if msg.role == "user"), None
        )

        if latest_user_message:
            user_db_message = Message(
                chat_id=request.chatId,
                role="user",
                content=latest_user_message.content,
            )
            db.add(user_db_message)
            db.commit()
            db.refresh(user_db_message)

        # Set up streaming
        api_payload = request.model_dump(mode="json")
        api_payload["stream"] = True
        app_logger.info(f"Stream chat request (GET): {api_payload}")

        # Create a placeholder for the assistant's message
        assistant_db_message = Message(
            chat_id=request.chatId,
            role="assistant",
            content="",  # Will be updated as the stream progresses
        )
        db.add(assistant_db_message)
        db.commit()
        db.refresh(assistant_db_message)

        message_id = str(assistant_db_message.id)
        accumulated_content = []

        async def generate_stream():
            nonlocal accumulated_content

            async with httpx.AsyncClient(timeout=None) as client:
                try:
                    async with client.stream(
                        "POST", f"{OLLAMA_API_BASE_URL}/api/chat", json=api_payload
                    ) as resp:
                        resp.raise_for_status()

                        async for chunk in resp.aiter_text():
                            try:
                                chunk_data = json.loads(chunk)
                                content = chunk_data.get("message", {}).get(
                                    "content", ""
                                )

                                if content:
                                    accumulated_content.append(content)
                                    yield f"data: {json.dumps({'id': message_id, 'content': content})}\n\n"

                                # Check if this is the final chunk (done=true)
                                if chunk_data.get("done", False):
                                    # Update the database with the complete message
                                    full_content = "".join(accumulated_content)
                                    app_logger.info(
                                        f"Completed message: {full_content[:100]}..."
                                    )

                                    # Update the message in the database
                                    db.query(Message).filter(
                                        Message.id == UUID(message_id)
                                    ).update(
                                        {
                                            "content": full_content,
                                            "tokens_used": chunk_data.get(
                                                "eval_count", 0
                                            ),
                                            "extended_metadata": {
                                                "prompt_eval_count": chunk_data.get(
                                                    "prompt_eval_count", 0
                                                ),
                                                "eval_count": chunk_data.get(
                                                    "eval_count", 0
                                                ),
                                                "eval_duration": chunk_data.get(
                                                    "eval_duration", 0
                                                ),
                                            },
                                        }
                                    )

                                    # Update chat timestamp
                                    setattr(chat, "updated_at", datetime.now())
                                    db.commit()

                                    # Send the "done" event
                                    yield f"data: {json.dumps({'done': True, 'id': message_id})}\n\n"
                            except json.JSONDecodeError:
                                app_logger.error(f"Failed to parse JSON chunk: {chunk}")
                                continue
                            except Exception as e:
                                app_logger.error(f"Error processing chunk: {str(e)}")
                                continue
                except httpx.HTTPError as e:
                    error_msg = f"Error from Ollama API: {str(e)}"
                    app_logger.error(error_msg)
                    yield f"data: {json.dumps({'error': error_msg})}\n\n"
                except Exception as e:
                    error_msg = f"Unexpected error: {str(e)}"
                    app_logger.error(error_msg)
                    yield f"data: {json.dumps({'error': error_msg})}\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            },
        )
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid payload format")
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing required field: {str(e)}")
    except Exception as e:
        app_logger.error(f"Unexpected error in stream_chat_ollama_get: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
