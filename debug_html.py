"""
Debug script to examine the HTML structure of the RSI citizen profile page
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
        
        # Find the left column
        left_col = soup.select_one(".left-col")
        if left_col:
            print("\nLeft Column HTML Structure:")
            print(left_col.prettify())
            
            # Find all entries in the left column
            entries = left_col.select(".entry")
            print(f"\nFound {len(entries)} entries in the left column")
            
            for i, entry in enumerate(entries):
                print(f"\nEntry {i+1}:")
                print(entry.prettify())
                
                label = entry.select_one(".label")
                value = entry.select_one(".value")
                
                if label:
                    print(f"Label: '{label.text.strip()}'")
                if value:
                    print(f"Value: '{value.text.strip()}'")
        else:
            print("Left column not found")
            
    except Exception as e:
        print(f"Error: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python debug_html.py <handle>")
        print("Example: python debug_html.py KenzoKai")
        return
    
    handle = sys.argv[1]
    get_html_structure(handle)

if __name__ == "__main__":
    main()
