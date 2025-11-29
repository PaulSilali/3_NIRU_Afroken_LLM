#!/usr/bin/env python3
"""
Chunk extracted text files and write as Markdown with YAML front-matter.

This script:
1. Reads raw/fetch_manifest.json (created by fetch_and_extract.py)
2. For each entry, reads the extracted .txt file
3. Cleans the text (removes garbage, JavaScript, navigation)
4. Chunks text into ~200-word pieces (respecting paragraph boundaries)
5. Detects category using keyword heuristics
6. Writes each chunk as a separate .md file with YAML front-matter
7. Saves files to data/docs/ directory (repo root)

Reads raw/fetch_manifest.json and creates data/docs/*.md files.
"""

# Standard library imports
import json      # For reading manifest.json and writing YAML tags as JSON
import re        # For regular expressions (text cleaning, slugification)
from datetime import datetime  # For timestamp in YAML front-matter
from pathlib import Path  # For cross-platform file path handling

# ===== CATEGORY DETECTION KEYWORDS =====
# Dictionary mapping category names to lists of keywords that indicate that category
# Used by detect_category() to automatically classify documents
# The category with the most matching keywords wins
CATEGORY_KEYWORDS = {
    # Service workflow: Step-by-step instructions, how-to guides
    'service_workflow': ['how to', 'steps', 'process', 'procedure', 'apply', 'register', 'application'],
    
    # Ministry FAQ: Question-answer format, frequently asked questions
    'ministry_faq': ['faq', 'frequently asked', 'question', 'answer', 'q&a'],
    
    # County service: Local government services, county-specific
    'county_service': ['county', 'local', 'municipal'],
    
    # Legal snippet: Laws, regulations, legal documents
    'legal_snippet': ['act', 'law', 'regulation', 'legal', 'constitution', 'right'],
    
    # USSD/SMS: Mobile services, short codes, text messaging
    'ussd_sms': ['ussd', 'sms', 'text', 'mobile', 'short code'],
    
    # Language pack: Translations, phrases, dictionaries
    'language_pack': ['translation', 'language', 'phrase', 'dictionary'],
    
    # Agent ops: Operational procedures, guidelines for agents
    'agent_ops': ['agent', 'operation', 'procedure', 'guideline', 'policy'],
    
    # Safety & ethics: Privacy, security, ethical guidelines
    'safety_ethics': ['safety', 'ethics', 'privacy', 'data protection', 'security'],
    
    # Officer template: Response templates, scripts, formats
    'officer_template': ['template', 'response', 'script', 'format']
}

def detect_category(url: str, title: str, text: str) -> str:
    """
    Automatically detect document category using keyword matching.
    
    This function uses heuristics to classify documents into one of 9 categories.
    It searches for category-specific keywords in the URL, title, and first 500 chars of text.
    The category with the most keyword matches wins.
    
    Args:
        url: Source URL (may contain category hints like "faq", "services")
        title: Document title (often contains category words)
        text: Document content (first 500 chars checked for efficiency)
    
    Returns:
        Category name string (e.g., "service_workflow", "ministry_faq")
        Defaults to "service_workflow" if no matches found
    
    Example:
        detect_category("https://kra.go.ke/faq", "Frequently Asked Questions", "Q: How do I...")
        # Returns: "ministry_faq" (matches "faq" keyword)
    """
    # Combine URL, title, and first 500 chars of text into one searchable string
    # Convert to lowercase for case-insensitive matching
    # Only use first 500 chars of text for performance (most category indicators are near the start)
    combined = f"{url} {title} {text[:500]}".lower()
    
    # Dictionary to store match scores for each category
    # Key: category name, Value: number of keyword matches
    scores = {}
    
    # Loop through each category and its keywords
    for category, keywords in CATEGORY_KEYWORDS.items():
        # Count how many keywords appear in the combined text
        # sum() adds up 1 for each keyword found (True = 1, False = 0)
        # Example: if "faq" and "question" both found, score = 2
        score = sum(1 for kw in keywords if kw in combined)
        scores[category] = score
    
    # If we found any matches, return the category with the highest score
    if scores:
        # max(scores, key=scores.get) finds the key (category) with the maximum value (score)
        # Example: if scores = {'service_workflow': 2, 'ministry_faq': 3}, returns 'ministry_faq'
        return max(scores, key=scores.get)
    
    # Default category if no keywords matched
    return 'service_workflow'  # Default

def clean_text(text: str) -> str:
    """
    Clean extracted text by removing garbage, JavaScript, and navigation elements.
    
    Web scraping often captures unwanted content:
    - Very long lines (often base64 encoded data, minified JS)
    - JavaScript code that wasn't properly removed
    - Navigation breadcrumbs ("Home > Services > Registration")
    - Standalone navigation words
    
    This function filters out these unwanted elements to keep only readable content.
    
    Args:
        text: Raw extracted text (may contain garbage)
    
    Returns:
        Cleaned text with unwanted lines removed
    
    Example:
        Input: "Home > Services\nfunction() { ... }\nRegister for NHIF here..."
        Output: "Register for NHIF here..."
    """
    # Split text into individual lines for processing
    # Each line will be evaluated separately
    lines = text.split('\n')
    
    # List to store lines that pass the cleaning filters
    cleaned_lines = []
    
    # Process each line individually
    for line in lines:
        # Remove leading/trailing whitespace
        # This handles lines with only spaces/tabs
        line = line.strip()
        
        # FILTER 1: Skip very long lines (likely garbage)
        # Long lines are often:
        # - Base64 encoded images/data
        # - Minified JavaScript
        # - CSS with no line breaks
        # - Corrupted text
        # 300 characters is a reasonable threshold (normal paragraphs are shorter)
        if len(line) > 300:
            continue  # Skip this line
        
        # FILTER 2: Skip JavaScript remnants
        # Sometimes JavaScript code leaks through HTML extraction
        # Check for common JS patterns:
        # - "function(": Function declarations
        # - "var ": Variable declarations (old JS)
        # - "const ": Constant declarations (modern JS)
        if 'function(' in line or 'var ' in line or 'const ' in line:
            continue  # Skip this line
        
        # FILTER 3: Skip menu breadcrumbs
        # Breadcrumbs are navigation elements like "Home > Services > Registration"
        # They're not useful content for RAG
        # Pattern: contains " > " (arrow) and is short (< 100 chars)
        # Short check prevents false positives on actual content mentioning "greater than"
        if ' > ' in line and len(line) < 100:
            continue  # Skip this line
        
        # FILTER 4: Skip common standalone navigation words
        # These are often leftover from navigation menus
        # Convert to lowercase for case-insensitive matching
        if line.lower() in ['home', 'back', 'next', 'previous', 'menu']:
            continue  # Skip this line
        
        # If line passed all filters and is not empty, keep it
        if line:
            cleaned_lines.append(line)
    
    # Join cleaned lines back into a single string
    # Use '\n' as separator to preserve line breaks between paragraphs
    return '\n'.join(cleaned_lines)

def chunk_text(text: str, chunk_size: int = 200) -> list[str]:
    """
    Split text into chunks of approximately chunk_size words, respecting paragraph boundaries.
    
    Chunking is important for RAG because:
    - Large documents don't fit in LLM context windows
    - Smaller chunks improve retrieval precision
    - ~200 words is optimal for most embedding models
    
    This function respects paragraph boundaries (doesn't split mid-paragraph)
    to maintain semantic coherence.
    
    Args:
        text: Full text to chunk
        chunk_size: Target number of words per chunk (default 200)
    
    Returns:
        List of text chunks, each approximately chunk_size words
    
    Example:
        Input: "Para 1 (50 words)...\n\nPara 2 (100 words)...\n\nPara 3 (80 words)..."
        Output: ["Para 1...\n\nPara 2...", "Para 3..."]
        # First chunk: 150 words, Second chunk: 80 words
    """
    # STEP 1: Clean the text first (remove garbage, JS, navigation)
    # This ensures chunks contain only useful content
    text = clean_text(text)
    
    # STEP 2: Split text into paragraphs
    # Paragraphs are separated by double newlines (\n\n)
    # This preserves the natural structure of the document
    # p.strip() removes leading/trailing whitespace from each paragraph
    # if p.strip() filters out empty paragraphs (whitespace-only lines)
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    # STEP 3: Build chunks by grouping paragraphs
    # List to store completed chunks
    chunks = []
    
    # Current chunk being built (list of paragraphs)
    current_chunk = []
    
    # Word count for current chunk (for size tracking)
    current_words = 0
    
    # Process each paragraph
    for para in paragraphs:
        # Count words in this paragraph
        # Split by whitespace and count resulting pieces
        # Example: "How do I register?" -> 4 words
        para_words = len(para.split())
        
        # Check if adding this paragraph would exceed chunk_size
        # AND we already have content in current_chunk
        if current_words + para_words > chunk_size and current_chunk:
            # Save the current chunk (it's full)
            # Join paragraphs with double newline to preserve structure
            chunks.append('\n\n'.join(current_chunk))
            
            # Start a new chunk with this paragraph
            current_chunk = [para]
            current_words = para_words
        else:
            # Add paragraph to current chunk (still under size limit)
            current_chunk.append(para)
            current_words += para_words
    
    # STEP 4: Add the last chunk if it has content
    # (The loop might end with a partially-filled chunk)
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    # Return list of chunks
    return chunks

def slugify(text: str, max_length: int = 60) -> str:
    """
    Convert text to a filename-friendly slug.
    
    A slug is a URL/filename-safe version of text:
    - Lowercase
    - Special characters removed
    - Spaces/hyphens converted to underscores
    - Limited length
    
    Used to create readable filenames from document titles.
    
    Args:
        text: Input text (e.g., "KRA PIN Registration Process")
        max_length: Maximum length of output (default 60 chars)
    
    Returns:
        Slug string (e.g., "kra_pin_registration_process")
    
    Example:
        slugify("KRA PIN Registration - Step by Step") -> "kra_pin_registration_step_by_step"
    """
    # Convert to lowercase for consistency
    # Example: "KRA PIN" -> "kra pin"
    text = text.lower()
    
    # Remove all characters that aren't word characters (\w), whitespace (\s), or hyphens (-)
    # This removes special chars like /, :, ?, &, etc. that aren't valid in filenames
    # Example: "kra-pin/registration" -> "kra-pinregistration"
    text = re.sub(r'[^\w\s-]', '', text)
    
    # Replace one or more spaces or hyphens with a single underscore
    # This normalizes spacing and converts to underscore format
    # Example: "kra  pin-registration" -> "kra_pin_registration"
    text = re.sub(r'[-\s]+', '_', text)
    
    # Truncate to max_length and remove leading/trailing underscores/hyphens
    # This prevents overly long filenames and removes edge separators
    # Example: "kra_pin_registration_process" -> "kra_pin_registration_process" (if <= 60)
    return text[:max_length].strip('_-')

def sanitize_title(title: str, max_length: int = 100) -> str:
    """
    Sanitize title for safe use in YAML front-matter.
    
    YAML has special characters that need escaping. This function:
    - Trims whitespace
    - Truncates long titles
    - Escapes problematic characters (quotes)
    
    Args:
        title: Raw title text
        max_length: Maximum title length (default 100 chars)
    
    Returns:
        Sanitized title safe for YAML
    
    Example:
        sanitize_title('  "KRA PIN" Registration  ') -> "'KRA PIN' Registration"
    """
    # Remove leading/trailing whitespace
    title = title.strip()
    
    # Truncate if too long, add ellipsis
    # max_length-3 leaves room for "..."
    # Example: "Very long title..." -> "Very long tit..."
    if len(title) > max_length:
        title = title[:max_length-3] + '...'
    
    # Escape double quotes (YAML uses them for strings)
    # Replace with single quotes to avoid YAML parsing issues
    # Example: 'Title with "quotes"' -> "Title with 'quotes'"
    title = title.replace('"', "'")
    
    return title

def extract_tags(text: str, url: str) -> list[str]:
    """
    Extract relevant tags from URL and text content.
    
    Tags help with document organization and searchability.
    This function identifies:
    - Government agencies (KRA, NHIF, etc.) from URL
    - Service types (PIN, registration, etc.) from text
    
    Args:
        text: Document text content
        url: Source URL
    
    Returns:
        List of tag strings (max 5 tags)
    
    Example:
        extract_tags("Register for KRA PIN...", "https://kra.go.ke/services/pin")
        # Returns: ['auto_import', 'kra', 'pin', 'registration']
    """
    # Start with base tag indicating this was auto-imported
    tags = ['auto_import']
    
    # ===== EXTRACT AGENCY TAGS FROM URL =====
    # URLs often contain agency names, so check URL first
    # Convert to lowercase for case-insensitive matching
    url_lower = url.lower()
    
    # Check for KRA (Kenya Revenue Authority) indicators
    # Matches URLs like "kra.go.ke" or pages about "tax"
    if 'kra' in url_lower or 'tax' in url_lower:
        tags.append('kra')
    
    # Check for NHIF (National Hospital Insurance Fund) indicators
    # Matches URLs with "nhif" or pages about "health"
    if 'nhif' in url_lower or 'health' in url_lower:
        tags.append('nhif')
    
    # Check for Huduma Centre indicators
    if 'huduma' in url_lower:
        tags.append('huduma')
    
    # Check for eCitizen platform indicators
    if 'ecitizen' in url_lower:
        tags.append('ecitizen')
    
    # Check for Immigration services (passport, visa, etc.)
    if 'immigration' in url_lower or 'passport' in url_lower:
        tags.append('immigration')
    
    # Check for NSSF (National Social Security Fund) indicators
    if 'nssf' in url_lower:
        tags.append('nssf')
    
    # ===== EXTRACT SERVICE TAGS FROM TEXT =====
    # Check first 200 characters of text for service-related keywords
    # Only check beginning for performance (most relevant info is usually at start)
    text_lower = text[:200].lower()
    
    # Check for PIN-related content
    if 'pin' in text_lower:
        tags.append('pin')
    
    # Check for registration-related content
    if 'registration' in text_lower:
        tags.append('registration')
    
    # Check for application-related content
    if 'application' in text_lower:
        tags.append('application')
    
    # Limit to 5 tags total to keep metadata manageable
    # [:5] takes first 5 elements (if more than 5 were added)
    return tags[:5]  # Limit to 5 tags

def main():
    """
    Main function: Orchestrates the chunking and Markdown file creation process.
    
    This function:
    1. Reads fetch_manifest.json (created by fetch_and_extract.py)
    2. For each entry, reads the extracted .txt file
    3. Chunks the text into ~200-word pieces
    4. Detects category and extracts tags
    5. Writes each chunk as a separate .md file with YAML front-matter
    6. Saves files to data/docs/ directory
    """
    # Import argparse here (not at top) since it's only used in main()
    import argparse
    
    # ===== COMMAND-LINE ARGUMENT PARSING =====
    parser = argparse.ArgumentParser(description='Chunk text and write Markdown files')
    
    # Optional flag: Re-index existing docs without re-fetching
    # (Currently prepared for future use - could skip chunking if docs already exist)
    parser.add_argument('--re-index-only', action='store_true',
                       help='Re-index existing docs without re-fetching')
    args = parser.parse_args()
    
    # ===== PATH SETUP =====
    # Get the directory where this script is located (scripts/rag/)
    script_dir = Path(__file__).parent
    
    # Get backend root (two levels up from scripts/rag/)
    backend_dir = script_dir.parent.parent
    
    # Path to raw/ directory (contains fetched HTML/text files)
    raw_dir = backend_dir / 'data' / 'raw'
    
    # Path to data/docs/ directory (where Markdown files will be written)
    docs_dir = backend_dir / 'data' / 'docs'
    
    # Create docs directory if it doesn't exist
    # parents=True creates parent directories if needed (e.g., creates 'data/docs' if missing)
    # exist_ok=True prevents error if directory already exists
    docs_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    
    # ===== READ MANIFEST =====
    # Manifest file created by fetch_and_extract.py
    # Contains list of all fetched URLs with metadata
    # Located in data/raw/ directory
    manifest_file = raw_dir / 'fetch_manifest.json'
    
    # Check if manifest exists (user must run fetch_and_extract.py first)
    if not manifest_file.exists():
        print(f"Error: {manifest_file} not found. Run fetch_and_extract.py first.")
        return  # Exit if manifest not found
    
    # Read and parse JSON manifest
    with open(manifest_file, 'r', encoding='utf-8') as f:
        manifest = json.load(f)  # Parse JSON into Python list of dictionaries
    
    # Log how many entries we'll process
    print(f"Processing {len(manifest)} entries from manifest...")
    
    # Counter for total chunks created (for summary at end)
    chunk_count = 0
    
    # ===== PROCESS EACH MANIFEST ENTRY =====
    # Loop through each entry in the manifest
    # Each entry represents one URL that was fetched
    for entry in manifest:
        # Construct path to the .txt file for this entry
        # entry['txt_file'] is a relative path like "raw/001_kra_services_abc123.txt"
        txt_file = backend_dir / entry['txt_file']
        
        # Check if text file exists (should always exist if manifest is correct)
        if not txt_file.exists():
            print(f"Warning: {txt_file} not found, skipping")
            continue  # Skip to next entry
        
        # ===== READ TEXT FILE =====
        # Read the extracted text content
        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()  # Read entire file content
        
        # ===== EXTRACT TITLE AND TEXT =====
        # Text files are saved with format: "Title\n\nText content..."
        # Split on first newline to separate title from content
        lines = content.split('\n', 1)  # Split into max 2 parts (title, rest)
        
        if len(lines) > 1:
            # If file has title line, extract it
            # lines[0] is the title, lines[1] is the text content
            title = lines[0].strip()  # Remove whitespace from title
            text = lines[1]  # Rest is the text content
        else:
            # If no title line (unusual), use title from manifest or default
            title = entry.get('title', 'Untitled')
            text = content  # Entire content is text
        
        # ===== CHUNK THE TEXT =====
        # Split text into ~200-word chunks
        # Returns list of text chunks
        chunks = chunk_text(text)
        
        # ===== DETECT CATEGORY =====
        # Automatically classify document using keyword heuristics
        # Returns category like "service_workflow", "ministry_faq", etc.
        category = detect_category(entry['url'], title, text)
        
        # ===== EXTRACT TAGS =====
        # Extract relevant tags for metadata (KRA, NHIF, registration, etc.)
        # Returns list of tag strings
        tags = extract_tags(text, entry['url'])
        
        # ===== WRITE EACH CHUNK AS SEPARATE MD FILE =====
        # If text was split into multiple chunks, write each as separate file
        # This improves retrieval precision (smaller, focused chunks)
        for chunk_idx, chunk in enumerate(chunks):
            chunk_count += 1  # Increment total chunk counter
            
            # ===== GENERATE FILENAME =====
            # Create filename from title slug
            base_slug = slugify(title)  # Convert title to filename-safe slug
            
            # If multiple chunks, add chunk number to filename
            # Example: "001_kra_pin_registration_chunk1.md", "001_kra_pin_registration_chunk2.md"
            # If single chunk, no chunk number needed
            if len(chunks) > 1:
                filename = f"{entry['index']:03d}_{base_slug}_chunk{chunk_idx+1}.md"
            else:
                filename = f"{entry['index']:03d}_{base_slug}.md"
            
            # ===== SANITIZE TITLE FOR YAML =====
            # Prepare title for YAML front-matter (escape quotes, truncate if needed)
            chunk_title = sanitize_title(title)
            
            # If multiple chunks, add part number to title
            # Example: "KRA PIN Registration (Part 1)", "KRA PIN Registration (Part 2)"
            if len(chunks) > 1:
                chunk_title = f"{chunk_title} (Part {chunk_idx + 1})"
            
            # ===== WRITE MARKDOWN FILE =====
            # Create full path to output Markdown file
            md_file = docs_dir / filename
            
            # Open file for writing
            with open(md_file, 'w', encoding='utf-8') as f:
                # ===== YAML FRONT-MATTER =====
                # YAML front-matter is metadata at the top of Markdown files
                # Enclosed in --- delimiters
                # Used by static site generators and our indexing script
                
                f.write("---\n")  # YAML start delimiter
                
                # Title of the document
                f.write(f'title: "{chunk_title}"\n')
                
                # Filename for reference
                f.write(f'filename: "{filename}"\n')
                
                # Auto-detected category
                f.write(f'category: "{category}"\n')
                
                # Jurisdiction (always Kenya for this project)
                f.write('jurisdiction: "Kenya"\n')
                
                # Language (defaults to English, can be updated)
                f.write('lang: "en"\n')
                
                # Source URL (where content was scraped from)
                f.write(f'source: "{entry["url"]}"\n')
                
                # Last updated date (today's date in ISO format)
                f.write(f'last_updated: "{datetime.now().strftime("%Y-%m-%d")}"\n')
                
                # Tags as JSON array (YAML can parse JSON arrays)
                # json.dumps() converts Python list to JSON string
                # Example: ['auto_import', 'kra', 'pin'] -> '["auto_import", "kra", "pin"]'
                f.write(f'tags: {json.dumps(tags)}\n')
                
                f.write("---\n\n")  # YAML end delimiter + blank line
                
                # ===== MARKDOWN CONTENT =====
                # Write the actual text content (the chunk)
                f.write(chunk)
                f.write("\n\n")  # Blank lines for readability
                
                # ===== SOURCES SECTION =====
                # Add sources section at bottom (for citation)
                f.write("Sources:\n")
                f.write(f"- {entry['url']}\n")
            
            # Log each file created
            print(f"Created {md_file.name}")
    
    # ===== SUMMARY =====
    # Print final summary
    print(f"\nChunking complete. Created {chunk_count} Markdown files in {docs_dir}")

if __name__ == '__main__':
    main()

