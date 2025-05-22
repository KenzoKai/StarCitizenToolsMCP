"""
Debug script to find the bio element in the RSI citizen profile page
"""

import requests
import sys
from bs4 import BeautifulSoup

def find_bio(handle):
    """Find the bio element in a citizen's profile"""
    print(f"Looking for bio for citizen: {handle}")
    
    url = f"https://robertsspaceindustries.com/en/citizens/{handle}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for elements containing "Bio"
        print("\nSearching for elements containing 'Bio':")
        bio_elements = soup.find_all(string=lambda text: text and "Bio" in text)
        for i, elem in enumerate(bio_elements):
            print(f"\nBio Element {i+1}:")
            parent = elem.parent
            print(f"Parent: {parent.name}")
            print(f"Parent HTML: {parent}")
            
            # Try to find the corresponding value
            if parent.name == "span" and "label" in parent.get("class", []):
                entry = parent.parent
                if entry:
                    print(f"Entry: {entry.name}")
                    print(f"Entry class: {entry.get('class', 'None')}")
                    value = entry.select_one(".value")
                    if value:
                        print(f"Value: '{value.text.strip()[:100]}...'")
        
        # Look for elements with class "bio"
        print("\nSearching for elements with class 'bio':")
        bio_class_elements = soup.select(".bio")
        for i, elem in enumerate(bio_class_elements):
            print(f"\nBio Class Element {i+1}:")
            print(f"Element: {elem.name}")
            print(f"Class: {elem.get('class', 'None')}")
            
            # Try to find the value inside
            value = elem.select_one(".value")
            if value:
                print(f"Value: '{value.text.strip()[:100]}...'")
        
        # Look for right column elements
        print("\nSearching for right column elements:")
        right_cols = soup.select(".right-col")
        for i, right_col in enumerate(right_cols):
            print(f"\nRight Column {i+1}:")
            print(f"Element: {right_col.name}")
            print(f"Class: {right_col.get('class', 'None')}")
            
            # Try to find bio elements inside
            bio_in_right = right_col.select(".bio")
            if bio_in_right:
                print(f"Found {len(bio_in_right)} bio elements inside")
                for j, bio_elem in enumerate(bio_in_right):
                    print(f"Bio Element {j+1} in Right Column {i+1}:")
                    value = bio_elem.select_one(".value")
                    if value:
                        print(f"Value: '{value.text.strip()[:100]}...'")
            
    except Exception as e:
        print(f"Error: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python debug_bio.py <handle>")
        print("Example: python debug_bio.py KenzoKai")
        return
    
    handle = sys.argv[1]
    find_bio(handle)

if __name__ == "__main__":
    main()
