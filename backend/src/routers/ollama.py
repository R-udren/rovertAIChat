import os
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from src.auth.service import get_current_active_admin, get_current_active_user
from src.core.logger import app_logger
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


@router.post("/chat")
async def chat_ollama(request: OllamaChatRequest):
    """
    Stream or get instant chat responses from an Ollama model.
    """
    payload = request.model_dump(mode="json")
    app_logger.info(f"Chat request: {payload}")
    with httpx.Client(timeout=None) as client:
        response = client.post(
            f"{OLLAMA_API_BASE_URL}/api/chat",
            json=payload,
        )
        app_logger.info(f"Chat response: {response.json()}")
    return response.json()
