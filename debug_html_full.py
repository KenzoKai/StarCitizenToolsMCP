"""
Debug script to examine the full HTML structure of the RSI citizen profile page
"""

import requests
import sys
from bs4 import BeautifulSoup

def get_html_structure(handle):
    """Retrieve and print the HTML structure of a citizen's profile"""
    print(f"Looking up HTML structure for citizen: {handle}")
    
    url = f"https://robertsspaceindustries.com/en/citizens/{handle}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for elements containing "Enlisted", "Location", and "Fluency"
        print("\nSearching for elements containing 'Enlisted':")
        enlisted_elements = soup.find_all(string=lambda text: text and "Enlisted" in text)
        for i, elem in enumerate(enlisted_elements):
            print(f"\nEnlisted Element {i+1}:")
            parent = elem.parent
            print(f"Parent: {parent.name}")
            print(f"Parent HTML: {parent}")
            
            # Try to find the corresponding value
            if parent.name == "span" and "label" in parent.get("class", []):
                entry = parent.parent
                if entry:
                    value = entry.select_one(".value")
                    if value:
                        print(f"Value: '{value.text.strip()}'")
        
        print("\nSearching for elements containing 'Location':")
        location_elements = soup.find_all(string=lambda text: text and "Location" in text)
        for i, elem in enumerate(location_elements):
            print(f"\nLocation Element {i+1}:")
            parent = elem.parent
            print(f"Parent: {parent.name}")
            print(f"Parent HTML: {parent}")
            
            # Try to find the corresponding value
            if parent.name == "span" and "label" in parent.get("class", []):
                entry = parent.parent
                if entry:
                    value = entry.select_one(".value")
                    if value:
                        print(f"Value: '{value.text.strip()}'")
        
        print("\nSearching for elements containing 'Fluency':")
        fluency_elements = soup.find_all(string=lambda text: text and "Fluency" in text)
        for i, elem in enumerate(fluency_elements):
            print(f"\nFluency Element {i+1}:")
            parent = elem.parent
            print(f"Parent: {parent.name}")
            print(f"Parent HTML: {parent}")
            
            # Try to find the corresponding value
            if parent.name == "span" and "label" in parent.get("class", []):
                entry = parent.parent
                if entry:
                    value = entry.select_one(".value")
                    if value:
                        print(f"Value: '{value.text.strip()}'")
        
        # Look for the div with class "left-col" that is not inside the profile section
        print("\nSearching for other left-col elements:")
        left_cols = soup.select("div.left-col")
        for i, left_col in enumerate(left_cols):
            print(f"\nLeft Column {i+1}:")
            print(left_col.prettify())
            
    except Exception as e:
        print(f"Error: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python debug_html_full.py <handle>")
        print("Example: python debug_html_full.py KenzoKai")
        return
    
    handle = sys.argv[1]
    get_html_structure(handle)

if __name__ == "__main__":
    main()
