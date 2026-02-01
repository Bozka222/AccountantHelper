import lxml.etree as ET
import json
import os

def get_text_with_spaces(element):
    """Extract text from element and its children, ensuring spaces between elements."""
    if element is None:
        return ""
    # Use lxml's method to get all text nodes and join them
    text_parts = element.xpath('.//text()')
    # Normalize spaces: join parts and replace non-breaking spaces with normal spaces
    full_text = " ".join(part.strip() for part in text_parts if part.strip())
    return full_text.replace("\u00a0", " ")

def parse_xml_dom(file_path, output_path):
    print(f"Parsing {file_path} using DOM...")
    
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except Exception as e:
        print(f"Error parsing XML: {e}")
        return

    results = []
    
    # 1. Process Regulation Articles (ENACTING.TERMS)
    enacting_terms = root.find('.//ENACTING.TERMS')
    if enacting_terms is not None:
        for article in enacting_terms.findall('.//ARTICLE'):
            # Get full text of the article
            text = get_text_with_spaces(article)
            
            # Get the "Article X" title from TI.ART
            ti_art = article.find('TI.ART')
            art_num_raw = get_text_with_spaces(ti_art)
            
            # Extract just the number for the ID
            import re
            num_match = re.search(r'\d+', art_num_raw)
            clean_num = num_match.group(0) if num_match else art_num_raw
            
            ref_id = f"REG:{clean_num}"
            
            entry = {
                "type": "regulation_article",
                "content": text,
                "metadata": {
                    "ref_id": ref_id,
                    "article_number": art_num_raw,
                    "section": "ENACTING TERMS",
                    "source_file": os.path.basename(file_path)
                }
            }
            results.append(entry)

    # 2. Process Annexes (Standards)
    annex = root.find('.//CONS.ANNEX')
    if annex is not None:
        for np in annex.iter('NP'):
            text = get_text_with_spaces(np)
            no_p = np.find('NO.P')
            num_text = get_text_with_spaces(no_p)
            
            hierarchy = []
            standard_name = "Unknown Standard"
            
            parent = np.getparent()
            while parent is not None:
                if parent.tag in ('GR.SEQ', 'ANNEX', 'CONS.ANNEX', 'LEVEL'):
                    title_elem = parent.find('TITLE')
                    if title_elem is not None:
                        t_text = get_text_with_spaces(title_elem)
                        if t_text:
                            hierarchy.append(t_text)
                            # Heuristic for Standard Name
                            if "STANDARD" in t_text.upper() or "INTERPRETACE" in t_text.upper():
                                standard_name = t_text
                
                if parent == annex:
                    break
                parent = parent.getparent()
            
            hierarchy.reverse()
            
            if standard_name == "Unknown Standard" and hierarchy:
                 for h in hierarchy:
                     if "STANDARD" in h.upper() or "INTERPRETACE" in h.upper():
                         standard_name = h
                         break
            
            # --- NEW: Clean and Abbreviate Standard Name ---
            clean_std = standard_name
            import re
            if "MEZINÁRODNÍ ÚČETNÍ STANDARD" in clean_std.upper():
                num = re.search(r'\d+', clean_std)
                clean_std = f"IAS {num.group(0)}" if num else clean_std
            elif "MEZINÁRODNÍ STANDARD ÚČETNÍHO VÝKAZNICTVÍ" in clean_std.upper():
                num = re.search(r'\d+', clean_std)
                clean_std = f"IFRS {num.group(0)}" if num else clean_std
            elif "INTERPRETACE" in clean_std.upper():
                # Handling IFRIC/SIC might need more care, but let's try to extract name
                # Usually it's like "INTERPRETACE IFRIC 19"
                if "IFRIC" in clean_std.upper():
                    num = re.search(r'\d+', clean_std)
                    clean_std = f"IFRIC {num.group(0)}" if num else clean_std
                elif "SIC" in clean_std.upper():
                    num = re.search(r'\d+', clean_std)
                    clean_std = f"SIC {num.group(0)}" if num else clean_std

            # Generate Reference ID: STD:STANDARD:PARAGRAPH
            ref_id = f"STD:{clean_std}:{num_text}" if num_text else f"STD:{clean_std}"
            
            entry = {
                "type": "standard_paragraph",
                "content": text,
                "metadata": {
                    "ref_id": ref_id,
                    "paragraph_number": num_text,
                    "standard": clean_std,
                    "standard_full": standard_name,
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
