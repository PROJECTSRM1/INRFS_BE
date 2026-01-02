from typing import Optional
import datetime
import decimal

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Double, ForeignKeyConstraint, Index, Integer, Numeric, PrimaryKeyConstraint, String, UniqueConstraint, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class MasterBank(Base):
    __tablename__ = 'master_bank'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_master_bank_id'),
        UniqueConstraint('bank_name', name='uk_master_bank_bank_name')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bank_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('true'))

    user_registration: Mapped[list['UserRegistration']] = relationship('UserRegistration', back_populates='bank')


class MasterGender(Base):
    __tablename__ = 'master_gender'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_master_gender_id'),
        UniqueConstraint('gender_name', name='uk_master_gender_gender_name')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    gender_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('true'))

    user_registration: Mapped[list['UserRegistration']] = relationship('UserRegistration', back_populates='gender')


class MasterPlanType(Base):
    __tablename__ = 'master_plan_type'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_master_plan_type_id'),
        UniqueConstraint('plan_type', name='uk_master_plan_type_plan_type')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plan_type: Mapped[str] = mapped_column(String(255), nullable=False)
    percentage: Mapped[str] = mapped_column(String(10), nullable=False)
    returns_in_days: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('true'))

    inv_config: Mapped[list['InvConfig']] = relationship('InvConfig', back_populates='plan_type')


class MasterRole(Base):
    __tablename__ = 'master_role'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_master_role_id'),
        UniqueConstraint('role_name', name='uk_master_role_role_name')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('true'))

    user_registration: Mapped[list['UserRegistration']] = relationship('UserRegistration', back_populates='role')


class Plans(Base):
    __tablename__ = 'plans'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='plans_pkey'),
        UniqueConstraint('name', name='plans_name_key'),
        Index('ix_plans_id', 'id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    returns_percentage: Mapped[float] = mapped_column(Double(53), nullable=False)
    duration_months: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String)
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('now()'))


class InvConfig(Base):
    __tablename__ = 'inv_config'
    __table_args__ = (
        ForeignKeyConstraint(['plan_type_id'], ['master_plan_type.id'], name='fk_inv_config_plan_type_id'),
        PrimaryKeyConstraint('id', name='pk_inv_config_id'),
        UniqueConstraint('uk_inv_id', name='uk_inv_config_uk_inv_id')
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    principal_amount: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    plan_type_id: Mapped[int] = mapped_column(Integer, nullable=False)
    interest_amount: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    maturity_amount: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    uk_inv_id: Mapped[str] = mapped_column(String(255), nullable=False)
    maturity_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    created_by: Mapped[Optional[int]] = mapped_column(BigInteger)
    created_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('now()'))
    modified_by: Mapped[Optional[int]] = mapped_column(BigInteger)
    modified_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('true'))
    upload_file: Mapped[Optional[str]] = mapped_column(String(500))

    plan_type: Mapped['MasterPlanType'] = relationship('MasterPlanType', back_populates='inv_config')


class UserRegistration(Base):
    __tablename__ = 'user_registration'
    __table_args__ = (
        ForeignKeyConstraint(['bank_id'], ['master_bank.id'], name='fk_user_registration_bank_id'),
        ForeignKeyConstraint(['gender_id'], ['master_gender.id'], name='fk_user_registration_gender_id'),
        ForeignKeyConstraint(['role_id'], ['master_role.id'], name='fk_user_registration_role_id'),
        PrimaryKeyConstraint('id', name='pk_user_registration_id'),
        UniqueConstraint('email', name='uk_user_registration_email'),
        UniqueConstraint('inv_reg_id', name='uk_user_registration_inv_reg_id'),
        UniqueConstraint('mobile', name='uk_user_registration_mobile')
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    mobile: Mapped[str] = mapped_column(String(255), nullable=False)
    password: Mapped[str] = mapped_column(String(500), nullable=False)
    gender_id: Mapped[int] = mapped_column(Integer, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    dob: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    inv_reg_id: Mapped[str] = mapped_column(String(255), nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, nullable=False)
    created_by: Mapped[Optional[int]] = mapped_column(BigInteger)
    created_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('now()'))
    modified_by: Mapped[Optional[int]] = mapped_column(BigInteger)
    modified_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('true'))
    is_verified: Mapped[Optional[bool]] = mapped_column(Boolean)
    bank_id: Mapped[Optional[int]] = mapped_column(Integer)
    bank_account_no: Mapped[Optional[int]] = mapped_column(Integer)
    ifsc_code: Mapped[Optional[str]] = mapped_column(String(100))

    bank: Mapped[Optional['MasterBank']] = relationship('MasterBank', back_populates='user_registration')
    gender: Mapped['MasterGender'] = relationship('MasterGender', back_populates='user_registration')
    role: Mapped['MasterRole'] = relationship('MasterRole', back_populates='user_registration')
