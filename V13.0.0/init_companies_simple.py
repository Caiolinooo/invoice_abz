"""
Simple company initialization - no prompts
"""
import json
import sys
from pathlib import Path

# Add dev directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database.database import get_db_session, create_tables
from app.database.models import Company, Invoice

def init_companies_simple():
    """Initialize companies without prompts"""
    print("=" * 80)
    print("🏢 COMPANY INITIALIZATION")
    print("=" * 80)
    
    # Ensure tables exist
    create_tables()
    
    db = get_db_session()
    
    try:
        # Update or create ABZ Group (ID=1)
        abz_group = db.query(Company).filter(Company.id == 1).first()
        
        if abz_group:
            print(f"\n🔄 Updating existing company: {abz_group.name}")
            abz_group.name = "ABZ Group"
            abz_group.domain = "abzgroup.com"
            abz_group.settings = json.dumps({
                "clients": ["FMS", "OMEGA"],
                "filename_format": "ABZ Group {invoice_no}-{year} {client} {month} {year} {first_name}",
                "currency": "GBP",
                "company_full_name": "ABZ Serviços Ltda",
                "address": "UK Office Address",
                "tax_id": "UK-TAX-ID",
                "logo_path": "/assets/abz_group_logo.png"
            })
            abz_group.is_active = True
            print("✅ Updated ABZ Group (ID: 1)")
        else:
            print("\n➕ Creating ABZ Group...")
            abz_group = Company(
                id=1,
                name="ABZ Group",
                domain="abzgroup.com",
                settings=json.dumps({
                    "clients": ["FMS", "OMEGA"],
                    "filename_format": "ABZ Group {invoice_no}-{year} {client} {month} {year} {first_name}",
                    "currency": "GBP",
                    "company_full_name": "ABZ Serviços Ltda",
                    "address": "UK Office Address",
                    "tax_id": "UK-TAX-ID",
                    "logo_path": "/assets/abz_group_logo.png"
                }),
                is_active=True
            )
            db.add(abz_group)
            print("✅ Created ABZ Group (ID: 1)")
        
        db.commit()
        
        # Create or update ABZ International (ID=2)
        abz_intl = db.query(Company).filter(Company.id == 2).first()
        
        if abz_intl:
            print(f"\n🔄 Updating existing company: {abz_intl.name}")
            abz_intl.name = "ABZ International"
            abz_intl.domain = "abzinternational.com"
            abz_intl.settings = json.dumps({
                "clients": ["Jifmar Group"],
                "filename_format": "ABZ International {invoice_no}-{year} {vessel} {month} {year} {first_name}",
                "currency": "GBP",
                "company_full_name": "ABZ International Ltd",
                "address": "International Office Address",
                "tax_id": "INTL-TAX-ID",
                "logo_path": "/assets/abz_international_logo.png",
                "vessel_based": True
            })
            abz_intl.is_active = True
            print("✅ Updated ABZ International (ID: 2)")
        else:
            print("\n➕ Creating ABZ International...")
            abz_intl = Company(
                id=2,
                name="ABZ International",
                domain="abzinternational.com",
                settings=json.dumps({
                    "clients": ["Jifmar Group"],
                    "filename_format": "ABZ International {invoice_no}-{year} {vessel} {month} {year} {first_name}",
                    "currency": "GBP",
                    "company_full_name": "ABZ International Ltd",
                    "address": "International Office Address",
                    "tax_id": "INTL-TAX-ID",
                    "logo_path": "/assets/abz_international_logo.png",
                    "vessel_based": True
                }),
                is_active=True
            )
            db.add(abz_intl)
            print("✅ Created ABZ International (ID: 2)")
        
        db.commit()
        
        # Show summary
        print("\n" + "=" * 80)
        print("📋 COMPANY SUMMARY")
        print("=" * 80)
        
        companies = db.query(Company).all()
        for company in companies:
            print(f"\n{company.id}. {company.name}")
            print(f"   Domain: {company.domain}")
            print(f"   Active: {'Yes' if company.is_active else 'No'}")
            
            if company.settings:
                settings = json.loads(company.settings)
                if 'clients' in settings:
                    print(f"   Clients: {', '.join(settings['clients'])}")
        
        # Update existing invoices to ABZ Group
        print("\n" + "=" * 80)
        print("🔄 UPDATING EXISTING INVOICES")
        print("=" * 80)
        
        # Count invoices without company_id
        count = db.query(Invoice).filter(Invoice.company_id == None).count()
        
        if count > 0:
            print(f"\n📊 Found {count} invoices without company_id")
            print("🔄 Assigning to ABZ Group (company_id=1)...")
            
            db.query(Invoice).filter(Invoice.company_id == None).update(
                {"company_id": 1},
                synchronize_session=False
            )
            db.commit()
            
            print(f"✅ Updated {count} invoices")
        else:
            print("\n✅ All invoices already have company_id")
        
        # Show invoice stats
        print("\n" + "=" * 80)
        print("📊 INVOICE STATISTICS")
        print("=" * 80)
        
        from sqlalchemy import func
        
        for company in companies:
            invoice_count = db.query(func.count(Invoice.id)).filter(
                Invoice.company_id == company.id
            ).scalar()
            
            total_amount = db.query(func.sum(Invoice.total_amount)).filter(
                Invoice.company_id == company.id
            ).scalar() or 0
            
            print(f"\n{company.name} (ID: {company.id}):")
            print(f"  Invoices: {invoice_count}")
            print(f"  Total Amount: £{total_amount:,.2f}")
        
        print("\n" + "=" * 80)
        print("✅ INITIALIZATION COMPLETE!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_companies_simple()

