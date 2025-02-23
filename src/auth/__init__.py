"""
Authentication and Authorization Module.
Handles user authentication, permissions and security.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from firebase_admin import auth as firebase_auth

from ..core.config import config

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class AuthHandler:
    """Handles authentication and authorization logic."""
    
    def __init__(self):
        self.secret_key = config.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        
    async def create_access_token(self, data: Dict[str, Any]) -> str:
        """
        Create JWT access token.
        
        Args:
            data: Data to encode in token
            
        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify JWT token.
        
        Args:
            token: Token to verify
            
        Returns:
            Decoded token payload
            
        Raises:
            HTTPException: If token is invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    async def verify_firebase_token(self, token: str) -> Dict[str, Any]:
        """
        Verify Firebase token.
        
        Args:
            token: Firebase ID token
            
        Returns:
            Token claims
            
        Raises:
            HTTPException: If token is invalid
        """
        try:
            decoded_token = firebase_auth.verify_id_token(token)
            return decoded_token
        except Exception:
            raise HTTPException(
                status_code=401,
                detail="Invalid Firebase token",
                headers={"WWW-Authenticate": "Bearer"},
            )

# Auth dependency
async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Get current authenticated user from token.
    
    Args:
        token: JWT token from request
        
    Returns:
        User data from token
        
    Raises:
        HTTPException: If token is invalid
    """
    auth_handler = AuthHandler()
    return await auth_handler.verify_token(token)

# Permission decorators
def requires_permission(permission: str):
    """
    Decorator to check if user has required permission.
    
    Args:
        permission: Required permission name
    """
    async def permission_checker(
        current_user: Dict[str, Any] = Security(get_current_user)
    ) -> None:
        if permission not in current_user.get("permissions", []):
            raise HTTPException(
                status_code=403,
                detail=f"Missing required permission: {permission}"
            )
    return permission_checker
