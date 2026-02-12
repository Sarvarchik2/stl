"""Dependencies for FastAPI endpoints."""
from typing import Annotated, List, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from .database import get_db
from .services.auth import decode_token
from .models.user import User
from .models.enums import Role, ROLE_HIERARCHY

# Security scheme
security = HTTPBearer()

async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """
    Get current user from JWT token.
    Throws 401 if token is invalid or user doesn't exist.
    """
    try:
        token = credentials.credentials
        payload = decode_token(token)
        
        if not payload or payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing subject",
            )
        
        result = await db.execute(select(User).where(User.id == UUID(user_id)))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
            
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is disabled",
            )
        
        # Debug trace
        role_val = _get_role_val(user.role)
        print(f"AUTH DEBUG: User {user.phone} role={user.role} normalized={role_val}")
            
        return user
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
        )

def _get_role_val(r) -> str:
    """Helper to get string value of a role (Enum or String)."""
    if r is None:
        return ""
    if hasattr(r, 'value'):
        return str(r.value).lower()
    if hasattr(r, 'name'):
        return str(r.name).lower()
    return str(r).lower()

def _get_role_level(r) -> int:
    """Get numeric level of a role for hierarchy checks."""
    val = _get_role_val(r)
    # Map of role values to levels
    levels = {
        "client": 1,
        "operator": 2,
        "manager": 3,
        "admin": 4
    }
    return levels.get(val, 0)

def require_roles(*allowed_roles: Role):
    """Dependency factory for role-based access control."""
    async def role_checker(
        current_user: Annotated[User, Depends(get_current_user)]
    ) -> User:
        user_role_val = _get_role_val(current_user.role)
        allowed_role_vals = [_get_role_val(r) for r in allowed_roles]
        
        user_level = _get_role_level(current_user.role)
        max_required_level = max([_get_role_level(r) for r in allowed_roles]) if allowed_roles else 0

        if user_role_val not in allowed_role_vals and user_level < max_required_level:
            print(f"RBAC SHIELD (require_roles): 403 Forbidden. User: {current_user.phone}, Role: {user_role_val}, Required: {allowed_role_vals}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires level {max_required_level}",
            )
        return current_user
    return role_checker

def require_min_role(min_role: Role):
    """Dependency for minimum role level check."""
    async def role_checker(
        current_user: Annotated[User, Depends(get_current_user)]
    ) -> User:
        user_level = _get_role_level(current_user.role)
        required_level = _get_role_level(min_role)
        
        if user_level < required_level:
            user_role_val = _get_role_val(current_user.role)
            print(f"RBAC SHIELD (min_role): 403 Forbidden. User: {current_user.phone}, Role: {user_role_val}, Required Min: {_get_role_val(min_role)} ({required_level})")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires {_get_role_val(min_role)} privileges",
            )
        return current_user
    return role_checker

async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, else None."""
    if not credentials:
        return None
    try:
        token = credentials.credentials
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            return None
        user_id = payload.get("sub")
        if not user_id:
            return None
        result = await db.execute(select(User).where(User.id == UUID(user_id)))
        user = result.scalar_one_or_none()
        if not user or not user.is_active:
            return None
        return user
    except Exception:
        return None

# Common dependencies
CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[Optional[User], Depends(get_optional_current_user)]
DB = Annotated[AsyncSession, Depends(get_db)]

# Role-based dependencies
StaffUser = Annotated[User, Depends(require_min_role(Role.OPERATOR))]
ManagerUser = Annotated[User, Depends(require_min_role(Role.MANAGER))]
AdminUser = Annotated[User, Depends(require_min_role(Role.ADMIN))]
