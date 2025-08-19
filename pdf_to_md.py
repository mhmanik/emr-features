#!/usr/bin/env python3
"""
Convert PDF to Markdown format
"""

import PyPDF2
import re
import sys

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                text += f"\n--- Page {page_num + 1} ---\n"
                text += page_text
                
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None
    
    return text

def clean_and_format_text(text):
    """Clean and format text for markdown"""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    
    # Fix common issues with PDF text extraction
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Add space between camelCase
    text = re.sub(r'(\w)(\d)', r'\1 \2', text)  # Add space between word and number
    text = re.sub(r'(\d)(\w)', r'\1 \2', text)  # Add space between number and word
    
    # Format headers (lines that are all caps or start with numbers)
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            formatted_lines.append('')
            continue
            
        # Check if line might be a header
        if (line.isupper() and len(line) > 3 and len(line) < 100) or \
           (re.match(r'^\d+\.?\s+[A-Z]', line)) or \
           (line.startswith('---')):
            # This looks like a header
            if not line.startswith('#'):
                formatted_lines.append(f"\n## {line}\n")
            else:
                formatted_lines.append(line)
        else:
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

def main():
    pdf_file = "EMR Features.pdf"
    output_file = "EMR_Features.md"
    
    print(f"Converting {pdf_file} to {output_file}...")
    
    # Extract text from PDF
    raw_text = extract_text_from_pdf(pdf_file)
    
    if raw_text is None:
        print("Failed to extract text from PDF")
        return 1
    
    # Clean and format text
    markdown_text = clean_and_format_text(raw_text)
    
    # Add markdown header
    final_content = f"# EMR Features\n\n*Converted from PDF on {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}*\n\n{markdown_text}"
    
    # Write to markdown file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_content)
        print(f"Successfully converted to {output_file}")
        return 0
    except Exception as e:
        print(f"Error writing markdown file: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
