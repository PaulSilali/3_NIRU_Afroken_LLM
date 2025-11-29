#!/usr/bin/env python3
"""
Fetch and extract content from URLs listed in urls.txt.

This script:
1. Reads URLs from urls.txt (one per line, comments allowed with #)
2. Checks robots.txt for each domain to respect crawling rules
3. Fetches HTML content from each URL with polite rate limiting
4. Extracts readable text using readability-lxml (with BeautifulSoup fallback)
5. Saves both raw HTML and extracted text to afroken_llm_backend/raw/
6. Creates fetch_manifest.json listing all processed URLs with metadata

Saves HTML and extracted text to afroken_llm_backend/raw/
Creates fetch_manifest.json with metadata.
"""

# Standard library imports
import argparse  # For command-line argument parsing
import hashlib   # For generating MD5 hashes of URLs (for unique filenames)
import json      # For reading/writing JSON manifest file
import logging   # For structured logging output
import re        # For regular expressions (text cleaning, slugification)
import time      # For rate limiting between requests
from pathlib import Path  # For cross-platform file path handling
from urllib.parse import urlparse, urljoin  # For URL parsing and manipulation
from urllib.robotparser import RobotFileParser  # For robots.txt compliance checking

# Third-party imports
import requests  # HTTP library for fetching web pages
from bs4 import BeautifulSoup  # HTML parsing and text extraction
from readability import Document  # Main content extraction (removes ads, nav, etc.)

# Setup logging configuration
# INFO level shows progress messages, WARNING shows robots.txt issues, ERROR shows fetch failures
logging.basicConfig(
    level=logging.INFO,  # Log level: INFO shows normal progress, DEBUG would show more detail
    format='%(asctime)s - %(levelname)s - %(message)s'  # Format: timestamp, level, message
)
logger = logging.getLogger(__name__)  # Get logger instance for this module

# User agent string for HTTP requests
# Identifies our bot to web servers - should be polite and include contact info
# Some sites block requests without proper user agents
USER_AGENT = "AfroKen-LLM-Bot/1.0 (Educational; Contact: support@afroken.go.ke)"

def check_robots_allowed(url: str, user_agent: str = USER_AGENT) -> bool:
    """
    Check if URL is allowed by robots.txt.
    
    This function respects web crawling etiquette by checking robots.txt before fetching.
    robots.txt is a standard file that websites use to tell crawlers which URLs they can access.
    
    Args:
        url: The URL we want to fetch
        user_agent: Our bot's user agent string (defaults to USER_AGENT constant)
    
    Returns:
        True if URL is allowed by robots.txt, False if disallowed.
        Returns True by default if robots.txt check fails (fail-open policy).
    
    Example:
        check_robots_allowed("https://www.kra.go.ke/services/pin")
        # Returns True if robots.txt allows it, False if it blocks our user agent
    """
    try:
        # Parse the URL to extract scheme (http/https) and netloc (domain)
        # Example: "https://www.kra.go.ke/services/pin" -> scheme="https", netloc="www.kra.go.ke"
        parsed = urlparse(url)
        
        # Construct robots.txt URL for the same domain
        # Example: "https://www.kra.go.ke/robots.txt"
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        
        # Create RobotFileParser instance to read and parse robots.txt
        rp = RobotFileParser()
        rp.set_url(robots_url)  # Tell parser where to find robots.txt
        rp.read()  # Fetch and parse robots.txt file
        
        # Check if our user agent is allowed to fetch this specific URL
        # Returns True if allowed, False if disallowed
        return rp.can_fetch(user_agent, url)
    except Exception as e:
        # If robots.txt check fails (network error, malformed robots.txt, etc.)
        # Log a warning but allow the fetch (fail-open policy)
        # This prevents one broken robots.txt from stopping the entire pipeline
        logger.warning(f"Robots check failed for {url}: {e}. Allowing by default.")
        return True  # Allow by default if check fails

def slugify(text: str, max_length: int = 50) -> str:
    """
    Convert text to URL-friendly slug for use in filenames.
    
    A slug is a URL-safe version of text (lowercase, no special chars, spaces become hyphens).
    Used to create readable filenames from URLs or titles.
    
    Args:
        text: Input text to convert (e.g., "KRA Services - PIN Registration")
        max_length: Maximum length of output slug (default 50 chars)
    
    Returns:
        URL-friendly slug (e.g., "kra-services-pin-registration")
    
    Example:
        slugify("KRA Services - PIN Registration") -> "kra-services-pin-registration"
        slugify("https://www.kra.go.ke/services/pin") -> "httpswwwkragokeservicespin"
    """
    # Convert to lowercase for consistency
    # Example: "KRA Services" -> "kra services"
    text = text.lower()
    
    # Remove all characters that aren't word characters (\w = letters, digits, underscore),
    # whitespace (\s), or hyphens (-)
    # This removes special chars like /, :, ?, &, etc.
    # Example: "https://www.kra.go.ke" -> "httpswwwkragoke"
    text = re.sub(r'[^\w\s-]', '', text)
    
    # Replace one or more spaces or hyphens with a single hyphen
    # Example: "kra  services" -> "kra-services", "kra---services" -> "kra-services"
    text = re.sub(r'[-\s]+', '-', text)
    
    # Truncate to max_length and remove leading/trailing hyphens
    # Example: "kra-services-pin-registration" -> "kra-services-pin-registration" (if <= 50)
    return text[:max_length].strip('-')

def extract_text(html: str, url: str) -> tuple[str, str]:
    """
    Extract readable text content and title from HTML.
    
    This function uses a two-stage approach:
    1. Primary: readability-lxml library (removes ads, nav, sidebars automatically)
    2. Fallback: BeautifulSoup manual extraction (if readability fails)
    
    Also tries to extract a better title from <h1> or <h2> tags rather than just <title>.
    
    Args:
        html: Raw HTML content as string
        url: Source URL (used for error logging)
    
    Returns:
        Tuple of (title, text_content) where:
        - title: Extracted page title (from h1, h2, or <title> tag)
        - text_content: Clean, readable text with HTML tags removed
    
    Example:
        extract_text("<html><h1>KRA PIN</h1><p>Register here...</p></html>", "https://kra.go.ke")
        # Returns: ("KRA PIN", "Register here...")
    """
    try:
        # PRIMARY METHOD: Use readability-lxml library
        # This library is specifically designed to extract main article content
        # It automatically removes navigation, ads, sidebars, footers, etc.
        # Works well for news articles and blog posts
        doc = Document(html)
        
        # Get title from readability's extraction
        # If readability can't find a title, default to "Untitled"
        title = doc.title() or "Untitled"
        
        # Get the main content summary (HTML still present, needs cleaning)
        text = doc.summary()
        
        # Clean HTML tags from the summary to get plain text
        # BeautifulSoup parses the HTML and extracts just the text content
        soup = BeautifulSoup(text, 'html.parser')
        # get_text() extracts all text, separator='\n' puts line breaks between elements
        # strip=True removes leading/trailing whitespace from each line
        text = soup.get_text(separator='\n', strip=True)
        
        # IMPROVEMENT: Try to get a better title from HTML structure
        # <h1> tags usually contain the main page heading (better than <title>)
        # Parse the full HTML again to search for h1/h2
        soup_full = BeautifulSoup(html, 'html.parser')
        
        # Look for <h1> tag (main heading)
        h1 = soup_full.find('h1')
        if h1:
            # Extract text from h1, remove extra whitespace
            h1_text = h1.get_text(strip=True)
            # Only use if it's a reasonable length (very long h1 might be garbage)
            if h1_text and len(h1_text) < 200:  # Reasonable title length
                title = h1_text
        else:
            # If no h1, try h2 (subheading, but still better than <title>)
            h2 = soup_full.find('h2')
            if h2:
                h2_text = h2.get_text(strip=True)
                if h2_text and len(h2_text) < 200:
                    title = h2_text
        
        return title, text
        
    except Exception as e:
        # FALLBACK METHOD: If readability fails, use BeautifulSoup manually
        # This happens when readability can't parse the HTML structure
        logger.warning(f"Readability failed for {url}, using BeautifulSoup fallback: {e}")
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements that clutter the text
        # These elements typically don't contain main content:
        # - <script>: JavaScript code
        # - <style>: CSS styles
        # - <nav>: Navigation menus
        # - <footer>: Footer content
        # - <header>: Header/navigation
        # decompose() removes the element and all its children from the tree
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Extract title with priority: h1 > h2 > <title> tag
        title = "Untitled"  # Default if nothing found
        
        # Try h1 first (most important heading)
        h1 = soup.find('h1')
        if h1:
            title = h1.get_text(strip=True)
        else:
            # Try h2 if no h1
            h2 = soup.find('h2')
            if h2:
                title = h2.get_text(strip=True)
            else:
                # Fallback to <title> tag (usually in <head>)
                title_tag = soup.find('title')
                if title_tag:
                    title = title_tag.get_text(strip=True)
        
        # Extract all remaining text from the cleaned HTML
        # separator='\n' preserves paragraph structure
        # strip=True removes extra whitespace
        text = soup.get_text(separator='\n', strip=True)
        
        return title, text

def fetch_url(url: str, timeout: int = 10) -> tuple[str, str] | None:
    """
    Fetch HTML content from a URL and extract title.
    
    This function performs the actual HTTP request to download the webpage.
    It includes proper error handling and uses a polite user agent.
    
    Args:
        url: The URL to fetch (must be a valid HTTP/HTTPS URL)
        timeout: Maximum seconds to wait for response (default 10)
                Prevents hanging on slow/unresponsive servers
    
    Returns:
        Tuple of (html_content, title) if successful
        None if fetch fails (network error, 404, timeout, etc.)
    
    Example:
        fetch_url("https://www.kra.go.ke/services/pin")
        # Returns: ("<html>...", "KRA PIN Registration") or None if failed
    """
    try:
        # Set HTTP headers for the request
        # User-Agent identifies our bot (required by some sites, polite to include)
        headers = {'User-Agent': USER_AGENT}
        
        # Perform HTTP GET request
        # headers: Include our user agent
        # timeout: Abort if server doesn't respond within timeout seconds
        response = requests.get(url, headers=headers, timeout=timeout)
        
        # Raise an exception if HTTP status code indicates an error (4xx, 5xx)
        # This catches 404 (not found), 500 (server error), etc.
        # If status is 200-299, this does nothing
        response.raise_for_status()
        
        # Get the HTML content as a string
        # response.text automatically decodes the response body using the charset
        # specified in Content-Type header (usually UTF-8)
        html = response.text
        
        # Extract title and text from the HTML
        # This uses the extract_text() function which handles readability/BeautifulSoup
        title, text = extract_text(html, url)
        
        # Return both HTML (for archiving) and title (for manifest)
        # Note: text is extracted but not returned here (saved separately in main())
        return html, title
        
    except Exception as e:
        # If anything goes wrong (network error, timeout, HTTP error, parsing error)
        # Log the error and return None to indicate failure
        # The main() function will skip this URL and continue with others
        logger.error(f"Failed to fetch {url}: {e}")
        return None

def main():
    """
    Main function: Orchestrates the URL fetching and extraction process.
    
    This function:
    1. Parses command-line arguments
    2. Reads URLs from urls.txt file
    3. For each URL: checks robots.txt, fetches content, extracts text, saves files
    4. Creates a manifest.json file listing all processed URLs
    5. Implements rate limiting to be polite to web servers
    """
    # ===== COMMAND-LINE ARGUMENT PARSING =====
    # Create argument parser to handle CLI options
    parser = argparse.ArgumentParser(description='Fetch and extract content from URLs')
    
    # Positional argument: path to urls.txt file
    # nargs='?' means it's optional (defaults to 'urls.txt' if not provided)
    parser.add_argument('urls_file', type=str, default='urls.txt', nargs='?',
                       help='Path to urls.txt file')
    
    # Optional flag: limit number of URLs to fetch (useful for testing)
    # Example: --max-pages 5 will only fetch first 5 URLs
    parser.add_argument('--max-pages', type=int, default=None,
                       help='Maximum number of pages to fetch')
    
    # Optional flag: control delay between requests (rate limiting)
    # Default 1.5 seconds is polite - prevents overwhelming servers
    parser.add_argument('--rate-limit', type=float, default=1.5,
                       help='Seconds to wait between requests')
    
    # Optional flag: force re-fetch even if files already exist
    # By default, script skips URLs that were already fetched (idempotent)
    parser.add_argument('--force', action='store_true',
                       help='Re-fetch even if files exist')
    parser.add_argument('--skip-disallowed', action='store_true',
                       help='Skip URLs marked as disallowed in robots_report.json (if exists)')
    
    # Parse command-line arguments into args object
    args = parser.parse_args()
    
    # ===== PATH SETUP =====
    # Get the directory where this script is located (scripts/rag/)
    # Path(__file__) is the current script file, .parent gets its directory
    script_dir = Path(__file__).parent
    
    # Get backend root (two levels up from scripts/rag/)
    backend_dir = script_dir.parent.parent
    
    # Construct path to urls.txt file (in config/ directory)
    # If user provided a path, use it; otherwise use default 'urls.txt' in config directory
    if args.urls_file == 'urls.txt':
        urls_file = backend_dir / 'config' / 'urls.txt'
    else:
        urls_file = Path(args.urls_file) if Path(args.urls_file).is_absolute() else backend_dir / args.urls_file
    
    # Create raw/ directory in data/ for storing fetched HTML and text files
    # exist_ok=True means don't error if directory already exists
    raw_dir = backend_dir / 'data' / 'raw'
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    # ===== READ URLS FROM FILE =====
    # List to store all valid URLs from the file
    urls = []
    
    # Open urls.txt file for reading
    # encoding='utf-8' ensures we can handle international characters
    with open(urls_file, 'r', encoding='utf-8') as f:
        # Read file line by line
        for line in f:
            # Remove leading/trailing whitespace (spaces, tabs, newlines)
            line = line.strip()
            
            # Skip empty lines and comment lines (lines starting with #)
            # This allows users to add comments in urls.txt like:
            #   # KRA URLs
            #   https://www.kra.go.ke/services/pin
            if line and not line.startswith('#'):
                urls.append(line)
    
    # If --max-pages was specified, limit the URL list
    # Useful for testing with a small subset
    if args.max_pages:
        urls = urls[:args.max_pages]
    
    # Log how many URLs we found
    logger.info(f"Found {len(urls)} URLs to fetch")
    
    # ===== LOAD ROBOTS REPORT (IF AVAILABLE) =====
    # If --skip-disallowed flag is set, try to load robots_report.json
    # This allows skipping disallowed URLs without re-checking robots.txt
    robots_report = {}
    if args.skip_disallowed:
        robots_report_file = backend_dir / 'robots_report.json'
        if robots_report_file.exists():
            try:
                with open(robots_report_file, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                    # Create lookup dict: url -> allowed status
                    robots_report = {r['url']: r['allowed'] for r in report_data}
                logger.info(f"Loaded robots report: {len(robots_report)} URLs")
            except Exception as e:
                logger.warning(f"Could not load robots_report.json: {e}. Will check robots.txt on-the-fly.")
    
    # ===== PROCESS EACH URL =====
    # List to store metadata about each processed URL
    # This will be saved as fetch_manifest.json at the end
    manifest = []
    
    # Loop through each URL with index (starting at 1 for human-readable numbering)
    # enumerate(urls, 1) gives us (1, url1), (2, url2), etc.
    for idx, url in enumerate(urls, 1):
        # Log progress: [1/10] Processing https://...
        logger.info(f"[{idx}/{len(urls)}] Processing {url}")
        
        # ===== ROBOTS.TXT CHECK =====
        # Check if this URL is allowed by robots.txt
        # If using robots report, check that first (faster)
        if args.skip_disallowed and url in robots_report:
            # Use pre-checked status from report
            if robots_report[url] == 'disallowed':
                logger.warning(f"Skipping {url} - disallowed by robots.txt (from report)")
                continue  # Skip to next URL in loop
            # If allowed or unknown, continue to fetch
        elif not check_robots_allowed(url):
            # On-the-fly robots.txt check (if not using report)
            logger.warning(f"Skipping {url} - disallowed by robots.txt")
            continue  # Skip to next URL in loop
        
        # ===== GENERATE FILENAMES =====
        # Create unique, readable filenames for this URL
        
        # Generate MD5 hash of URL (first 8 chars) for uniqueness
        # This ensures different URLs get different files even if slug is similar
        # Example: "https://kra.go.ke/pin" -> "a1b2c3d4"
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        
        # Convert URL to a slug (URL-friendly filename)
        # Example: "https://www.kra.go.ke/services/pin" -> "httpswwwkragokeservicespin"
        slug = slugify(url)
        
        # Create filenames with format: 001_slug_hash.html and 001_slug_hash.txt
        # {idx:03d} formats index as 3-digit zero-padded number (001, 002, 003, ...)
        # This keeps files sorted by processing order
        html_file = raw_dir / f"{idx:03d}_{slug}_{url_hash}.html"
        txt_file = raw_dir / f"{idx:03d}_{slug}_{url_hash}.txt"
        
        # ===== SKIP IF ALREADY EXISTS =====
        # If files already exist and --force flag not used, skip fetching
        # This makes the script idempotent (safe to run multiple times)
        if not args.force and html_file.exists() and txt_file.exists():
            logger.info(f"Skipping {url} - files already exist")
            
            # Still add to manifest (read title from existing file)
            # Open existing text file and read first line (which contains title)
            with open(txt_file, 'r', encoding='utf-8') as f:
                title = f.readline().strip() or "Untitled"
            
            # Add entry to manifest even though we didn't re-fetch
            manifest.append({
                'index': idx,  # Processing order number
                'url': url,  # Original URL
                'title': title,  # Extracted title
                'base': urlparse(url).netloc,  # Domain name (e.g., "www.kra.go.ke")
                'html_file': str(html_file.relative_to(backend_dir)),  # Relative path to HTML file
                'txt_file': str(txt_file.relative_to(backend_dir))  # Relative path to text file
            })
            continue  # Skip to next URL
        
        # ===== FETCH URL =====
        # Call fetch_url() to download HTML content
        # Returns (html, title) if successful, None if failed
        result = fetch_url(url)
        if result is None:
            # If fetch failed, log error and continue to next URL
            # (Error already logged in fetch_url function)
            continue
        
        # Unpack the result tuple
        html, title = result
        
        # ===== SAVE HTML FILE =====
        # Save raw HTML for archival/reference purposes
        # Open file in write mode ('w'), encoding='utf-8' for international characters
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html)  # Write entire HTML content
        
        # ===== EXTRACT AND SAVE TEXT =====
        # Extract clean text from HTML (removes tags, gets main content)
        # We already have title from fetch_url, so use _ to ignore it
        _, text = extract_text(html, url)
        
        # Save extracted text to .txt file
        # Format: first line is title, then blank line, then text content
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(f"{title}\n\n")  # Write title and blank line
            f.write(text)  # Write extracted text content
        
        # ===== ADD TO MANIFEST =====
        # Create manifest entry with all metadata about this URL
        manifest.append({
            'index': idx,  # Processing order (1, 2, 3, ...)
            'url': url,  # Original URL that was fetched
            'title': title,  # Extracted page title
            'base': urlparse(url).netloc,  # Domain name for grouping
            'html_file': str(html_file.relative_to(backend_dir)),  # Path to HTML (relative to backend dir)
            'txt_file': str(txt_file.relative_to(backend_dir))  # Path to text (relative to backend dir)
        })
        
        # Log success
        logger.info(f"Saved {html_file.name} and {txt_file.name}")
        
        # ===== RATE LIMITING =====
        # Wait before fetching next URL to be polite to web servers
        # Only wait if there are more URLs to process (don't wait after last one)
        # args.rate_limit defaults to 1.5 seconds
        if idx < len(urls):
            time.sleep(args.rate_limit)
    
    # ===== SAVE MANIFEST =====
    # Create manifest.json file listing all processed URLs
    # This file is used by chunk_and_write_md.py to know which files to process
    manifest_file = raw_dir / 'fetch_manifest.json'
    
    # Write manifest as pretty-printed JSON
    # indent=2: Makes JSON readable with 2-space indentation
    # ensure_ascii=False: Allows Unicode characters (important for international content)
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    # Log completion
    logger.info(f"Fetch complete. Manifest saved to {manifest_file}")
    logger.info(f"Processed {len(manifest)} URLs")

if __name__ == '__main__':
    main()

