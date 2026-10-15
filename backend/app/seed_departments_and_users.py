"""
Seed script for canonical departments and roles in NagrikSaarathi
"""
import sys, os
sys.path.insert(0, os.path.abspath('.'))

from sqlalchemy import select
from backend.app.database import get_session_factory
from backend.app.models import Department, User, GovernmentScheme
from backend.app.services.auth_service import hash_password

def seed_departments_and_users():
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        # 1. Collect unique department names from existing schemes
        schemes = db.execute(select(GovernmentScheme)).scalars().all()
        dept_names = set()
        for s in schemes:
            if s.department_name:
                dept_names.add(s.department_name.strip())

        # Add common canonical ministries
        dept_names.add("Ministry of Agriculture and Farmers Welfare")
        dept_names.add("Department of Higher Education")
        dept_names.add("Ministry of Women and Child Development")
        dept_names.add("Department of School Education and Literacy")
        dept_names.add("Ministry of Rural Development")
        dept_names.add("Department of Social Justice and Empowerment")

        created_dept_count = 0
        for name in dept_names:
            existing = db.execute(select(Department).where(Department.name == name)).scalar_one_or_none()
            if not existing:
                dept = Department(
                    name=name,
                    ministry_name=name if "Ministry" in name else None,
                    government_level="central" if "Ministry" in name or "Department of" in name else "state",
                    is_active=True,
                )
                db.add(dept)
                created_dept_count += 1
        db.commit()
        print(f"Seeded {created_dept_count} departments (total unique in catalogue: {len(dept_names)})")

        # 2. Seed / Update Demo Users
        # A. Principal Administrator
        admin_user = db.execute(select(User).where(User.identifier == "admin@nagrik.gov.in")).scalar_one_or_none()
        if not admin_user:
            admin_user = User(
                identifier="admin@nagrik.gov.in",
                email="admin@nagrik.gov.in",
                hashed_password=hash_password("Admin@2026"),
                role="admin",
                full_name="मुख्य प्रशासनिक अधिकारी (Principal Administrator)",
                department="National Informatics Centre & MoE",
                designation="Principal System Administrator",
                is_active=True,
                is_demo=True,
            )
            db.add(admin_user)
            print("Created Principal Administrator demo account: admin@nagrik.gov.in / Admin@2026")
        else:
            admin_user.role = "admin"
            admin_user.hashed_password = hash_password("Admin@2026")
            print("Updated Principal Administrator role to 'admin'")

        # B. Department Official (Agriculture)
        official_agri = db.execute(select(User).where(User.identifier == "officer@dept.gov.in")).scalar_one_or_none()
        agri_dept_name = "Ministry of Agriculture and Farmers Welfare"
        if not official_agri:
            official_agri = User(
                identifier="officer@dept.gov.in",
                email="officer@dept.gov.in",
                hashed_password=hash_password("Officer@2026"),
                role="official",
                full_name="विभागीय नोडल अधिकारी (Department Nodal Officer)",
                department=agri_dept_name,
                designation="Nodal Scheme Officer (Agriculture)",
                state_scope=None,
                is_active=True,
                is_demo=True,
            )
            db.add(official_agri)
            print("Created Agriculture Department Official: officer@dept.gov.in / Officer@2026")
        else:
            official_agri.role = "official"
            official_agri.department = agri_dept_name
            official_agri.designation = "Nodal Scheme Officer (Agriculture)"
            official_agri.hashed_password = hash_password("Officer@2026")
            print("Updated Agriculture Department Official")

        # C. Second Department Official (Education) - for testing cross-department security
        official_edu = db.execute(select(User).where(User.identifier == "officer.edu@dept.gov.in")).scalar_one_or_none()
        edu_dept_name = "Department of Higher Education"
        if not official_edu:
            official_edu = User(
                identifier="officer.edu@dept.gov.in",
                email="officer.edu@dept.gov.in",
                hashed_password=hash_password("Officer@2026"),
                role="official",
                full_name="शिक्षा विभाग अधिकारी (Higher Education Officer)",
                department=edu_dept_name,
                designation="Joint Director (Scholarships)",
                state_scope=None,
                is_active=True,
                is_demo=True,
            )
            db.add(official_edu)
            print("Created Education Department Official: officer.edu@dept.gov.in / Officer@2026")

        # D. State Department Official (Maharashtra State Agriculture)
        official_mh = db.execute(select(User).where(User.identifier == "officer.mh@agri.gov.in")).scalar_one_or_none()
        if not official_mh:
            official_mh = User(
                identifier="officer.mh@agri.gov.in",
                email="officer.mh@agri.gov.in",
                hashed_password=hash_password("Officer@2026"),
                role="official",
                full_name="कृषि विभाग अधिकारी - महाराष्ट्र (MH State Officer)",
                department="Department of Agriculture",
                designation="State Nodal Officer",
                state_scope="MH",
                is_active=True,
                is_demo=True,
            )
            db.add(official_mh)
            print("Created State Scope Official: officer.mh@agri.gov.in / Officer@2026")

        # E. Citizen Demo User
        citizen = db.execute(select(User).where(User.identifier == "9876543210")).scalar_one_or_none()
        if not citizen:
            citizen = User(
                identifier="9876543210",
                mobile="9876543210",
                email="citizen@nagrik.gov.in",
                hashed_password=hash_password("Citizen@2026"),
                role="citizen",
                full_name="नागरिक उपयोगकर्ता (Demo Citizen)",
                is_active=True,
                is_demo=True,
            )
            db.add(citizen)
            print("Created Citizen Demo User: 9876543210 / Citizen@2026")

        db.commit()
        print("All canonical departments and 3-tier users successfully seeded!")

    finally:
        db.close()

if __name__ == "__main__":
    seed_departments_and_users()
