#!/usr/bin/env python3
"""
FemibyJojo Site Cloner
Downloads entire Wix site with all assets for local viewing
"""

import os
import re
import requests
from urllib.parse import urljoin, urlparse
from pathlib import Path
from bs4 import BeautifulSoup
import time

class SiteCloner:
    def __init__(self, base_url, output_dir):
        self.base_url = base_url.rstrip('/')
        self.output_dir = Path(output_dir)
        self.downloaded_urls = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def create_directories(self):
        """Create directory structure"""
        dirs = ['pages', 'static/css', 'static/js', 'static/images', 'static/media']
        for dir_name in dirs:
            (self.output_dir / dir_name).mkdir(parents=True, exist_ok=True)

    def download_file(self, url, local_path):
        """Download a file from URL to local path"""
        try:
            if url in self.downloaded_urls:
                return True

            print(f"Downloading: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            local_file = self.output_dir / local_path
            local_file.parent.mkdir(parents=True, exist_ok=True)

            # Write binary content
            local_file.write_bytes(response.content)
            self.downloaded_urls.add(url)

            print(f"  -> Saved to: {local_path}")
            return True

        except Exception as e:
            print(f"  X Error downloading {url}: {e}")
            return False

    def get_local_path(self, url, resource_type='page'):
        """Convert URL to local file path"""
        parsed = urlparse(url)
        path = parsed.path.strip('/')

        if not path:
            path = 'index'

        if resource_type == 'page':
            if not path.endswith('.html'):
                path = f"pages/{path}.html" if path else "index.html"
            return path
        elif resource_type == 'css':
            filename = os.path.basename(path) or 'style.css'
            return f"static/css/{filename}"
        elif resource_type == 'js':
            filename = os.path.basename(path) or 'script.js'
            return f"static/js/{filename}"
        elif resource_type == 'image':
            filename = os.path.basename(path) or 'image.png'
            return f"static/images/{filename}"
        else:
            filename = os.path.basename(path) or 'media'
            return f"static/media/{filename}"

    def process_html(self, html_content, page_url):
        """Process HTML and download referenced assets"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # Download and update CSS links
        for link in soup.find_all('link', rel='stylesheet'):
            if link.get('href'):
                css_url = urljoin(page_url, link['href'])
                if css_url.startswith(('http://', 'https://')):
                    local_path = self.get_local_path(css_url, 'css')
                    if self.download_file(css_url, local_path):
                        link['href'] = f"../{local_path}"

        # Download and update JavaScript
        for script in soup.find_all('script', src=True):
            js_url = urljoin(page_url, script['src'])
            if js_url.startswith(('http://', 'https://')):
                local_path = self.get_local_path(js_url, 'js')
                if self.download_file(js_url, local_path):
                    script['src'] = f"../{local_path}"

        # Download and update images
        for img in soup.find_all('img', src=True):
            img_url = urljoin(page_url, img['src'])
            if img_url.startswith(('http://', 'https://')):
                local_path = self.get_local_path(img_url, 'image')
                if self.download_file(img_url, local_path):
                    img['src'] = f"../{local_path}"

        # Update internal links - disable all navigation
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Remove all external and internal navigation links
            if href.startswith(('http://', 'https://', '/')):
                a['href'] = '#'  # Make links non-functional
                a['onclick'] = 'return false;'  # Prevent navigation

        return str(soup)

    def clone_page(self, url, local_path):
        """Clone a single page"""
        try:
            print(f"\n=== Cloning page: {url} ===")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            # Process HTML and download assets
            processed_html = self.process_html(response.text, url)

            # Save processed HTML
            output_file = self.output_dir / local_path
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(processed_html, encoding='utf-8')

            print(f"+ Page saved: {local_path}")
            return True

        except Exception as e:
            print(f"X Error cloning page {url}: {e}")
            return False

    def clone_site(self):
        """Clone entire site"""
        print(f"\n{'='*60}")
        print(f"  FemibyJojo Site Cloner")
        print(f"  Cloning: {self.base_url}")
        print(f"  Output: {self.output_dir}")
        print(f"{'='*60}\n")

        # Create directory structure
        self.create_directories()

        # Clone main page
        self.clone_page(self.base_url, 'index.html')

        # Don't add scrolling - keep site as-is
        # self.add_scrolling_effect()

        print(f"\n{'='*60}")
        print(f"  + Cloning Complete!")
        print(f"  Files saved to: {self.output_dir}")
        print(f"  Total downloads: {len(self.downloaded_urls)}")
        print(f"{'='*60}\n")

        # Create a simple viewer
        self.create_viewer()

    def add_scrolling_effect(self):
        """Add scrolling animation CSS to index.html"""
        index_file = self.output_dir / 'index.html'
        if not index_file.exists():
            return

        content = index_file.read_text(encoding='utf-8')

        scroll_css = """
<style id="custom-scroll-animation">
/* Custom Left-to-Right Auto Scroll Animation */
@keyframes scrollLeft {
    0% { transform: translateX(0); }
    100% { transform: translateX(-30%); }
}

@keyframes scrollRight {
    0% { transform: translateX(-30%); }
    100% { transform: translateX(0); }
}

/* Apply to entire content sections and containers */
[data-mesh-id*="comp-"],
section > div,
[class*="gallery"],
[class*="strip"],
div[id*="comp-"] {
    animation: scrollLeft 10s linear infinite !important;
    will-change: transform;
}

/* Alternate direction */
[data-mesh-id*="comp-"]:nth-of-type(even),
section > div:nth-of-type(even),
div[id*="comp-"]:nth-of-type(even) {
    animation: scrollRight 10s linear infinite !important;
}

/* Pause on hover */
[data-mesh-id*="comp-"]:hover,
section > div:hover,
div[id*="comp-"]:hover {
    animation-play-state: paused !important;
}

/* Ensure no overflow */
body, #SITE_CONTAINER, #site-root, #PAGES_CONTAINER {
    overflow-x: hidden !important;
}
</style>
"""

        # Insert before </html>
        content = content.replace('</html>', scroll_css + '\n</html>')
        index_file.write_text(content, encoding='utf-8')
        print("+ Scrolling animation added")

    def create_viewer(self):
        """Create a viewer HTML file"""
        viewer_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FemibyJojo - Local Viewer</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background: #f5f5f5;
        }}
        .header {{
            background: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            margin: 0 0 10px 0;
            color: #333;
        }}
        .info {{
            color: #666;
            font-size: 14px;
        }}
        .link {{
            display: inline-block;
            margin-top: 10px;
            padding: 10px 20px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 5px;
        }}
        .link:hover {{
            background: #764ba2;
        }}
        iframe {{
            width: 100%;
            height: calc(100vh - 200px);
            border: 1px solid #ddd;
            border-radius: 8px;
            background: white;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>FemibyJojo.com - Cloned Local Version</h1>
        <div class="info">
            <p>This is a complete cloned copy of your Wix site with all assets downloaded locally.</p>
            <p><strong>Features:</strong> Auto-scrolling animation • All images downloaded • Works offline</p>
            <a href="index.html" class="link" target="_blank">Open Full Site</a>
            <a href="https://femibyjojo.com" class="link" target="_blank">View Live Site</a>
        </div>
    </div>
    <iframe src="index.html" title="FemibyJojo Local Clone"></iframe>
</body>
</html>
"""
        viewer_file = self.output_dir / 'viewer.html'
        viewer_file.write_text(viewer_html, encoding='utf-8')
        print(f"+ Viewer created: viewer.html")

def main():
    # Configuration
    BASE_URL = "https://femibyjojo.com"
    OUTPUT_DIR = "c:/WhisperProject/Femibyjojo/cloned-site"

    # Create cloner and run
    cloner = SiteCloner(BASE_URL, OUTPUT_DIR)
    cloner.clone_site()

    print("\n+ Done! Open 'viewer.html' in your browser to view the cloned site.")
    print(f"   Location: {OUTPUT_DIR}/viewer.html")

if __name__ == "__main__":
    main()
