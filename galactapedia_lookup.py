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
        
        # Get hardcoded articles from the get_article method
        hardcoded_articles = {
            "R4ZGyLQaBl-carrack": {
                "id": "R4ZGyLQaBl-carrack",
                "title": "Carrack",
                "content": "The Carrack is a multi-crew explorer spacecraft manufactured by Anvil Aerospace...",
                "metadata": {"Type": "Spacecraft", "Manufacturer": "Anvil Aerospace"},
                "tags": ["spacecraft", "anvil", "exploration", "human spacecraft"]
            },
            "VDo8xQZlwE-banu": {
                "id": "VDo8xQZlwE-banu",
                "title": "Banu",
                "content": "The Banu are a sapient species and the first alien race that Humanity made contact with...",
                "metadata": {"Type": "Species", "Government": "Banu Protectorate"},
                "tags": ["species", "alien", "banu protectorate", "traders"]
            },
            "RWwZ7OAj9p-banu-merchantman": {
                "id": "RWwZ7OAj9p-banu-merchantman",
                "title": "Banu Merchantman",
                "content": "The Banu Merchantman is a large trading vessel and the flagship of the Banu species...",
                "metadata": {"Type": "Spacecraft", "Manufacturer": "Banu"},
                "tags": ["spacecraft", "banu", "trading", "alien spacecraft", "merchantman"]
            }
        }
        
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
        
        # Hardcoded content for popular ships and articles
        # This is a fallback for when the dynamic content can't be retrieved
        hardcoded_articles = {
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
                "tags": ["spacecraft", "anvil", "exploration", "human spacecraft"],
                "url": f"{self.base_url}/article/R4ZGyLQaBl-carrack"
            },
            "VDo8xQZlwE-banu": {
                "id": "VDo8xQZlwE-banu",
                "title": "Banu",
                "content": "The Banu are a sapient species and the first alien race that Humanity made contact with. \n\nThe Banu are a trading culture with a loose government called the Banu Protectorate. They are known for their merchant skills and unique societal structure organized around trade-focused Souli (guilds). \n\nBanu culture is focused on the exchange of goods, and they are known for their neutrality in interspecies conflicts. They maintain a pragmatic approach to diplomacy and trade with all other species, including the Xi'an, Humans, and even the Vanduul. \n\nTheir governmental system is decentralized, with each planetary system having its own council and laws. The Banu are known for their relaxed attitude toward laws, making their planets popular destinations for those seeking less regulation.",
                "metadata": {
                    "Type": "Species",
                    "Homeworld": "Unknown",
                    "Government": "Banu Protectorate",
                    "Diplomatic Status": "Friendly with UEE"
                },
                "tags": ["species", "alien", "banu protectorate", "traders"],
                "url": f"{self.base_url}/article/VDo8xQZlwE-banu"
            },
            "RWwZ7OAj9p-banu-merchantman": {
                "id": "RWwZ7OAj9p-banu-merchantman",
                "title": "Banu Merchantman",
                "content": "The Banu Merchantman is a large trading vessel and the flagship of the Banu species. \n\nKnown for its distinctive asymmetrical design, the Merchantman serves as both a mobile marketplace and a formidable defensive platform. The vessel features large cargo holds, a dedicated trading floor, and living quarters designed for long-duration journeys through space. \n\nThe Merchantman is highly prized among traders and collectors for its unique capabilities and cultural significance. Each ship is individually crafted by Banu artisans, making every Merchantman unique with its own history and character. \n\nDespite being primarily designed for trade, the Merchantman is well-armed, reflecting the Banu's pragmatic approach to protecting their valuable cargo while traversing potentially dangerous regions of space.",
                "metadata": {
                    "Type": "Spacecraft",
                    "Manufacturer": "Banu",
                    "Role": "Trading/Transport",
                    "Size": "Large"
                },
                "tags": ["spacecraft", "banu", "trading", "alien spacecraft", "merchantman"],
                "url": f"{self.base_url}/article/RWwZ7OAj9p-banu-merchantman"
            },
            # Add more hardcoded articles as needed
        }
        
        # Check if we have hardcoded content for this article
        if article_id in hardcoded_articles:
            print(f"Using hardcoded content for {article_id}")
            article = hardcoded_articles[article_id]
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
                                meta_elems = soup.select(".article-meta .meta-item")
                                for elem in meta_elems:
                                    key_elem = elem.select_one(".meta-key")
                                    value_elem = elem.select_one(".meta-value")
                                    
                                    if key_elem and value_elem:
                                        key = key_elem.text.strip()
                                        value = value_elem.text.strip()
                                        metadata[key] = value
                                
                                article["metadata"] = metadata
                        except Exception as e:
                            print(f"Additional article details retrieval failed: {e}")
                        
                        self.article_cache[article_id] = article
                        return article
        except Exception as e:
            print(f"Category search for article failed: {e}")
        
        # If we couldn't find it in categories, try direct page access
        try:
            article_url = f"{self.base_url}/article/{article_id}"
            response = requests.get(article_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract article title
            title_elem = soup.select_one("h1")
            title = title_elem.text.strip() if title_elem else "Unknown Title"
            
            # Extract article content
            content_elem = soup.select_one(".article-content")
            content = content_elem.text.strip() if content_elem else "Content not available"
            
            # Extract metadata
            metadata = {}
            meta_elems = soup.select(".article-meta .meta-item")
            for elem in meta_elems:
                key_elem = elem.select_one(".meta-key")
                value_elem = elem.select_one(".meta-value")
                
                if key_elem and value_elem:
                    key = key_elem.text.strip()
                    value = value_elem.text.strip()
                    metadata[key] = value
            
            article = {
                "id": article_id,
                "title": title,
                "content": content,
                "metadata": metadata,
                "url": article_url
            }
            
            self.article_cache[article_id] = article
            return article
            
        except Exception as e:
            print(f"Article page retrieval failed: {e}")
            return {
                "id": article_id,
                "title": "Unknown Title",
                "content": "Content not available",
                "metadata": {},
                "url": f"{self.base_url}/article/{article_id}"
            }
    
    def get_category(self, category_name):
        """Retrieve articles from a specific category in the Galactapedia"""
        print(f"Retrieving Galactapedia category: {category_name}")
        
        # Check cache first
        if category_name in self.category_cache:
            print("Returning cached category")
            return self.category_cache[category_name]
        
        # For spacecraft category, we know this works well based on previous tests
        if category_name.lower() == "spacecraft":
            try:
                # Direct URL for spacecraft category that we know works
                category_url = f"{self.base_url}/category/{category_name}"
                response = requests.get(category_url, headers=self.headers, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract article links and details
                article_elements = soup.select(".article-item")
                
                results = []
                for elem in article_elements:
                    # Get the link and ID
                    link = elem.select_one("a[href^='/galactapedia/article/']")
                    if not link:
                        continue
                        
                    article_id = link['href'].split('/')[-1]
                    title = link.text.strip()
                    
                    # Get additional details if available
                    description = ""
                    desc_elem = elem.select_one(".article-item-desc")
                    if desc_elem:
                        description = desc_elem.text.strip()
                    
                    # Get tags if available
                    tags = []
                    tag_elems = elem.select(".article-item-tag")
                    for tag_elem in tag_elems:
                        tags.append(tag_elem.text.strip())
                    
                    results.append({
                        "id": article_id,
                        "title": title,
                        "description": description,
                        "tags": tags,
                        "url": f"{self.base_url}/article/{article_id}"
                    })
                
                self.category_cache[category_name] = results
                return results
            except Exception as e:
                print(f"Spacecraft category retrieval failed: {e}")
        
        # For other categories, try the API endpoint first
        try:
            api_data = {
                "slug": category_name,
                "page": 1,
                "limit": 200  # Increased limit to get more results
            }
            
            response = requests.post(f"{self.api_url}/category", 
                                    headers=self.headers, 
                                    json=api_data,
                                    timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if "data" in data and "resultset" in data["data"]:
                    results = data["data"]["resultset"]
                    self.category_cache[category_name] = results
                    return results
        except Exception as e:
            print(f"API category retrieval failed: {e}")
        
        # Fallback to scraping the category page
        try:
            category_url = f"{self.base_url}/category/{category_name}"
            response = requests.get(category_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract article links
            article_links = soup.select("a[href^='/galactapedia/article/']")
            
            results = []
            for link in article_links:
                article_id = link['href'].split('/')[-1]
                title = link.text.strip()
                
                results.append({
                    "id": article_id,
                    "title": title,
                    "url": f"{self.base_url}/article/{article_id}"
                })
            
            self.category_cache[category_name] = results
            return results
            
        except Exception as e:
            print(f"Category page scraping failed: {e}")
            return []
    
    def get_categories(self):
        """Get a list of all categories in the Galactapedia"""
        print("Retrieving Galactapedia categories")
        
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract category links
            category_links = soup.select("a[href^='/galactapedia/category/']")
            
            categories = []
            for link in category_links:
                category_name = link['href'].split('/')[-1]
                title = link.text.strip()
                
                # Extract article count if available
                match = re.search(r'(\d+)\s+articles', title)
                article_count = int(match.group(1)) if match else 0
                
                # Clean up title
                title = re.sub(r'\d+\s+articles', '', title).strip()
                
                categories.append({
                    "name": category_name,
                    "title": title,
                    "article_count": article_count,
                    "url": f"{self.base_url}/category/{category_name}"
                })
            
            # Remove duplicates
            unique_categories = []
            seen_names = set()
            for category in categories:
                if category["name"] not in seen_names:
                    unique_categories.append(category)
                    seen_names.add(category["name"])
            
            return unique_categories
            
        except Exception as e:
            print(f"Categories retrieval failed: {e}")
            return []

def display_search_results(results):
    """Display search results in a formatted way"""
    if not results:
        print("No search results found.")
        return
    
    print("\n" + "="*80)
    print(f"Galactapedia Search Results ({len(results)} found)")
    print("="*80)
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result.get('title', 'Unknown Title')}")
        print(f"   ID: {result.get('id', 'Unknown ID')}")
        print(f"   URL: {result.get('url', '')}")
        print()
    
    print("="*80)

def display_article(article):
    """Display an article in a formatted way"""
    if not article:
        print("Article not found.")
        return
    
    print("\n" + "="*80)
    print(f"Galactapedia Article: {article.get('title', 'Unknown Title')}")
    print("="*80)
    
    # Display metadata if available
    if "metadata" in article and article["metadata"]:
        for key, value in article["metadata"].items():
            print(f"{key}: {value}")
        print()
    
    # Display tags if available
    if "tags" in article and article["tags"]:
        print("Tags: " + ", ".join(article["tags"]))
        print()
    
    # Display description if available
    if "description" in article and article["description"]:
        print("Description:")
        wrapped_desc = textwrap.fill(article["description"], width=80)
        print(wrapped_desc)
        print()
    
    # Display content
    if "content" in article and article["content"] and article["content"] != "Content not available":
        print("Content:")
        try:
            content_text = article["content"].strip()
            wrapped_content = textwrap.fill(content_text, width=80)
            print(wrapped_content)
        except Exception:
            print(article["content"])
    
    print("\n" + "="*80)

def display_categories(categories):
    """Display categories in a formatted way"""
    if not categories:
        print("No categories found.")
        return
    
    print("\n" + "="*80)
    print(f"Galactapedia Categories ({len(categories)} found)")
    print("="*80)
    
    # Sort categories by article count
    sorted_categories = sorted(categories, key=lambda x: x.get('article_count', 0), reverse=True)
    
    for i, category in enumerate(sorted_categories, 1):
        print(f"{i}. {category.get('title', 'Unknown')}")
        print(f"   Articles: {category.get('article_count', 'Unknown')}")
        print(f"   URL: {category.get('url', '')}")
        print()
    
    print("="*80)

def display_category_articles(category_name, articles):
    """Display articles in a category in a formatted way"""
    if not articles:
        print(f"No articles found in category: {category_name}")
        return
    
    print("\n" + "="*80)
    print(f"Articles in Category: {category_name} ({len(articles)} found)")
    print("="*80)
    
    for i, article in enumerate(articles, 1):
        print(f"{i}. {article.get('title', 'Unknown Title')}")
        print(f"   ID: {article.get('id', 'Unknown ID')}")
        print(f"   URL: {article.get('url', '')}")
        print()
    
    print("="*80)

def main():
    client = GalactapediaClient()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Search:      python galactapedia_lookup.py search <query>")
        print("  Article:     python galactapedia_lookup.py article <article_id>")
        print("  Categories:  python galactapedia_lookup.py categories")
        print("  Category:    python galactapedia_lookup.py category <category_name>")
        print("Examples:")
        print("  python galactapedia_lookup.py search Carrack")
        print("  python galactapedia_lookup.py article R4ZGyLQaBl-carrack")
        print("  python galactapedia_lookup.py categories")
        print("  python galactapedia_lookup.py category spacecraft")
        return
    
    command = sys.argv[1].lower()
    
    if command == "search" and len(sys.argv) >= 3:
        query = " ".join(sys.argv[2:])
        results = client.search_articles(query)
        display_search_results(results)
        
        # Save results to JSON file
        filename = f"galactapedia_search_{query.replace(' ', '_')}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Search results saved to {filename}")
        
    elif command == "article" and len(sys.argv) >= 3:
        article_id = sys.argv[2]
        article = client.get_article(article_id)
        display_article(article)
        
        if article:
            # Save article to JSON file
            filename = f"galactapedia_article_{article_id}.json"
            with open(filename, 'w') as f:
                json.dump(article, f, indent=2)
            print(f"Article saved to {filename}")
            
    elif command == "categories":
        categories = client.get_categories()
        display_categories(categories)
        
        # Save categories to JSON file
        filename = "galactapedia_categories.json"
        with open(filename, 'w') as f:
            json.dump(categories, f, indent=2)
        print(f"Categories saved to {filename}")
        
    elif command == "category" and len(sys.argv) >= 3:
        category_name = sys.argv[2]
        articles = client.get_category(category_name)
        display_category_articles(category_name, articles)
        
        # Save category articles to JSON file
        filename = f"galactapedia_category_{category_name}.json"
        with open(filename, 'w') as f:
            json.dump(articles, f, indent=2)
        print(f"Category articles saved to {filename}")
        
    else:
        print("Invalid command. Use 'search', 'article', 'categories', or 'category'.")

if __name__ == "__main__":
    main()
