"""SQLAlchemy Models - Enums."""
import enum


class Role(str, enum.Enum):
    """User roles with hierarchy."""
    CLIENT = "client"
    OPERATOR = "operator"
    MANAGER = "manager"
    ADMIN = "admin"


# Role hierarchy (higher number = more permissions)
ROLE_HIERARCHY = {
    Role.CLIENT: 1,
    Role.OPERATOR: 2,
    Role.MANAGER: 3,
    Role.ADMIN: 4,
}


class ApplicationStatus(str, enum.Enum):
    """Application lifecycle statuses."""
    NEW = "new"
    IN_CALLCENTER = "in_callcenter"
    CONFIRMED = "confirmed"
    WAITING_VISIT = "waiting_visit"
    WAITING_PAYMENT = "waiting_payment"
    PAID = "paid"
    CONTRACT_SIGNED = "contract_signed"
    CARGO_BOOKED = "cargo_booked"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ContactStatus(str, enum.Enum):
    """Call center contact statuses."""
    NOT_TOUCHED = "not_touched"
    NO_ANSWER = "no_answer"
    CONTACTED = "contacted"
    CALLBACK = "callback"
    REJECTED = "rejected"
    CONFIRMED_INTEREST = "confirmed_interest"


class PaymentMethod(str, enum.Enum):
    """Payment methods."""
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"


class PaymentStatus(str, enum.Enum):
    """Payment statuses."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


class DocumentType(str, enum.Enum):
    """Document types."""
    CONTRACT = "contract"
    VIDEO_SIGNATURE = "video_signature"
    RECEIPT = "receipt"
    INVOICE = "invoice"
    OTHER = "other"


class BlockType(str, enum.Enum):
    """Blacklist block types."""
    DAYS_7 = "days_7"
    DAYS_30 = "days_30"
    PERMANENT = "permanent"


class RejectionReason(str, enum.Enum):
    """Rejection reasons for applications."""
    EXPENSIVE = "expensive"
    CHANGED_MIND = "changed_mind"
    NO_TRUST = "no_trust" 
    NOT_AVAILABLE = "not_available"
    BOUGHT_ELSEWHERE = "bought_elsewhere"
    OTHER = "other"


class BlacklistReason(str, enum.Enum):
    """Blacklist reasons."""
    NO_SHOW = "no_show"
    REJECTED_AFTER_CONFIRM = "rejected_after_confirm"
    FAKE_DATA = "fake_data"
    OTHER = "other"
