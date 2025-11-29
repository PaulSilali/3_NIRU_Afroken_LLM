# Robots.txt Pre-Check Guide

## Overview

The `check_robots_report.py` script allows you to **pre-check all URLs** in `urls.txt` for robots.txt compliance **before** running the full fetch pipeline. This saves time by identifying disallowed URLs upfront and generates useful reports for analysis.

## Why Use This?

1. **Time Savings**: Check robots.txt once per domain instead of on every fetch
2. **Early Detection**: Identify disallowed URLs before spending time fetching them
3. **Documentation**: Generate reports (JSON + CSV) for analysis and record-keeping
4. **URL Curation**: Make informed decisions about which URLs to keep/remove

## Quick Start

### Step 1: Run the Robots Check

```bash
cd afroken_llm_backend
python check_robots_report.py urls.txt
```

### Step 2: Review the Reports

The script generates two files:

- **`robots_report.json`**: Full structured report with all details
- **`robots_report.csv`**: Spreadsheet-friendly format for analysis

### Step 3: Analyze Results

Open `robots_report.csv` in Excel/Google Sheets to see:
- Which URLs are **allowed** ✓
- Which URLs are **disallowed** ✗
- Which domains have **no robots.txt** 📄
- Which fetches had **errors** ⚠

### Step 4: Update urls.txt (Optional)

Based on the report:
- Remove disallowed URLs
- Find alternative pages for important disallowed content
- Keep allowed URLs for fetching

### Step 5: Use Report in Fetch Script (Optional)

When running `fetch_and_extract.py`, use the `--skip-disallowed` flag to automatically skip URLs marked as disallowed in the report:

```bash
python fetch_and_extract.py urls.txt --skip-disallowed
```

This avoids re-checking robots.txt for each URL (faster).

## Report Format

### JSON Report Structure

```json
[
  {
    "url": "https://www.kra.go.ke/services/pin",
    "domain": "https://www.kra.go.ke",
    "robots_url": "https://www.kra.go.ke/robots.txt",
    "robots_status_code": 200,
    "fetch_status": "ok",
    "allowed": "allowed",
    "matched_rules": [],
    "detail": ""
  },
  {
    "url": "https://example.com/private",
    "domain": "https://example.com",
    "robots_url": "https://example.com/robots.txt",
    "robots_status_code": 200,
    "fetch_status": "ok",
    "allowed": "disallowed",
    "matched_rules": [["*", "disallow", "/private", 8]],
    "detail": ""
  }
]
```

### CSV Columns

- `url`: The URL being checked
- `domain`: Domain of the URL
- `robots_url`: Full robots.txt URL that was checked
- `robots_status_code`: HTTP status (200, 404, None for errors)
- `fetch_status`: Status of robots.txt fetch (`ok`, `no_robots`, `error`, `http_XXX`)
- `allowed`: Whether URL is allowed (`allowed`, `disallowed`, `unknown`)
- `matched_rules`: JSON array of matching robots.txt rules
- `detail`: Error details (if any)

## Command-Line Options

```bash
# Basic usage (default output files)
python check_robots_report.py urls.txt

# Custom output files
python check_robots_report.py urls.txt my_report.json my_report.csv
```

## Integration with Fetch Pipeline

### Option 1: Pre-Check Then Fetch (Recommended)

```bash
# Step 1: Check robots.txt for all URLs
python check_robots_report.py urls.txt

# Step 2: Review robots_report.csv and update urls.txt if needed

# Step 3: Fetch with report integration (skips disallowed URLs)
python fetch_and_extract.py urls.txt --skip-disallowed
```

### Option 2: Fetch Without Pre-Check

```bash
# Fetch and check robots.txt on-the-fly (slower but simpler)
python fetch_and_extract.py urls.txt
```

## Understanding the Output

### Summary Statistics

After running, you'll see:

```
============================================================
Robots.txt Check Complete
============================================================
Total URLs checked: 50
  ✓ Allowed:        35
  ✗ Disallowed:     10
  ? Unknown:        2
  📄 No robots.txt: 3
  ⚠ Errors:         0

Reports saved:
  - robots_report.json
  - robots_report.csv
```

### Status Meanings

- **✓ Allowed**: URL is allowed by robots.txt (safe to fetch)
- **✗ Disallowed**: URL is blocked by robots.txt (should not fetch)
- **? Unknown**: Could not determine status (error fetching robots.txt)
- **📄 No robots.txt**: Domain has no robots.txt (assumed allowed, but be polite)
- **⚠ Errors**: Network/timeout errors when fetching robots.txt

## Best Practices

1. **Run Before First Fetch**: Check robots.txt before your first full fetch to identify issues early

2. **Review Disallowed URLs**: 
   - Check if disallowed URLs are critical
   - Find alternative official pages if needed
   - Consider contacting site owners for permission (for important content)

3. **Respect robots.txt**: Even if a URL is "allowed", be polite:
   - Use rate limiting (already built into scripts)
   - Set proper User-Agent (already configured)
   - Don't fetch too many pages too quickly

4. **Update Reports**: Re-run `check_robots_report.py` if you add new URLs to `urls.txt`

5. **Document Decisions**: Keep `robots_report.json` in version control to track compliance over time

## Troubleshooting

### Issue: "No robots.txt" for many domains

**Solution**: This is normal. Many sites don't have robots.txt. The script assumes these are allowed, but you should still be polite with rate limiting.

### Issue: Many URLs marked "disallowed"

**Solution**: 
1. Review `robots_report.csv` to see which URLs are blocked
2. Check if alternative pages exist (e.g., public documentation instead of admin pages)
3. Consider manually downloading important content and placing it in `raw/` directory

### Issue: "Errors" when fetching robots.txt

**Solution**:
- Check your internet connection
- Some sites may block automated requests
- Increase `TIMEOUT` in `check_robots_report.py` if timeouts are common

## Example Workflow

```bash
# 1. Check robots.txt compliance
python check_robots_report.py urls.txt

# 2. Review results
# Open robots_report.csv and identify disallowed URLs

# 3. (Optional) Update urls.txt
# Remove disallowed URLs or find alternatives

# 4. Fetch allowed URLs (with report integration)
python fetch_and_extract.py urls.txt --skip-disallowed

# 5. Continue with chunking and indexing
python chunk_and_write_md.py
python index_faiss.py
```

## Technical Details

- **Rate Limiting**: 1.0 second delay between domain checks (polite)
- **Timeout**: 8 seconds per robots.txt fetch
- **User-Agent**: Checks rules for `User-agent: *` (wildcard/default)
- **Grouping**: URLs are grouped by domain to minimize robots.txt fetches
- **Caching**: Each domain's robots.txt is fetched once and reused for all URLs from that domain

## Integration Notes

The `fetch_and_extract.py` script can use the robots report via the `--skip-disallowed` flag:

- If `robots_report.json` exists and `--skip-disallowed` is set, the fetch script will skip URLs marked as "disallowed" in the report
- This avoids re-checking robots.txt for each URL (much faster)
- URLs not in the report will still be checked on-the-fly using `check_robots_allowed()`

