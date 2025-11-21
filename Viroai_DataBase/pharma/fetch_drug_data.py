# fetch_drug_data.py
"""
Fetch antiviral compound data from PubChem and ChEMBL databases.
Downloads drug names, SMILES, molecular properties for binding affinity prediction.
"""

import requests
import pandas as pd
import time
import os
from pathlib import Path

# === CONFIGURATION ===
OUTPUT_DIR = "Viroai_DataBase/pharma/approved-drugs"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "antiviral_compounds.csv")

# HACKATHON OPTIMIZATION: Expanded curated list of ~200+ antivirals
# Balance between dataset size and download speed (~5-10 minutes)
CURATED_ANTIVIRALS = {
    # === SARS-CoV-2 / COVID-19 ===
    "Remdesivir": "121304016",
    "Molnupiravir": "145996610",
    "Nirmatrelvir": "155903259",  # Paxlovid component
    "Ritonavir": "392622",
    "Bebtelovimab": "158515747",
    "Sotrovimab": "156588005",
    "Bamlanivimab": "146170251",
    "Casirivimab": "145996610",
    "Tocilizumab": "3010818",
    "Baricitinib": "44205240",
    
    # === Influenza ===
    "Oseltamivir": "65028",
    "Zanamivir": "60855",
    "Peramivir": "150610",
    "Baloxavir marboxil": "118025530",
    "Amantadine": "2130",
    "Rimantadine": "5071",
    "Laninamivir": "9938448",
    
    # === Broad Spectrum Antivirals ===
    "Favipiravir": "492405",
    "Ribavirin": "37542",
    "Umifenovir": "131411",  # Arbidol
    "Nitazoxanide": "41684",
    "Brincidofovir": "16132283",
    "Tecovirimat": "16118730",
    
    # === Herpes Viruses (HSV, VZV, CMV) ===
    "Acyclovir": "2478",
    "Valacyclovir": "60773",
    "Famciclovir": "3324",
    "Penciclovir": "4725",
    "Ganciclovir": "3449",
    "Valganciclovir": "135398745",
    "Cidofovir": "60613",
    "Foscarnet": "3415",
    "Maribavir": "219090",
    "Letermovir": "57379345",
    "Brivudine": "59768",
    "Idoxuridine": "3716",
    "Trifluridine": "6256",
    "Vidarabine": "21704",
    
    # === HIV Antivirals - Protease Inhibitors ===
    "Lopinavir": "92727",
    "Darunavir": "213039",
    "Atazanavir": "148192",
    "Indinavir": "5362440",
    "Nelfinavir": "64143",
    "Saquinavir": "441243",
    "Tipranavir": "54682461",
    "Fosamprenavir": "119607",
    "Amprenavir": "65016",
    
    # === HIV - Reverse Transcriptase Inhibitors (NRTIs) ===
    "Zidovudine": "35370",  # AZT
    "Lamivudine": "73339",  # 3TC
    "Emtricitabine": "60877",  # FTC
    "Tenofovir": "464205",
    "Abacavir": "441300",
    "Stavudine": "18283",  # d4T
    "Didanosine": "50599",  # ddI
    
    # === HIV - NNRTIs ===
    "Efavirenz": "64139",
    "Nevirapine": "4463",
    "Rilpivirine": "5329102",
    "Etravirine": "193962",
    "Doravirine": "71731823",
    
    # === HIV - Integrase Inhibitors ===
    "Raltegravir": "54671008",
    "Dolutegravir": "54726191",
    "Elvitegravir": "5277135",
    "Bictegravir": "71364374",
    "Cabotegravir": "11957837",
    
    # === Hepatitis C (HCV) ===
    "Sofosbuvir": "45375808",
    "Ledipasvir": "67505836",
    "Velpatasvir": "67683363",
    "Daclatasvir": "24873435",
    "Simeprevir": "24873435",
    "Paritaprevir": "25077993",
    "Ombitasvir": "56842208",
    "Dasabuvir": "56640146",
    "Glecaprevir": "67683334",
    "Pibrentasvir": "71748875",
    "Elbasvir": "71301904",
    "Grazoprevir": "71481076",
    
    # === Hepatitis B (HBV) ===
    "Entecavir": "153941",
    "Adefovir": "60871",
    "Telbivudine": "159269",
    "Tenofovir alafenamide": "54671008",
    
    # === RSV (Respiratory Syncytial Virus) ===
    "Palivizumab": "16220172",
    "Ribavirin": "37542",  # duplicate but different use
    
    # === Ebola ===
    "Remdesivir": "121304016",  # Also for Ebola
    "Favipiravir": "492405",  # Also for Ebola
    "Atoltivimab": "135501042",
    
    # === Immunomodulators (COVID-19 treatment) ===
    "Dexamethasone": "5743",
    "Tocilizumab": "3010818",
    "Anakinra": "5311027",
    "Interferon alfa": "5360373",
    "Interferon beta": "5351280",
    
    # === Experimental/Repurposed ===
    "Hydroxychloroquine": "3652",
    "Chloroquine": "2719",
    "Ivermectin": "6321424",
    "Azithromycin": "447043",
    "Colchicine": "6167",
    "Fluvoxamine": "5324346",
    "Camostat": "2536",
    "Nafamostat": "4413",
    
    # === Monoclonal Antibodies (various viruses) ===
    "Palivizumab": "16220172",
    "Mavrilimumab": "135501042",
    "Sarilumab": "135501042",
}

# === ADDITIONAL DIVERSE COMPOUNDS ===
# Adding more CIDs from different antiviral classes for diversity
ADDITIONAL_DRUG_CIDS = [
    # Nucleoside analogs
    "14969", "119607", "65015", "441300", "73339",
    "60877", "50599", "18283", "60750", "135398738",
    
    # Protease inhibitors
    "5362440", "392622", "5360373", "65016", "119607",
    
    # Polymerase inhibitors
    "11979606", "9853053", "11949646", "25137854",
    
    # Entry inhibitors
    "5311027", "6435415", "5282379",
    
    # Integrase inhibitors
    "11957837", "71364374", "5277135",
    
    # Additional antivirals from drug libraries
    "2764", "3000226", "135398737", "71496458", "131801",
    "5281078", "3062316", "216239", "5329102", "193962",
    "64139", "4463", "71731823", "24873435", "67683363",
    "56842208", "25077993", "56640146", "71748875", "71301904",
    "71481076", "159269", "54671008", "16220172", "6167",
    "5324346", "2536", "4413", "14969", "65015",
    
    # More experimental compounds
    "135445969", "138388892", "138708", "139291706", "71301904",
    "91666821", "91825966", "121232966", "11949646", "25137854",
    "49863002", "60823", "65399", "441300", "5070",
    "3010818", "135501042", "158515747", "156588005", "146170251",
    
    # Natural product antivirals
    "5280445", "5280343", "5280961", "5281654", "5280863",
    "969516", "5281855", "11250133", "5280443", "5281800",
    
    # Additional approved drugs with antiviral potential
    "2733526", "5311217", "441243", "392622", "3062316",
    "5281078", "216239", "5329102", "193962", "64139"
]

# === FUNCTION TO FETCH PUBCHEM COMPOUND DATA ===
def fetch_pubchem_compound(cid):
    """
    Fetch compound properties from PubChem by CID.
    
    Args:
        cid: PubChem Compound ID
    
    Returns:
        Dictionary with compound data or None if error
    """
    try:
        # PubChem REST API endpoint
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/MolecularFormula,MolecularWeight,CanonicalSMILES,XLogP/JSON"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            props = data['PropertyTable']['Properties'][0]
            
            # PubChem returns either CanonicalSMILES or ConnectivitySMILES
            smiles = props.get('CanonicalSMILES') or props.get('ConnectivitySMILES', '')
            
            return {
                'drug_id': f"CID{cid}",
                'smiles': smiles,
                'mol_weight': props.get('MolecularWeight', 0),
                'logP': props.get('XLogP', 0),
                'molecular_formula': props.get('MolecularFormula', '')
            }
        else:
            print(f"  [WARNING] Failed to fetch CID {cid}: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"  [ERROR] CID {cid}: {str(e)}")
        return None

def fetch_compound_name(cid):
    """Fetch compound name from PubChem."""
    try:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/description/JSON"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'InformationList' in data and 'Information' in data['InformationList']:
                return data['InformationList']['Information'][0].get('Title', f"Compound_{cid}")
        return f"Compound_{cid}"
        
    except:
        return f"Compound_{cid}"

# === FUNCTION TO GET CURATED COMPOUND LIST ===
def get_curated_compound_list():
    """
    HACKATHON OPTIMIZED: Return curated list of antiviral CIDs.
    Skips slow similarity searches - focuses on proven compounds.
    
    Returns:
        List of tuples: [(name, cid), ...]
    """
    print("\n[FAST MODE] Using curated antiviral compound list...")
    
    # Combine named drugs with their CIDs
    compound_list = [(name, cid) for name, cid in CURATED_ANTIVIRALS.items()]
    
    # Add additional CIDs (will fetch names from PubChem)
    compound_list.extend([(None, cid) for cid in ADDITIONAL_DRUG_CIDS])
    
    print(f"[OK] Total compounds to fetch: {len(compound_list)}")
    print(f"[ESTIMATE] Will take ~{len(compound_list) * 0.2 / 60:.1f} minutes")
    
    return compound_list

# === MAIN EXECUTION ===
def main():
    print("\n" + "="*70)
    print("FETCHING ANTIVIRAL DRUG DATA FROM PUBCHEM")
    print("="*70)
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Step 1: Get curated compound list (FAST - no searching)
    compound_list = get_curated_compound_list()
    
    # Step 2: Fetch detailed data for each compound
    print(f"\n[FETCH] Retrieving compound properties from PubChem...")
    
    compounds_data = []
    success_count = 0
    
    for i, (name, cid) in enumerate(compound_list, 1):
        if i % 10 == 0:
            print(f"  Progress: {i}/{len(compound_list)} compounds...")
        
        # Get compound properties
        comp_data = fetch_pubchem_compound(cid)
        
        if comp_data:
            # Use known name or fetch if needed
            if name:
                comp_data['name'] = name
            else:
                comp_data['name'] = fetch_compound_name(cid)
            
            comp_data['known_targets'] = "Viral proteins"  # Placeholder
            
            compounds_data.append(comp_data)
            success_count += 1
        
        # Rate limiting (PubChem allows ~5 requests/second)
        time.sleep(0.15)  # Slightly faster for hackathon
    
    # Step 3: Create DataFrame and save
    if compounds_data:
        df = pd.DataFrame(compounds_data)
        
        # Reorder columns
        column_order = ['drug_id', 'name', 'smiles', 'mol_weight', 'logP', 'molecular_formula', 'known_targets']
        df = df[column_order]
        
        # Save to CSV
        df.to_csv(OUTPUT_FILE, index=False)
        
        print("\n" + "="*70)
        print(f"[SUCCESS] Downloaded {success_count}/{len(compound_list)} compounds")
        print(f"[SAVED] {OUTPUT_FILE}")
        print(f"[SIZE] {len(df)} compounds, {df.memory_usage(deep=True).sum() / 1024:.1f} KB")
        print("="*70)
        
        # Display sample
        print("\nSample compounds:")
        print(df.head(10).to_string(index=False))
        
        return True
    else:
        print("\n[ERROR] No compounds retrieved!")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n[OK] Drug data acquisition complete!")
    else:
        print("\n[ERROR] Drug data acquisition failed!")

