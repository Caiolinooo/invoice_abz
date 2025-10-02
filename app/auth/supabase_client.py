"""
Supabase client for Employee Hub integration
"""
import os
from typing import Optional, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class SupabaseClient:
    """Singleton Supabase client"""
    _instance: Optional[Client] = None
    
    @classmethod
    def get_client(cls) -> Client:
        """Get or create Supabase client instance"""
        if cls._instance is None:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_SERVICE_KEY")  # Use service key for admin operations
            
            if not supabase_url or not supabase_key:
                raise ValueError(
                    "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env file"
                )
            
            cls._instance = create_client(supabase_url, supabase_key)
            print(f"✅ Supabase client initialized: {supabase_url}")
        
        return cls._instance


def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    return SupabaseClient.get_client()


async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Get user from Supabase by email

    Args:
        email: User email address

    Returns:
        User data dict or None if not found
    """
    try:
        client = get_supabase_client()

        # Query users_unified table (correct table name)
        response = client.table("users_unified").select("*").eq("email", email).execute()

        if response.data and len(response.data) > 0:
            user = response.data[0]
            print(f"✅ User found: {email} (role: {user.get('role')})")
            return user
        else:
            print(f"❌ User not found: {email}")
            return None

    except Exception as e:
        print(f"❌ Error fetching user: {e}")
        import traceback
        traceback.print_exc()
        return None


async def verify_user_credentials(email: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Verify user credentials using hybrid approach:
    1. Try Supabase Auth first (for users like Caio)
    2. Fall back to users_unified with bcrypt (for users like Rosana)

    Args:
        email: User email
        password: User password

    Returns:
        User data if credentials are valid, None otherwise
    """
    try:
        import bcrypt

        client = get_supabase_client()

        print(f"🔐 Attempting authentication for: {email}")

        # Strategy 1: Try Supabase Auth first
        try:
            print(f"📍 Strategy 1: Trying Supabase Auth...")
            auth_response = client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if auth_response.user:
                print(f"✅ Supabase Auth successful for: {email}")

                # Get user data from users table
                user_response = client.table("users").select("*").eq("email", email).execute()

                if user_response.data:
                    user_data = user_response.data[0]

                    # Check if user is active
                    if not user_data.get("active", False):
                        print(f"❌ User account is inactive: {email}")
                        return None

                    # Build full name from first_name and last_name
                    first_name = user_data.get("first_name", "")
                    last_name = user_data.get("last_name", "")
                    full_name = f"{first_name} {last_name}".strip()

                    print(f"✅ User data retrieved from users table: role={user_data.get('role')}")
                    return {
                        "id": user_data.get("id"),
                        "email": user_data.get("email"),
                        "name": full_name or email.split("@")[0],
                        "role": user_data.get("role", "USER"),
                        "is_active": user_data.get("active", True),
                        "created_at": user_data.get("created_at")
                    }
        except Exception as auth_error:
            print(f"⚠️  Supabase Auth failed: {auth_error}")

        # Strategy 2: Try users_unified with bcrypt
        print(f"📍 Strategy 2: Trying users_unified with bcrypt...")
        user_response = client.table("users_unified").select("*").eq("email", email).execute()

        if not user_response.data:
            print(f"❌ User not found in users_unified table: {email}")
            return None

        user_data = user_response.data[0]

        # Check if user has a password hash
        password_hash = user_data.get("password") or user_data.get("password_hash")

        if not password_hash:
            print(f"❌ User has no password set: {email}")
            return None

        # Verify password using bcrypt
        print(f"🔑 Verifying password hash...")

        password_bytes = password.encode('utf-8') if isinstance(password, str) else password
        hash_bytes = password_hash.encode('utf-8') if isinstance(password_hash, str) else password_hash

        is_valid = bcrypt.checkpw(password_bytes, hash_bytes)

        if not is_valid:
            print(f"❌ Invalid password for: {email}")
            return None

        print(f"✅ Password verified successfully for: {email}")

        # Check if user is active
        if not user_data.get("active", False):
            print(f"❌ User account is inactive: {email}")
            return None

        # Return user data
        print(f"✅ User data retrieved from users_unified: role={user_data.get('role')}")
        return {
            "id": user_data.get("id"),
            "email": user_data.get("email"),
            "name": user_data.get("name") or email.split("@")[0],
            "role": user_data.get("role", "USER"),
            "is_active": user_data.get("active", True),
            "created_at": user_data.get("created_at")
        }

    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def check_user_role(user_id: str, allowed_roles: list[str]) -> bool:
    """
    Check if user has one of the allowed roles
    
    Args:
        user_id: User ID
        allowed_roles: List of allowed roles (e.g., ["Admin", "Gerente"])
        
    Returns:
        True if user has allowed role, False otherwise
    """
    try:
        client = get_supabase_client()
        
        response = client.table("users").select("role").eq("id", user_id).execute()
        
        if response.data and len(response.data) > 0:
            user_role = response.data[0].get("role")
            return user_role in allowed_roles
        
        return False
        
    except Exception as e:
        print(f"❌ Error checking user role: {e}")
        return False


async def is_user_active(user_id: str) -> bool:
    """
    Check if user account is active
    Checks both users and users_unified tables

    Args:
        user_id: User ID

    Returns:
        True if user is active, False otherwise
    """
    try:
        client = get_supabase_client()

        # Try users table first
        response = client.table("users").select("active").eq("id", user_id).execute()

        if response.data and len(response.data) > 0:
            return response.data[0].get("active", False)

        # Try users_unified table
        response = client.table("users_unified").select("active").eq("id", user_id).execute()

        if response.data and len(response.data) > 0:
            return response.data[0].get("active", False)

        return False

    except Exception as e:
        print(f"❌ Error checking user status: {e}")
        return False

