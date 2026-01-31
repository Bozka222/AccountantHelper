import json
import re
import os

def clean_text(text):
    """Normalize whitespace."""
    return " ".join(text.split())

def remove_prefix(text, prefix):
    """Remove prefix from text if it starts with it, ignoring whitespace."""
    # This is tricky because of potential whitespace differences.
    # Simple approach: clean both and check.
    
    clean_t = clean_text(text)
    clean_p = clean_text(prefix)
    
    if clean_t.startswith(clean_p):
        # Return the slice of original text corresponding to the length, 
        # but we normalized, so indices might be off.
        # Safer: use regex to match the prefix pattern at start
        pass
    return text

def process_data(input_path, output_path):
    print(f"Cleaning {input_path}...")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cleaned_data = []
    
    for item in data:
        original_content = item.get('content', '')
        
        # 1. Normalize Whitespace
        content = clean_text(original_content)
        
        # 2. Separate Number/Heading from Body
        # For Standard Paragraphs
        paragraph_num = item.get('metadata', {}).get('paragraph_number', '').strip()
        if item['type'] == 'standard_paragraph' and paragraph_num:
            # The parser included NO.P in the full text. We want to remove it from 'content' 
            # and keep it as a separate field or just format it nicely.
            # Example: "1Tento standard..." -> "1 Tento standard..."
            
            # If content starts with the number, add a space
            if content.startswith(paragraph_num):
                # Check if there is already a space
                rest = content[len(paragraph_num):]
                if not rest.startswith(' '):
                    content = f"{paragraph_num} {rest}"
        
        # For Regulation Articles
        # Example: "Článek 1Přijímají se..." -> "Článek 1 Přijímají se..."
        if item['type'] == 'regulation_article':
            match = re.match(r"(Článek\s+\d+)(.*)", content)
            if match:
                heading = match.group(1)
                body = match.group(2)
                if not body.startswith(' '):
                    content = f"{heading} {body}"

        # 3. Create 'text_to_embed'
        # Context: Hierarchy + Content
        hierarchy = item.get('metadata', {}).get('hierarchy', [])
        # Filter out generic titles like "PŘÍLOHA" if desired, but they add context.
        # Join with " > "
        context_str = " > ".join([clean_text(h) for h in hierarchy])
        
        text_to_embed = f"{context_str}\n{content}"
        
        # Update Item
        item['content'] = content
        item['text_to_embed'] = text_to_embed
        
        cleaned_data.append(item)
        
    print(f"Cleaning complete. Processed {len(cleaned_data)} items.")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    input_path = "data/processed/parsed_data.json"
    output_path = "data/processed/cleaned_data.json"
    process_data(input_path, output_path)
