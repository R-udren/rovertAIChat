from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from src.core.logger import app_logger


def get_remote_address(request: Request) -> str:
    """Get the remote address of the request"""
    # Check for X-Real-IP first (set by nginx)
    x_real_ip = request.headers.get("X-Real-IP")
    if x_real_ip:
        return x_real_ip.strip()

    # Then check X-Forwarded-For
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        # Get the leftmost IP (original client)
        return x_forwarded_for.split(",")[0].strip()

    # Fallback to socket IP
    return request.client.host if request.client else "127.0.0.1"


# Create a limiter instance that will identify clients by their IP address
limiter = Limiter(key_func=get_remote_address)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded with logging"""
    client_ip = get_remote_address(request)
    endpoint = request.url.path

    app_logger.warning(
        f"Rate limit exceeded: IP={client_ip}, endpoint={endpoint}, limit={exc.detail}"
    )

    return JSONResponse(
        status_code=429,
        content={
            "detail": f"Rate limit exceeded: {exc.detail}",
            "retry_after": exc.headers.get("Retry-After", "unknown")
            if exc.headers
            else "unknown",
        },
    )


def setup_limiter(app):
    """Setup rate limiter for FastAPI app"""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    return limiter
