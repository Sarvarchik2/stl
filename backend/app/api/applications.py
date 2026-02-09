"""Applications API routes."""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy import select, func, desc, or_
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Optional
from datetime import datetime

from ..dependencies import (
    DB, CurrentUser, StaffUser, SupervisorUser, 
    ManagerUser, AdminUser
)
from ..models.application import Application, StatusHistory
from ..models.car import Car
from ..models.user import User
from ..models.enums import (
    Role, ApplicationStatus, ContactStatus, 
    RejectionReason, DocumentType
)
from ..schemas.application import (
    ApplicationCreate, AdminApplicationCreate, ApplicationResponse, ApplicationDetailResponse,
    ApplicationListResponse, ApplicationListParams,
    ApplicationStatusUpdate, ContactStatusUpdate, ChecklistUpdate,
    RejectionUpdate, AssignOperatorRequest, CommentUpdate,
    InternalNoteUpdate, ConfirmCarRequest, CargoBookingRequest,
    CommentCreate, CommentResponse, StatusHistoryResponse
)
from ..services.pricing import get_final_price
from ..services.blacklist import is_phone_blocked
from ..services.audit import log_action

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    request: ApplicationCreate,
    current_user: CurrentUser,
    db: DB
):
    """
    Create a new application (Client only).
    
    - Checks blacklist
    - Checks car availability
    - Snapshots price
    """
    # 1. Check blacklist
    is_blocked, reason = await is_phone_blocked(db, current_user.phone)
    if is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot create application: {reason}"
        )
        
    # 2. Check car
    result = await db.execute(select(Car).where(Car.id == request.car_id))
    car = result.scalar_one_or_none()
    
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
        
    if not car.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Car is not available"
        )
        
    # 3. Calculate price snapshot
    final_price, markup = await get_final_price(db, car.source_price_usd)
    
    # 4. Create application
    app = Application(
        client_id=current_user.id,
        car_id=car.id,
        source_price_snapshot=car.source_price_usd,
        markup_percent=markup,
        final_price=final_price,
        status=ApplicationStatus.NEW,
        contact_status=ContactStatus.NOT_TOUCHED,
        checklist={
            "confirmed_interest": False,
            "confirmed_budget": False,
            "confirmed_timeline": False,
            "agreed_visit": False,
            "agreed_contract": False,
            "test_drive": False,
            "documents": False
        }
    )
    db.add(app)
    await db.flush()
    
    # Log status change
    status_history = StatusHistory(
        application_id=app.id,
        new_status=ApplicationStatus.NEW,
        changed_by=current_user.id,
        reason="Application created"
    )
    db.add(status_history)
    
    await log_action(
        db=db,
        action="application_created",
        entity_type="application",
        entity_id=app.id,
        user_id=current_user.id,
        new_value={"car_id": str(car.id), "final_price": str(final_price)}
    )
    
    await db.commit()
    await db.refresh(app)
    return app


@router.post("/admin", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def admin_create_application(
    request: AdminApplicationCreate,
    current_user: StaffUser,
    db: DB
):
    """
    Manually create an application (Staff only).
    Used for phone leads or offline sales.
    """
    # 1. Determine client
    client_id = request.client_id
    
    if not client_id:
        if not request.client_phone:
            raise HTTPException(status_code=400, detail="Either client_id or client_phone is required")
            
        # Try to find by phone
        stmt = select(User).where(User.phone == request.client_phone)
        res = await db.execute(stmt)
        existing_client = res.scalar_one_or_none()
        
        if existing_client:
            client_id = existing_client.id
        else:
            # Create a simple client account
            name_parts = (request.client_name or "New Lead").split(" ", 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else "-"
            
            new_client = User(
                phone=request.client_phone,
                first_name=first_name,
                last_name=last_name,
                role=Role.CLIENT,
                is_active=True
            )
            db.add(new_client)
            await db.flush()
            client_id = new_client.id

    # 2. Check car
    result = await db.execute(select(Car).where(Car.id == request.car_id))
    car = result.scalar_one_or_none()
    
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
        
    # 3. Calculate price snapshot
    final_price, markup = await get_final_price(db, car.source_price_usd)
    
    # 4. Create application
    app = Application(
        client_id=client_id,
        car_id=car.id,
        operator_id=current_user.id, # Auto-assign to creator
        source_price_snapshot=car.source_price_usd,
        markup_percent=markup,
        final_price=final_price,
        status=ApplicationStatus.NEW,
        contact_status=ContactStatus.CONTACTED, # Since it's manual, we've contacted them
        internal_note=f"Manually created by {current_user.full_name}. Source: {request.source}",
        checklist={
            "confirmed_interest": True,
            "confirmed_budget": False,
            "confirmed_timeline": False,
            "agreed_visit": False,
            "agreed_contract": False,
            "test_drive": False,
            "documents": False
        }
    )
    db.add(app)
    await db.flush()
    
    # History
    db.add(StatusHistory(
        application_id=app.id,
        new_status=ApplicationStatus.NEW,
        changed_by=current_user.id,
        reason="Manual creation by staff"
    ))
    
    await log_action(
        db=db,
        action="admin_application_created",
        entity_type="application",
        entity_id=app.id,
        user_id=current_user.id,
        new_value={"client_id": str(client_id), "car_id": str(car.id)}
    )
    
    await db.commit()
    await db.refresh(app)
    return app


@router.get("", response_model=ApplicationListResponse)
async def list_applications(
    db: DB,
    current_user: CurrentUser,
    params: ApplicationListParams = Depends()
):
    """
    List applications.
    - Clients see only their own.
    - Staff see all (with filters).
    """
    query = select(Application)
    
    # Role-based filtering
    if current_user.role == Role.CLIENT:
        query = query.where(Application.client_id == current_user.id)
    else:
        # Staff filters
        if params.my_only:
            query = query.where(Application.operator_id == current_user.id)
        if params.unassigned:
            query = query.where(Application.operator_id == None)
        if params.operator_id:
            query = query.where(Application.operator_id == params.operator_id)
        if params.client_id:
            query = query.where(Application.client_id == params.client_id)
            
    # Common filters
    if params.status:
        query = query.where(Application.status == params.status)
    if params.contact_status:
        query = query.where(Application.contact_status == params.contact_status)
    if params.date_from:
        query = query.where(Application.created_at >= params.date_from)
    if params.date_to:
        query = query.where(Application.created_at <= params.date_to)
        
    # Sorting
    if params.sort_order == "asc":
        query = query.order_by(asc(getattr(Application, params.sort_by, Application.created_at)))
    else:
        query = query.order_by(desc(getattr(Application, params.sort_by, Application.created_at)))
        
    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()
    
    # Pagination
    query = query.offset((params.page - 1) * params.per_page).limit(params.per_page)
    
    # Load relations for schemas
    from sqlalchemy.orm import joinedload
    query = query.options(joinedload(Application.car), joinedload(Application.client))
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    # Map model objects to schemas with denormalized fields
    response_items = []
    for app in items:
        resp = ApplicationResponse.model_validate(app)
        if app.car:
            resp.car_brand = app.car.brand
            resp.car_model = app.car.model
            resp.car_year = app.car.year
            resp.car_image_url = app.car.image_url
        if app.client:
            resp.client_first_name = app.client.first_name
            resp.client_last_name = app.client.last_name
            resp.client_phone = app.client.phone
        response_items.append(resp)
    
    return ApplicationListResponse(
        items=response_items,
        total=total,
        page=params.page,
        per_page=params.per_page,
        pages=(total + params.per_page - 1) // params.per_page
    )


@router.get("/{app_id}", response_model=ApplicationDetailResponse)
async def get_application(
    app_id: UUID,
    current_user: CurrentUser,
    db: DB
):
    """Get application details."""
    query = select(Application).where(Application.id == app_id)
    result = await db.execute(query)
    app = result.scalar_one_or_none()
    
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
        
    # Access check
    if current_user.role == Role.CLIENT and app.client_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
    # For staff, load relations
    from sqlalchemy.orm import selectinload
    query = select(Application).where(Application.id == app_id).options(
        selectinload(Application.car),
        selectinload(Application.client),
        selectinload(Application.comments),
        selectinload(Application.status_history),
        selectinload(Application.documents)
    )
    result = await db.execute(query)
    app = result.scalar_one_or_none()
    
    # Convert to response
    resp = ApplicationDetailResponse.model_validate(app)
    if app.car:
        resp.car_brand = app.car.brand
        resp.car_model = app.car.model
        resp.car_year = app.car.year
        resp.car_image_url = app.car.image_url
        # Also set the nested car object
        from ..schemas.car import CarResponse
        # Calculate markup for nested car
        from ..services.pricing import get_final_price
        final_price, markup = await get_final_price(db, app.car.source_price_usd)
        car_dict = {
            "id": app.car.id,
            "source": app.car.source,
            "brand": app.car.brand,
            "make": app.car.make,
            "model": app.car.model,
            "year": app.car.year,
            "source_price_usd": app.car.source_price_usd,
            "final_price_usd": final_price,
            "markup_percent": float(markup),
            "image_url": app.car.image_url,
            "photos": app.car.photos or [],
            "features": app.car.features or [],
            "is_active": app.car.is_active,
            "exterior_color": app.car.exterior_color,
            "engine": app.car.engine,
            "vin": app.car.vin if current_user.role != Role.CLIENT else None
        }
        resp.car = car_dict
        
    if app.client:
        resp.client_first_name = app.client.first_name
        resp.client_last_name = app.client.last_name
        resp.client_phone = app.client.phone
        resp.client = {
             "id": app.client.id,
             "first_name": app.client.first_name,
             "last_name": app.client.last_name,
             "phone": app.client.phone,
             "email": app.client.email
        }
        
    return resp


@router.patch("/{app_id}/status", response_model=ApplicationResponse)
async def update_status(
    app_id: UUID,
    update: ApplicationStatusUpdate,
    current_user: StaffUser,
    db: DB
):
    """
    Update application status (Staff only).
    Enforces business rules for transitions.
    """
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
        
    old_status = app.status
    new_status = update.status
    
    # Business Rules
    
    # 1. CONFIRMED requires positive contact + Checklist (unless Override logic needed)
    if new_status == ApplicationStatus.CONFIRMED:
        # Allow both CONTACTED and CONFIRMED_INTEREST
        allowed_contact = [ContactStatus.CONTACTED, ContactStatus.CONFIRMED_INTEREST]
        if app.contact_status not in allowed_contact:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Cannot confirm: Contact status must be 'Contacted' or 'Confirmed Interest' (current: {app.contact_status})"
            )
        # Check checklist
        checklist = app.checklist or {}
        # We only require the first few items to be checked for basic confirmation if needed, 
        # but let's keep it as is but maybe more informative
        if not all(checklist.values()):
             missing = [k for k, v in checklist.items() if not v]
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Cannot confirm: Checklist incomplete. Missing: {', '.join(missing)}"
            )
            
    # 2. PAID requires Payment Confirmation (handled in payments module usually, but check here)
    if new_status == ApplicationStatus.PAID:
        # Check if there is a confirmed payment covering the amount? 
        # For simplicity, we assume manager checks this manually or system auto-updates
        if current_user.role not in [Role.MANAGER, Role.ADMIN, Role.OWNER]:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Only Manager can set PAID status"
            )
            
    # 3. CONTRACT_SIGNED requires Document
    if new_status == ApplicationStatus.CONTRACT_SIGNED:
        # Check for contract document
        # This would require a query to documents table
        pass 
        
    # Update
    app.status = new_status
    
    # History
    history = StatusHistory(
        application_id=app.id,
        old_status=old_status,
        new_status=new_status,
        changed_by=current_user.id,
        reason=update.reason
    )
    db.add(history)
    
    await log_action(
        db=db,
        action="application_status_changed",
        entity_type="application",
        entity_id=app.id,
        user_id=current_user.id,
        old_value={"status": old_status.value},
        new_value={"status": new_status.value, "reason": update.reason}
    )
    
    await db.commit()
    await db.refresh(app)
    return app


@router.patch("/{app_id}/contact-status", response_model=ApplicationResponse)
async def update_contact_status(
    app_id: UUID,
    update: ContactStatusUpdate,
    current_user: StaffUser,
    db: DB
):
    """Update contact status (Operator+)."""
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
        
    app.contact_status = update.contact_status
    if update.note:
        app.operator_comment = (app.operator_comment or "") + f"\n[{datetime.now()}] {update.note}"
        
    await db.commit()
    await db.refresh(app)
    return app


@router.patch("/{app_id}/checklist", response_model=ApplicationResponse)
async def update_checklist(
    app_id: UUID,
    update: ChecklistUpdate,
    current_user: StaffUser,
    db: DB
):
    """Update CRM checklist."""
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
        
    app.checklist = update.checklist
    
    await db.commit()
    await db.refresh(app)
    return app


@router.patch("/{app_id}/assign", response_model=ApplicationResponse)
async def assign_operator(
    app_id: UUID,
    request: AssignOperatorRequest,
    current_user: SupervisorUser,
    db: DB
):
    """Assign operator to application (Supervisor+)."""
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
        
    app.operator_id = request.operator_id
    
    await log_action(
        db=db,
        action="application_assigned",
        entity_type="application",
        entity_id=app.id,
        user_id=current_user.id,
        new_value={"operator_id": str(request.operator_id)}
    )
    
    await db.commit()
    await db.refresh(app)
    return app


@router.post("/{app_id}/comments", response_model=CommentResponse)
async def add_comment(
    app_id: UUID,
    request: CommentCreate,
    current_user: StaffUser,
    db: DB
):
    """Add a comment to application (Staff only)."""
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
        
    from ..models.application import ApplicationComment
    comment = ApplicationComment(
        application_id=app.id,
        user_id=current_user.id,
        text=request.text,
        is_internal=request.is_internal
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


@router.get("/{app_id}/comments", response_model=List[CommentResponse])
async def list_comments(
    app_id: UUID,
    current_user: CurrentUser,
    db: DB
):
    """List comments for application."""
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
        
    # Access check
    if current_user.role == Role.CLIENT and app.client_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
    from ..models.application import ApplicationComment
    query = select(ApplicationComment).where(ApplicationComment.application_id == app.id)
    
    # Clients don't see internal comments
    if current_user.role == Role.CLIENT:
        query = query.where(ApplicationComment.is_internal == False)
        
    query = query.order_by(desc(ApplicationComment.created_at))
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{app_id}/status-history", response_model=List[StatusHistoryResponse])
async def get_status_history(
    app_id: UUID,
    current_user: CurrentUser,
    db: DB
):
    """Get status history for application."""
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
        
    # Access check
    if current_user.role == Role.CLIENT and app.client_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
    query = select(StatusHistory).where(StatusHistory.application_id == app.id).order_by(desc(StatusHistory.created_at))
    result = await db.execute(query)
    return result.scalars().all()
