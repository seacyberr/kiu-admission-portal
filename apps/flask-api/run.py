#!/usr/bin/env python3
"""
Cross-platform server runner for KIU Admission Portal
Automatically detects operating system and uses appropriate server
Works on Linux, macOS, and Windows
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def is_windows():
    return sys.platform.startswith('win')

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    
    print("=" * 60)
    print("  KIU ADMISSION PORTAL API SERVER")
    print(f"  Running on: {'Windows' if is_windows() else sys.platform}")
    print("=" * 60)
    
    from app import create_app
    app = create_app()
    
    print(f"\nServer starting at: http://localhost:{port}")
    print("Press CTRL+C to stop server\n")
    
    # Use flask dev server which works cross-platform
    app.run(
        host="0.0.0.0",
        port=port,
        debug=True,
        use_reloader=True,
        passthrough_errors=True
    )