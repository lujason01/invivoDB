#!/usr/bin/env python3
"""Check and add missing species in database"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'web'))

from app import app, db
from models.database import Species

species_to_add = [
    {"common_name": "Dog", "scientific_name": "Canis lupus familiaris", "taxonomy_id": "9615"},
    {"common_name": "Macaque", "scientific_name": "Macaca mulatta", "taxonomy_id": "9544"},
    {"common_name": "Hamster", "scientific_name": "Mesocricetus auratus", "taxonomy_id": "10036"},
]

with app.app_context():
    existing = {s.scientific_name for s in Species.query.all()}
    for s in species_to_add:
        if s["scientific_name"] not in existing:
            new_species = Species(**s)
            db.session.add(new_species)
            print(f"Added: {s['common_name']} ({s['scientific_name']})")
        else:
            print(f"Already present: {s['common_name']} ({s['scientific_name']})")
    db.session.commit()
    print("Done.") 