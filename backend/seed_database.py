#!/usr/bin/env python3
# run this file to seed the database with initial data
# python seed_database.py

from setup.database_seeder import seed_database

if __name__ == '__main__':
    print("Seeding database...")
    stats = seed_database(silent=False)
    print("\nDone!")

