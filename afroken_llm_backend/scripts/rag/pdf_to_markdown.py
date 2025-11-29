#!/usr/bin/env python3
"""
Extract text from PDF and convert to Markdown format for RAG corpus.

This script:
1. Reads a PDF file
2. Extracts text content
3. Creates a Markdown file with YAML front-matter
4. Saves to data/docs/ directory
5. Ready to be indexed by index_faiss.py

Usage:
    python scripts/rag/pdf_to_markdown.py path/to/handbook.pdf
    python scripts/rag/pdf_to_markdown.py path/to/handbook.pdf --title "SHA Handbook" --category "ministry_faq"
"""

import argparse
import re
from datetime import datetime
from pathlib import Path

# Try to import PDF libraries, with auto-install fallback
PDF_LIBRARY = None
PyPDF2 = None
pdfplumber = None

def ensure_pdf_library():
    """Ensure a PDF library is available, install if needed."""
    global PDF_LIBRARY, PyPDF2, pdfplumber
    
    # Try PyPDF2 first (lighter, faster)
    try:
        import PyPDF2 as _PyPDF2
        PyPDF2 = _PyPDF2
        PDF_LIBRARY = "PyPDF2"
        return True
    except ImportError:
        pass
    
    # Try pdfplumber (better for complex PDFs)
    try:
        import pdfplumber as _pdfplumber
        pdfplumber = _pdfplumber
        PDF_LIBRARY = "pdfplumber"
        return True
    except ImportError:
        pass
    
    # Neither available - try to install
    print("⚠ No PDF library found. Attempting to install PyPDF2...")
    import subprocess
    import sys
    
    try:
        # Try installing PyPDF2 first (lighter)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2", "--quiet"])
        import PyPDF2 as _PyPDF2
        PyPDF2 = _PyPDF2
        PDF_LIBRARY = "PyPDF2"
        print("✅ Installed PyPDF2 successfully")
        return True
    except (subprocess.CalledProcessError, ImportError):
        # If PyPDF2 fails, try pdfplumber
        try:
            print("⚠ PyPDF2 installation failed. Trying pdfplumber...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pdfplumber", "--quiet"])
            import pdfplumber as _pdfplumber
            pdfplumber = _pdfplumber
            PDF_LIBRARY = "pdfplumber"
            print("✅ Installed pdfplumber successfully")
            return True
        except (subprocess.CalledProcessError, ImportError):
            print("❌ Failed to install PDF libraries automatically.")
            print("\nPlease install manually:")
            print("  pip install PyPDF2")
            print("  OR")
            print("  pip install pdfplumber")
            return False

# Initialize PDF library on import
ensure_pdf_library()


def extract_text_pypdf2(pdf_path: Path) -> str:
    """Extract text from PDF using PyPDF2."""
    global PyPDF2
    if PyPDF2 is None:
        import PyPDF2 as _PyPDF2
        PyPDF2 = _PyPDF2
    
    text = ""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    return text


def extract_text_pdfplumber(pdf_path: Path) -> str:
    """Extract text from PDF using pdfplumber."""
    global pdfplumber
    if pdfplumber is None:
        import pdfplumber as _pdfplumber
        pdfplumber = _pdfplumber
    
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract text from PDF using available library."""
    global PDF_LIBRARY
    
    # Ensure library is available
    if not PDF_LIBRARY:
        if not ensure_pdf_library():
            raise ImportError(
                "No PDF library found. Install one:\n"
                "  pip install PyPDF2\n"
                "  OR\n"
                "  pip install pdfplumber"
            )
    
    if PDF_LIBRARY == "PyPDF2":
        return extract_text_pypdf2(pdf_path)
    elif PDF_LIBRARY == "pdfplumber":
        return extract_text_pdfplumber(pdf_path)
    else:
        raise ImportError(
            "No PDF library found. Install one:\n"
            "  pip install PyPDF2\n"
            "  OR\n"
            "  pip install pdfplumber"
        )


def clean_text(text: str) -> str:
    """Clean extracted PDF text."""
    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Remove page numbers and headers/footers (common patterns)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
    # Remove excessive spaces
    text = re.sub(r' {2,}', ' ', text)
    # Strip leading/trailing whitespace
    return text.strip()


def create_markdown_from_pdf(
    pdf_path: Path,
    output_dir: Path,
    title: str = None,
    category: str = "service_workflow",
    source: str = None,
    tags: list = None
) -> Path:
    """
    Convert PDF to Markdown file with YAML front-matter.
    
    Args:
        pdf_path: Path to PDF file
        output_dir: Directory to save Markdown file
        title: Document title (defaults to PDF filename)
        category: Document category (default: service_workflow)
        source: Source URL or reference
        tags: List of tags
    
    Returns:
        Path to created Markdown file
    """
    # Extract text from PDF
    print(f"Extracting text from {pdf_path.name}...")
    text = extract_text_from_pdf(pdf_path)
    text = clean_text(text)
    
    if not text or len(text.strip()) < 50:
        raise ValueError(f"Extracted text is too short or empty. PDF may be image-based or corrupted.")
    
    # Generate filename from PDF name
    pdf_stem = pdf_path.stem
    # Sanitize filename (remove special chars, spaces)
    safe_name = re.sub(r'[^\w\-_]', '_', pdf_stem.lower())
    safe_name = re.sub(r'_+', '_', safe_name).strip('_')
    md_filename = f"{safe_name}.md"
    md_path = output_dir / md_filename
    
    # Default title if not provided
    if not title:
        title = pdf_stem.replace('_', ' ').title()
    
    # Default source if not provided
    if not source:
        source = f"PDF: {pdf_path.name}"
    
    # Default tags if not provided
    if not tags:
        tags = ["pdf_import", "handbook"]
        # Auto-detect tags from title/text
        text_lower = text.lower()
        if 'sha' in text_lower or 'social health' in text_lower:
            tags.append('sha')
        if 'nhif' in text_lower:
            tags.append('nhif')
        if 'health' in text_lower:
            tags.append('health')
    
    # Create YAML front-matter
    yaml_frontmatter = f"""---
title: "{title}"
filename: "{md_filename}"
category: "{category}"
jurisdiction: "Kenya"
lang: "en"
source: "{source}"
last_updated: "{datetime.now().strftime('%Y-%m-%d')}"
tags: {tags}
---

"""
    
    # Combine front-matter and content
    markdown_content = yaml_frontmatter + text
    
    # Add sources section at end
    markdown_content += f"\n\nSources:\n- {source}\n"
    
    # Write Markdown file
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"✅ Created: {md_path}")
    print(f"   Title: {title}")
    print(f"   Category: {category}")
    print(f"   Text length: {len(text)} characters")
    
    return md_path


def check_if_already_converted(pdf_path: Path, output_dir: Path) -> bool:
    """
    Check if PDF has already been converted to Markdown.
    
    Returns True if corresponding .md file exists in output_dir.
    """
    pdf_stem = pdf_path.stem
    safe_name = re.sub(r'[^\w\-_]', '_', pdf_stem.lower())
    safe_name = re.sub(r'_+', '_', safe_name).strip('_')
    md_filename = f"{safe_name}.md"
    md_path = output_dir / md_filename
    return md_path.exists()


def process_all_pdfs_in_directory(
    pdf_dir: Path,
    output_dir: Path,
    category: str = "service_workflow",
    force: bool = False
) -> list:
    """
    Process all PDFs in a directory, skipping already converted ones.
    
    Args:
        pdf_dir: Directory containing PDF files
        output_dir: Directory to save Markdown files
        category: Default category for PDFs
        force: If True, re-convert even if .md exists
    
    Returns:
        List of created Markdown file paths
    """
    if not pdf_dir.exists():
        print(f"⚠ PDF directory not found: {pdf_dir}")
        print(f"  Creating directory...")
        pdf_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {pdf_dir}")
        print(f"\nPlace your PDF files in: {pdf_dir}")
        return []
    
    # Find all PDF files
    pdf_files = list(pdf_dir.glob("*.pdf")) + list(pdf_dir.glob("*.PDF"))
    
    if not pdf_files:
        print(f"ℹ No PDF files found in: {pdf_dir}")
        print(f"  Place PDF files here to auto-convert them")
        return []
    
    print(f"\n📚 Found {len(pdf_files)} PDF file(s) in {pdf_dir}")
    
    converted = []
    skipped = []
    failed = []
    
    for pdf_path in pdf_files:
        # Check if already converted
        if not force and check_if_already_converted(pdf_path, output_dir):
            pdf_stem = pdf_path.stem
            safe_name = re.sub(r'[^\w\-_]', '_', pdf_stem.lower())
            safe_name = re.sub(r'_+', '_', safe_name).strip('_')
            md_filename = f"{safe_name}.md"
            print(f"⏭ Skipping {pdf_path.name} (already converted: {md_filename})")
            skipped.append(pdf_path)
            continue
        
        try:
            # Auto-detect title from filename
            title = pdf_path.stem.replace('_', ' ').replace('-', ' ').title()
            
            # Auto-detect category from filename/content
            pdf_lower = pdf_path.stem.lower()
            detected_category = category
            if 'faq' in pdf_lower or 'question' in pdf_lower:
                detected_category = 'ministry_faq'
            elif 'handbook' in pdf_lower or 'guide' in pdf_lower:
                detected_category = 'service_workflow'
            elif 'legal' in pdf_lower or 'act' in pdf_lower:
                detected_category = 'legal_snippet'
            
            # Convert PDF
            md_path = create_markdown_from_pdf(
                pdf_path=pdf_path,
                output_dir=output_dir,
                title=title,
                category=detected_category,
                source=f"PDF: {pdf_path.name}",
                tags=None  # Auto-detect tags
            )
            converted.append(md_path)
            
        except Exception as e:
            print(f"❌ Failed to convert {pdf_path.name}: {e}")
            failed.append(pdf_path)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 Conversion Summary:")
    print(f"  ✅ Converted: {len(converted)}")
    print(f"  ⏭ Skipped (already converted): {len(skipped)}")
    if failed:
        print(f"  ❌ Failed: {len(failed)}")
    print(f"{'='*60}")
    
    return converted


def main():
    """Main function: Parse arguments and convert PDF to Markdown."""
    parser = argparse.ArgumentParser(
        description="Convert PDF to Markdown for RAG corpus",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert a single PDF
  python pdf_to_markdown.py path/to/file.pdf
  
  # Convert all PDFs in data/pdfs/ directory (auto-mode)
  python pdf_to_markdown.py --auto
  
  # Force re-convert all PDFs (even if already converted)
  python pdf_to_markdown.py --auto --force
        """
    )
    parser.add_argument(
        'pdf_path',
        type=Path,
        nargs='?',
        default=None,
        help='Path to PDF file (or use --auto to process all PDFs in data/pdfs/)'
    )
    parser.add_argument(
        '--auto',
        action='store_true',
        help='Auto-process all PDFs in data/pdfs/ directory'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force re-conversion even if .md file already exists'
    )
    parser.add_argument(
        '--title',
        type=str,
        help='Document title (defaults to PDF filename)'
    )
    parser.add_argument(
        '--category',
        type=str,
        default='service_workflow',
        choices=['service_workflow', 'ministry_faq', 'county_service', 'legal_snippet', 'ussd_sms', 'language_pack', 'agent_ops', 'safety_ethics', 'officer_template'],
        help='Document category'
    )
    parser.add_argument(
        '--source',
        type=str,
        help='Source URL or reference'
    )
    parser.add_argument(
        '--tags',
        nargs='+',
        help='Tags (space-separated)'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=None,
        help='Output directory (default: data/docs/)'
    )
    parser.add_argument(
        '--pdf-dir',
        type=Path,
        default=None,
        help='PDF directory for --auto mode (default: data/pdfs/)'
    )
    
    args = parser.parse_args()
    
    # Determine directories
    script_dir = Path(__file__).parent.parent.parent
    if args.output_dir:
        output_dir = args.output_dir
    else:
        output_dir = script_dir / 'data' / 'docs'
    
    if args.pdf_dir:
        pdf_dir = args.pdf_dir
    else:
        pdf_dir = script_dir / 'data' / 'pdfs'
    
    # Auto-mode: process all PDFs in directory
    if args.auto or args.pdf_path is None:
        try:
            converted = process_all_pdfs_in_directory(
                pdf_dir=pdf_dir,
                output_dir=output_dir,
                category=args.category,
                force=args.force
            )
            
            if converted:
                print(f"\n✅ Success! Converted {len(converted)} PDF(s)")
                print(f"\nNext steps:")
                print(f"  1. Review files in: {output_dir}")
                print(f"  2. Re-index the corpus:")
                print(f"     python scripts/rag/index_faiss.py")
                print(f"  3. Restart backend to use the new content")
            elif not args.force:
                print(f"\n💡 Tip: Use --force to re-convert existing PDFs")
            
            return 0
            
        except ImportError as e:
            print(f"❌ Error: {e}")
            return 1
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1
    
    # Single file mode
    if not args.pdf_path:
        print("❌ Error: Please provide a PDF path or use --auto")
        parser.print_help()
        return 1
    
    # Validate PDF exists
    if not args.pdf_path.exists():
        print(f"❌ Error: PDF file not found: {args.pdf_path}")
        return 1
    
    try:
        # Convert PDF to Markdown
        md_path = create_markdown_from_pdf(
            pdf_path=args.pdf_path,
            output_dir=output_dir,
            title=args.title,
            category=args.category,
            source=args.source,
            tags=args.tags
        )
        
        print(f"\n✅ Success! Markdown file created: {md_path}")
        print(f"\nNext steps:")
        print(f"  1. Review the file: {md_path}")
        print(f"  2. Re-index the corpus:")
        print(f"     python scripts/rag/index_faiss.py")
        print(f"  3. Restart backend to use the new content")
        
        return 0
        
    except ImportError as e:
        print(f"❌ Error: {e}")
        print(f"\nInstall a PDF library:")
        print(f"  pip install PyPDF2")
        print(f"  OR")
        print(f"  pip install pdfplumber")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())

