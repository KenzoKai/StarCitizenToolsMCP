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
        
        # First, try direct scraping of the search results page
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
                
                # Calculate relevance score based on query match
                relevance_score = 0
                query_terms = query.lower().split()
                title_lower = title.lower()
                description_lower = description.lower()
                
                # Check for exact title match (highest priority)
                if query.lower() == title_lower:
                    relevance_score += 100
                
                # Check for title containing the full query
                elif query.lower() in title_lower:
                    relevance_score += 75
                
                # Check for all query terms in title
                elif all(term in title_lower for term in query_terms):
                    relevance_score += 60
                
                # Check for any query terms in title (partial matches)
                else:
                    for term in query_terms:
                        if term in title_lower:
                            relevance_score += 15
                
                # Check for query terms in description
                for term in query_terms:
                    if term in description_lower:
                        relevance_score += 5
                
                # Boost score for spacecraft if looking for ships
                ship_terms = ["ship", "spacecraft", "vessel", "fighter", "frigate", "cruiser", "carrier"]
                if any(term in query.lower() for term in ship_terms) and article_type.lower() == "spacecraft":
                    relevance_score += 20
                
                # Add the result with its relevance score
                results.append({
                    "id": article_id,
                    "title": title,
                    "description": description,
                    "type": article_type,
                    "url": f"{self.base_url}/article/{article_id}",
                    "relevance_score": relevance_score
                })
            
            if results:
                # Sort results by relevance score (highest first)
                results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
                
                # Remove the relevance_score field before returning
                for result in results:
                    if "relevance_score" in result:
                        del result["relevance_score"]
                
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
            
            # Filter and score results based on query - check title and description
            scored_results = []
            query_terms = query.lower().split()
            
            for article in all_results:
                title = article.get("title", "").lower()
                description = article.get("description", "").lower()
                tags = [tag.lower() for tag in article.get("tags", [])]
                article_type = article.get("type", "").lower()
                
                # Calculate relevance score
                relevance_score = 0
                
                # Check for exact title match (highest priority)
                if query.lower() == title:
                    relevance_score += 100
                    
                # Check for title containing the full query
                elif query.lower() in title:
                    relevance_score += 75
                
                # Check for all query terms in title
                elif all(term in title for term in query_terms):
                    relevance_score += 60
                
                # Check for any query terms in title (partial matches)
                else:
                    # Check for fuzzy matches in title (handles misspellings)
                    for term in query_terms:
                        if term in title:
                            relevance_score += 15
                        # Check for partial matches (e.g., "conste" matching "constellation")
                        elif len(term) > 3 and any(term[:min(len(term), i+3)] in title for i in range(len(term)-2)):
                            relevance_score += 10
                        # Check for character-swapped misspellings (e.g., "pheonix" vs "phoenix")
                        elif len(term) > 4 and any(term.replace(term[i:i+2], term[i+1]+term[i], 1) in title for i in range(len(term)-1)):
                            relevance_score += 8
                
                # Check for query terms in description
                for term in query_terms:
                    if term in description:
                        relevance_score += 5
                    elif len(term) > 3 and any(term[:min(len(term), i+3)] in description for i in range(len(term)-2)):
                        relevance_score += 3
                
                # Check for query terms in tags
                for term in query_terms:
                    if any(term in tag for tag in tags):
                        relevance_score += 10
                
                # Boost score for spacecraft if looking for ships
                ship_terms = ["ship", "spacecraft", "vessel", "fighter", "frigate", "cruiser", "carrier"]
                if any(term in query.lower() for term in ship_terms) and "spacecraft" in tags:
                    relevance_score += 20
                
                # Only include results with some relevance
                if relevance_score > 0:
                    article_copy = article.copy()
                    article_copy["relevance_score"] = relevance_score
                    scored_results.append(article_copy)
            
            # Sort by relevance score
            scored_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
            
            # Remove the relevance_score field before returning
            filtered_results = []
            for result in scored_results:
                if "relevance_score" in result:
                    del result["relevance_score"]
                filtered_results.append(result)
            
            print(f"Found {len(filtered_results)} matching articles from categories")
            
            # If we found results, return them
            if filtered_results:
                self.search_cache[query] = filtered_results
                return filtered_results
            
            # If no results found, try to fallback to our common ship database
            print("No results found in Galactapedia, checking common ship database...")
            ship_results = self.get_common_ship_info(query)
            if ship_results:
                print(f"Found ship information in common database")
                self.search_cache[query] = ship_results
                return ship_results
            
            # If we still have no results, return an empty list
            return []
            
        except Exception as e:
            print(f"Category-based search failed: {e}")
            
            # Try our common ship database as a last resort
            ship_results = self.get_common_ship_info(query)
            if ship_results:
                print(f"Found ship information in common database")
                self.search_cache[query] = ship_results
                return ship_results
                
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
    
    def get_common_ship_info(self, query):
        """Provide information about common ships based on the query"""
        # Dictionary of common ships with their variants and information
        common_ships = {
            # RSI Constellation series
            "constellation": {
                "variants": ["andromeda", "aquila", "phoenix", "taurus"],
                "title": "Constellation",
                "manufacturer": "Roberts Space Industries",
                "content": "The RSI Constellation is a multi-crew spacecraft that comes in several variants. It's known for its versatility and is one of the most iconic ships in the Star Citizen universe.",
                "type": "Spacecraft",
                "role": "Multi-purpose",
                "size": "Large"
            },
            "phoenix": {
                "parent": "constellation",
                "title": "Constellation Phoenix",
                "manufacturer": "Roberts Space Industries",
                "content": "The Constellation Phoenix is the luxury variant of the RSI Constellation series. It features high-end accommodations, a private lounge, and upgraded components compared to other Constellation variants.",
                "type": "Spacecraft",
                "role": "Luxury/VIP Transport",
                "size": "Large"
            },
            
            # Aegis ships
            "idris": {
                "variants": ["idris-m", "idris-p", "idris-k"],
                "title": "Idris",
                "manufacturer": "Aegis Dynamics",
                "content": "The Aegis Idris is a capital-class frigate used by the UEE Navy and private organizations. It can carry multiple smaller ships and serves as a mobile base of operations.",
                "type": "Spacecraft",
                "role": "Frigate",
                "size": "Capital"
            },
            "sabre": {
                "title": "Sabre",
                "manufacturer": "Aegis Dynamics",
                "content": "The Aegis Sabre is a stealth fighter designed for dogfighting. It features a reduced cross-section and advanced stealth features, making it difficult to detect.",
                "type": "Spacecraft",
                "role": "Stealth Fighter",
                "size": "Medium"
            },
            
            # Anvil ships
            "carrack": {
                "title": "Carrack",
                "manufacturer": "Anvil Aerospace",
                "content": "The Anvil Carrack is an expedition vessel designed for long-range exploration. It features advanced jump drives, a medical bay, repair facilities, and a modular cargo system.",
                "type": "Spacecraft",
                "role": "Exploration",
                "size": "Large"
            },
            
            # Origin ships
            "890 jump": {
                "title": "890 Jump",
                "manufacturer": "Origin Jumpworks",
                "content": "The Origin 890 Jump is a luxury touring spacecraft and the flagship of Origin's lineup. It represents the pinnacle of luxury space travel with opulent interiors and high-end amenities.",
                "type": "Spacecraft",
                "role": "Luxury Touring",
                "size": "Capital"
            },
            
            # Drake ships
            "cutlass": {
                "variants": ["black", "blue", "red"],
                "title": "Cutlass",
                "manufacturer": "Drake Interplanetary",
                "content": "The Drake Cutlass is a multi-purpose ship that balances cargo capacity with combat capability. It's popular among independent operators and pirates.",
                "type": "Spacecraft",
                "role": "Multi-purpose",
                "size": "Medium"
            }
        }
        
        # Normalize the query
        query_lower = query.lower()
        
        # Check for exact matches
        if query_lower in common_ships:
            ship_info = common_ships[query_lower]
            return self._format_ship_result(ship_info, query_lower)
        
        # Check for variant matches (e.g., "constellation phoenix")
        query_parts = query_lower.split()
        for part in query_parts:
            if part in common_ships:
                ship_info = common_ships[part]
                # Check if another part matches a variant (including fuzzy matching)
                for other_part in query_parts:
                    if other_part != part and 'variants' in ship_info:
                        # Check exact variant match first
                        if other_part in ship_info['variants']:
                            variant_key = other_part
                            if variant_key in common_ships:
                                return self._format_ship_result(common_ships[variant_key], variant_key)
                            else:
                                # Create a variant result based on the parent ship
                                variant_info = ship_info.copy()
                                variant_info['title'] = f"{ship_info['title']} {other_part.capitalize()}"
                                variant_info['content'] = f"The {variant_info['title']} is a variant of the {ship_info['title']} series by {ship_info['manufacturer']}."
                                return self._format_ship_result(variant_info, f"{part}_{other_part}")
                        
                        # Check for fuzzy variant matches
                        for variant in ship_info['variants']:
                            if self._fuzzy_match(other_part, variant):
                                # Found a fuzzy match for the variant
                                if variant in common_ships:
                                    return self._format_ship_result(common_ships[variant], variant)
                                else:
                                    # Create a variant result based on the parent ship
                                    variant_info = ship_info.copy()
                                    variant_info['title'] = f"{ship_info['title']} {variant.capitalize()}"
                                    variant_info['content'] = f"The {variant_info['title']} is a variant of the {ship_info['title']} series by {ship_info['manufacturer']}."
                                    return self._format_ship_result(variant_info, f"{part}_{variant}")
                
                # Just the base ship was mentioned
                return self._format_ship_result(ship_info, part)
        
        # Check for fuzzy matches (handle misspellings)
        for ship_key, ship_info in common_ships.items():
            # Check for simple misspellings (e.g., "pheonix" instead of "phoenix")
            if self._fuzzy_match(query_lower, ship_key):
                return self._format_ship_result(ship_info, ship_key)
            
            # Check for variant misspellings
            if 'variants' in ship_info:
                for variant in ship_info['variants']:
                    variant_full = f"{ship_key} {variant}"
                    if self._fuzzy_match(query_lower, variant_full):
                        # Check if we have specific info for this variant
                        if variant in common_ships:
                            return self._format_ship_result(common_ships[variant], variant)
                        else:
                            # Create a variant result based on the parent ship
                            variant_info = ship_info.copy()
                            variant_info['title'] = f"{ship_info['title']} {variant.capitalize()}"
                            variant_info['content'] = f"The {variant_info['title']} is a variant of the {ship_info['title']} series by {ship_info['manufacturer']}."
                            return self._format_ship_result(variant_info, f"{ship_key}_{variant}")
        
        # No matches found
        return []
    
    def _format_ship_result(self, ship_info, ship_id):
        """Format ship information into a result object"""
        result = {
            "id": f"ship_{ship_id.replace(' ', '_')}",
            "title": ship_info['title'],
            "content": ship_info['content'],
            "type": ship_info.get('type', 'Spacecraft'),
            "url": f"https://robertsspaceindustries.com/galactapedia",
            "source": "Star Citizen Ship Database"
        }
        
        # Add metadata
        metadata = {}
        for key in ['manufacturer', 'role', 'size']:
            if key in ship_info:
                metadata[key.capitalize()] = ship_info[key]
        
        if metadata:
            result["metadata"] = metadata
        
        return [result]
    
    def _fuzzy_match(self, query, target):
        """Simple fuzzy matching to handle common misspellings"""
        # Exact match
        if query == target:
            return True
        
        # Check if query is contained in target
        if query in target or target in query:
            return True
        
        # Check for character swaps (e.g., "pheonix" vs "phoenix")
        if len(query) > 4 and len(target) > 4:
            for i in range(len(query) - 1):
                swapped = query[:i] + query[i+1] + query[i] + query[i+2:]
                if swapped == target or swapped in target:
                    return True
            
            # Check for common typos (missing or extra letters)
            if abs(len(query) - len(target)) <= 2:
                # Check if removing one character from query matches target
                for i in range(len(query)):
                    if query[:i] + query[i+1:] == target:
                        return True
                
                # Check if removing one character from target matches query
                for i in range(len(target)):
                    if target[:i] + target[i+1:] == query:
                        return True
        
        return False
    
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
