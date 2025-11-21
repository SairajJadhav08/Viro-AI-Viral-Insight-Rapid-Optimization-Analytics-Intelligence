"""
Migrations/Geographic Spread Data Generator for Viro-AI
Generates virus migration and geographic spread data
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_cleaner import DataCleaner

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIGRATIONS_DIR = os.path.join(BASE_DIR, "migrations")

# Create migrations data directory if it doesn't exist
if not os.path.exists(MIGRATIONS_DIR):
    os.makedirs(MIGRATIONS_DIR)

# Geographic regions
REGIONS = {
    "North America": ["USA", "Canada", "Mexico"],
    "South America": ["Brazil", "Argentina", "Chile", "Colombia", "Peru"],
    "Europe": ["UK", "Germany", "France", "Italy", "Spain", "Netherlands", "Sweden"],
    "Asia": ["China", "India", "Japan", "South Korea", "Singapore", "Thailand", "Indonesia"],
    "Africa": ["South Africa", "Nigeria", "Kenya", "Ghana", "Egypt"],
    "Oceania": ["Australia", "New Zealand"],
    "Middle East": ["Saudi Arabia", "UAE", "Israel", "Turkey"]
}

# Virus origin regions
VIRUS_ORIGINS = {
    "SARS-CoV-2": "Asia",
    "Influenza": "Asia",
    "Ebola": "Africa",
    "HIV-1": "Africa",
    "HCV": "Global",
    "HBV": "Asia",
    "HSV-1": "Global",
    "CMV": "Global",
    "Dengue": "Asia",
    "Zika": "Africa",
    "Monkeypox": "Africa",
    "Rabies": "Global",
    "RSV": "Global",
    "Adenovirus": "Global"
}

def generate_geographic_spread(virus, num_records=150):
    """Generate geographic spread/migration data"""
    data = []
    
    origin_region = VIRUS_ORIGINS.get(virus, "Global")
    all_countries = [country for countries in REGIONS.values() for country in countries]
    
    # Start date (virus emergence)
    start_date = datetime(2020, 1, 1) if virus == "SARS-CoV-2" else datetime(2015, 1, 1)
    
    for i in range(num_records):
        # Select country
        if origin_region != "Global" and random.random() < 0.3:
            # 30% chance to be in origin region
            origin_countries = [c for region, countries in REGIONS.items() 
                              if region == origin_region for c in countries]
            country = random.choice(origin_countries if origin_countries else all_countries)
        else:
            country = random.choice(all_countries)
        
        # Determine region
        region = next((r for r, countries in REGIONS.items() if country in countries), "Unknown")
        
        # Date (spread over time)
        days_offset = random.randint(0, 1000)
        date = start_date + timedelta(days=days_offset)
        
        # Case count (log-normal distribution)
        cases = int(np.random.lognormal(mean=5, sigma=1.5))
        cases = max(1, min(cases, 1000000))
        
        # Deaths (based on case fatality rate)
        cfr = {
            "Ebola": 0.50, "Rabies": 0.99, "SARS-CoV-2": 0.02,
            "Influenza": 0.001, "Dengue": 0.01, "Zika": 0.001,
            "Monkeypox": 0.01, "HIV-1": 0.05, "HCV": 0.02,
            "HBV": 0.01, "HSV-1": 0.001, "CMV": 0.01,
            "RSV": 0.001, "Adenovirus": 0.001
        }.get(virus, 0.01)
        
        deaths = int(cases * cfr * np.random.uniform(0.5, 1.5))
        
        # Variant/lineage
        variants = {
            "SARS-CoV-2": ["Alpha", "Beta", "Gamma", "Delta", "Omicron"],
            "Influenza": ["H1N1", "H3N2", "H5N1"],
            "Ebola": ["Zaire", "Sudan"],
            "HIV-1": ["Group M", "CRF01_AE"],
            "HCV": ["Genotype 1a", "Genotype 1b", "Genotype 2"],
            "HBV": ["Genotype A", "Genotype B", "Genotype C"],
            "Dengue": ["DENV-1", "DENV-2", "DENV-3", "DENV-4"],
            "Zika": ["Asian", "African"],
            "Monkeypox": ["Clade I", "Clade IIa", "Clade IIb"],
            "RSV": ["RSV-A", "RSV-B"]
        }
        variant = random.choice(variants.get(virus, ["Default"]))
        
        # Transmission route
        transmission_routes = ["Human-to-human", "Animal-to-human", "Vector-borne", "Airborne", "Contact"]
        route = random.choice(transmission_routes)
        
        # Travel-related (boolean)
        travel_related = random.random() < 0.3
        
        # Population density factor
        population_density = np.random.uniform(50, 5000)  # people per km²
        
        # Healthcare capacity (0-1 scale)
        healthcare_capacity = np.random.beta(a=2, b=2)
        
        data.append({
            'virus': virus,
            'country': country,
            'region': region,
            'date': date.strftime('%Y-%m-%d'),
            'cases': cases,
            'deaths': deaths,
            'case_fatality_rate': round(cfr, 4),
            'variant': variant,
            'transmission_route': route,
            'travel_related': travel_related,
            'population_density': round(population_density, 2),
            'healthcare_capacity': round(healthcare_capacity, 3),
            'latitude': round(np.random.uniform(-60, 70), 4),
            'longitude': round(np.random.uniform(-180, 180), 4)
        })
    
    return pd.DataFrame(data)

def generate_migration_paths(virus, num_paths=50):
    """Generate migration paths between countries"""
    data = []
    all_countries = [country for countries in REGIONS.values() for country in countries]
    
    for i in range(num_paths):
        # Select origin and destination
        origin = random.choice(all_countries)
        destination = random.choice([c for c in all_countries if c != origin])
        
        # Migration date
        date = datetime.now() - timedelta(days=random.randint(0, 1000))
        
        # Number of cases migrated
        cases = int(np.random.lognormal(mean=3, sigma=1))
        cases = max(1, min(cases, 10000))
        
        # Migration type
        migration_types = ["Air travel", "Land border", "Sea port", "Human migration", "Animal migration"]
        migration_type = random.choice(migration_types)
        
        # Distance (km) - approximate
        distance = np.random.uniform(100, 15000)
        
        # Time to spread (days)
        spread_time = int(np.random.gamma(shape=2, scale=7))
        spread_time = max(1, min(spread_time, 90))
        
        data.append({
            'virus': virus,
            'origin_country': origin,
            'destination_country': destination,
            'date': date.strftime('%Y-%m-%d'),
            'cases_migrated': cases,
            'migration_type': migration_type,
            'distance_km': round(distance, 2),
            'spread_time_days': spread_time
        })
    
    return pd.DataFrame(data)

def generate_temporal_trends(virus, num_months=24):
    """Generate temporal trends over time"""
    data = []
    
    start_date = datetime(2020, 1, 1) if virus == "SARS-CoV-2" else datetime(2015, 1, 1)
    
    base_cases = {
        "SARS-CoV-2": 1000, "Influenza": 500, "Ebola": 10,
        "HIV-1": 200, "HCV": 150, "HBV": 100
    }.get(virus, 50)
    
    for month in range(num_months):
        date = start_date + timedelta(days=month * 30)
        
        # Seasonal variation (for some viruses)
        if virus == "Influenza":
            seasonal_factor = 1 + 0.5 * np.sin(2 * np.pi * month / 12)  # Winter peak
        else:
            seasonal_factor = 1 + 0.2 * np.random.uniform(-1, 1)
        
        # Cases with trend
        cases = int(base_cases * seasonal_factor * np.random.uniform(0.7, 1.3))
        
        # Growth rate
        growth_rate = np.random.normal(loc=0.05, scale=0.1)
        growth_rate = max(-0.5, min(growth_rate, 0.5))
        
        # R0 (reproduction number)
        r0 = np.random.normal(loc=2.0, scale=0.5)
        r0 = max(0.5, min(r0, 5.0))
        
        data.append({
            'virus': virus,
            'date': date.strftime('%Y-%m'),
            'cases': cases,
            'growth_rate': round(growth_rate, 3),
            'r0': round(r0, 2),
            'seasonal_factor': round(seasonal_factor, 3)
        })
    
    return pd.DataFrame(data)

def generate_migrations_data_for_virus(virus):
    """Generate all migration data for a single virus"""
    # Initialize data cleaner
    cleaner = DataCleaner(BASE_DIR)
    
    # Ensure correct folder structure
    paths = cleaner.ensure_folder_structure(virus, "migrations")
    if not cleaner.validate_file_paths(paths):
        print(f"    ✗ Failed to create folder structure for {virus}")
        return False
    
    print(f"\n  Generating migration data for {virus}...")
    
    # Generate geographic spread
    geographic_data = generate_geographic_spread(virus, num_records=150)
    
    # Clean geographic data
    print(f"    [CLEAN] Cleaning geographic data...")
    geographic_data = cleaner.clean_geographic_data(geographic_data)
    
    # Check for existing data and merge
    geo_file = os.path.join(paths['base'], "geographic_spread.csv")
    exists, existing_geo = cleaner.check_existing_data(geo_file)
    if exists and existing_geo is not None:
        geographic_data = cleaner.merge_and_deduplicate(
            existing_geo, geographic_data,
            ['country', 'date', 'virus']
        )
    
    cleaner.save_cleaned_data(geographic_data, geo_file, clean_func=cleaner.clean_geographic_data)
    
    # Generate migration paths
    migration_paths = generate_migration_paths(virus, num_paths=50)
    
    # Clean migration paths
    migration_paths = cleaner.clean_dataframe(
        migration_paths,
        duplicate_subset=['origin_country', 'destination_country', 'date', 'virus'] 
        if all(c in migration_paths.columns for c in ['origin_country', 'destination_country', 'date', 'virus']) 
        else None
    )
    
    paths_file = os.path.join(paths['base'], "migration_paths.csv")
    exists, existing_paths = cleaner.check_existing_data(paths_file)
    if exists and existing_paths is not None:
        migration_paths = cleaner.merge_and_deduplicate(
            existing_paths, migration_paths,
            ['origin_country', 'destination_country', 'date', 'virus']
        )
    
    cleaner.save_cleaned_data(migration_paths, paths_file)
    
    # Generate temporal trends
    temporal_trends = generate_temporal_trends(virus, num_months=24)
    
    # Clean temporal trends
    temporal_trends = cleaner.clean_dataframe(
        temporal_trends,
        duplicate_subset=['date', 'virus'] if all(c in temporal_trends.columns for c in ['date', 'virus']) else None
    )
    
    trends_file = os.path.join(paths['base'], "temporal_trends.csv")
    exists, existing_trends = cleaner.check_existing_data(trends_file)
    if exists and existing_trends is not None:
        temporal_trends = cleaner.merge_and_deduplicate(
            existing_trends, temporal_trends,
            ['date', 'virus']
        )
    
    cleaner.save_cleaned_data(temporal_trends, trends_file)
    
    # Generate summary metadata
    summary = {
        'virus': virus,
        'generation_date': datetime.now().isoformat(),
        'origin_region': VIRUS_ORIGINS.get(virus, "Global"),
        'total_countries': geographic_data['country'].nunique(),
        'total_cases': int(geographic_data['cases'].sum()),
        'total_deaths': int(geographic_data['deaths'].sum()),
        'avg_case_fatality_rate': round(geographic_data['case_fatality_rate'].mean(), 4),
        'migration_paths': len(migration_paths),
        'time_period_months': len(temporal_trends)
    }
    
    summary_file = os.path.join(virus_dir, "summary.json")
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"    ✓ Saved summary.json")
    
    return True

def generate_migrations_datasets(viruses):
    """Generate migration datasets for all viruses"""
    print(f"\nGenerating migration/geographic spread data for {len(viruses)} viruses...")
    
    success_count = 0
    for virus in viruses:
        try:
            if generate_migrations_data_for_virus(virus):
                success_count += 1
        except Exception as e:
            print(f"    ✗ Error generating data for {virus}: {e}")
            import traceback
            traceback.print_exc()
    
    # Create combined summary
    try:
        all_summaries = []
        for virus in viruses:
            summary_file = os.path.join(MIGRATIONS_DIR, virus, "summary.json")
            if os.path.exists(summary_file):
                with open(summary_file, 'r') as f:
                    all_summaries.append(json.load(f))
        
        if all_summaries:
            combined_summary = {
                'generation_date': datetime.now().isoformat(),
                'total_viruses': len(all_summaries),
                'viruses': all_summaries
            }
            combined_file = os.path.join(MIGRATIONS_DIR, "all_viruses_summary.json")
            with open(combined_file, 'w') as f:
                json.dump(combined_summary, f, indent=2)
            print(f"\n✓ Combined summary: {combined_file}")
    except Exception as e:
        print(f"Warning: Could not create combined summary: {e}")
    
    print(f"\n✓ Generated migration data for {success_count}/{len(viruses)} viruses")
    return success_count == len(viruses)

if __name__ == "__main__":
    test_viruses = ["SARS-CoV-2", "Ebola", "Influenza"]
    generate_migrations_datasets(test_viruses)

