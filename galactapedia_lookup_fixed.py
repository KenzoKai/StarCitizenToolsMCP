"""
Galactapedia Lookup Example - Demonstrates how to retrieve information from the RSI Galactapedia
"""

import requests
import json
import sys
import re
import time
import textwrap
from bs4 import BeautifulSoup
from urllib.parse import quote

class GalactapediaClient:
    def __init__(self):
        self.base_url = "https://robertsspaceindustries.com/galactapedia"
        self.api_url = "https://robertsspaceindustries.com/api/galactapedia"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        # Store article cache to avoid repeated requests
        self.article_cache = {}
        self.search_cache = {}
        self.category_cache = {}
    
    def get_hardcoded_articles(self):
        """Return dictionary of hardcoded articles for common ships and topics"""
        return {
            # Anvil Aerospace Ships
            "R4ZGyLQaBl-carrack": {
                "id": "R4ZGyLQaBl-carrack",
                "title": "Carrack",
                "content": "The Carrack is a multi-crew explorer spacecraft manufactured by Anvil Aerospace. \n\nOriginally a military vessel for deep space exploration, the Carrack has since been adapted for civilian use. It features advanced jump drives, a medical bay, repair facilities, a drone bay, a rover bay, and a modular cargo system. \n\nThe Carrack is designed for long-duration, self-sufficient exploration missions in uncharted space. It has become the vessel of choice for pathfinders and explorers across the galaxy, with its robust construction and versatile capabilities making it ideal for venturing into the unknown.",
                "metadata": {
                    "Type": "Spacecraft",
                    "Manufacturer": "Anvil Aerospace",
                    "Role": "Exploration",
                    "Size": "Large"
                },
                "tags": ["spacecraft", "anvil", "exploration", "human spacecraft"]
            },
            # Aegis Ships
            "RWnZ1lGj02-sabre": {
                "id": "RWnZ1lGj02-sabre",
                "title": "Sabre",
                "content": "The Sabre is a stealth fighter spacecraft manufactured by Aegis Dynamics. \n\nDesigned as a dedicated dogfighter, the Sabre combines speed, maneuverability, and firepower with a reduced cross-section and advanced stealth features. Its sleek design and powerful engines make it one of the most agile medium fighters in the UEE fleet.",
                "metadata": {
                    "Type": "Spacecraft",
                    "Manufacturer": "Aegis Dynamics",
                    "Role": "Stealth Fighter",
                    "Size": "Medium"
                },
                "tags": ["spacecraft", "aegis", "stealth", "fighter", "human spacecraft"]
            },
            "RWwZ1lGjo2-idris-m": {
                "id": "RWwZ1lGjo2-idris-m",
                "title": "Idris-M",
                "content": "The Idris-M is a military frigate manufactured by Aegis Dynamics for the United Empire of Earth Navy (UEEN). \n\nDesigned as a patrol carrier, the Idris-M is equipped with a spinal-mounted railgun, making it a formidable combat vessel. The ship can carry multiple fighters in its hangar bay, serving as a mobile base of operations for extended missions.",
                "metadata": {
                    "Type": "Spacecraft",
                    "Manufacturer": "Aegis Dynamics",
                    "Role": "Military Frigate",
                    "Size": "Capital"
                },
                "tags": ["spacecraft", "aegis", "military", "capital ship", "frigate", "human spacecraft"]
            },
            # RSI Ships
            "RWnZ1lGj04-constellation": {
                "id": "RWnZ1lGj04-constellation",
                "title": "Constellation",
                "content": "The Constellation is a multi-role spacecraft series manufactured by Roberts Space Industries (RSI). \n\nThe Constellation line represents RSI's premier multi-crew ships, designed to be versatile platforms capable of fulfilling various roles including cargo transport, exploration, and combat.",
                "metadata": {
                    "Type": "Spacecraft",
                    "Manufacturer": "Roberts Space Industries",
                    "Role": "Multi-role",
                    "Size": "Large"
                },
                "tags": ["spacecraft", "rsi", "multi-role", "human spacecraft", "constellation"]
            },
            "RWnZ1lGj05-andromeda": {
                "id": "RWnZ1lGj05-andromeda",
                "title": "Constellation Andromeda",
                "content": "The Constellation Andromeda is the base variant of the Constellation series manufactured by Roberts Space Industries (RSI). \n\nDesigned as a multi-purpose vessel, the Andromeda balances cargo capacity with combat capability, featuring four size 4 hardpoints and a complement of missiles that make it a formidable opponent despite its size.",
                "metadata": {
                    "Type": "Spacecraft",
                    "Manufacturer": "Roberts Space Industries",
                    "Role": "Multi-role",
                    "Size": "Large"
                },
                "tags": ["spacecraft", "rsi", "multi-role", "human spacecraft", "constellation", "andromeda"]
            },
            # Alien Species
            "VDo8xQZlwE-banu": {
                "id": "VDo8xQZlwE-banu",
                "title": "Banu",
                "content": "The Banu are a sapient species and the first alien race that Humanity made contact with. \n\nThe Banu are a trading culture with a loose government called the Banu Protectorate. They are known for their merchant skills and unique societal structure organized around trade-focused Souli (guilds).",
                "metadata": {
                    "Type": "Species",
                    "Homeworld": "Unknown",
                    "Government": "Banu Protectorate",
                    "Diplomatic Status": "Friendly with UEE"
                },
                "tags": ["species", "alien", "banu protectorate", "traders"]
            },
            # Alien Ships
            "RWwZ7OAj9p-banu-merchantman": {
                "id": "RWwZ7OAj9p-banu-merchantman",
                "title": "Banu Merchantman",
                "content": "The Banu Merchantman is a large trading vessel and the flagship of the Banu species. \n\nKnown for its distinctive asymmetrical design, the Merchantman serves as both a mobile marketplace and a formidable defensive platform.",
                "metadata": {
                    "Type": "Spacecraft",
                    "Manufacturer": "Banu",
                    "Role": "Trading/Transport",
                    "Size": "Large"
                },
                "tags": ["spacecraft", "banu", "trading", "alien spacecraft", "merchantman"]
            }
        }
    
    def search_articles(self, query):
        """Search for articles in the Galactapedia"""
        print(f"Searching Galactapedia for: {query}")
        
        # Check cache first
        if query in self.search_cache:
            print("Returning cached search results")
            return self.search_cache[query]
        
        # First, check our hardcoded articles for matches
        query_lower = query.lower()
        hardcoded_results = []
        
        # Get hardcoded articles
        hardcoded_articles = self.get_hardcoded_articles()
        
        for article_id, article in hardcoded_articles.items():
            title = article.get("title", "").lower()
            content = article.get("content", "").lower()
            tags = [tag.lower() for tag in article.get("tags", [])]
            
            if (query_lower in title or 
                query_lower in content or 
                any(query_lower in tag for tag in tags)):
                # Create a copy with URL
                result = article.copy()
                result["url"] = f"{self.base_url}/article/{article_id}"
                hardcoded_results.append(result)
        
        if hardcoded_results:
            print(f"Found {len(hardcoded_results)} matching articles in hardcoded content")
            self.search_cache[query] = hardcoded_results
            return hardcoded_results
        
        # Next, try direct scraping of the search results page
        try:
            search_url = f"{self.base_url}/search?query={quote(query)}"
            print(f"Scraping search results from: {search_url}")
            
            response = requests.get(search_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for search results in the page
            results = []
            
            # Find all search result items
            result_items = soup.select(".search-result-item")
            
            for item in result_items:
                # Extract article ID and title
                link = item.select_one("a[href^='/galactapedia/article/']")
                if not link:
                    continue
                    
                article_id = link['href'].split('/')[-1]
                title = link.text.strip()
                
                # Extract description if available
                desc_elem = item.select_one(".search-result-description")
                description = desc_elem.text.strip() if desc_elem else ""
                
                # Extract type/category if available
                type_elem = item.select_one(".search-result-type")
                article_type = type_elem.text.strip() if type_elem else ""
                
                results.append({
                    "id": article_id,
                    "title": title,
                    "description": description,
                    "type": article_type,
                    "url": f"{self.base_url}/article/{article_id}"
                })
            
            if results:
                print(f"Found {len(results)} search results from web scraping")
                self.search_cache[query] = results
                return results
                
            print("No direct search results found, trying category-based search")
        except Exception as e:
            print(f"Direct search scraping failed: {e}")
        
        # Fallback: Try the category browsing approach and filter results
        try:
            # Add more categories that might contain general lore
            categories_to_check = ["spacecraft", "planets", "people", "history", "military", 
                                   "species", "locations", "organizations", "technology"]
            all_results = []
            
            for category in categories_to_check:
                print(f"Checking category: {category}")
                category_articles = self.get_category(category)
                all_results.extend(category_articles)
            
            # Filter results based on query - check title and description
            filtered_results = []
            for article in all_results:
                title = article.get("title", "").lower()
                description = article.get("description", "").lower()
                tags = [tag.lower() for tag in article.get("tags", [])]
                
                if (query_lower in title or 
                    query_lower in description or 
                    any(query_lower in tag for tag in tags)):
                    filtered_results.append(article)
            
            print(f"Found {len(filtered_results)} matching articles from categories")
            self.search_cache[query] = filtered_results
            return filtered_results
            
        except Exception as e:
            print(f"Category-based search failed: {e}")
            return []
    
    def get_article(self, article_id):
        """Get a specific article from the Galactapedia"""
        print(f"Retrieving Galactapedia article: {article_id}")
        
        # Check cache first
        if article_id in self.article_cache:
            print("Returning cached article")
            return self.article_cache[article_id]
        
        # Check if we have hardcoded content for this article
        hardcoded_articles = self.get_hardcoded_articles()
        if article_id in hardcoded_articles:
            print(f"Using hardcoded content for {article_id}")
            article = hardcoded_articles[article_id].copy()
            article["url"] = f"{self.base_url}/article/{article_id}"
            self.article_cache[article_id] = article
            return article
        
        # First, check if we can find this article in our category listings
        try:
            # Get articles from multiple categories to increase chances of finding it
            categories_to_check = ["spacecraft", "planets", "people", "history", "military"]
            for category in categories_to_check:
                category_articles = self.get_category(category)
                for article in category_articles:
                    if article.get("id") == article_id:
                        # Found the article in a category, add more details
                        article_url = f"{self.base_url}/article/{article_id}"
                        article["url"] = article_url
                        
                        # Try to get more content from the article page
                        try:
                            response = requests.get(article_url, headers=self.headers, timeout=15)
                            if response.status_code == 200:
                                soup = BeautifulSoup(response.text, 'html.parser')
                                
                                # Extract article content
                                content_elem = soup.select_one(".article-content")
                                if content_elem:
                                    article["content"] = content_elem.text.strip()
                                
                                # Extract metadata
                                metadata = {}
                                metadata_items = soup.select(".article-metadata-item")
                                for item in metadata_items:
                                    label_elem = item.select_one(".article-metadata-label")
                                    value_elem = item.select_one(".article-metadata-value")
                                    if label_elem and value_elem:
                                        label = label_elem.text.strip().rstrip(":")
                                        value = value_elem.text.strip()
                                        metadata[label] = value
                                
                                if metadata:
                                    article["metadata"] = metadata
                        except Exception as e:
                            print(f"Failed to get article details: {e}")
                        
                        self.article_cache[article_id] = article
                        return article
        except Exception as e:
            print(f"Category-based article lookup failed: {e}")
        
        # If we haven't found it yet, try direct access to the article page
        try:
            article_url = f"{self.base_url}/article/{article_id}"
            response = requests.get(article_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract article title
            title_elem = soup.select_one(".article-title")
            if not title_elem:
                raise Exception("Could not find article title")
            
            title = title_elem.text.strip()
            
            # Extract article content
            content_elem = soup.select_one(".article-content")
            content = content_elem.text.strip() if content_elem else ""
            
            # Extract metadata
            metadata = {}
            metadata_items = soup.select(".article-metadata-item")
            for item in metadata_items:
                label_elem = item.select_one(".article-metadata-label")
                value_elem = item.select_one(".article-metadata-value")
                if label_elem and value_elem:
                    label = label_elem.text.strip().rstrip(":")
                    value = value_elem.text.strip()
                    metadata[label] = value
            
            # Create article object
            article = {
                "id": article_id,
                "title": title,
                "content": content,
                "url": article_url
            }
            
            if metadata:
                article["metadata"] = metadata
            
            self.article_cache[article_id] = article
            return article
            
        except Exception as e:
            print(f"Direct article retrieval failed: {e}")
            
            # Return a minimal article object if we couldn't get the full details
            article = {
                "id": article_id,
                "title": article_id,
                "url": f"{self.base_url}/article/{article_id}",
                "metadata": {}
            }
            
            self.article_cache[article_id] = article
            return article
    
    def get_category(self, category_name):
        """Retrieve articles from a specific category in the Galactapedia"""
        print(f"Retrieving Galactapedia category: {category_name}")
        
        # Check cache first
        if category_name in self.category_cache:
            return self.category_cache[category_name]
        
        try:
            # Try to scrape the category page
            category_url = f"{self.base_url}/category/{category_name}"
            response = requests.get(category_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all article items
            articles = []
            article_items = soup.select(".category-article-item")
            
            for item in article_items:
                # Extract article ID and title
                link = item.select_one("a[href^='/galactapedia/article/']")
                if not link:
                    continue
                    
                article_id = link['href'].split('/')[-1]
                title = link.text.strip()
                
                # Extract description if available
                desc_elem = item.select_one(".category-article-description")
                description = desc_elem.text.strip() if desc_elem else ""
                
                articles.append({
                    "id": article_id,
                    "title": title,
                    "description": description,
                    "url": f"{self.base_url}/article/{article_id}",
                    "tags": [category_name]
                })
            
            self.category_cache[category_name] = articles
            return articles
            
        except Exception as e:
            print(f"Failed to retrieve category: {e}")
            return []
    
    def get_categories(self):
        """Get a list of all categories in the Galactapedia"""
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            categories = []
            category_links = soup.select("a[href^='/galactapedia/category/']")
            
            for link in category_links:
                category_id = link['href'].split('/')[-1]
                title = link.text.strip()
                
                categories.append({
                    "id": category_id,
                    "title": title,
                    "url": f"{self.base_url}/category/{category_id}"
                })
            
            return categories
            
        except Exception as e:
            print(f"Failed to retrieve categories: {e}")
            return []

# Display functions for command-line usage
def display_search_results(results):
    """Display search results in a formatted way"""
    if not results:
        print("No results found.")
        return
    
    print(f"\nFound {len(results)} results:\n")
    
    for i, result in enumerate(results, 1):
        title = result.get("title", "Unknown")
        description = result.get("description", "")
        article_type = result.get("type", "")
        url = result.get("url", "")
        
        print(f"{i}. {title}")
        if article_type:
            print(f"   Type: {article_type}")
        if description:
            print(f"   {description}")
        print(f"   URL: {url}")
        print()

def display_article(article):
    """Display an article in a formatted way"""
    if not article:
        print("Article not found.")
        return
    
    title = article.get("title", "Unknown")
    content = article.get("content", "No content available.")
    metadata = article.get("metadata", {})
    url = article.get("url", "")
    
    print("\n" + "=" * 80)
    print(f"TITLE: {title}")
    print("=" * 80)
    
    if metadata:
        print("\nMETADATA:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")
    
    print("\nCONTENT:")
    # Wrap text for better readability
    wrapped_content = textwrap.fill(content, width=80)
    print(wrapped_content)
    
    print("\nURL:")
    print(url)
    print("=" * 80 + "\n")

def display_categories(categories):
    """Display categories in a formatted way"""
    if not categories:
        print("No categories found.")
        return
    
    print(f"\nFound {len(categories)} categories:\n")
    
    for i, category in enumerate(categories, 1):
        title = category.get("title", "Unknown")
        url = category.get("url", "")
        
        print(f"{i}. {title}")
        print(f"   URL: {url}")
        print()

def display_category_articles(category_name, articles):
    """Display articles in a category in a formatted way"""
    if not articles:
        print(f"No articles found in category: {category_name}")
        return
    
    print(f"\nFound {len(articles)} articles in category '{category_name}':\n")
    
    for i, article in enumerate(articles, 1):
        title = article.get("title", "Unknown")
        description = article.get("description", "")
        url = article.get("url", "")
        
        print(f"{i}. {title}")
        if description:
            print(f"   {description}")
        print(f"   URL: {url}")
        print()

def main():
    """Main function for command-line usage"""
    client = GalactapediaClient()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python galactapedia_lookup.py search <query>")
        print("  python galactapedia_lookup.py article <article_id>")
        print("  python galactapedia_lookup.py category <category_name>")
        print("  python galactapedia_lookup.py categories")
        return
    
    command = sys.argv[1].lower()
    
    if command == "search" and len(sys.argv) >= 3:
        query = sys.argv[2]
        results = client.search_articles(query)
        display_search_results(results)
    
    elif command == "article" and len(sys.argv) >= 3:
        article_id = sys.argv[2]
        article = client.get_article(article_id)
        display_article(article)
    
    elif command == "category" and len(sys.argv) >= 3:
        category_name = sys.argv[2]
        articles = client.get_category(category_name)
        display_category_articles(category_name, articles)
    
    elif command == "categories":
        categories = client.get_categories()
        display_categories(categories)
    
    else:
        print("Invalid command or missing arguments.")
        print("Usage:")
        print("  python galactapedia_lookup.py search <query>")
        print("  python galactapedia_lookup.py article <article_id>")
        print("  python galactapedia_lookup.py category <category_name>")
        print("  python galactapedia_lookup.py categories")

if __name__ == "__main__":
    main()
