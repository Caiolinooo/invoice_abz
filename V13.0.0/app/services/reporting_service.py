"""
Advanced Reporting Service
Provides detailed financial reports by company, client, period, etc.
"""
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from datetime import datetime, timedelta
from app.database.models import Invoice, Company, Client
import calendar


class ReportingService:
    """Service for generating financial reports"""
    
    @staticmethod
    def get_company_summary(
        db: Session,
        company_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get summary report for a company or all companies
        
        Returns:
        {
            "total_revenue": float,
            "total_invoices": int,
            "by_company": {...},
            "by_client": {...},
            "by_month": [...]
        }
        """
        query = db.query(Invoice)
        
        # Apply filters
        if company_id:
            query = query.filter(Invoice.company_id == company_id)
        if date_from:
            query = query.filter(Invoice.invoice_date >= date_from)
        if date_to:
            query = query.filter(Invoice.invoice_date <= date_to)
        
        invoices = query.all()
        
        # Calculate totals
        total_revenue = sum(inv.total_amount or 0 for inv in invoices)
        total_invoices = len(invoices)
        
        # Group by company
        by_company = {}
        for inv in invoices:
            comp_id = inv.company_id
            if comp_id not in by_company:
                company = db.query(Company).filter(Company.id == comp_id).first()
                by_company[comp_id] = {
                    "company_name": company.name if company else f"Company {comp_id}",
                    "revenue": 0,
                    "invoices": 0,
                    "employees": set()
                }
            
            by_company[comp_id]["revenue"] += inv.total_amount or 0
            by_company[comp_id]["invoices"] += 1
            by_company[comp_id]["employees"].add(inv.employee_name)
        
        # Convert sets to counts
        for comp_data in by_company.values():
            comp_data["employees"] = len(comp_data["employees"])
        
        # Group by client
        by_client = {}
        for inv in invoices:
            client_id = inv.client_id or "Unknown"
            client_name = inv.client_name or "Unknown"
            
            if client_id not in by_client:
                by_client[client_id] = {
                    "client_name": client_name,
                    "revenue": 0,
                    "invoices": 0,
                    "employees": set(),
                    "category": inv.client_category or "uncategorized"
                }
            
            by_client[client_id]["revenue"] += inv.total_amount or 0
            by_client[client_id]["invoices"] += 1
            by_client[client_id]["employees"].add(inv.employee_name)
        
        # Convert sets to counts
        for client_data in by_client.values():
            client_data["employees"] = len(client_data["employees"])
        
        # Group by month
        by_month = {}
        for inv in invoices:
            if inv.invoice_date:
                month_key = inv.invoice_date.strftime("%Y-%m")
                if month_key not in by_month:
                    by_month[month_key] = {
                        "month": month_key,
                        "revenue": 0,
                        "invoices": 0
                    }
                
                by_month[month_key]["revenue"] += inv.total_amount or 0
                by_month[month_key]["invoices"] += 1
        
        # Sort by month
        by_month_list = sorted(by_month.values(), key=lambda x: x["month"])
        
        return {
            "total_revenue": round(total_revenue, 2),
            "total_invoices": total_invoices,
            "by_company": by_company,
            "by_client": by_client,
            "by_month": by_month_list
        }
    
    @staticmethod
    def get_client_detailed_report(
        db: Session,
        client_id: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get detailed report for a specific client
        
        Includes:
        - Revenue breakdown (base, overtime, expenses, etc.)
        - Employee list with totals
        - Monthly trends
        - Invoice status breakdown
        """
        query = db.query(Invoice).filter(Invoice.client_id == client_id)
        
        if date_from:
            query = query.filter(Invoice.invoice_date >= date_from)
        if date_to:
            query = query.filter(Invoice.invoice_date <= date_to)
        
        invoices = query.all()
        
        if not invoices:
            return {
                "client_id": client_id,
                "error": "No invoices found for this client"
            }
        
        # Basic info
        first_invoice = invoices[0]
        client_name = first_invoice.client_name or client_id
        company_id = first_invoice.company_id
        
        # Financial breakdown
        total_revenue = sum(inv.total_amount or 0 for inv in invoices)
        base_amount = sum(inv.base_amount or 0 for inv in invoices)
        overtime_amount = sum(inv.overtime_amount or 0 for inv in invoices)
        expenses_amount = sum(inv.expenses_amount or 0 for inv in invoices)
        insurance_amount = sum(inv.insurance_amount or 0 for inv in invoices)
        other_amount = sum(inv.other_amount or 0 for inv in invoices)
        
        # Employee breakdown
        by_employee = {}
        for inv in invoices:
            emp_name = inv.employee_name
            if emp_name not in by_employee:
                by_employee[emp_name] = {
                    "name": emp_name,
                    "position": inv.employee_position or "Unknown",
                    "invoices": 0,
                    "total_amount": 0
                }
            
            by_employee[emp_name]["invoices"] += 1
            by_employee[emp_name]["total_amount"] += inv.total_amount or 0
        
        # Status breakdown
        by_status = {}
        for inv in invoices:
            status = inv.status or "unknown"
            by_status[status] = by_status.get(status, 0) + 1
        
        # Monthly trend
        by_month = {}
        for inv in invoices:
            if inv.invoice_date:
                month_key = inv.invoice_date.strftime("%Y-%m")
                if month_key not in by_month:
                    by_month[month_key] = {
                        "month": month_key,
                        "revenue": 0,
                        "invoices": 0,
                        "employees": set()
                    }
                
                by_month[month_key]["revenue"] += inv.total_amount or 0
                by_month[month_key]["invoices"] += 1
                by_month[month_key]["employees"].add(inv.employee_name)
        
        # Convert sets to counts
        for month_data in by_month.values():
            month_data["employees"] = len(month_data["employees"])
        
        by_month_list = sorted(by_month.values(), key=lambda x: x["month"])
        
        return {
            "client_id": client_id,
            "client_name": client_name,
            "company_id": company_id,
            "period": {
                "from": date_from.isoformat() if date_from else None,
                "to": date_to.isoformat() if date_to else None
            },
            "summary": {
                "total_revenue": round(total_revenue, 2),
                "total_invoices": len(invoices),
                "total_employees": len(by_employee)
            },
            "financial_breakdown": {
                "base_amount": round(base_amount, 2),
                "overtime_amount": round(overtime_amount, 2),
                "expenses_amount": round(expenses_amount, 2),
                "insurance_amount": round(insurance_amount, 2),
                "other_amount": round(other_amount, 2)
            },
            "by_employee": list(by_employee.values()),
            "by_status": by_status,
            "monthly_trend": by_month_list
        }
    
    @staticmethod
    def get_combined_report(
        db: Session,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get combined report across all companies and clients
        Perfect for annual/monthly reports
        """
        # Get all companies
        companies = db.query(Company).filter(Company.is_active == True).all()
        
        combined_data = {
            "period": {
                "from": date_from.isoformat() if date_from else None,
                "to": date_to.isoformat() if date_to else None
            },
            "grand_total": 0,
            "total_invoices": 0,
            "by_company": {},
            "by_client": {},
            "by_category": {},
            "top_clients": [],
            "monthly_comparison": []
        }
        
        for company in companies:
            company_report = ReportingService.get_company_summary(
                db, company.id, date_from, date_to
            )
            
            combined_data["grand_total"] += company_report["total_revenue"]
            combined_data["total_invoices"] += company_report["total_invoices"]
            
            combined_data["by_company"][company.name] = {
                "revenue": company_report["total_revenue"],
                "invoices": company_report["total_invoices"],
                "clients": len(company_report["by_client"])
            }
            
            # Merge client data
            for client_id, client_data in company_report["by_client"].items():
                combined_data["by_client"][client_id] = client_data
                
                # Group by category
                category = client_data.get("category", "uncategorized")
                if category not in combined_data["by_category"]:
                    combined_data["by_category"][category] = {
                        "revenue": 0,
                        "invoices": 0,
                        "clients": 0
                    }
                
                combined_data["by_category"][category]["revenue"] += client_data["revenue"]
                combined_data["by_category"][category]["invoices"] += client_data["invoices"]
                combined_data["by_category"][category]["clients"] += 1
        
        # Top clients by revenue
        top_clients = sorted(
            combined_data["by_client"].items(),
            key=lambda x: x[1]["revenue"],
            reverse=True
        )[:10]
        
        combined_data["top_clients"] = [
            {
                "client_id": client_id,
                "client_name": data["client_name"],
                "revenue": round(data["revenue"], 2),
                "invoices": data["invoices"]
            }
            for client_id, data in top_clients
        ]
        
        # Round totals
        combined_data["grand_total"] = round(combined_data["grand_total"], 2)
        
        return combined_data


if __name__ == "__main__":
    print("📊 Reporting Service - Ready for use!")
    print("\nAvailable reports:")
    print("  - get_company_summary() - Summary by company")
    print("  - get_client_detailed_report() - Detailed client report")
    print("  - get_combined_report() - Combined report across all companies")

