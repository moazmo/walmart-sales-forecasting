"""
Demo Image Creation Script
=========================

This script helps create a professional demo image for the GitHub repository.
"""

import webbrowser
import os
from pathlib import Path

def create_demo_image():
    """Create demo image for GitHub repository."""
    
    print("🎨 Creating Demo Image for GitHub Repository")
    print("=" * 50)
    
    # Get current directory
    current_dir = Path(__file__).parent
    demo_banner_path = current_dir / "docs" / "demo-banner.html"
    
    if demo_banner_path.exists():
        print("✅ Demo banner HTML found")
        
        # Open the demo banner in default browser
        banner_url = f"file:///{demo_banner_path.absolute()}"
        print(f"🌐 Opening demo banner: {banner_url}")
        webbrowser.open(banner_url)
        
        print("\n📸 Screenshot Instructions:")
        print("1. The demo banner should now be open in your browser")
        print("2. Take a full-page screenshot (Ctrl+Shift+S in most browsers)")
        print("3. Save the screenshot as 'docs/demo-image.png'")
        print("4. Recommended resolution: 1200x800 or higher")
        print("5. Use PNG format for best quality")
        
    else:
        print("❌ Demo banner HTML not found")
        print("Please ensure docs/demo-banner.html exists")
    
    print("\n🚀 Alternative: Live Application Screenshot")
    print("1. Run: python start_full_system.py --frontend")
    print("2. Open: http://localhost:3000")
    print("3. Fill the prediction form with sample data")
    print("4. Take screenshots of both prediction and dashboard views")
    print("5. Create a composite image showing both interfaces")
    
    print("\n📋 Next Steps:")
    print("1. Create the demo image following instructions above")
    print("2. Follow REPOSITORY_CONFIGURATION.md for GitHub setup")
    print("3. Upload the demo image to your repository")
    print("4. Configure repository settings as described")
    
    print("\n🎯 Repository Configuration:")
    config_path = current_dir / "REPOSITORY_CONFIGURATION.md"
    if config_path.exists():
        print(f"📖 See detailed instructions: {config_path}")
    
    print("\n✨ Your repository will look professional and attract more visitors!")

if __name__ == "__main__":
    create_demo_image()