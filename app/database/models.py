"""
Database models for the Invoice System
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import json

Base = declarative_base()


class Company(Base):
    """Company/Tenant model for multi-tenant support"""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), unique=True, nullable=True)
    logo_path = Column(String(500), nullable=True)
    settings = Column(Text, nullable=True)  # JSON string
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="company")
    invoices = relationship("Invoice", back_populates="company")
    templates = relationship("Template", back_populates="company")
    configurations = relationship("Configuration", back_populates="company")


class User(Base):
    """User model with company association"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    role = Column(String(50), default="user")  # admin, user, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="users")


class Invoice(Base):
    """Invoice tracking model"""
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    session_id = Column(String(255), nullable=False, index=True)
    invoice_number = Column(String(100), nullable=False)
    employee_name = Column(String(255), nullable=False)
    employee_position = Column(String(255), nullable=True)
    invoice_date = Column(DateTime, nullable=False)
    call_off = Column(String(255), nullable=True)
    
    # File paths
    file_path_xlsx = Column(String(500), nullable=True)
    file_path_pdf = Column(String(500), nullable=True)
    
    # Financial data
    total_amount = Column(Float, nullable=True)
    currency = Column(String(10), default="GBP")
    
    # Status and metadata
    status = Column(String(50), default="generated")  # generated, sent, paid, cancelled
    invoice_metadata = Column(Text, nullable=True)  # JSON string for additional data
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="invoices")


class Template(Base):
    """Template management model"""
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=False)
    is_default = Column(Boolean, default=False)
    client_specific = Column(String(255), nullable=True)  # For client-specific templates
    version = Column(String(50), default="1.0")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="templates")


class Configuration(Base):
    """System configuration model"""
    __tablename__ = "configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    key = Column(String(255), nullable=False)
    value = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    config_type = Column(String(50), default="general")  # general, email, template, ui
    is_encrypted = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="configurations")


class Session(Base):
    """Session tracking model"""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    abz_filename = Column(String(255), nullable=True)
    anfin_filename = Column(String(255), nullable=True)
    status = Column(String(50), default="active")  # active, completed, failed
    employee_count = Column(Integer, default=0)
    invoices_generated = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company")


class EmailLog(Base):
    """Email sending log"""
    __tablename__ = "email_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    recipient_email = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=False)
    status = Column(String(50), default="pending")  # pending, sent, failed
    error_message = Column(Text, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    company = relationship("Company")
    invoice = relationship("Invoice")


class AuditLog(Base):
    """Audit log for security and compliance"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=True)  # UUID from Supabase
    user_email = Column(String(255), nullable=True)
    action = Column(String(100), nullable=False)  # login, logout, access_denied, etc.
    resource = Column(String(255), nullable=True)  # Resource accessed (e.g., /api/invoices)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)
    success = Column(Boolean, default=True)
    details = Column(Text, nullable=True)  # Additional details (JSON string)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
