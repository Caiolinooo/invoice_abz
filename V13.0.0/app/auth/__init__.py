"""
Authentication module for Invoice System
Integrates with Supabase Employee Hub for user authentication
"""

from .supabase_client import get_supabase_client
from .jwt_handler import create_access_token, verify_token
from .dependencies import get_current_user, require_role
from .models import User, Token, LoginRequest

__all__ = [
    'get_supabase_client',
    'create_access_token',
    'verify_token',
    'get_current_user',
    'require_role',
    'User',
    'Token',
    'LoginRequest',
]

