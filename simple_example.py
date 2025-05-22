"""
Simple example script to demonstrate how to use the Star Citizen Tools MCP server.
This script provides a more direct way to interact with the wiki.
"""

import requests
import json
import sys

def search_wiki(search_term, limit=5):
    """Search the Star Citizen Tools wiki for articles"""
    print(f"Searching for: {search_term}")
    
    url = "https://starcitizen.tools/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": search_term,
        "format": "json",
        "srlimit": str(limit)
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "query" in data and "search" in data["query"]:
            results = data["query"]["search"]
            if not results:
                print("No results found.")
                return []
            
            print(f"Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['title']}")
                print(f"   Page ID: {result['pageid']}")
                if 'snippet' in result:
                    print(f"   Snippet: {result['snippet'].replace('<span class=\"searchmatch\">', '').replace('</span>', '')}")
                print()
            
            return results
        else:
            print("Unexpected response format.")
            return []
            
    except Exception as e:
        print(f"Error searching wiki: {e}")
        return []

def get_wiki_page(page_title):
    """Get information about a specific wiki page"""
    print(f"Getting information about: {page_title}")
    
    url = "https://starcitizen.tools/api.php"
    params = {
        "action": "parse",
        "page": page_title,
        "format": "json",
        "prop": "text",
        "redirects": "1"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "parse" in data:
            parse_data = data["parse"]
            print(f"Title: {parse_data.get('title', 'Unknown')}")
            print(f"Page ID: {parse_data.get('pageid', 'Unknown')}")
            
            # Extract a sample of the text content (it's HTML)
            if "text" in parse_data and "*" in parse_data["text"]:
                html_content = parse_data["text"]["*"]
                # Print just the first 500 characters to avoid overwhelming output
                print("\nSample content (first 500 chars):")
                print(html_content[:500] + "...\n")
            
            return parse_data
        else:
            print("Page not found or other error occurred.")
            return None
            
    except Exception as e:
        print(f"Error getting wiki page: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Search:  python simple_example.py search <term>")
        print("  Get page: python simple_example.py page <page_title>")
        return
    
    command = sys.argv[1].lower()
    
    if command == "search" and len(sys.argv) >= 3:
        search_term = " ".join(sys.argv[2:])
        search_wiki(search_term)
    elif command == "page" and len(sys.argv) >= 3:
        page_title = " ".join(sys.argv[2:])
        get_wiki_page(page_title)
    else:
        print("Invalid command. Use 'search' or 'page'.")

if __name__ == "__main__":
    main()
