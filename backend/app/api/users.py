"""Users API routes."""
from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy import select, func
from uuid import UUID
from typing import List, Optional

from ..dependencies import DB, CurrentUser, AdminUser, StaffUser, ManagerUser
from ..models.user import User
from ..models.enums import Role
from ..schemas.user import (
    UserResponse, UserUpdate, UserCreateStaff, 
    UserRoleUpdate, UserStatusUpdate
)
from ..services.auth import get_password_hash
from ..services.audit import log_action

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: CurrentUser):
    """Get current user's profile."""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_my_profile(request: UserUpdate, current_user: CurrentUser, db: DB):
    """Update current user's profile."""
    update_data = request.model_dump(exclude_unset=True)
    
    if update_data:
        old_values = {k: getattr(current_user, k) for k in update_data.keys()}
        
        for key, value in update_data.items():
            setattr(current_user, key, value)
        
        await log_action(
            db=db,
            action="user_profile_updated",
            entity_type="user",
            entity_id=current_user.id,
            user_id=current_user.id,
            old_value=old_values,
            new_value=update_data
        )
        await db.commit()
        await db.refresh(current_user)
    
    return current_user


@router.get("", response_model=List[UserResponse])
async def list_users(
    staff_user: StaffUser,
    db: DB,
    role: Optional[Role] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100)
):
    """
    List all users (Admin only).
    
    - Filter by role, active status, or search by name/phone
    """
    query = select(User)
    
    if role:
        query = query.where(User.role == role)
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            (User.phone.ilike(search_pattern)) |
            (User.first_name.ilike(search_pattern)) |
            (User.last_name.ilike(search_pattern))
        )
    
    query = query.order_by(User.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/staff", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_staff_user(request: UserCreateStaff, admin_user: AdminUser, db: DB):
    """
    Create a new staff member (Admin only).
    
    - Cannot create users with OWNER role
    - Admin can create operators, supervisors, managers
    """
    # Admin can create staff
    pass
    
    # Check if phone exists
    result = await db.execute(select(User).where(User.phone == request.phone))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )
    
    user = User(
        phone=request.phone,
        password_hash=get_password_hash(request.password),
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email,
        role=request.role
    )
    db.add(user)
    await db.flush()
    
    await log_action(
        db=db,
        action="staff_created",
        entity_type="user",
        entity_id=user.id,
        user_id=admin_user.id,
        new_value={"phone": user.phone, "role": user.role.value}
    )
    
    await db.commit()
    await db.refresh(user)
    return user


@router.patch("/{user_id}/role", response_model=UserResponse)
async def update_user_role(user_id: UUID, request: UserRoleUpdate, current_admin: AdminUser, db: DB):
    """
    Update user's role (Admin only).
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change own role"
        )
    
    old_role = user.role
    user.role = request.role
    
    await log_action(
        db=db,
        action="user_role_changed",
        entity_type="user",
        entity_id=user.id,
        user_id=current_admin.id,
        old_value={"role": old_role.value},
        new_value={"role": request.role.value}
    )
    
    await db.commit()
    await db.refresh(user)
    return user


@router.patch("/{user_id}/status", response_model=UserResponse)
async def update_user_status(user_id: UUID, request: UserStatusUpdate, admin_user: AdminUser, db: DB):
    """
    Enable/disable user account (Admin only).
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if user.id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot disable own account"
        )
    
    old_status = user.is_active
    user.is_active = request.is_active
    
    await log_action(
        db=db,
        action="user_status_changed",
        entity_type="user",
        entity_id=user.id,
        user_id=admin_user.id,
        old_value={"is_active": old_status},
        new_value={"is_active": request.is_active}
    )
    
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID, staff_user: StaffUser, db: DB):
    """Get user by ID (Staff only)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user
