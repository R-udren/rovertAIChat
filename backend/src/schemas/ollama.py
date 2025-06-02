from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field
from src.schemas.chat import ChatMessage


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


class ModelDetails(BaseModel):
    """Schema for model details within a tag response."""

    parent_model: str
    format: str
    family: str
    families: List[str]
    parameter_size: str
    quantization_level: str


class OllamaShowResponse(BaseModel):
    """Schema for Ollama show API response."""

    modelfile: str
    parameters: str
    template: str
    details: ModelDetails
    model_info: Dict[str, Any]
    capabilities: Optional[List[str]] = None


class ModelName(BaseModel):
    """Schema for requesting a model by name."""

    model: str = Field(
        ...,
        description="Name of the model to request",
        examples=["gemma3:4b", "qwen3:8b"],
    )


class OllamaModel(ModelName):
    """Schema for individual Ollama model in tags response."""

    name: str
    modified_at: datetime
    size: int
    digest: str
    details: ModelDetails


class OllamaModelWithCapabilities(OllamaModel):
    """Schema for Ollama model with capabilities information."""

    capabilities: Optional[List[str]] = None


class OllamaModelsWithCapabilitiesResponse(BaseModel):
    """Schema for combined Ollama models with capabilities response."""

    models: List[OllamaModelWithCapabilities]
