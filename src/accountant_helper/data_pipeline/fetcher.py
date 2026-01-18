import requests
import os
import zipfile
import io
import re
from lxml import etree
from typing import Optional

# Configuration
BASE_CELEX = "02023R1803"
DATE_VERSION = "20250730"
LANGUAGE = "CES" # Czech
OUTPUT_DIR = "data/raw"

# The entry point URL for the consolidated version metadata (RDF)
# Note: %2F is encoded forward slash, required by the API often
METADATA_URL = f"http://publications.europa.eu/resource/consolidation/2023R1803%2F{DATE_VERSION}.{LANGUAGE}.fmx4"

def fetch_url_content(url: str, timeout: int = 60) -> Optional[bytes]:
    """
    Fetches raw bytes from a URL.
    """
    print(f"Fetching: {url}")
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None

def extract_zip_url_from_rdf(rdf_content: bytes) -> Optional[str]:
    """
    Parses EUR-Lex RDF metadata to find the direct download link (usually a ZIP).
    """
    try:
        root = etree.fromstring(rdf_content)
        # Namespaces commonly used in EUR-Lex RDF
        ns = {
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'owl': 'http://www.w3.org/2002/07/owl#'
        }
        
        # Strategy 1: Look for owl:sameAs resource ending in .zip
        for element in root.xpath('//owl:sameAs', namespaces=ns):
            resource = element.get('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource')
            if resource and resource.endswith('.zip'):
                return resource
        
        # Strategy 2: Regex fallback if XML parsing fails or structure varies
        print("XML parsing didn't find a ZIP link. Trying regex fallback...")
        content_str = rdf_content.decode('utf-8', errors='ignore')
        match = re.search(r'http://[^"].zip', content_str)
        if match:
            return match.group(0)
            
        return None
    except Exception as e:
        print(f"Error processing RDF content: {e}")
        return None

def process_zip_content(zip_bytes: bytes, output_dir: str) -> Optional[str]:
    """
    Extracts the main XML/Formex file from the downloaded zip bytes.
    Returns the path to the main extracted file.
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
            print(f"Archive contains: {z.namelist()}")
            
            # Filter for likely content files (Formex .xml or .doc.xml)
            # We prefer the one that isn't just metadata (often larger, or specific naming)
            # Usually there is '...doc.xml' (wrapper) and '...xml' (content) or just one.
            # Based on previous run: 'CL...doc.xml' and 'CL...xml'.
            
            extracted_files = []
            for file_info in z.infolist():
                if file_info.filename.endswith('.xml') or file_info.filename.endswith('.fmx4'):
                    z.extract(file_info, output_dir)
                    extracted_files.append(os.path.join(output_dir, file_info.filename))
            
            if not extracted_files:
                print("No XML files found in the archive.")
                return None
            
            print(f"Extracted: {extracted_files}")
            # Return the first one for now, or the one that looks like the main doc
            # 'doc.xml' usually imports the other one.
            return extracted_files[0] 

    except zipfile.BadZipFile:
        print("Error: Invalid zip file format.")
        return None

def main():
    print(f"--- Starting Download for {BASE_CELEX} [{LANGUAGE}] ---")
    
    # 1. Fetch Metadata
    rdf_content = fetch_url_content(METADATA_URL)
    if not rdf_content:
        print("Failed to fetch metadata. Check URL or network.")
        return

    # 2. Find ZIP Link
    zip_url = extract_zip_url_from_rdf(rdf_content)
    if not zip_url:
        print("Could not find a ZIP download link in the metadata.")
        return
    
    print(f"Found ZIP URL: {zip_url}")

    # 3. Download ZIP
    zip_content = fetch_url_content(zip_url)
    if not zip_content:
        print("Failed to download the ZIP archive.")
        return

    # 4. Extract
    final_path = process_zip_content(zip_content, OUTPUT_DIR)
    
    if final_path:
        print(f"\nSUCCESS: Data available at {final_path}")
    else:
        print("\nFAILURE: Could not extract valid data.")

if __name__ == "__main__":
    main()
