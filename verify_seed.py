# verify_seed.py
from app.db.seed import seed_sample_data
from app.db.models import *

seed_sample_data()
print("Sample data seeded successfully")