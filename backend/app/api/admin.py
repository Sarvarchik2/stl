"""Admin API routes."""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from ..dependencies import DB, AdminUser
from ..models.application import Application
from ..models.audit import AuditLog, Setting
from ..schemas.common import (
    AuditLogListResponse, AuditLogResponse, 
    SettingResponse, SettingUpdate,
    PriceOverrideRequest, StatusOverrideRequest
)
from ..services.audit import log_action

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/audit-logs", response_model=AuditLogListResponse)
async def list_audit_logs(
    db: DB,
    user: AdminUser,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200)
):
    """View system audit logs."""
    query = select(AuditLog).order_by(AuditLog.created_at.desc())
    
    # Count
    from sqlalchemy import func
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()
    
    # Pagination
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    return AuditLogListResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page
    )


@router.patch("/applications/{app_id}/price", response_model=dict)
async def override_price(
    app_id: UUID,
    request: PriceOverrideRequest,
    current_user: AdminUser,
    db: DB
):
    """Override application price (Admin only)."""
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
        
    old_price = app.final_price
    app.final_price = request.new_final_price
    
    await log_action(
        db=db,
        action="admin_price_override",
        entity_type="application",
        entity_id=app.id,
        user_id=current_user.id,
        old_value={"price": str(old_price)},
        new_value={"price": str(request.new_final_price)},
        reason=request.reason
    )
    
    await db.commit()
    return {"status": "success", "new_price": request.new_final_price}


@router.get("/settings", response_model=List[SettingResponse])
async def list_settings(db: DB, user: AdminUser):
    """List system settings."""
    result = await db.execute(select(Setting))
    return result.scalars().all()


@router.patch("/settings/{key}", response_model=SettingResponse)
async def update_setting(
    key: str,
    setting_in: SettingUpdate,
    db: DB,
    user: AdminUser
):
    """Update a system setting."""
    result = await db.execute(select(Setting).where(Setting.key == key))
    setting = result.scalar_one_or_none()
    
    if not setting:
        # Create new setting if it doesn't exist
        setting = Setting(key=key, value=str(setting_in.value))
        db.add(setting)
    else:
        setting.value = str(setting_in.value)
            
    setting.updated_by = user.id
    
    await log_action(
        db=db,
        action="update_setting",
        entity_type="setting",
        entity_id=setting.id,
        user_id=user.id,
        old_value={"value": setting.value} if setting.id else None,
        new_value={"value": setting_in.value, "key": key},
        reason=setting_in.reason
    )
    
    await db.commit()
    await db.refresh(setting)
    return setting


@router.patch("/applications/{app_id}/status", response_model=dict)
async def override_status(
    app_id: UUID,
    request: StatusOverrideRequest,
    current_user: AdminUser,
    db: DB
):
    """
    Override application status (Admin only).
    Bypasses business rules.
    """
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
        
    old_status = app.status
    
    # Validate status enum
    try:
        from ..models.enums import ApplicationStatus
        new_status_enum = ApplicationStatus(request.new_status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Invalid status. Allowed: {[s.value for s in ApplicationStatus]}"
        )
        
    app.status = new_status_enum
    
    # Add to history
    from ..models.application import StatusHistory
    history = StatusHistory(
        application_id=app.id,
        old_status=old_status,
        new_status=new_status_enum,
        changed_by=current_user.id,
        reason=f"[ADMIN OVERRIDE] {request.reason}"
    )
    db.add(history)
    
    await log_action(
        db=db,
        action="admin_status_override",
        entity_type="application",
        entity_id=app.id,
        user_id=current_user.id,
        old_value={"status": old_status.value},
        new_value={"status": request.new_status},
        reason=request.reason
    )
    
    await db.commit()
    return {"status": "success", "new_status": request.new_status}


@router.get("/stats")
async def get_stats(
    db: DB, 
    user: AdminUser,
    period: str = Query("all", enum=["day", "week", "month", "all"])
):
    """
    Get real-time dashboard statistics.
    Optional period filter: day, week, month, all.
    """
    from sqlalchemy import func
    from datetime import datetime, timedelta
    from ..models.car import Car
    from ..models.enums import ApplicationStatus
    
    # Time filtering
    start_date = None
    now = datetime.now()
    if period == "day":
        start_date = now - timedelta(days=1)
    elif period == "week":
        start_date = now - timedelta(weeks=1)
    elif period == "month":
        start_date = now - timedelta(days=30)
        
    def apply_filter(q, date_col):
        if start_date:
            return q.where(date_col >= start_date)
        return q

    # 1. Total Volume (Revenue) & Profit
    # Revenue = Sum(final_price)
    # Profit = Sum(final_price - source_price_snapshot)
    
    # Note: source_price_snapshot might be null for old records, handle gracefully
    profit_expr = Application.final_price - func.coalesce(Application.source_price_snapshot, 0)
    
    financials_query = select(
        func.sum(Application.final_price).label("revenue"),
        func.sum(profit_expr).label("profit")
    ).where(
        Application.status.in_([ApplicationStatus.DELIVERED, ApplicationStatus.COMPLETED])
    )
    financials_query = apply_filter(financials_query, Application.updated_at) # Use updated_at for completed deals
    
    fin_result = (await db.execute(financials_query)).one()
    total_volume = fin_result.revenue or 0
    total_profit = fin_result.profit or 0
    
    # 2. In Pipeline (Active applications)
    pipeline_query = select(func.count(Application.id)).where(
        Application.status.in_([
            ApplicationStatus.NEW, ApplicationStatus.CONFIRMED, 
            ApplicationStatus.CONTRACT_SIGNED, ApplicationStatus.PAID,
            ApplicationStatus.IN_TRANSIT, ApplicationStatus.WAITING_PAYMENT
        ])
    )
    # Pipeline is usually "current", so maybe date filter applies to created_at?
    # User likely wants "New applications in this period" OR "Current pipeline state".
    # Usually Dashboard count is state-based, not time-based. 
    # BUT if filtering by "This Month", maybe they want "Created this month and currently in pipeline"? 
    # Let's apply filter to created_at for pipeline to show "Volume of work generated in period"
    pipeline_query = apply_filter(pipeline_query, Application.created_at)
    in_pipeline = (await db.execute(pipeline_query)).scalar() or 0
    
    # 3. Fleet Status (Snapshot, not time filtered usually)
    total_cars_query = select(func.count(Car.id)).where(Car.is_active == True)
    total_cars = (await db.execute(total_cars_query)).scalar() or 0
    
    # 4. Conversion Rate (Based on created_at in period)
    total_apps_query = select(func.count(Application.id))
    total_apps_query = apply_filter(total_apps_query, Application.created_at)
    total_apps = (await db.execute(total_apps_query)).scalar() or 0
    
    sold_query = select(func.count(Application.id)).where(
        Application.status.in_([ApplicationStatus.COMPLETED, ApplicationStatus.DELIVERED])
    )
    sold_query = apply_filter(sold_query, Application.updated_at) # Closed in period
    sold_count = (await db.execute(sold_query)).scalar() or 0
    
    # Conversion = Sold (in period) / Created (in period) ? 
    # Or Sold (in period) / Total Apps? 
    # Standard is usually Closed / Opened (if cohort) or just Closed / Total Active. 
    # Let's keep smooth logic: Sold / Total Apps (Created in period)
    conversion = (sold_count / total_apps * 100) if total_apps > 0 else 0
    
    # Prior logic used logs for "Recent Activity". 
    # If user wants "5 last actions" filtered by date, we can filter logs too.
    logs_query = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(5)
    logs_query = apply_filter(logs_query, AuditLog.created_at)
    logs = (await db.execute(logs_query)).scalars().all()
    
    # 5. Canceled/Rejected
    canceled_query = select(func.count(Application.id)).where(
        Application.status == ApplicationStatus.CANCELLED
    )
    canceled_query = apply_filter(canceled_query, Application.updated_at)
    canceled_count = (await db.execute(canceled_query)).scalar() or 0

    return {
        "total_volume_uzs": float(total_volume) * 12500,
        "total_volume_usd": float(total_volume),
        "total_profit_usd": float(total_profit),
        "in_pipeline": in_pipeline,
        "fleet_count": total_cars,
        "conversion_rate": round(conversion, 1),
        "total_applications": total_apps,
        "sold_count": sold_count,
        "canceled_count": canceled_count,
        "recent_activity": logs
    }
