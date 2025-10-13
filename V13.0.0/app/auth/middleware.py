"""
Authentication and security middleware
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import time
from datetime import datetime
from collections import defaultdict
import asyncio

from .jwt_handler import verify_token
from .supabase_client import is_user_active


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to protect routes that require authentication
    """
    
    # Public routes that don't require authentication
    PUBLIC_ROUTES = [
        "/",
        "/health",
        "/api/auth/login",
        "/api/auth/logout",
        "/api/auth/verify",
        "/ui/login.html",
        "/ui/login.js",
        "/ui/auth.js",
        "/ui/i18n.js",
        "/ui/styles.css",
    ]

    # Routes that start with these prefixes are public
    PUBLIC_PREFIXES = [
        "/ui/assets/",
        "/ui/styles/",
        "/ui/images/",
        "/out/",
    ]
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Process each request"""
        
        # Check if route is public
        if self._is_public_route(request.url.path):
            return await call_next(request)
        
        # Check if route requires authentication
        if self._requires_auth(request.url.path):
            # Get Authorization header
            auth_header = request.headers.get("Authorization")
            
            if not auth_header or not auth_header.startswith("Bearer "):
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "detail": "Missing or invalid authorization header",
                        "redirect": "/ui/login.html"
                    }
                )
            
            # Extract token
            token = auth_header.replace("Bearer ", "")
            
            # Verify token
            payload = verify_token(token)
            if not payload:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "detail": "Invalid or expired token",
                        "redirect": "/ui/login.html"
                    }
                )
            
            # Check if user is active
            user_id = payload.get("user_id")
            if not await is_user_active(user_id):
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "User account is inactive"}
                )
            
            # Add user info to request state
            request.state.user = payload
        
        # Continue processing request
        response = await call_next(request)
        return response
    
    def _is_public_route(self, path: str) -> bool:
        """Check if route is public"""
        # Exact match
        if path in self.PUBLIC_ROUTES:
            return True
        
        # Prefix match
        for prefix in self.PUBLIC_PREFIXES:
            if path.startswith(prefix):
                return True
        
        return False
    
    def _requires_auth(self, path: str) -> bool:
        """Check if route requires authentication"""
        # API routes require auth (except /api/auth/login and /api/auth/logout)
        if path.startswith("/api/"):
            # Public API endpoints
            if path in ["/api/auth/login", "/api/auth/logout", "/api/auth/verify", "/api/invoice-seq"]:
                return False
            return True

        # HTML pages don't require auth at middleware level
        # They will check authentication via JavaScript and redirect if needed
        return False


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware to prevent brute force attacks
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
        self.cleanup_interval = 60  # Clean up old entries every 60 seconds
        self.last_cleanup = time.time()
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Process each request with rate limiting"""
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Clean up old entries periodically
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_entries()
            self.last_cleanup = current_time
        
        # Check rate limit for sensitive endpoints
        if self._is_rate_limited_endpoint(request.url.path):
            # Get request timestamps for this IP
            timestamps = self.requests[client_ip]
            
            # Remove timestamps older than 1 minute
            cutoff_time = current_time - 60
            timestamps = [ts for ts in timestamps if ts > cutoff_time]
            
            # Check if limit exceeded
            if len(timestamps) >= self.requests_per_minute:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per minute.",
                        "retry_after": 60
                    }
                )
            
            # Add current timestamp
            timestamps.append(current_time)
            self.requests[client_ip] = timestamps
        
        # Continue processing request
        response = await call_next(request)
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check X-Forwarded-For header (for proxies)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # Use direct client IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _is_rate_limited_endpoint(self, path: str) -> bool:
        """Check if endpoint should be rate limited"""
        # Rate limit authentication endpoints
        rate_limited_paths = [
            "/api/auth/login",
            "/api/auth/refresh",
        ]
        
        return path in rate_limited_paths
    
    def _cleanup_old_entries(self):
        """Remove old entries from rate limit tracking"""
        current_time = time.time()
        cutoff_time = current_time - 120  # Keep last 2 minutes
        
        for ip in list(self.requests.keys()):
            timestamps = [ts for ts in self.requests[ip] if ts > cutoff_time]
            if timestamps:
                self.requests[ip] = timestamps
            else:
                del self.requests[ip]


class AuditLogMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all API requests for audit trail
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Log request and response"""
        
        # Record start time
        start_time = time.time()
        
        # Get request info
        method = request.method
        path = request.url.path
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Get user info if authenticated
        user_id = None
        user_email = None
        if hasattr(request.state, "user"):
            user_id = request.state.user.get("user_id")
            user_email = request.state.user.get("email")
        
        # Process request
        try:
            response = await call_next(request)
            status_code = response.status_code
            success = status_code < 400
        except Exception as e:
            status_code = 500
            success = False
            raise
        finally:
            # Calculate duration
            duration = time.time() - start_time
            
            # Log to console (can be extended to database)
            if self._should_log(path):
                log_entry = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "method": method,
                    "path": path,
                    "status_code": status_code,
                    "duration_ms": round(duration * 1000, 2),
                    "client_ip": client_ip,
                    "user_agent": user_agent,
                    "user_id": user_id,
                    "user_email": user_email,
                    "success": success
                }
                
                print(f"📝 Audit: {method} {path} - {status_code} ({log_entry['duration_ms']}ms) - {user_email or 'anonymous'}")
                
                # TODO: Store in database
                # await self._store_audit_log(log_entry)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _should_log(self, path: str) -> bool:
        """Check if path should be logged"""
        # Don't log static files
        if path.startswith("/ui/assets/") or path.startswith("/ui/styles/"):
            return False
        
        # Don't log health checks
        if path == "/health":
            return False
        
        return True
    
    async def _store_audit_log(self, log_entry: dict):
        """Store audit log in database"""
        # TODO: Implement database storage
        pass

