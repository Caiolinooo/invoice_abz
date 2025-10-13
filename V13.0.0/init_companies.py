"""
Initialize companies in the database
Creates ABZ Group and ABZ International records
"""
import json
import sys
from pathlib import Path

# Add dev directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database.database import get_db_session, create_tables
from app.database.models import Company, Invoice

def init_companies():
    """Initialize company records in database"""
    print("🏢 Initializing Companies...")

    # Ensure tables exist
    create_tables()

    db = get_db_session()
    
    try:
        # Check if companies already exist
        existing = db.query(Company).filter(Company.id.in_([1, 2])).all()
        if existing:
            print(f"⚠️  Found {len(existing)} existing companies:")
            for comp in existing:
                print(f"   - ID {comp.id}: {comp.name}")

            response = input("\n❓ Do you want to update them? (y/n): ")
            if response.lower() != 'y':
                print("❌ Cancelled")
                return

            # Update existing companies instead of deleting
            print("🔄 Updating existing companies...")
            for comp in existing:
                if comp.id == 1:
                    comp.name = "ABZ Group"
                    comp.domain = "abzgroup.com"
                    comp.settings = json.dumps({
                        "clients": ["FMS", "OMEGA"],
                        "filename_format": "ABZ Group {invoice_no}-{year} {client} {month} {year} {first_name}",
                        "currency": "GBP",
                        "company_full_name": "ABZ Serviços Ltda",
                        "address": "UK Office Address",
                        "tax_id": "UK-TAX-ID",
                        "logo_path": "/assets/abz_group_logo.png"
                    })
                    comp.is_active = True
                    print("✅ Updated ABZ Group (ID: 1)")

            db.commit()

            # Check if ABZ International exists
            abz_intl = db.query(Company).filter(Company.id == 2).first()
            if not abz_intl:
                print("➕ Creating ABZ International...")
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
                db.commit()
                print("✅ Created ABZ International (ID: 2)")
            else:
                print("✅ ABZ International already exists")

            print("\n✅ Companies updated successfully!")
            return
        
        # Create ABZ Group
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
        
        # Create ABZ International
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
                "vessel_based": True  # Flag to indicate vessel-based structure
            }),
            is_active=True
        )
        
        db.add(abz_group)
        db.add(abz_intl)
        db.commit()
        
        print("\n✅ Companies created successfully!")
        print("\n📋 Company Details:")
        print(f"\n1️⃣  ABZ Group (ID: 1)")
        print(f"   - Clients: FMS, OMEGA")
        print(f"   - Format: ABZ Group {{invoice_no}}-{{year}} {{client}} {{month}} {{year}} {{first_name}}")
        print(f"   - Currency: GBP")
        
        print(f"\n2️⃣  ABZ International (ID: 2)")
        print(f"   - Clients: Jifmar Group")
        print(f"   - Format: ABZ International {{invoice_no}}-{{year}} {{vessel}} {{month}} {{year}} {{first_name}}")
        print(f"   - Currency: GBP")
        print(f"   - Vessel-based: Yes")
        
        print("\n🎉 Initialization complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def update_existing_invoices():
    """
    Update existing invoices to associate with ABZ Group (company_id=1)
    This ensures backward compatibility with existing data
    """
    print("\n🔄 Updating existing invoices...")

    db = get_db_session()
    
    try:
        # Count invoices without company_id
        count = db.query(Invoice).filter(Invoice.company_id == None).count()
        
        if count == 0:
            print("✅ No invoices need updating")
            return
        
        print(f"📊 Found {count} invoices without company_id")
        
        # Update all to ABZ Group (company_id=1)
        db.query(Invoice).filter(Invoice.company_id == None).update(
            {"company_id": 1},
            synchronize_session=False
        )
        db.commit()
        
        print(f"✅ Updated {count} invoices to ABZ Group (company_id=1)")
        
    except Exception as e:
        print(f"❌ Error updating invoices: {e}")
        db.rollback()
    finally:
        db.close()


def show_company_stats():
    """Show statistics for each company"""
    print("\n📊 Company Statistics:")

    db = get_db_session()
    
    try:
        from app.database.models import Invoice
        from sqlalchemy import func
        
        companies = db.query(Company).all()
        
        for company in companies:
            invoice_count = db.query(func.count(Invoice.id)).filter(
                Invoice.company_id == company.id
            ).scalar()
            
            total_amount = db.query(func.sum(Invoice.total_amount)).filter(
                Invoice.company_id == company.id
            ).scalar() or 0
            
            print(f"\n{company.name} (ID: {company.id}):")
            print(f"  - Invoices: {invoice_count}")
            print(f"  - Total Amount: £{total_amount:,.2f}")
            print(f"  - Active: {'Yes' if company.is_active else 'No'}")
        
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 80)
    print("🏢 COMPANY INITIALIZATION SCRIPT")
    print("=" * 80)
    
    # Initialize companies
    init_companies()
    
    # Update existing invoices
    update_existing_invoices()
    
    # Show stats
    show_company_stats()
    
    print("\n" + "=" * 80)
    print("✅ ALL DONE!")
    print("=" * 80)

