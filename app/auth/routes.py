"""
Authentication routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any
from datetime import datetime

from .models import LoginRequest, Token, User
from .supabase_client import verify_user_credentials, check_user_role
from .jwt_handler import create_access_token, verify_token
from .dependencies import get_current_user

# Create router
router = APIRouter(prefix="/api/auth", tags=["authentication"])


# Helper function for audit logging
async def log_audit_event(
    user_id: str,
    action: str,
    ip_address: str,
    user_agent: str,
    success: bool,
    details: str = None
):
    """
    Log authentication event to audit trail

    This can be extended to store in database for compliance
    """
    timestamp = datetime.utcnow().isoformat()

    log_entry = {
        "timestamp": timestamp,
        "user_id": user_id,
        "action": action,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "success": success,
        "details": details
    }

    # For now, just print to console
    # TODO: Store in database audit_logs table
    print(f"📝 Audit Log: {log_entry}")

    # You can extend this to write to database:
    # from app.database.database import get_db_session
    # from app.database.models import AuditLog
    # db = get_db_session()
    # audit_log = AuditLog(**log_entry)
    # db.add(audit_log)
    # db.commit()


@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, request: Request):
    """
    Authenticate user and return JWT token
    
    Only users with role "Admin" or "Gerente" can access the invoice system
    """
    try:
        print(f"🔐 Login attempt: {login_data.email}")
        
        # Verify credentials with Supabase
        user_data = await verify_user_credentials(login_data.email, login_data.password)
        
        if not user_data:
            print(f"❌ Invalid credentials for: {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if not user_data.get("is_active", False):
            print(f"❌ Inactive user: {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Check if user has required role (Admin or Gerente) - case insensitive
        user_role = user_data.get("role", "")
        user_role_lower = user_role.lower()
        allowed_roles = ["admin", "gerente", "manager"]  # Accept multiple variations

        if user_role_lower not in allowed_roles:
            print(f"❌ Insufficient permissions: {login_data.email} (role: {user_role})")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Only Admin and Gerente roles can access this system. Your role: {user_role}"
            )
        
        # Create JWT token
        token_data = create_access_token(user_data)
        
        print(f"✅ Login successful: {login_data.email} (role: {user_role})")
        
        # Log successful login (audit trail)
        await log_audit_event(
            user_id=user_data["id"],
            action="login",
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "unknown"),
            success=True
        )
        
        return Token(**token_data)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"❌ Login error: {e}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed due to server error"
        )


@router.post("/logout")
async def logout(user: User = Depends(get_current_user), request: Request = None):
    """
    Logout current user
    
    Note: JWT tokens are stateless, so logout is handled client-side by removing the token.
    This endpoint is mainly for audit logging.
    """
    try:
        print(f"👋 Logout: {user.email}")
        
        # Log logout event
        if request:
            await log_audit_event(
                user_id=user.id,
                action="logout",
                ip_address=request.client.host if request.client else "unknown",
                user_agent=request.headers.get("user-agent", "unknown"),
                success=True
            )
        
        return {
            "success": True,
            "message": "Logged out successfully"
        }
        
    except Exception as e:
        print(f"❌ Logout error: {e}")
        return {
            "success": False,
            "message": "Logout failed"
        }


@router.get("/verify")
async def verify(user: User = Depends(get_current_user)):
    """
    Verify current JWT token and return user info
    
    This endpoint is used by the frontend to check if the user is still authenticated
    """
    return {
        "valid": True,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "is_active": user.is_active
        }
    }


@router.get("/me")
async def get_current_user_info(user: User = Depends(get_current_user)):
    """
    Get current authenticated user information
    """
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "is_active": user.is_active
    }


@router.post("/refresh")
async def refresh_token(user: User = Depends(get_current_user)):
    """
    Refresh JWT token (extend expiration)
    """
    try:
        # Create new token with same user data
        user_data = {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role
        }
        
        token_data = create_access_token(user_data)
        
        return Token(**token_data)
        
    except Exception as e:
        print(f"❌ Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token"
        )


