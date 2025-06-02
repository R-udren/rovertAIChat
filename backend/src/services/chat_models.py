import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp
from src.core.logger import app_logger

# Base URL for local Ollama instance
OLLAMA_API_BASE_URL = os.getenv("OLLAMA_API_BASE_URL", "http://localhost:11434")


# Simple in-memory cache for model data
class ModelCache:
    def __init__(self, ttl_minutes: int = 5):
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, datetime] = {}
        self._ttl = timedelta(minutes=ttl_minutes)

    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            if datetime.now() - self._timestamps[key] < self._ttl:
                return self._cache[key]
            else:
                # Expired, remove from cache
                del self._cache[key]
                del self._timestamps[key]
        return None

    def set(self, key: str, value: Any):
        self._cache[key] = value
        self._timestamps[key] = datetime.now()

    def clear(self):
        self._cache.clear()
        self._timestamps.clear()


# Global cache instance
model_cache = ModelCache()


class OllamaService:
    """Service class for handling Ollama API interactions"""

    @staticmethod
    async def get_version() -> Dict[str, Any]:
        """Get Ollama API version"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{OLLAMA_API_BASE_URL}/api/version") as resp:
                resp.raise_for_status()
                return await resp.json()

    @staticmethod
    async def get_model_capabilities(
        session: aiohttp.ClientSession, model_name: str
    ) -> List[str]:
        """Get capabilities for a specific model"""
        try:
            async with session.post(
                f"{OLLAMA_API_BASE_URL}/api/show", json={"name": model_name}
            ) as show_resp:
                show_resp.raise_for_status()
                show_data = await show_resp.json()
                return show_data.get("capabilities", [])
        except Exception as e:
            app_logger.warning(
                f"Failed to fetch capabilities for model {model_name}: {str(e)}"
            )
            return []

    @staticmethod
    async def get_models_with_capabilities() -> Dict[str, List[Any]]:
        """Get all models with their capabilities"""
        # Check cache first
        cached_models = model_cache.get("models_with_capabilities")
        if cached_models:
            app_logger.info("Returning cached models with capabilities")
            return cached_models

        app_logger.info(
            f"Fetching Ollama tags from API: {OLLAMA_API_BASE_URL}/api/tags"
        )

        async with aiohttp.ClientSession() as session:
            # Get the tags/models list
            async with session.get(f"{OLLAMA_API_BASE_URL}/api/tags") as resp:
                resp.raise_for_status()
                tags_data = await resp.json()

            # Fetch capabilities for each model
            models_with_capabilities = []
            for model in tags_data.get("models", []):
                model_name = model["name"]
                app_logger.info(f"Fetching capabilities for model: {model_name}")

                capabilities = await OllamaService.get_model_capabilities(
                    session, model_name
                )

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

            result = {"models": models_with_capabilities}

            # Cache the result
            model_cache.set("models_with_capabilities", result)
            app_logger.info(
                f"Cached {len(models_with_capabilities)} models with capabilities"
            )

            return result

    @staticmethod
    async def get_model_details(model_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific model"""
        # Check cache first
        cache_key = f"model_details_{model_name}"
        cached_details = model_cache.get(cache_key)
        if cached_details:
            app_logger.info(f"Returning cached details for model: {model_name}")
            return cached_details

        app_logger.info(f"Fetching details for model: {model_name}")

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{OLLAMA_API_BASE_URL}/api/show", json={"model": model_name}
            ) as resp:
                resp.raise_for_status()
                result = await resp.json()

                # Cache the result
                model_cache.set(cache_key, result)
                app_logger.info(f"Cached details for model: {model_name}")

                return result

    @staticmethod
    async def pull_model(model_name: str) -> str:
        """Pull a model from Ollama registry"""
        app_logger.info(f"Pulling model: {model_name}")

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{OLLAMA_API_BASE_URL}/api/pull", json={"model": model_name}
            ) as resp:
                resp.raise_for_status()
                result = await resp.text()

                # Clear cache since model list has changed
                model_cache.clear()
                app_logger.info(f"Cleared cache after pulling model: {model_name}")

                return result

    @staticmethod
    async def delete_model(model_name: str) -> Dict[str, str]:
        """Delete a model from Ollama"""
        app_logger.info(f"Deleting model: {model_name}")

        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{OLLAMA_API_BASE_URL}/api/delete", json={"model": model_name}
            ) as resp:
                resp.raise_for_status()

                # Clear cache since model list has changed
                model_cache.clear()
                app_logger.info(f"Cleared cache after deleting model: {model_name}")

                return {"message": "Model deleted successfully"}

    @staticmethod
    async def chat_with_model(chat_request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send chat request to Ollama model"""
        app_logger.info(f"Chat request for model: {chat_request_data.get('model')}")

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{OLLAMA_API_BASE_URL}/api/chat",
                json=chat_request_data,
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

                return await response.json()

    @staticmethod
    def clear_cache():
        """Clear all cached data"""
        model_cache.clear()
        app_logger.info("Cleared all model cache data")
