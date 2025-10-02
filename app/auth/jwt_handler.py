"""
JWT token handling for authentication
"""
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from dotenv import load_dotenv

load_dotenv()

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "8"))


def create_access_token(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create JWT access token for authenticated user
    
    Args:
        user_data: User information dict with id, email, role
        
    Returns:
        Dict with access_token, token_type, expires_in
    """
    # Calculate expiration
    expires_delta = timedelta(hours=JWT_EXPIRATION_HOURS)
    expire = datetime.utcnow() + expires_delta
    
    # Create JWT payload
    payload = {
        "user_id": user_data["id"],
        "email": user_data["email"],
        "role": user_data["role"],
        "name": user_data.get("name", ""),
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": secrets.token_urlsafe(16)  # Unique token ID
    }
    
    # Encode JWT
    encoded_jwt = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    return {
        "access_token": encoded_jwt,
        "token_type": "bearer",
        "expires_in": int(expires_delta.total_seconds()),
        "user": {
            "id": user_data["id"],
            "email": user_data["email"],
            "name": user_data.get("name", ""),
            "role": user_data["role"],
            "is_active": user_data.get("is_active", True)
        }
    }


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        # Decode and verify token
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # Check if token has expired
        exp = payload.get("exp")
        if exp:
            exp_datetime = datetime.fromtimestamp(exp)
            if datetime.utcnow() > exp_datetime:
                print("❌ Token has expired")
                return None
        
        # Validate required fields
        required_fields = ["user_id", "email", "role"]
        if not all(field in payload for field in required_fields):
            print("❌ Token missing required fields")
            return None
        
        return payload
        
    except JWTError as e:
        print(f"❌ JWT verification failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Token verification error: {e}")
        return None


def decode_token_without_verification(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode JWT token without verification (for debugging only)
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload or None
    """
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload
    except Exception as e:
        print(f"❌ Token decode error: {e}")
        return None


def get_token_expiration(token: str) -> Optional[datetime]:
    """
    Get expiration datetime from token
    
    Args:
        token: JWT token string
        
    Returns:
        Expiration datetime or None
    """
    try:
        payload = decode_token_without_verification(token)
        if payload and "exp" in payload:
            return datetime.fromtimestamp(payload["exp"])
        return None
    except Exception:
        return None


def is_token_expired(token: str) -> bool:
    """
    Check if token is expired
    
    Args:
        token: JWT token string
        
    Returns:
        True if expired, False otherwise
    """
    exp = get_token_expiration(token)
    if exp:
        return datetime.utcnow() > exp
    return True


def refresh_token(old_token: str) -> Optional[Dict[str, Any]]:
    """
    Refresh an existing token (create new token with same user data)
    
    Args:
        old_token: Existing JWT token
        
    Returns:
        New token dict or None if old token is invalid
    """
    payload = verify_token(old_token)
    if not payload:
        return None
    
    # Create new token with same user data
    user_data = {
        "id": payload["user_id"],
        "email": payload["email"],
        "role": payload["role"],
        "name": payload.get("name", "")
    }
    
    return create_access_token(user_data)

