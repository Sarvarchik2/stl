"""Authentication API routes."""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.user import User
from ..models.enums import Role
from ..schemas.user import (
    LoginRequest, RegisterRequest, Token, TokenRefresh,
    UserResponse, OTPRequest, OTPVerify
)
from ..services.auth import (
    verify_password, get_password_hash, create_tokens, decode_token
)
from ..services.blacklist import is_phone_blocked
from ..services.audit import log_action
from ..dependencies import CurrentUser, DB

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: DB):
    """
    Register a new client account.
    
    - **phone**: Phone number (unique)
    - **password**: At least 6 characters
    - **first_name**: First name
    - **last_name**: Last name
    """
    # Check if phone is blocked
    is_blocked, reason = await is_phone_blocked(db, request.phone)
    if is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Registration blocked: {reason}"
        )
    
    # Check if phone already exists
    result = await db.execute(select(User).where(User.phone == request.phone))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )
    
    # Create user
    user = User(
        phone=request.phone,
        password_hash=get_password_hash(request.password),
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email,
        role=Role.CLIENT
    )
    db.add(user)
    await db.flush()
    
    # Log action
    await log_action(
        db=db,
        action="user_registered",
        entity_type="user",
        entity_id=user.id,
        new_value={"phone": user.phone, "role": user.role.value}
    )
    
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=Token)
async def login(request: LoginRequest, db: DB):
    """
    Login with phone and password.
    
    Returns access and refresh tokens.
    """
    # Check if phone is blocked
    is_blocked, reason = await is_phone_blocked(db, request.phone)
    if is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Login blocked: {reason}"
        )
    
    # Find user
    result = await db.execute(select(User).where(User.phone == request.phone))
    user = result.scalar_one_or_none()
    
    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone or password"
        )
    
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Log action
    await log_action(
        db=db,
        action="user_login",
        entity_type="user",
        entity_id=user.id
    )
    await db.commit()
    
    # Return tokens directly, bypassing OTP
    return create_tokens(str(user.id), user.role.value)


@router.post("/refresh", response_model=Token)
async def refresh_token(request: TokenRefresh, db: DB):
    """
    Refresh access token using refresh token.
    """
    payload = decode_token(request.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or disabled"
        )
    
    return create_tokens(str(user.id), user.role.value)


@router.post("/send-otp", status_code=status.HTTP_200_OK)
async def send_otp(request: OTPRequest, db: DB):
    """
    Request OTP code for phone number.
    In dev mode, code is always 1234.
    """
    # Check if blocked
    is_blocked, reason = await is_phone_blocked(db, request.phone)
    if is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Blocked: {reason}"
        )
        
    # Simulate sending SMS
    # In production: call SMS provider here
    print(f"OTP for {request.phone}: 1234")
    
    return {"message": "OTP sent successfully", "dev_code": "1234"}


@router.post("/verify-otp", response_model=Token)
async def verify_otp(request: OTPVerify, db: DB):
    """
    Verify OTP and login/register.
    """
    # Bypass OTP verification for development
    # if request.code != "1234":
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Invalid OTP code"
    #     )
        
    # Check if user exists
    result = await db.execute(select(User).where(User.phone == request.phone))
    user = result.scalar_one_or_none()
    
    if not user:
        # Auto-register user if not found (Bypass for dev/testing)
        user = User(
            phone=request.phone,
            first_name="User",
            last_name=request.phone[-4:],
            role=Role.CLIENT,
            is_active=True
        )
        db.add(user)
        await db.flush()
        
        # Log action
        await log_action(
            db=db,
            action="user_auto_registered",
            entity_type="user",
            entity_id=user.id,
            new_value={"phone": user.phone, "role": user.role.value}
        )
        await db.commit()
        await db.refresh(user)
        
    if not user.is_active:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account disabled"
        )
        
    return create_tokens(str(user.id), user.role.value)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: CurrentUser):
    """
    Get current authenticated user's profile.
    """
    return current_user
