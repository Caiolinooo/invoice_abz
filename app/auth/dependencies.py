"""
FastAPI dependencies for authentication
"""
from typing import Optional, List
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .jwt_handler import verify_token
from .supabase_client import check_user_role, is_user_active
from .models import User

# Security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer token from Authorization header
        
    Returns:
        User object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    
    # Verify token
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    user_id = payload.get("user_id")
    if not await is_user_active(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create User object
    user = User(
        id=payload["user_id"],
        email=payload["email"],
        name=payload.get("name", ""),
        role=payload["role"],
        is_active=True
    )
    
    return user


async def get_optional_user(
    authorization: Optional[str] = Header(None)
) -> Optional[User]:
    """
    Get current user if token is provided, otherwise return None
    Useful for endpoints that work with or without authentication
    
    Args:
        authorization: Authorization header (optional)
        
    Returns:
        User object or None
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = verify_token(token)
        
        if not payload:
            return None
        
        user = User(
            id=payload["user_id"],
            email=payload["email"],
            name=payload.get("name", ""),
            role=payload["role"],
            is_active=True
        )
        
        return user
    except Exception:
        return None


def require_role(allowed_roles: List[str]):
    """
    Dependency factory to require specific roles (case-insensitive)

    Args:
        allowed_roles: List of allowed roles (e.g., ["Admin", "Gerente"])

    Returns:
        Dependency function

    Example:
        @app.get("/admin")
        async def admin_endpoint(user: User = Depends(require_role(["Admin"]))):
            ...
    """
    async def role_checker(user: User = Depends(get_current_user)) -> User:
        # Case-insensitive role comparison
        user_role_lower = user.role.lower()
        allowed_roles_lower = [role.lower() for role in allowed_roles]

        if user_role_lower not in allowed_roles_lower:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
            )
        return user

    return role_checker


def require_admin():
    """
    Dependency to require Admin role (case-insensitive)
    Accepts: Admin, ADMIN, admin

    Example:
        @app.delete("/users/{user_id}")
        async def delete_user(user: User = Depends(require_admin())):
            ...
    """
    return require_role(["Admin", "ADMIN", "admin"])


def require_manager_or_admin():
    """
    Dependency to require Manager or Admin role (case-insensitive)
    Accepts: Admin, ADMIN, admin, Gerente, GERENTE, gerente, Manager, MANAGER, manager

    Example:
        @app.get("/invoices")
        async def get_invoices(user: User = Depends(require_manager_or_admin())):
            ...
    """
    return require_role(["Admin", "ADMIN", "admin", "Gerente", "GERENTE", "gerente", "Manager", "MANAGER", "manager"])


async def verify_token_header(authorization: str = Header(...)) -> dict:
    """
    Verify JWT token from Authorization header
    
    Args:
        authorization: Authorization header value
        
    Returns:
        Token payload dict
        
    Raises:
        HTTPException: If token is invalid
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected: Bearer <token>"
        )
    
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return payload

