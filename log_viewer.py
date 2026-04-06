#!/usr/bin/env python3
"""
Moltbook Agent Log Viewer
A simple web server to browse agent.log with pagination.
Run: python3 log_viewer.py
Then open: http://<pi-ip>:8080
"""

import os
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agent.log")
PORT = 8080
LINES_PER_PAGE = 100


def load_log_lines():
    """Load and return log lines in reverse order, grouped into runs by timestamp."""
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return []
    return list(reversed([l.rstrip("\n") for l in lines if l.strip()]))


def colorize(line):
    """Apply color classes based on line content."""
    l = line.lower()
    if "error" in l or "failed" in l or "429" in l or "suspended" in l:
        return "error"
    if "challenge" in l or "solving" in l or "submitting" in l:
        return "challenge"
    if "posted successfully" in l or "verification successful" in l or "challenge solved" in l:
        return "success"
    if "new interaction" in l or "reply" in l:
        return "interaction"
    if "routing to" in l or "crafting" in l or "deciding" in l or "llama" in l or "thinking" in l:
        return "info"
    if re.match(r"\[\d{4}-\d{2}-\d{2}", line):
        return "timestamp"
    return "normal"


def render_page(lines, page, total_pages, total_lines, search=""):
    start = (page - 1) * LINES_PER_PAGE
    end = start + LINES_PER_PAGE
    page_lines = lines[start:end]

    rows = ""
    for i, line in enumerate(page_lines, start=start + 1):
        css = colorize(line)
        escaped = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        rows += f'<tr class="{css}"><td class="ln">{total_lines - i + 1}</td><td class="msg">{escaped}</td></tr>\n'

    search_val = search.replace('"', "&quot;")

    # Pagination links
    def page_link(p, label=None):
        label = label or str(p)
        if p == page:
            return f'<span class="cur">{label}</span>'
        s = f'?page={p}'
        if search:
            s += f'&search={search}'
        return f'<a href="{s}">{label}</a>'

    pages_html = ""
    if total_pages > 1:
        pages_html += page_link(1, "« First") + " "
        if page > 1:
            pages_html += page_link(page - 1, "‹ Prev") + " "
        # Show window of pages
        lo = max(1, page - 3)
        hi = min(total_pages, page + 3)
        for p in range(lo, hi + 1):
            pages_html += page_link(p) + " "
        if page < total_pages:
            pages_html += page_link(page + 1, "Next ›") + " "
        pages_html += page_link(total_pages, "Last »")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>🦞 Moltbook Agent Log</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #0d1117; color: #c9d1d9; font-family: 'Courier New', monospace; font-size: 13px; }}
  header {{ background: #161b22; border-bottom: 1px solid #30363d; padding: 14px 20px; display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }}
  header h1 {{ font-size: 16px; color: #58a6ff; flex: 1; }}
  .meta {{ color: #8b949e; font-size: 12px; }}
  .search-bar {{ display: flex; gap: 8px; }}
  .search-bar input {{ background: #0d1117; border: 1px solid #30363d; color: #c9d1d9; padding: 5px 10px; border-radius: 6px; font-family: inherit; font-size: 12px; width: 220px; }}
  .search-bar button {{ background: #21262d; border: 1px solid #30363d; color: #c9d1d9; padding: 5px 12px; border-radius: 6px; cursor: pointer; font-size: 12px; }}
  .search-bar button:hover {{ background: #30363d; }}
  table {{ width: 100%; border-collapse: collapse; }}
  td {{ padding: 2px 10px; vertical-align: top; border-bottom: 1px solid #161b22; }}
  .ln {{ color: #484f58; width: 60px; text-align: right; user-select: none; padding-right: 16px; }}
  .msg {{ white-space: pre-wrap; word-break: break-all; }}
  tr.error .msg   {{ color: #f85149; }}
  tr.success .msg {{ color: #3fb950; }}
  tr.challenge .msg {{ color: #d2a8ff; }}
  tr.interaction .msg {{ color: #79c0ff; }}
  tr.info .msg    {{ color: #e3b341; }}
  tr.timestamp .msg {{ color: #8b949e; }}
  tr:hover {{ background: #161b22; }}
  .pagination {{ padding: 16px 20px; text-align: center; background: #161b22; border-top: 1px solid #30363d; }}
  .pagination a, .pagination .cur, .pagination span {{ display: inline-block; padding: 4px 10px; margin: 2px; border-radius: 4px; text-decoration: none; font-size: 12px; }}
  .pagination a {{ background: #21262d; color: #c9d1d9; border: 1px solid #30363d; }}
  .pagination a:hover {{ background: #30363d; }}
  .pagination .cur {{ background: #1f6feb; color: #fff; border: 1px solid #1f6feb; }}
  .legend {{ padding: 8px 20px; background: #0d1117; border-bottom: 1px solid #30363d; display: flex; gap: 16px; flex-wrap: wrap; font-size: 11px; }}
  .legend span {{ padding: 2px 8px; border-radius: 10px; }}
  .l-error {{ color: #f85149; }} .l-success {{ color: #3fb950; }} .l-challenge {{ color: #d2a8ff; }}
  .l-interaction {{ color: #79c0ff; }} .l-info {{ color: #e3b341; }}
</style>
</head>
<body>
<header>
  <h1>🦞 Moltbook Agent Log</h1>
  <span class="meta">Showing {total_lines} lines · Page {page}/{total_pages}</span>
  <form class="search-bar" method="get">
    <input type="hidden" name="page" value="1">
    <input type="text" name="search" value="{search_val}" placeholder="Filter lines...">
    <button type="submit">Search</button>
    {'<a href="/" style="color:#8b949e;font-size:12px;text-decoration:none">✕ Clear</a>' if search else ''}
  </form>
</header>
<div class="legend">
  <span class="l-success">● Success</span>
  <span class="l-error">● Error / Failed</span>
  <span class="l-challenge">● AI Challenge</span>
  <span class="l-interaction">● Interaction</span>
  <span class="l-info">● LLM Activity</span>
</div>
<table>
<tbody>
{rows}
</tbody>
</table>
<div class="pagination">{pages_html}</div>
</body>
</html>"""


class LogHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress default request logs

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        search = params.get("search", [""])[0].strip().lower()

        all_lines = load_log_lines()

        if search:
            all_lines = [l for l in all_lines if search in l.lower()]

        total_lines = len(all_lines)

        try:
            page = max(1, int(params.get("page", [1])[0]))
        except ValueError:
            page = 1

        total_pages = max(1, (total_lines + LINES_PER_PAGE - 1) // LINES_PER_PAGE)
        page = min(page, total_pages)

        html = render_page(all_lines, page, total_pages, total_lines, search)
        encoded = html.encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), LogHandler)
    print(f"Log viewer running at http://0.0.0.0:{PORT}")
    print(f"Reading: {LOG_FILE}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
