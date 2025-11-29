#!/usr/bin/env python3
"""
check_robots_report.py

Pre-check robots.txt compliance for all URLs before fetching.

Usage:
  python check_robots_report.py urls.txt

Outputs:
  - robots_report.json (full structured report)
  - robots_report.csv (spreadsheet-friendly summary)

Notes:
  - Respects robots.txt rules for User-agent: *
  - Polite rate limit (default 1.0s between distinct domains)
  - If robots.txt missing -> marks "no_robots"
  - If fetch fails -> marks "error" with status / exception
  - Groups URLs by domain to minimize robots.txt fetches
"""

import sys
import requests
from urllib.parse import urlparse
import time
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

# HTTP headers for polite crawling
HEADERS = {"User-Agent": "AfroKen-RAG-Crawler/1.0 (Educational; Contact: support@afroken.go.ke)"}

# Rate limiting: seconds between domain robots.txt fetches
# Prevents overwhelming servers when checking multiple URLs from same domain
RATE_LIMIT = 1.0  # seconds between domain robots fetches

# Timeout for HTTP requests (prevents hanging on slow servers)
TIMEOUT = 8  # seconds per HTTP request

# User agent to check rules for (robots.txt can have different rules per user-agent)
USER_AGENT_TO_CHECK = "*"  # rules applied to user-agent "*" (default/wildcard)


def canonical_domain(url: str) -> str:
    """
    Extract canonical domain URL from a full URL.
    
    Args:
        url: Full URL (e.g., "https://www.kra.go.ke/services/pin")
    
    Returns:
        Canonical domain URL (e.g., "https://www.kra.go.ke")
    
    Example:
        canonical_domain("https://www.kra.go.ke/services/pin")
        # Returns: "https://www.kra.go.ke"
    """
    # Parse URL to extract components
    p = urlparse(url)
    
    # Default to https if no scheme specified
    scheme = p.scheme or "https"
    
    # Get network location (domain)
    netloc = p.netloc
    
    # Return canonical domain URL
    return f"{scheme}://{netloc}"


def fetch_robots(domain_url: str) -> dict:
    """
    Fetch robots.txt file for a domain.
    
    Args:
        domain_url: Canonical domain URL (e.g., "https://www.kra.go.ke")
    
    Returns:
        Dictionary with:
        - status_code: HTTP status code (200, 404, None if error)
        - text: robots.txt content (if status 200)
        - url: Full robots.txt URL
        - error: Error message (if fetch failed)
    
    Example:
        fetch_robots("https://www.kra.go.ke")
        # Returns: {"status_code": 200, "text": "User-agent: *\nDisallow: /admin", ...}
    """
    # Construct robots.txt URL
    # rstrip("/") removes trailing slash to avoid double slashes
    robots_url = domain_url.rstrip("/") + "/robots.txt"
    
    try:
        # Fetch robots.txt with polite headers and timeout
        r = requests.get(robots_url, headers=HEADERS, timeout=TIMEOUT)
        
        # Return result with status code and text (only if 200)
        return {
            "status_code": r.status_code,
            "text": r.text if r.status_code == 200 else "",
            "url": robots_url
        }
    except Exception as e:
        # Return error information if fetch failed
        return {
            "status_code": None,
            "text": "",
            "error": str(e),
            "url": robots_url
        }


def parse_robots(robots_text: str) -> dict:
    """
    Parse robots.txt into a dictionary of user-agent -> list of rules.
    
    robots.txt format:
        User-agent: *
        Disallow: /admin
        Allow: /public
    
    Args:
        robots_text: Raw robots.txt content
    
    Returns:
        Dictionary mapping user-agent strings to lists of (rule_type, path) tuples
        rule_type: "allow" or "disallow"
        Example: {"*": [("disallow", "/admin"), ("allow", "/public")]}
    
    Example:
        parse_robots("User-agent: *\nDisallow: /admin")
        # Returns: {"*": [("disallow", "/admin")]}
    """
    # Dictionary to store rules per user-agent
    rules = defaultdict(list)
    
    # Current user-agent being processed (None initially)
    ua = None
    
    # Process each line of robots.txt
    for raw in robots_text.splitlines():
        # Remove comments (everything after #)
        line = raw.split("#", 1)[0].strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Match "User-agent: <name>" line
        # (?i) makes it case-insensitive
        m_ua = re.match(r'(?i)User-agent\s*:\s*(.+)$', line)
        if m_ua:
            # Extract user-agent name
            ua = m_ua.group(1).strip()
            continue  # Move to next line
        
        # Match "Disallow: <path>" line
        m_dis = re.match(r'(?i)Disallow\s*:\s*(.*)$', line)
        if m_dis and ua is not None:
            # Extract path pattern
            path = m_dis.group(1).strip()
            # Add disallow rule for current user-agent
            rules[ua].append(("disallow", path))
            continue
        
        # Match "Allow: <path>" line
        m_all = re.match(r'(?i)Allow\s*:\s*(.*)$', line)
        if m_all and ua is not None:
            # Extract path pattern
            path = m_all.group(1).strip()
            # Add allow rule for current user-agent
            rules[ua].append(("allow", path))
            continue
    
    # Convert defaultdict to regular dict for return
    return dict(rules)


def path_matches(pattern: str, path: str) -> bool:
    """
    Check if a URL path matches a robots.txt pattern.
    
    This is a basic prefix matching implementation.
    Full robots.txt spec supports wildcards (*) and end-of-path ($), but this
    simplified version uses prefix matching which covers most common cases.
    
    Args:
        pattern: robots.txt pattern (e.g., "/admin", "/private/")
        path: URL path to check (e.g., "/admin/users")
    
    Returns:
        True if path matches pattern, False otherwise
    
    Note:
        Empty pattern (disallow: ) means no restriction (allow all)
    
    Example:
        path_matches("/admin", "/admin/users")  # Returns: True
        path_matches("/admin", "/public")  # Returns: False
    """
    # Empty pattern means no restriction (allow all)
    if pattern == "":
        return False
    
    # Normalize path to start with /
    if not path.startswith("/"):
        path = "/" + path
    
    # Check if path starts with pattern (prefix match)
    return path.startswith(pattern)


def is_path_allowed_for_ua(rules_dict: dict, path: str, ua_to_check: str = "*") -> tuple:
    """
    Determine if a path is allowed or disallowed based on robots.txt rules.
    
    This function checks rules for the specified user-agent (and wildcard "*")
    and applies rule precedence: more specific (longer) patterns take precedence,
    and Allow rules override Disallow rules when patterns have same length.
    
    Args:
        rules_dict: Parsed robots.txt rules (from parse_robots())
        path: URL path to check (e.g., "/services/pin")
        ua_to_check: User-agent to check rules for (default "*")
    
    Returns:
        Tuple of (status, matched_rules) where:
        - status: "allowed", "disallowed", or "unknown"
        - matched_rules: List of matched rules with details
    
    Example:
        rules = {"*": [("disallow", "/admin")]}
        is_path_allowed_for_ua(rules, "/admin/users", "*")
        # Returns: ("disallowed", [("*", "disallow", "/admin", 6)])
    """
    candidates = []
    
    # Collect rules for exact user-agent match
    if ua_to_check in rules_dict:
        candidates.extend([(ua_to_check, r[0], r[1]) for r in rules_dict[ua_to_check]])
    
    # Collect rules for wildcard user-agent
    if "*" in rules_dict:
        candidates.extend([("*", r[0], r[1]) for r in rules_dict["*"]])
    
    # If no rules found, allow by default (no robots.txt restrictions)
    if not candidates:
        return ("allowed", [])
    
    matched = []
    
    # Find all rules whose pattern matches the path
    for u, typ, patt in candidates:
        # Empty disallow pattern means no restriction
        if patt == "":
            continue
        
        # Check if pattern matches path
        if path_matches(patt, path):
            # Store match with pattern length (for specificity sorting)
            matched.append((u, typ, patt, len(patt)))
    
    # If no rules matched, allow by default
    if not matched:
        return ("allowed", [])
    
    # Sort by specificity (longer patterns first) and rule type (allow before disallow)
    # This implements robots.txt precedence: more specific rules win, allow overrides disallow
    matched.sort(key=lambda x: (x[3], 0 if x[1] == "allow" else 1), reverse=True)
    
    # Get the most specific rule (first after sorting)
    best = matched[0]
    _, typ, patt, plen = best
    
    # Return status based on rule type
    if typ.lower() == "allow":
        return ("allowed", matched)
    else:
        return ("disallowed", matched)


def main(urls_file: str, out_json: str = "robots_report.json", out_csv: str = "robots_report.csv"):
    """
    Main function: Check robots.txt for all URLs and generate reports.
    
    Args:
        urls_file: Path to urls.txt file
        out_json: Output JSON report filename
        out_csv: Output CSV report filename
    """
    # Get the directory where this script is located (scripts/rag/)
    script_dir = Path(__file__).parent
    
    # Get backend root (two levels up from scripts/rag/)
    backend_dir = script_dir.parent.parent
    
    # Resolve paths relative to backend directory
    # Default urls.txt is in config/ directory
    if urls_file == 'urls.txt':
        urls_path = backend_dir / 'config' / 'urls.txt'
    else:
        urls_path = Path(urls_file) if Path(urls_file).is_absolute() else backend_dir / urls_file
    
    json_path = backend_dir / out_json
    csv_path = backend_dir / out_csv
    
    # Read URLs from file
    with open(urls_path, "r", encoding="utf-8") as f:
        # Filter out empty lines and comments (lines starting with #)
        lines = [l.strip() for l in f if l.strip() and not l.strip().startswith("#")]
    
    # Group URLs by domain to minimize robots.txt fetches
    # Multiple URLs from same domain only need one robots.txt fetch
    by_domain = defaultdict(list)
    for url in lines:
        dom = canonical_domain(url)
        by_domain[dom].append(url)
    
    print(f"Found {len(lines)} URLs across {len(by_domain)} domains")
    
    # List to store report rows (one per URL)
    report_rows = []
    
    # Cache robots.txt results per domain (avoid re-fetching)
    domain_cache = {}
    
    # Process each domain
    for i, (domain, urls) in enumerate(by_domain.items(), start=1):
        # Polite rate limiting: wait between domain checks
        if i > 1:
            time.sleep(RATE_LIMIT)
        
        print(f"[{i}/{len(by_domain)}] Checking {domain}...")
        
        # Fetch robots.txt for this domain
        res = fetch_robots(domain)
        
        # Cache result for this domain
        domain_cache[domain] = res
        
        # Extract robots.txt content and status
        robots_text = res.get("text", "")
        status_code = res.get("status_code")
        
        # Parse robots.txt if successfully fetched
        parsed = {}
        if status_code == 200 and robots_text:
            parsed = parse_robots(robots_text)
        
        # Check each URL from this domain
        for url in urls:
            # Extract path from URL (default to "/" if no path)
            path = urlparse(url).path or "/"
            
            # Determine status based on fetch result
            if status_code is None:
                # Fetch failed (network error, timeout, etc.)
                status = "error"
                detail = res.get("error", "fetch_error")
                allowed = "unknown"
                matched = []
            elif status_code == 200:
                # Successfully fetched robots.txt
                allowed, matched = is_path_allowed_for_ua(parsed, path, USER_AGENT_TO_CHECK)
                status = "ok"
                detail = ""
            elif status_code == 404:
                # No robots.txt file found
                status = "no_robots"
                allowed = "allowed"  # No robots file -> assume allowed (but be polite)
                matched = []
                detail = ""
            else:
                # Other HTTP status (403, 500, etc.)
                status = f"http_{status_code}"
                allowed = "unknown"
                matched = []
                detail = ""
            
            # Add report row for this URL
            report_rows.append({
                "url": url,
                "domain": domain,
                "robots_url": res.get("url"),
                "robots_status_code": status_code,
                "fetch_status": status,
                "allowed": allowed,
                "matched_rules": matched,
                "detail": detail
            })
    
    # ===== WRITE JSON REPORT =====
    # Write full structured report as JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report_rows, f, indent=2, ensure_ascii=False)
    
    # ===== WRITE CSV REPORT =====
    # Write spreadsheet-friendly CSV report
    with open(csv_path, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        
        # Write header row
        writer.writerow([
            "url", "domain", "robots_url", "robots_status_code",
            "fetch_status", "allowed", "matched_rules", "detail"
        ])
        
        # Write data rows
        for r in report_rows:
            writer.writerow([
                r["url"],
                r["domain"],
                r["robots_url"],
                r["robots_status_code"],
                r["fetch_status"],
                r["allowed"],
                json.dumps(r["matched_rules"], ensure_ascii=False),  # JSON string for CSV
                r["detail"]
            ])
    
    # ===== SUMMARY STATISTICS =====
    # Count URLs by status
    allowed_count = sum(1 for r in report_rows if r["allowed"] == "allowed")
    disallowed_count = sum(1 for r in report_rows if r["allowed"] == "disallowed")
    unknown_count = sum(1 for r in report_rows if r["allowed"] == "unknown")
    no_robots_count = sum(1 for r in report_rows if r["fetch_status"] == "no_robots")
    error_count = sum(1 for r in report_rows if r["fetch_status"] == "error")
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Robots.txt Check Complete")
    print(f"{'='*60}")
    print(f"Total URLs checked: {len(report_rows)}")
    print(f"  ✓ Allowed:        {allowed_count}")
    print(f"  ✗ Disallowed:     {disallowed_count}")
    print(f"  ? Unknown:        {unknown_count}")
    print(f"  📄 No robots.txt: {no_robots_count}")
    print(f"  ⚠ Errors:         {error_count}")
    print(f"\nReports saved:")
    print(f"  - {json_path}")
    print(f"  - {csv_path}")
    
    # Warning if many URLs are disallowed
    if disallowed_count > 0:
        print(f"\n⚠ Warning: {disallowed_count} URLs are disallowed by robots.txt")
        print(f"  Consider removing them from urls.txt or finding alternative pages")


if __name__ == "__main__":
    # Check command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python check_robots_report.py urls.txt")
        print("\nOptional: python check_robots_report.py urls.txt output.json output.csv")
        sys.exit(1)
    
    # Get input file (required)
    urls_file = sys.argv[1]
    
    # Get output files (optional, with defaults)
    out_json = sys.argv[2] if len(sys.argv) > 2 else "robots_report.json"
    out_csv = sys.argv[3] if len(sys.argv) > 3 else "robots_report.csv"
    
    # Run main function
    main(urls_file, out_json, out_csv)

