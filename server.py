#!/usr/bin/env python3
"""
Simple local development server for the website.
Serves files on http://localhost:8000
"""

import http.server
import socketserver
import webbrowser
import sys

PORT = 8000

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

def main():
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"🚀 Server running at http://localhost:{PORT}/")
            print(f"📁 Serving files from: {sys.path[0]}")
            print("\n✨ Press Ctrl+C to stop the server\n")
            
            # Optionally open browser automatically
            # webbrowser.open(f'http://localhost:{PORT}')
            
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped.")
    except OSError:
        print(f"❌ Port {PORT} is already in use. Try closing other servers or use a different port.")

if __name__ == "__main__":
    main()


