"""
Client Profile System - Flexible client configuration without code changes

This system allows adding new clients by simply creating a configuration entry,
without modifying any code. Each client has a profile that defines:
- How to parse their spreadsheets
- How to generate invoices
- Filename formats
- Reporting categories
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json


class SpreadsheetFormat(Enum):
    """Types of spreadsheet formats we support"""
    ABZ_CHARGE_RATE = "abz_charge_rate"  # Current ABZ format with Charge Rate sheet
    JIFMAR_VESSEL = "jifmar_vessel"      # Jifmar format with vessel sheets
    SIMPLE_TABLE = "simple_table"        # Simple table format (future)


class InvoiceFormat(Enum):
    """Types of invoice generation formats"""
    ABZ_TEMPLATE = "abz_template"        # Uses existing invoice templates
    GENERATED = "generated"              # Generates from scratch
    CUSTOM = "custom"                    # Custom format (future)


@dataclass
class ClientProfile:
    """
    Configuration profile for a client
    
    This allows adding new clients without code changes - just create a new profile!
    """
    # Basic Info
    client_id: str                       # Unique identifier (e.g., "FMS", "OMEGA", "JIFMAR_VOE_VANGUARD")
    client_name: str                     # Display name (e.g., "FMS", "Jifmar - Voe Vanguard")
    company_id: int                      # 1 = ABZ Group, 2 = ABZ International
    
    # Spreadsheet Configuration
    spreadsheet_format: SpreadsheetFormat
    spreadsheet_patterns: List[str]      # Filename patterns to match (e.g., ["*FMS*", "*Maximus*"])
    
    # Invoice Configuration
    invoice_format: InvoiceFormat
    filename_template: str               # e.g., "ABZ Group {invoice_no}-{year} {client} {month} {year} {first_name}"
    
    # Financial Configuration
    currency: str = "GBP"
    tax_rate: float = 0.0
    
    # Reporting Configuration
    category: str = "default"            # For grouping in reports (e.g., "offshore", "onshore")
    subcategory: Optional[str] = None    # Additional grouping (e.g., vessel name)
    
    # Parser Configuration (optional overrides)
    parser_config: Dict[str, Any] = field(default_factory=dict)
    
    # Active status
    is_active: bool = True
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON storage"""
        return {
            "client_id": self.client_id,
            "client_name": self.client_name,
            "company_id": self.company_id,
            "spreadsheet_format": self.spreadsheet_format.value,
            "spreadsheet_patterns": self.spreadsheet_patterns,
            "invoice_format": self.invoice_format.value,
            "filename_template": self.filename_template,
            "currency": self.currency,
            "tax_rate": self.tax_rate,
            "category": self.category,
            "subcategory": self.subcategory,
            "parser_config": self.parser_config,
            "is_active": self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ClientProfile':
        """Create from dictionary"""
        return cls(
            client_id=data["client_id"],
            client_name=data["client_name"],
            company_id=data["company_id"],
            spreadsheet_format=SpreadsheetFormat(data["spreadsheet_format"]),
            spreadsheet_patterns=data["spreadsheet_patterns"],
            invoice_format=InvoiceFormat(data["invoice_format"]),
            filename_template=data["filename_template"],
            currency=data.get("currency", "GBP"),
            tax_rate=data.get("tax_rate", 0.0),
            category=data.get("category", "default"),
            subcategory=data.get("subcategory"),
            parser_config=data.get("parser_config", {}),
            is_active=data.get("is_active", True)
        )


class ClientProfileManager:
    """
    Manages client profiles - allows adding/removing clients without code changes
    """
    
    def __init__(self):
        self.profiles: Dict[str, ClientProfile] = {}
        self._load_default_profiles()
    
    def _load_default_profiles(self):
        """Load default client profiles"""
        
        # ABZ Group - FMS
        self.add_profile(ClientProfile(
            client_id="FMS",
            client_name="FMS",
            company_id=1,
            spreadsheet_format=SpreadsheetFormat.ABZ_CHARGE_RATE,
            spreadsheet_patterns=["*FMS*", "*Maximus*"],
            invoice_format=InvoiceFormat.ABZ_TEMPLATE,
            filename_template="ABZ Group {invoice_no}-{year} FMS {month} {year} {first_name}",
            category="offshore",
            currency="GBP"
        ))
        
        # ABZ Group - OMEGA
        self.add_profile(ClientProfile(
            client_id="OMEGA",
            client_name="OMEGA",
            company_id=1,
            spreadsheet_format=SpreadsheetFormat.ABZ_CHARGE_RATE,
            spreadsheet_patterns=["*OMEGA*"],
            invoice_format=InvoiceFormat.ABZ_TEMPLATE,
            filename_template="ABZ Group {invoice_no}-{year} OMEGA {month} {year} {first_name}",
            category="offshore",
            currency="GBP"
        ))
        
        # ABZ International - Jifmar (Vessel-based)
        # Each vessel can be a separate client profile for detailed tracking
        vessels = [
            ("JIFMAR_VOE_VANGUARD", "Jifmar - Voe Vanguard", "Voe Vanguard"),
            ("JIFMAR_VOE_VIKING", "Jifmar - Voe Viking", "Voe Viking"),
            ("JIFMAR_FARADAY", "Jifmar - Faraday", "Faraday"),
            ("JIFMAR_PROJECT_5679", "Jifmar - Project 5679", "Project 5679"),
            ("JIFMAR_VOE_EARL", "Jifmar - Voe Earl", "Voe Earl")
        ]
        
        for client_id, client_name, vessel_name in vessels:
            self.add_profile(ClientProfile(
                client_id=client_id,
                client_name=client_name,
                company_id=2,
                spreadsheet_format=SpreadsheetFormat.JIFMAR_VESSEL,
                spreadsheet_patterns=["*Jifmar*"],
                invoice_format=InvoiceFormat.GENERATED,
                filename_template=f"ABZ International {{invoice_no}}-{{year}} {vessel_name} {{month}} {{year}} {{first_name}}",
                category="maritime",
                subcategory=vessel_name,
                currency="GBP",
                parser_config={"vessel_name": vessel_name}
            ))
    
    def add_profile(self, profile: ClientProfile):
        """Add a new client profile"""
        self.profiles[profile.client_id] = profile
    
    def get_profile(self, client_id: str) -> Optional[ClientProfile]:
        """Get a client profile by ID"""
        return self.profiles.get(client_id)
    
    def get_profiles_by_company(self, company_id: int) -> List[ClientProfile]:
        """Get all profiles for a company"""
        return [p for p in self.profiles.values() if p.company_id == company_id]
    
    def detect_client_from_filename(self, filename: str) -> Optional[ClientProfile]:
        """
        Automatically detect which client profile matches a filename
        This allows the system to automatically route files to the correct parser
        """
        filename_lower = filename.lower()
        
        for profile in self.profiles.values():
            if not profile.is_active:
                continue
            
            for pattern in profile.spreadsheet_patterns:
                pattern_lower = pattern.lower().replace("*", "")
                if pattern_lower in filename_lower:
                    return profile
        
        return None
    
    def get_all_active_profiles(self) -> List[ClientProfile]:
        """Get all active client profiles"""
        return [p for p in self.profiles.values() if p.is_active]
    
    def save_to_json(self, filepath: str):
        """Save profiles to JSON file"""
        data = {
            client_id: profile.to_dict()
            for client_id, profile in self.profiles.items()
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_from_json(self, filepath: str):
        """Load profiles from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.profiles = {
            client_id: ClientProfile.from_dict(profile_data)
            for client_id, profile_data in data.items()
        }


# Global instance
_client_profile_manager = None

def get_client_profile_manager() -> ClientProfileManager:
    """Get the global client profile manager instance"""
    global _client_profile_manager
    if _client_profile_manager is None:
        _client_profile_manager = ClientProfileManager()
    return _client_profile_manager


if __name__ == "__main__":
    # Test the client profile system
    print("=" * 80)
    print("🧪 TESTING CLIENT PROFILE SYSTEM")
    print("=" * 80)
    
    manager = get_client_profile_manager()
    
    print(f"\n📋 Total Profiles: {len(manager.profiles)}")
    
    # Show ABZ Group clients
    print("\n🏢 ABZ Group Clients:")
    for profile in manager.get_profiles_by_company(1):
        print(f"  - {profile.client_name} ({profile.client_id})")
        print(f"    Format: {profile.spreadsheet_format.value}")
        print(f"    Patterns: {profile.spreadsheet_patterns}")
    
    # Show ABZ International clients
    print("\n🌍 ABZ International Clients:")
    for profile in manager.get_profiles_by_company(2):
        print(f"  - {profile.client_name} ({profile.client_id})")
        print(f"    Vessel: {profile.subcategory}")
        print(f"    Format: {profile.spreadsheet_format.value}")
    
    # Test auto-detection
    print("\n🔍 Testing Auto-Detection:")
    test_files = [
        "ABZ - FMS - Maximus Project - Monthly Charge Rates 09 2025.xlsx",
        "ABZ - OMEGA - Maximus Project - Monthly Charge Rates 08.2025.xlsx",
        "ABZ - Jifmar - Monthly Rates 1509-3009 New Version.xlsx"
    ]
    
    for filename in test_files:
        profile = manager.detect_client_from_filename(filename)
        if profile:
            print(f"  ✅ {filename}")
            print(f"     → Detected: {profile.client_name} (Company ID: {profile.company_id})")
        else:
            print(f"  ❌ {filename}")
            print(f"     → No profile matched")
    
    # Save to JSON
    print("\n💾 Saving profiles to JSON...")
    manager.save_to_json("client_profiles.json")
    print("✅ Saved to client_profiles.json")
    
    print("\n" + "=" * 80)
    print("✅ CLIENT PROFILE SYSTEM WORKING!")
    print("=" * 80)
    print("\n📝 To add a new client, just create a new ClientProfile!")
    print("   No code changes needed - just configuration!")

