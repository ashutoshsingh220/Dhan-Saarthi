import json
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.scheme import GovernmentScheme
from app.schemas.scheme import GovernmentSchemePublic

INITIAL_SCHEMES_SEED = [
    {
        "name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
        "short_name": "PM-KISAN",
        "category": "FARMER_SUPPORT",
        "tags": ["FARMER_SUPPORT", "AGRICULTURE_LOAN"],
        "target_groups": "Small and Marginal Landholder Farmer Families",
        "description": "A Central Sector Scheme providing direct income support of ₹6,000 per year to eligible landholding farmer families across India, transferred in 3 equal installments of ₹2,000 directly into bank accounts.",
        "benefits_summary": "Direct benefit transfer of ₹6,000 per year (3 installments of ₹2,000) for agricultural inputs and household needs.",
        "benefit_type": "DIRECT_BENEFIT_TRANSFER",
        "official_authority": "Ministry of Agriculture and Farmers Welfare, Govt of India",
        "official_url": "https://pmkisan.gov.in/",
        "application_url": "https://pmkisan.gov.in/RegistrationFormNew.aspx",
        "status": "ACTIVE",
        "geographic_scope": "NATIONAL",
        "states_supported": ["ALL"],
        "eligibility_rules": {
            "occupation_required": ["FARMER"],
            "landholding_required": True,
            "exclusions": ["Institutional landholders", "Government employees", "Income tax payers", "High income professionals"]
        },
        "required_documents": [
            "Aadhaar Card",
            "Land Ownership Documents (Khasra/Khatauni)",
            "Active Bank Account Details linked with Aadhaar",
            "Mobile Number linked to Aadhaar"
        ],
        "how_to_apply": [
            "Visit the official PM-KISAN portal (pmkisan.gov.in) or nearest CSC center.",
            "Click on 'Farmers Corner' -> 'New Farmer Registration'.",
            "Enter Aadhaar number, state, district, and land details.",
            "Submit and verify via OTP."
        ],
        "important_notes": "Aadhaar e-KYC is mandatory for receiving installments.",
        "source_last_verified_at": "2026-01-15T00:00:00Z"
    },
    {
        "name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "short_name": "PMFBY",
        "category": "CROP_INSURANCE",
        "tags": ["CROP_INSURANCE", "FARMER_SUPPORT"],
        "target_groups": "All farmers growing notified crops in notified areas",
        "description": "Comprehensive crop insurance coverage providing financial support to farmers suffering crop loss or damage arising out of natural calamities, pests, and diseases.",
        "benefits_summary": "Comprehensive risk insurance for crops with low premium rates paid by farmers (2% for Kharif, 1.5% for Rabi, 5% for commercial/horticultural crops).",
        "benefit_type": "INSURANCE",
        "official_authority": "Ministry of Agriculture and Farmers Welfare, Govt of India",
        "official_url": "https://pmfby.gov.in/",
        "application_url": "https://pmfby.gov.in/farmerRegistrationForm",
        "status": "ACTIVE",
        "geographic_scope": "NATIONAL",
        "states_supported": ["ALL"],
        "eligibility_rules": {
            "occupation_required": ["FARMER"],
            "crop_notified": True
        },
        "required_documents": [
            "Land possession certificate / Tenant agreement",
            "Aadhaar Card",
            "Bank Passbook copy",
            "Sowing Certificate / Declaration"
        ],
        "how_to_apply": [
            "Apply online through PMFBY portal or NCIP mobile app.",
            "Alternatively, enroll through participating commercial banks, RRBs, or CSCs before the cutoff date."
        ],
        "important_notes": "Enrollment cutoff dates vary by crop season (Kharif/Rabi).",
        "source_last_verified_at": "2026-01-15T00:00:00Z"
    },
    {
        "name": "Kisan Credit Card (KCC) Scheme",
        "short_name": "Kisan Credit Card",
        "category": "AGRICULTURE_LOAN",
        "tags": ["AGRICULTURE_LOAN", "FARMER_SUPPORT", "DAIRY_AND_LIVESTOCK", "FISHERIES"],
        "target_groups": "Farmers, Tenant Farmers, Sharecroppers, Animal Husbandry & Fishery Farmers",
        "description": "Provides timely credit to farmers to meet their short-term credit requirements for cultivation of crops, post-harvest expenses, produce marketing loan, and allied agricultural activities.",
        "benefits_summary": "Concessional credit facility up to ₹3 Lakhs at effective interest rate of 4% per annum (with prompt repayment incentive). No collateral required for loans up to ₹1.6 Lakhs.",
        "benefit_type": "SUBSIDIZED_LOAN",
        "official_authority": "NABARD & Ministry of Agriculture and Farmers Welfare",
        "official_url": "https://myscheme.gov.in/schemes/kcc",
        "application_url": "https://pmkisan.gov.in/",
        "status": "ACTIVE",
        "geographic_scope": "NATIONAL",
        "states_supported": ["ALL"],
        "eligibility_rules": {
            "occupation_required": ["FARMER"],
            "min_age": 18,
            "max_age": 75
        },
        "required_documents": [
            "Application form",
            "ID proof (Aadhaar / Voter ID / PAN)",
            "Address proof",
            "Land revenue record / Lease agreement",
            "Passport size photograph"
        ],
        "how_to_apply": [
            "Visit any nearest Commercial Bank, Regional Rural Bank (RRB), or Cooperative Bank branch.",
            "Or apply online through PM-KISAN portal under KCC section."
        ],
        "important_notes": "Also extended to Dairy, Livestock, and Inland/Marine Fisheries farmers.",
        "source_last_verified_at": "2026-01-15T00:00:00Z"
    },
    {
        "name": "Agriculture Infrastructure Fund (AIF)",
        "short_name": "AIF",
        "category": "AGRICULTURAL_INFRASTRUCTURE",
        "tags": ["AGRICULTURAL_INFRASTRUCTURE", "FARM_EQUIPMENT", "RURAL_ENTERPRISE"],
        "target_groups": "Farmers, Agri-Entrepreneurs, FPOs, PACS, SHGs, Startups",
        "description": "A medium-long term debt financing facility for investment in viable projects for post-harvest management infrastructure and community farming assets.",
        "benefits_summary": "Interest subvention of 3% per annum on loans up to ₹2 Crores for a maximum period of 7 years, along with credit guarantee coverage under CGTMSE.",
        "benefit_type": "SUBSIDIZED_LOAN",
        "official_authority": "Department of Agriculture and Farmers Welfare, Govt of India",
        "official_url": "https://agriinfra.dac.gov.in/",
        "application_url": "https://agriinfra.dac.gov.in/",
        "status": "ACTIVE",
        "geographic_scope": "NATIONAL",
        "states_supported": ["ALL"],
        "eligibility_rules": {
            "occupation_required": ["FARMER", "SELF_EMPLOYED", "BUSINESS_OWNER"],
            "infrastructure_project": True
        },
        "required_documents": [
            "Detailed Project Report (DPR)",
            "Entity registration certificate",
            "KYC documents of promoters",
            "Land ownership/lease documents",
            "Bank statement & IT returns"
        ],
        "how_to_apply": [
            "Register on the AIF online portal (agriinfra.dac.gov.in).",
            "Submit project proposal and select preferred participating lending institution."
        ],
        "important_notes": "Supports cold chains, warehouses, processing units, and custom hiring centers.",
        "source_last_verified_at": "2026-01-15T00:00:00Z"
    },
    {
        "name": "Pradhan Mantri MUDRA Yojana (PMMY)",
        "short_name": "MUDRA Yojana",
        "category": "SMALL_BUSINESS",
        "tags": ["SMALL_BUSINESS", "MICRO_ENTERPRISE", "SELF_EMPLOYMENT", "ENTREPRENEURSHIP", "WOMEN_ENTREPRENEURSHIP"],
        "target_groups": "Non-Corporate, Non-Farm Small/Micro Enterprises",
        "description": "Provides collateral-free loans up to ₹10 Lakhs to micro and small enterprises in manufacturing, trading, services, and agriculture-allied activities across Shishu, Kishor, and Tarun categories.",
        "benefits_summary": "Collateral-free business credit up to ₹10 Lakhs (Shishu: up to ₹50k, Kishor: ₹50k-5L, Tarun: ₹5L-10L) with affordable interest rates.",
        "benefit_type": "CREDIT_GUARANTEE",
        "official_authority": "Department of Financial Services, Ministry of Finance / SIDBI",
        "official_url": "https://www.mudra.org.in/",
        "application_url": "https://www.udyamimitra.in/",
        "status": "ACTIVE",
        "geographic_scope": "NATIONAL",
        "states_supported": ["ALL"],
        "eligibility_rules": {
            "non_farm_business": True,
            "min_age": 18
        },
        "required_documents": [
            "MUDRA application form",
            "Identity Proof (Aadhaar/Voter ID/PAN)",
            "Address Proof of business & applicant",
            "Quotation of machinery/items to be purchased",
            "Proof of business identity/license if existing"
        ],
        "how_to_apply": [
            "Apply online through JanSamarth (jansamarth.in) or UdyamiMitra portal.",
            "Or approach any Commercial Bank, RRB, MFI, or NBFC branch."
        ],
        "important_notes": "No processing fee for Shishu loans.",
        "source_last_verified_at": "2026-01-15T00:00:00Z"
    },
    {
        "name": "Prime Minister's Employment Generation Programme (PMEGP)",
        "short_name": "PMEGP",
        "category": "ENTREPRENEURSHIP",
        "tags": ["ENTREPRENEURSHIP", "MICRO_ENTERPRISE", "RURAL_ENTERPRISE", "SELF_EMPLOYMENT", "WOMEN_ENTREPRENEURSHIP"],
        "target_groups": "Individuals, SHGs, Institutions, Co-operative Societies, Trusts",
        "description": "A major credit-linked subsidy scheme aimed at generating self-employment opportunities through establishment of micro-enterprises in non-farm sector.",
        "benefits_summary": "Margin money subsidy of 15% to 35% of project cost (up to ₹50 Lakhs for manufacturing and ₹20 Lakhs for service sector), with higher subsidy for rural area applicants and special categories.",
        "benefit_type": "GRANT",
        "official_authority": "Khadi and Village Industries Commission (KVIC) / Ministry of MSME",
        "official_url": "https://www.kviconline.gov.in/pmegpeportal/",
        "application_url": "https://www.kviconline.gov.in/pmegpeportal/pmegpweb/index.jsp",
        "status": "ACTIVE",
        "geographic_scope": "NATIONAL",
        "states_supported": ["ALL"],
        "eligibility_rules": {
            "min_age": 18,
            "min_education": "8th Pass for manufacturing projects > ₹10L or service > ₹5L"
        },
        "required_documents": [
            "Project Report / Business Plan",
            "Aadhaar Card & Caste/Special Category Certificate",
            "Educational Qualification Certificate",
            "Rural Area Certificate (if applying under rural category)"
        ],
        "how_to_apply": [
            "Apply online through the KVIC PMEGP e-Portal.",
            "Upload project report, identity documents, and details of preferred bank branch."
        ],
        "important_notes": "Rural category applicants receive 25% (General) to 35% (Special/Women) margin subsidy.",
        "source_last_verified_at": "2026-01-15T00:00:00Z"
    },
    {
        "name": "Stand-Up India Scheme",
        "short_name": "Stand-Up India",
        "category": "WOMEN_ENTREPRENEURSHIP",
        "tags": ["WOMEN_ENTREPRENEURSHIP", "ENTREPRENEURSHIP", "SMALL_BUSINESS"],
        "target_groups": "Women and SC/ST Entrepreneurs setting up greenfield enterprises",
        "description": "Facilitates bank loans between ₹10 Lakhs and ₹1 Crore to at least one SC or ST borrower and at least one woman borrower per bank branch for setting up a greenfield enterprise.",
        "benefits_summary": "Bank credit from ₹10 Lakhs up to ₹1 Crore for greenfield projects in manufacturing, services, trading, or agriculture-allied activities.",
        "benefit_type": "SUBSIDIZED_LOAN",
        "official_authority": "Department of Financial Services, Ministry of Finance / SIDBI",
        "official_url": "https://www.standupmitra.in/",
        "application_url": "https://www.standupmitra.in/",
        "status": "ACTIVE",
        "geographic_scope": "NATIONAL",
        "states_supported": ["ALL"],
        "eligibility_rules": {
            "target_category": ["SC", "ST", "WOMEN"],
            "greenfield_project": True,
            "min_age": 18
        },
        "required_documents": [
            "Identity Proof & Category Certificate (if SC/ST)",
            "Proof of business address & project profile",
            "Bank statement & promoter's contribution details",
            "Pollution clearance / statutory approvals"
        ],
        "how_to_apply": [
            "Apply online through Stand-Up Mitra portal (standupmitra.in).",
            "Or directly at any Scheduled Commercial Bank branch."
        ],
        "important_notes": "Greenfield signifies the first-time venture of the applicant in the manufacturing/services/trading sector.",
        "source_last_verified_at": "2026-01-15T00:00:00Z"
    },
    {
        "name": "PM Formalisation of Micro Food Processing Enterprises (PMFME)",
        "short_name": "PMFME",
        "category": "RURAL_ENTERPRISE",
        "tags": ["RURAL_ENTERPRISE", "MICRO_ENTERPRISE", "FARMER_SUPPORT", "SMALL_BUSINESS"],
        "target_groups": "Individual Micro Food Processing Units, FPOs, SHGs, Cooperatives",
        "description": "Provides financial, technical, and business support for micro food processing enterprises, under the One District One Product (ODOP) framework.",
        "benefits_summary": "Credit-linked capital subsidy of 35% of eligible project cost with a maximum ceiling of ₹10 Lakhs per unit.",
        "benefit_type": "GRANT",
        "official_authority": "Ministry of Food Processing Industries, Govt of India",
        "official_url": "https://pmfme.mofpi.gov.in/",
        "application_url": "https://pmfme.mofpi.gov.in/pmfme/#/login",
        "status": "ACTIVE",
        "geographic_scope": "NATIONAL",
        "states_supported": ["ALL"],
        "eligibility_rules": {
            "sector": ["FOOD_PROCESSING"],
            "min_age": 18
        },
        "required_documents": [
            "Aadhaar Card",
            "Udyam Registration / FSSAI License (if available)",
            "Bank Account details & Project proposal",
            "Electricity bill / Land proof of unit location"
        ],
        "how_to_apply": [
            "Apply online on PMFME Portal (pmfme.mofpi.gov.in).",
            "Contact District Resource Persons (DRP) for assistance in project report preparation."
        ],
        "important_notes": "ODOP (One District One Product) products get priority for branding & marketing support.",
        "source_last_verified_at": "2026-01-15T00:00:00Z"
    },
    {
        "name": "Pradhan Mantri Matsya Sampada Yojana (PMMSY)",
        "short_name": "PMMSY",
        "category": "FISHERIES",
        "tags": ["FISHERIES", "FARMER_SUPPORT", "RURAL_ENTERPRISE"],
        "target_groups": "Fishers, Fish Farmers, Fish Workers, Micro/Small Fisheries Enterprises",
        "description": "A flagship scheme for focused and sustainable development of the fisheries sector in the country with financial support for aquaculture, boats, nets, and fish processing.",
        "benefits_summary": "Government subsidy up to 40% of project cost for General category and 60% for Women/SC/ST beneficiaries for fisheries infrastructure & activities.",
        "benefit_type": "GRANT",
        "official_authority": "Department of Fisheries, Ministry of Fisheries, Animal Husbandry & Dairying",
        "official_url": "https://pmmsy.dof.gov.in/",
        "application_url": "https://pmmsy.dof.gov.in/",
        "status": "ACTIVE",
        "geographic_scope": "NATIONAL",
        "states_supported": ["ALL"],
        "eligibility_rules": {
            "sector": ["FISHERIES"],
            "min_age": 18
        },
        "required_documents": [
            "Aadhaar Card",
            "Land/Water body lease deed or ownership document",
            "Project profile & Bank details",
            "Fisheries training certificate (if applicable)"
        ],
        "how_to_apply": [
            "Submit project application to District Fisheries Officer (DFO).",
            "Or apply online through PMMSY state portal."
        ],
        "important_notes": "Covers inland fisheries, marine fisheries, ornamental fish, and post-harvest infrastructure.",
        "source_last_verified_at": "2026-01-15T00:00:00Z"
    },
    {
        "name": "National Livestock Mission (NLM)",
        "short_name": "NLM",
        "category": "DAIRY_AND_LIVESTOCK",
        "tags": ["DAIRY_AND_LIVESTOCK", "FARMER_SUPPORT", "RURAL_ENTERPRISE"],
        "target_groups": "Individual Farmers, SHGs, FPOs, Farmers, Rural Entrepreneurs",
        "description": "Supports breed improvement, poultry, sheep, goat, piggery farming, and fodder infrastructure development for rural livestock farmers and entrepreneurs.",
        "benefits_summary": "Capital subsidy up to 50% (up to ₹50 Lakhs depending on component like poultry, goat/sheep breeding unit, fodder unit).",
        "benefit_type": "GRANT",
        "official_authority": "Department of Animal Husbandry and Dairying, Govt of India",
        "official_url": "https://nlm.udyamimitra.in/",
        "application_url": "https://nlm.udyamimitra.in/",
        "status": "ACTIVE",
        "geographic_scope": "NATIONAL",
        "states_supported": ["ALL"],
        "eligibility_rules": {
            "sector": ["DAIRY", "LIVESTOCK"],
            "min_age": 18
        },
        "required_documents": [
            "Aadhaar Card",
            "Land ownership/lease agreement for farm setup",
            "Bank passbook copy & CIBIL score",
            "Detailed Project Report (DPR)"
        ],
        "how_to_apply": [
            "Apply online through NLM UdyamiMitra portal (nlm.udyamimitra.in).",
            "Application is screened by State Level Executive Committee (SLEC)."
        ],
        "important_notes": "50% capital subsidy directly released to beneficiary bank account in two installments.",
        "source_last_verified_at": "2026-01-15T00:00:00Z"
    }
]

class SchemeService:
    @staticmethod
    def seed_initial_schemes(db: Session) -> int:
        """Seed initial curated scheme catalog idempotently."""
        added_count = 0
        for item in INITIAL_SCHEMES_SEED:
            existing = db.scalar(select(GovernmentScheme).where(GovernmentScheme.name == item["name"]))
            if not existing:
                scheme = GovernmentScheme(
                    name=item["name"],
                    short_name=item["short_name"],
                    category=item["category"],
                    tags_json=json.dumps(item["tags"]),
                    target_groups=item["target_groups"],
                    description=item["description"],
                    benefits_summary=item["benefits_summary"],
                    benefit_type=item["benefit_type"],
                    official_authority=item["official_authority"],
                    official_url=item["official_url"],
                    application_url=item.get("application_url"),
                    status=item["status"],
                    geographic_scope=item["geographic_scope"],
                    states_supported_json=json.dumps(item["states_supported"]),
                    eligibility_rules_json=json.dumps(item["eligibility_rules"]),
                    required_documents_json=json.dumps(item["required_documents"]),
                    how_to_apply_json=json.dumps(item["how_to_apply"]),
                    important_notes=item.get("important_notes"),
                    source_last_verified_at=item["source_last_verified_at"],
                )
                db.add(scheme)
                added_count += 1
        if added_count > 0:
            db.commit()
        return added_count

    @staticmethod
    def to_public_schema(scheme: GovernmentScheme) -> GovernmentSchemePublic:
        """Convert ORM model to GovernmentSchemePublic Pydantic schema."""
        return GovernmentSchemePublic(
            id=scheme.id,
            scheme_id=scheme.scheme_uuid,
            name=scheme.name,

            short_name=scheme.short_name,
            category=scheme.category,
            tags=json.loads(scheme.tags_json) if scheme.tags_json else [],
            target_groups=scheme.target_groups,
            description=scheme.description,
            benefits_summary=scheme.benefits_summary,
            benefit_type=scheme.benefit_type,
            official_authority=scheme.official_authority,
            official_url=scheme.official_url,
            application_url=scheme.application_url,
            status=scheme.status,
            geographic_scope=scheme.geographic_scope,
            states_supported=json.loads(scheme.states_supported_json) if scheme.states_supported_json else [],
            eligibility_rules=json.loads(scheme.eligibility_rules_json) if scheme.eligibility_rules_json else {},
            required_documents=json.loads(scheme.required_documents_json) if scheme.required_documents_json else [],
            how_to_apply=json.loads(scheme.how_to_apply_json) if scheme.how_to_apply_json else [],
            important_notes=scheme.important_notes,
            source_last_verified_at=scheme.source_last_verified_at,
        )

    @staticmethod
    def get_all_schemes(db: Session, category: str | None = None, search: str | None = None) -> list[GovernmentSchemePublic]:
        """Fetch list of active schemes with optional category/search filters."""
        # Ensure initial seed data exists
        SchemeService.seed_initial_schemes(db)

        query = select(GovernmentScheme).where(GovernmentScheme.status == "ACTIVE")
        schemes = db.scalars(query).all()

        results = []
        for s in schemes:
            tags = json.loads(s.tags_json) if s.tags_json else []
            # Category / Tag filter
            if category:
                cat_upper = category.upper()
                if s.category != cat_upper and cat_upper not in tags:
                    continue
            # Search query filter
            if search:
                s_lower = search.lower()
                text = f"{s.name} {s.short_name} {s.description} {s.target_groups}".lower()
                if s_lower not in text:
                    continue
            results.append(SchemeService.to_public_schema(s))
        return results

    @staticmethod
    def get_scheme_by_uuid_or_id(db: Session, identifier: str) -> GovernmentScheme | None:
        """Find scheme by integer id or string scheme_uuid."""
        SchemeService.seed_initial_schemes(db)
        if identifier.isdigit():
            s = db.scalar(select(GovernmentScheme).where(GovernmentScheme.id == int(identifier)))
            if s:
                return s
        return db.scalar(select(GovernmentScheme).where(GovernmentScheme.scheme_uuid == identifier))
