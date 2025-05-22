"""
Debug script to find the avatar image in the RSI citizen profile page
"""

import requests
import sys
from bs4 import BeautifulSoup

def find_avatar(handle):
    """Find the avatar image in a citizen's profile"""
    print(f"Looking for avatar image for citizen: {handle}")
    
    url = f"https://robertsspaceindustries.com/en/citizens/{handle}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for possible avatar images
        print("\nLooking for profile images:")
        
        # Check the profile section first
        profile_section = soup.select_one(".profile")
        if profile_section:
            thumb = profile_section.select_one(".thumb img")
            if thumb and thumb.has_attr('src'):
                print(f"Profile thumb image: {thumb['src']}")
        
        # Look for all images in the page
        all_images = soup.select("img")
        print(f"\nFound {len(all_images)} images on the page")
        
        # Print the first 10 images with their context
        for i, img in enumerate(all_images[:10]):
            if img.has_attr('src'):
                print(f"\nImage {i+1}:")
                print(f"Source: {img['src']}")
                print(f"Parent: {img.parent.name}")
                print(f"Parent class: {img.parent.get('class', 'None')}")
                parent_html = str(img.parent)
                if len(parent_html) > 100:
                    parent_html = parent_html[:100] + "..."
                print(f"Parent HTML: {parent_html}")
            
    except Exception as e:
        print(f"Error: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python debug_avatar.py <handle>")
        print("Example: python debug_avatar.py KenzoKai")
        return
    
    handle = sys.argv[1]
    find_avatar(handle)

if __name__ == "__main__":
    main()
