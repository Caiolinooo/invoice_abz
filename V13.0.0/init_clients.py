"""
Initialize client profiles in the database
"""
import json
import sys
from pathlib import Path

# Add dev directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database.database import get_db_session, create_tables
from app.database.models import Client
from app.models.client_profile import get_client_profile_manager, SpreadsheetFormat, InvoiceFormat


def init_clients():
    """Initialize client profiles in database"""
    print("=" * 80)
    print("👥 CLIENT PROFILES INITIALIZATION")
    print("=" * 80)
    
    # Ensure tables exist
    create_tables()
    
    db = get_db_session()
    
    try:
        # Get client profiles from manager
        manager = get_client_profile_manager()
        profiles = manager.get_all_active_profiles()
        
        print(f"\n📋 Found {len(profiles)} client profiles to initialize")
        
        created = 0
        updated = 0
        
        for profile in profiles:
            # Check if client already exists
            existing = db.query(Client).filter(Client.client_id == profile.client_id).first()
            
            if existing:
                # Update existing
                print(f"\n🔄 Updating: {profile.client_name}")
                existing.client_name = profile.client_name
                existing.company_id = profile.company_id
                existing.spreadsheet_format = profile.spreadsheet_format.value
                existing.invoice_format = profile.invoice_format.value
                existing.filename_template = profile.filename_template
                existing.currency = profile.currency
                existing.tax_rate = profile.tax_rate
                existing.category = profile.category
                existing.subcategory = profile.subcategory
                existing.config_json = json.dumps({
                    "spreadsheet_patterns": profile.spreadsheet_patterns,
                    "parser_config": profile.parser_config
                })
                existing.is_active = profile.is_active
                updated += 1
            else:
                # Create new
                print(f"\n➕ Creating: {profile.client_name}")
                new_client = Client(
                    client_id=profile.client_id,
                    client_name=profile.client_name,
                    company_id=profile.company_id,
                    spreadsheet_format=profile.spreadsheet_format.value,
                    invoice_format=profile.invoice_format.value,
                    filename_template=profile.filename_template,
                    currency=profile.currency,
                    tax_rate=profile.tax_rate,
                    category=profile.category,
                    subcategory=profile.subcategory,
                    config_json=json.dumps({
                        "spreadsheet_patterns": profile.spreadsheet_patterns,
                        "parser_config": profile.parser_config
                    }),
                    is_active=profile.is_active
                )
                db.add(new_client)
                created += 1
        
        db.commit()
        
        print("\n" + "=" * 80)
        print("📊 CLIENT SUMMARY")
        print("=" * 80)
        
        # Show all clients grouped by company
        print("\n🏢 ABZ Group Clients:")
        abz_group_clients = db.query(Client).filter(Client.company_id == 1).all()
        for client in abz_group_clients:
            print(f"  ✅ {client.client_name} ({client.client_id})")
            print(f"     Format: {client.spreadsheet_format}")
            print(f"     Category: {client.category}")
        
        print("\n🌍 ABZ International Clients:")
        abz_intl_clients = db.query(Client).filter(Client.company_id == 2).all()
        for client in abz_intl_clients:
            print(f"  ✅ {client.client_name} ({client.client_id})")
            print(f"     Format: {client.spreadsheet_format}")
            print(f"     Vessel: {client.subcategory}")
        
        print("\n" + "=" * 80)
        print(f"✅ INITIALIZATION COMPLETE!")
        print(f"   Created: {created} clients")
        print(f"   Updated: {updated} clients")
        print(f"   Total: {created + updated} clients")
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
    init_clients()

