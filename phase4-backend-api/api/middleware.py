"""
Middleware for Error Handling and Rate Limiting
Phase 4: Backend API Development
"""

import time
from collections import defaultdict
from typing import Dict
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, requests_per_minute: int = 60):
        """
        Initialize the rate limiter.
        
        Args:
            requests_per_minute: Maximum requests per minute per IP
        """
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = defaultdict(list)
    
    def is_allowed(self, client_ip: str) -> bool:
        """
        Check if a request is allowed for the given IP.
        
        Args:
            client_ip: Client IP address
            
        Returns:
            True if request is allowed, False otherwise
        """
        now = time.time()
        minute_ago = now - 60
        
        # Remove old requests
        self.requests[client_ip] = [
            timestamp for timestamp in self.requests[client_ip]
            if timestamp > minute_ago
        ]
        
        # Check if under limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return False
        
        # Record this request
        self.requests[client_ip].append(now)
        return True
    
    def get_remaining_requests(self, client_ip: str) -> int:
        """
        Get remaining requests for the given IP.
        
        Args:
            client_ip: Client IP address
            
        Returns:
            Number of remaining requests
        """
        now = time.time()
        minute_ago = now - 60
        
        # Remove old requests
        self.requests[client_ip] = [
            timestamp for timestamp in self.requests[client_ip]
            if timestamp > minute_ago
        ]
        
        return max(0, self.requests_per_minute - len(self.requests[client_ip]))


# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=60)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce rate limiting."""
    
    async def dispatch(self, request: Request, call_next):
        """Process request and enforce rate limiting."""
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Skip rate limiting for health check
        if request.url.path == "/api/health":
            return await call_next(request)
        
        # Check rate limit
        if not rate_limiter.is_allowed(client_ip):
            remaining = rate_limiter.get_remaining_requests(client_ip)
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded",
                    "remaining_requests": remaining,
                    "limit": rate_limiter.requests_per_minute
                }
            )
        
        # Add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(rate_limiter.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(rate_limiter.get_remaining_requests(client_ip))
        
        return response


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware for global error handling."""
    
    async def dispatch(self, request: Request, call_next):
        """Process request and handle errors."""
        try:
            return await call_next(request)
        except HTTPException as e:
            # Re-raise HTTP exceptions
            raise
        except ValueError as e:
            # Handle value errors
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": str(e)}
            )
        except FileNotFoundError as e:
            # Handle file not found errors
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": str(e)}
            )
        except Exception as e:
            # Handle unexpected errors
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": f"Internal server error: {str(e)}"}
            )
