#!/usr/bin/env python3
"""Seed demo tenant records for the 10 demo sites.

These are fully functional tenant records with intake submissions,
so /demos/{trade} → /sites/demo-{trade}/web renders a live site.
"""

import json
from datetime import datetime
import sys
import os

# Add webstaffr to path
sys.path.insert(0, os.path.dirname(__file__))
from webstaffr.db import get_connection

# 10 demo tenants with realistic data
DEMO_TENANTS = [
    {
        "tenant_id": "demo-salon",
        "biz_name": "Luna Salon",
        "phone": "(503) 555-0101",
        "email": "hello@lunasalon.local",
        "industry": "salon",
        "service_area": "Portland, OR",
        "tagline": "Modern cuts. Classic style. Your neighborhood salon.",
        "differentiator": "Hand-selected stylists with 10+ years of experience. Walk-ins welcome.",
        "services": ["Haircuts", "Color", "Styling", "Treatments"],
        "years_in_biz": 8,
        "certifications": "Licensed & Insured",
        "rating_value": 4.9,
        "review_count": 147,
    },
    {
        "tenant_id": "demo-plumbing",
        "biz_name": "Rivera Plumbing",
        "phone": "(503) 555-0102",
        "email": "hello@riveraplumbing.local",
        "industry": "plumbing",
        "service_area": "Portland, OR",
        "tagline": "24/7 Emergency Plumbing. No Surprise Fees.",
        "differentiator": "Licensed master plumber. Same-day service. 100% satisfaction guarantee.",
        "services": ["Emergency Repair", "Water Heater", "Drain Cleaning", "Inspections"],
        "years_in_biz": 12,
        "certifications": "Master License #OR-8734",
        "rating_value": 4.95,
        "review_count": 289,
    },
    {
        "tenant_id": "demo-electrician",
        "biz_name": "Kim Electric",
        "phone": "(503) 555-0103",
        "email": "hello@kimelectric.local",
        "industry": "electrician",
        "service_area": "Portland, OR",
        "tagline": "Residential & Commercial. Licensed. Bonded. Local.",
        "differentiator": "20 years of commercial experience. Same-day emergency response.",
        "services": ["Panel Upgrades", "Rewiring", "Generator", "Lighting"],
        "years_in_biz": 20,
        "certifications": "License #OR-4521",
        "rating_value": 4.88,
        "review_count": 156,
    },
    {
        "tenant_id": "demo-contractor",
        "biz_name": "Mendez Construction",
        "phone": "(503) 555-0104",
        "email": "hello@mendezconst.local",
        "industry": "contractor",
        "service_area": "Portland, OR",
        "tagline": "Full Service Home Renovation. Built Right the First Time.",
        "differentiator": "15+ years. Full service from design through final walkthrough.",
        "services": ["Remodel", "Addition", "Basement", "Kitchen"],
        "years_in_biz": 15,
        "certifications": "Licensed & Bonded #OR-9842",
        "rating_value": 4.92,
        "review_count": 203,
    },
    {
        "tenant_id": "demo-medspa",
        "biz_name": "Green Med Spa",
        "phone": "(503) 555-0105",
        "email": "hello@greenmedspa.local",
        "industry": "medspa",
        "service_area": "Portland, OR",
        "tagline": "Med-Grade Skincare. Results You Can See.",
        "differentiator": "RN on staff. Customized treatment plans. Visible results in 4 weeks.",
        "services": ["Facials", "Botox", "Fillers", "Laser"],
        "years_in_biz": 7,
        "certifications": "Registered Nurses on Staff",
        "rating_value": 4.96,
        "review_count": 124,
    },
    {
        "tenant_id": "demo-dentist",
        "biz_name": "Bright Smile Dental",
        "phone": "(503) 555-0106",
        "email": "hello@brightsmile.local",
        "industry": "dentist",
        "service_area": "Portland, OR",
        "tagline": "Family Dentistry You Can Trust. Pain-Free.",
        "differentiator": "Sedation options. Latest technology. Same-day crowns.",
        "services": ["Cleaning", "Fillings", "Crowns", "Implants"],
        "years_in_biz": 18,
        "certifications": "DDS License #OR-5632",
        "rating_value": 4.91,
        "review_count": 312,
    },
    {
        "tenant_id": "demo-realestate",
        "biz_name": "Park Realty Group",
        "phone": "(503) 555-0107",
        "email": "hello@parkrealty.local",
        "industry": "realestate",
        "service_area": "Portland, OR",
        "tagline": "Buy. Sell. Invest. We Know Portland.",
        "differentiator": "Local market experts. Average home sells in 8 days.",
        "services": ["Residential Sales", "Investment", "Rentals", "Consulting"],
        "years_in_biz": 11,
        "certifications": "Realtors Association",
        "rating_value": 4.87,
        "review_count": 178,
    },
    {
        "tenant_id": "demo-lawfirm",
        "biz_name": "Rodriguez Law",
        "phone": "(503) 555-0108",
        "email": "hello@rodriguezlaw.local",
        "industry": "lawfirm",
        "service_area": "Portland, OR",
        "tagline": "Criminal Defense. Family Law. Immigration.",
        "differentiator": "30+ years experience. Personalized attention. Payment plans available.",
        "services": ["Criminal", "Family", "Immigration", "Consultation"],
        "years_in_biz": 30,
        "certifications": "Oregon State Bar",
        "rating_value": 4.93,
        "review_count": 89,
    },
    {
        "tenant_id": "demo-gym",
        "biz_name": "Ironclad Fitness",
        "phone": "(503) 555-0109",
        "email": "hello@ironcladfitness.local",
        "industry": "gym",
        "service_area": "Portland, OR",
        "tagline": "Small Group Training. Big Results.",
        "differentiator": "Certified trainers. Nutrition coaching. Small classes.",
        "services": ["Personal Training", "Group Classes", "Nutrition", "Coaching"],
        "years_in_biz": 6,
        "certifications": "NASM Certified",
        "rating_value": 4.94,
        "review_count": 143,
    },
    {
        "tenant_id": "demo-restaurant",
        "biz_name": "Nonna's Recipe",
        "phone": "(503) 555-0110",
        "email": "hello@nonnas.local",
        "industry": "restaurant",
        "service_area": "Portland, OR",
        "tagline": "Authentic Italian. Made Fresh. Every Day.",
        "differentiator": "Family recipes since 1985. Farm-to-table ingredients. Full bar.",
        "services": ["Dine In", "Takeout", "Catering", "Private Events"],
        "years_in_biz": 13,
        "certifications": "Food Service License",
        "rating_value": 4.89,
        "review_count": 267,
    },
]

def seed_demo_tenants():
    """Create demo tenant records."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        for demo in DEMO_TENANTS:
            # Check if already exists
            cursor.execute(
                "SELECT tenant_id FROM tenants WHERE tenant_id = ?",
                (demo["tenant_id"],)
            )
            if cursor.fetchone():
                print(f"✓ {demo['biz_name']} already exists")
                continue

            # Insert tenant
            cursor.execute(
                """INSERT INTO tenants (tenant_id, biz_name, phone, email, industry, service_area, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    demo["tenant_id"],
                    demo["biz_name"],
                    demo["phone"],
                    demo["email"],
                    demo["industry"],
                    demo["service_area"],
                    datetime.utcnow().isoformat(),
                )
            )

            # Insert intake submission (latest)
            cursor.execute(
                """INSERT INTO intake_submissions
                   (tenant_id, tagline, differentiator, services, years_in_biz,
                    certifications, rating_value, review_count, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    demo["tenant_id"],
                    demo["tagline"],
                    demo["differentiator"],
                    json.dumps(demo["services"]),
                    demo["years_in_biz"],
                    demo["certifications"],
                    demo["rating_value"],
                    demo["review_count"],
                    datetime.utcnow().isoformat(),
                )
            )

            print(f"✓ Seeded {demo['biz_name']} ({demo['tenant_id']})")

        conn.commit()
        print(f"\n✓ {len(DEMO_TENANTS)} demo tenants seeded")
        return True
    except Exception as exc:
        print(f"✗ Seeding failed: {exc}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    seed_demo_tenants()
