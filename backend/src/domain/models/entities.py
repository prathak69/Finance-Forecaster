import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import (
    String,
    Numeric,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    accounts: Mapped[List["Account"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    categories: Mapped[List["Category"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    budgets: Mapped[List["Budget"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    account_type: Mapped[str] = mapped_column(
        String(50), default="CHECKING", nullable=False
    )
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    current_balance: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=Decimal("0.00"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="accounts")
    transactions: Mapped[List["Transaction"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_system_default: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    user: Mapped[Optional["User"]] = relationship(back_populates="categories")
    transactions: Mapped[List["Transaction"]] = relationship(back_populates="category")


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    raw_description: Mapped[str] = mapped_column(String(500), nullable=False)
    cleaned_description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    # ML categorization flags
    ml_confidence: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 2), nullable=True
    )
    is_flagged_for_review: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Cryptographic hash to block duplicate imports
    composite_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    # Raw statement row backup
    raw_payload: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    account: Mapped["Account"] = relationship(back_populates="transactions")
    category: Mapped[Optional["Category"]] = relationship(back_populates="transactions")

    __table_args__ = (
        UniqueConstraint(
            "account_id", "composite_hash", name="uq_account_transaction_hash"
        ),
        Index("idx_txn_account_date", "account_id", "date"),
    )


class Budget(Base):
    __tablename__ = "budgets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
    )
    monthly_limit: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    current_spent: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=Decimal("0.00"), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="budgets")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    merchant_name: Mapped[str] = mapped_column(String(100), nullable=False)
    expected_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    billing_cycle: Mapped[str] = mapped_column(
        String(20), default="MONTHLY", nullable=False
    )  # WEEKLY, MONTHLY, ANNUAL
    next_renewal_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
