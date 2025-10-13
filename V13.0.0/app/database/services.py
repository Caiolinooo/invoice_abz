"""
Database services for CRUD operations
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from datetime import datetime, timedelta
from .models import (
    Company, User, Invoice, Template, Configuration, 
    Session as SessionModel, EmailLog
)


class InvoiceService:
    """Service for invoice operations"""
    
    @staticmethod
    def create_invoice(db: Session, invoice_data: Dict[str, Any]) -> Invoice:
        """Create a new invoice record"""
        invoice = Invoice(**invoice_data)
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        return invoice
    
    @staticmethod
    def get_invoices(
        db: Session, 
        company_id: int,
        skip: int = 0, 
        limit: int = 100,
        employee_name: Optional[str] = None,
        status: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Invoice]:
        """Get invoices with filters"""
        query = db.query(Invoice).filter(Invoice.company_id == company_id)
        
        if employee_name:
            query = query.filter(Invoice.employee_name.ilike(f"%{employee_name}%"))
        
        if status:
            query = query.filter(Invoice.status == status)
        
        if date_from:
            query = query.filter(Invoice.invoice_date >= date_from)
        
        if date_to:
            query = query.filter(Invoice.invoice_date <= date_to)
        
        return query.order_by(desc(Invoice.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_invoice_by_id(db: Session, invoice_id: int, company_id: int) -> Optional[Invoice]:
        """Get invoice by ID"""
        return db.query(Invoice).filter(
            and_(Invoice.id == invoice_id, Invoice.company_id == company_id)
        ).first()
    
    @staticmethod
    def update_invoice_status(db: Session, invoice_id: int, company_id: int, status: str) -> Optional[Invoice]:
        """Update invoice status"""
        invoice = InvoiceService.get_invoice_by_id(db, invoice_id, company_id)
        if invoice:
            invoice.status = status
            invoice.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(invoice)
        return invoice

    @staticmethod
    def get_last_invoice_number(db: Session, company_id: int) -> Optional[Invoice]:
        """Get the invoice with the highest number for sequence suggestion"""
        return db.query(Invoice).filter(
            Invoice.company_id == company_id
        ).order_by(desc(Invoice.created_at)).first()

    @staticmethod
    def get_invoice_stats(db: Session, company_id: int) -> Dict[str, Any]:
        """Get invoice statistics"""
        total_invoices = db.query(func.count(Invoice.id)).filter(
            Invoice.company_id == company_id
        ).scalar()

        total_amount = db.query(func.sum(Invoice.total_amount)).filter(
            and_(Invoice.company_id == company_id, Invoice.total_amount.isnot(None))
        ).scalar() or 0

        # Last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_invoices = db.query(func.count(Invoice.id)).filter(
            and_(
                Invoice.company_id == company_id,
                Invoice.created_at >= thirty_days_ago
            )
        ).scalar()

        # Current month revenue (based on invoice_date)
        now = datetime.utcnow()
        current_month_start = datetime(now.year, now.month, 1)

        # Calculate next month start
        if now.month == 12:
            next_month_start = datetime(now.year + 1, 1, 1)
        else:
            next_month_start = datetime(now.year, now.month + 1, 1)

        current_month_amount = db.query(func.sum(Invoice.total_amount)).filter(
            and_(
                Invoice.company_id == company_id,
                Invoice.invoice_date >= current_month_start,
                Invoice.invoice_date < next_month_start,
                Invoice.total_amount.isnot(None)
            )
        ).scalar() or 0

        # Last month revenue (based on invoice_date)
        if now.month == 1:
            last_month_start = datetime(now.year - 1, 12, 1)
            last_month_end = datetime(now.year, 1, 1)
        else:
            last_month_start = datetime(now.year, now.month - 1, 1)
            last_month_end = datetime(now.year, now.month, 1)

        last_month_amount = db.query(func.sum(Invoice.total_amount)).filter(
            and_(
                Invoice.company_id == company_id,
                Invoice.invoice_date >= last_month_start,
                Invoice.invoice_date < last_month_end,
                Invoice.total_amount.isnot(None)
            )
        ).scalar() or 0

        # Status breakdown
        status_counts = db.query(
            Invoice.status, func.count(Invoice.id)
        ).filter(
            Invoice.company_id == company_id
        ).group_by(Invoice.status).all()

        return {
            "total_invoices": total_invoices,
            "total_amount": float(total_amount),
            "current_month_amount": float(current_month_amount),
            "last_month_amount": float(last_month_amount),
            "recent_invoices": recent_invoices,
            "status_breakdown": dict(status_counts)
        }


class ConfigurationService:
    """Service for configuration operations"""
    
    @staticmethod
    def get_config(db: Session, company_id: int, key: str) -> Optional[Configuration]:
        """Get configuration by key"""
        return db.query(Configuration).filter(
            and_(Configuration.company_id == company_id, Configuration.key == key)
        ).first()
    
    @staticmethod
    def get_configs_by_type(db: Session, company_id: int, config_type: str) -> List[Configuration]:
        """Get configurations by type"""
        return db.query(Configuration).filter(
            and_(Configuration.company_id == company_id, Configuration.config_type == config_type)
        ).all()
    
    @staticmethod
    def set_config(db: Session, company_id: int, key: str, value: str, 
                   description: str = None, config_type: str = "general") -> Configuration:
        """Set configuration value"""
        config = ConfigurationService.get_config(db, company_id, key)
        
        if config:
            config.value = value
            config.updated_at = datetime.utcnow()
            if description:
                config.description = description
        else:
            config = Configuration(
                company_id=company_id,
                key=key,
                value=value,
                description=description,
                config_type=config_type
            )
            db.add(config)
        
        db.commit()
        db.refresh(config)
        return config
    
    @staticmethod
    def get_all_configs(db: Session, company_id: int) -> Dict[str, str]:
        """Get all configurations as key-value dict"""
        configs = db.query(Configuration).filter(Configuration.company_id == company_id).all()
        return {config.key: config.value for config in configs}


class TemplateService:
    """Service for template operations"""
    
    @staticmethod
    def create_template(db: Session, template_data: Dict[str, Any]) -> Template:
        """Create a new template"""
        template = Template(**template_data)
        db.add(template)
        db.commit()
        db.refresh(template)
        return template
    
    @staticmethod
    def get_templates(db: Session, company_id: int) -> List[Template]:
        """Get all templates for company"""
        return db.query(Template).filter(Template.company_id == company_id).all()
    
    @staticmethod
    def get_default_template(db: Session, company_id: int) -> Optional[Template]:
        """Get default template for company"""
        return db.query(Template).filter(
            and_(Template.company_id == company_id, Template.is_default == True)
        ).first()
    
    @staticmethod
    def set_default_template(db: Session, company_id: int, template_id: int) -> bool:
        """Set template as default"""
        # Remove default from all templates
        db.query(Template).filter(Template.company_id == company_id).update(
            {"is_default": False}
        )
        
        # Set new default
        template = db.query(Template).filter(
            and_(Template.id == template_id, Template.company_id == company_id)
        ).first()
        
        if template:
            template.is_default = True
            db.commit()
            return True
        return False


class SessionService:
    """Service for session operations"""
    
    @staticmethod
    def create_session(db: Session, session_data: Dict[str, Any]) -> SessionModel:
        """Create a new session"""
        session = SessionModel(**session_data)
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    @staticmethod
    def get_session(db: Session, session_id: str, company_id: int) -> Optional[SessionModel]:
        """Get session by ID"""
        return db.query(SessionModel).filter(
            and_(SessionModel.session_id == session_id, SessionModel.company_id == company_id)
        ).first()
    
    @staticmethod
    def update_session_status(db: Session, session_id: str, company_id: int, 
                            status: str, invoices_generated: int = None) -> Optional[SessionModel]:
        """Update session status"""
        session = SessionService.get_session(db, session_id, company_id)
        if session:
            session.status = status
            if invoices_generated is not None:
                session.invoices_generated = invoices_generated
            session.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(session)
        return session


class EmailLogService:
    """Service for email log operations"""
    
    @staticmethod
    def log_email(db: Session, email_data: Dict[str, Any]) -> EmailLog:
        """Log email sending attempt"""
        email_log = EmailLog(**email_data)
        db.add(email_log)
        db.commit()
        db.refresh(email_log)
        return email_log
    
    @staticmethod
    def update_email_status(db: Session, log_id: int, status: str, 
                          error_message: str = None) -> Optional[EmailLog]:
        """Update email sending status"""
        email_log = db.query(EmailLog).filter(EmailLog.id == log_id).first()
        if email_log:
            email_log.status = status
            email_log.error_message = error_message
            if status == "sent":
                email_log.sent_at = datetime.utcnow()
            db.commit()
            db.refresh(email_log)
        return email_log
