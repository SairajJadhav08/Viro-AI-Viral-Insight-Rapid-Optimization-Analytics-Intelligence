"""
Quick test script to verify data generators work correctly
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from generate_clinical_data import generate_clinical_datasets
        print("  ✓ generate_clinical_data")
    except Exception as e:
        print(f"  ✗ generate_clinical_data: {e}")
        return False
    
    try:
        from generate_genomic_data import generate_genomic_datasets
        print("  ✓ generate_genomic_data")
    except Exception as e:
        print(f"  ✗ generate_genomic_data: {e}")
        return False
    
    try:
        from generate_pharma_data import generate_pharma_datasets
        print("  ✓ generate_pharma_data")
    except Exception as e:
        print(f"  ✗ generate_pharma_data: {e}")
        return False
    
    try:
        from generate_processed_data import generate_processed_datasets
        print("  ✓ generate_processed_data")
    except Exception as e:
        print(f"  ✗ generate_processed_data: {e}")
        return False
    
    try:
        from generate_migrations_data import generate_migrations_datasets
        print("  ✓ generate_migrations_data")
    except Exception as e:
        print(f"  ✗ generate_migrations_data: {e}")
        return False
    
    return True

def test_small_generation():
    """Test generating data for a small subset"""
    print("\nTesting small data generation...")
    test_viruses = ["SARS-CoV-2", "Ebola"]
    
    try:
        from generate_clinical_data import generate_clinical_datasets
        print("  Testing clinical data generation...")
        result = generate_clinical_datasets(test_viruses)
        print(f"    Result: {'✓ Success' if result else '✗ Failed'}")
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("="*70)
    print("VIRO-AI DATA GENERATORS TEST")
    print("="*70)
    
    if test_imports():
        print("\n✓ All imports successful!")
        if test_small_generation():
            print("\n✓ Test generation successful!")
            print("\nAll tests passed! You can now run generate_all_datasets.py")
        else:
            print("\n✗ Test generation failed!")
            sys.exit(1)
    else:
        print("\n✗ Import tests failed!")
        sys.exit(1)

