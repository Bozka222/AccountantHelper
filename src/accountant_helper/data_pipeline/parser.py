import lxml.etree as ET
import json
import os

def parse_xml_dom(file_path, output_path):
    print(f"Parsing {file_path} using DOM...")
    
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except Exception as e:
        print(f"Error parsing XML: {e}")
        return

    results = []
    
    # Namespaces might be an issue, but usually Formex doesn't use complex ones or lxml handles them.
    # We'll use local-name() if needed, but simple tags seem to work.

    # 1. Process Regulation Articles (ENACTING.TERMS)
    # Path: //ENACTING.TERMS/ARTICLE
    enacting_terms = root.find('.//ENACTING.TERMS')
    if enacting_terms is not None:
        for article in enacting_terms.findall('.//ARTICLE'):
            # Get full text of the article
            text = "".join(article.itertext()).strip()
            
            # Get the "Article X" title if possible. usually in STI or TI
            # But mostly it's just the order.
            
            entry = {
                "type": "regulation_article",
                "content": text,
                "metadata": {
                    "section": "ENACTING TERMS",
                    "source_file": os.path.basename(file_path)
                }
            }
            results.append(entry)

    # 2. Process Annexes (Standards)
    # Path: //CONS.ANNEX
    # Within Annex, we have GR.SEQ. We want to find the "Root" of each Standard.
    # Usually GR.SEQ level 1 or 2.
    # We will traverse all NPs inside CONS.ANNEX and find their "Context" by looking up.
    
    annex = root.find('.//CONS.ANNEX')
    if annex is not None:
        # Iterate all NPs in Annex
        for np in annex.iter('NP'):
            # Content
            text = "".join(np.itertext()).strip()
            
            # Find Paragraph Number (NO.P)
            no_p = np.find('NO.P')
            num_text = "".join(no_p.itertext()).strip() if no_p is not None else ""
            
            # Context Walking
            # Walk up parents to find titles
            hierarchy = []
            standard_name = "Unknown Standard"
            
            parent = np.getparent()
            while parent is not None:
                if parent.tag in ('GR.SEQ', 'ANNEX', 'CONS.ANNEX', 'LEVEL'):
                    # Check for title
                    title_elem = parent.find('TITLE')
                    if title_elem is not None:
                        t_text = "".join(title_elem.itertext()).strip()
                        if t_text:
                            hierarchy.append(t_text)
                            # Heuristic for Standard Name
                            if "STANDARD" in t_text.upper() or "INTERPRETACE" in t_text.upper():
                                standard_name = t_text
                
                if parent == annex:
                    break
                parent = parent.getparent()
            
            hierarchy.reverse() # Top-down
            
            # If we didn't find a specific standard name in hierarchy, stick to the last found one or "Annex"
            if standard_name == "Unknown Standard" and hierarchy:
                 # Try to find one that looks like a standard in the hierarchy list
                 for h in hierarchy:
                     if "STANDARD" in h.upper() or "INTERPRETACE" in h.upper():
                         standard_name = h
                         break
            
            entry = {
                "type": "standard_paragraph",
                "content": text,
                "metadata": {
                    "paragraph_number": num_text,
                    "standard": standard_name,
                    "hierarchy": hierarchy,
                    "source_file": os.path.basename(file_path)
                }
            }
            results.append(entry)

    print(f"Parsing complete. Extracted {len(results)} items.")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    file_path = "data/raw/CL2023R1803CS0050020.0001.xml"
    output_path = "data/processed/parsed_data.json"
    parse_xml_dom(file_path, output_path)
