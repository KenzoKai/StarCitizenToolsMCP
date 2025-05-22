# Star Citizen Tools MCP Server

This is a Model-Content-Provider (MCP) server for Star Citizen that references multiple data sources:

1. [Star Citizen Tools Wiki](https://starcitizen.tools/) - For game information and lore
2. [RSI Citizen Profiles](https://robertsspaceindustries.com/en/citizens/) - For player profiles
3. [RSI Organization Profiles](https://robertsspaceindustries.com/en/orgs/) - For organization details
4. [RSI Galactapedia](https://robertsspaceindustries.com/galactapedia) - For in-universe lore and information

## Project Structure

### Configuration Files
- `server.json` - Main server configuration file

### Modules
- `modules/wiki/module.json` - Wiki module for accessing Star Citizen Tools wiki
- `modules/citizens/module.json` - Citizens module for accessing RSI player profiles
- `modules/organizations/module.json` - Organizations module for accessing RSI organization profiles
- `modules/galactapedia/module.json` - Galactapedia module for accessing RSI Galactapedia articles and categories

### Client Scripts
- `client.py` - General Python client script to interact with the MCP server
- `simple_example.py` - Simple script to directly interact with the Star Citizen Tools wiki
- `citizen_lookup.py` - Script to retrieve citizen profiles from the RSI website
- `org_lookup.py` - Script to retrieve organization profiles and member lists from the RSI website
- `galactapedia_lookup.py` - Script to search and retrieve articles from the RSI Galactapedia

## Getting Started

### Prerequisites

- Python 3.6 or higher
- `requests` library (`pip install requests`)
- `beautifulsoup4` library (`pip install beautifulsoup4`) - For the standalone scripts

### Using the Client Script

The client script provides a simple way to interact with the MCP server. Here are some example commands:

#### List Available Modules

```bash
python client.py list-modules
```

#### List Resources in a Module

```bash
python client.py list-resources wiki
```

#### Call a Resource

To search for articles about "Anvil Carrack" using the wiki module:

```bash
python client.py call wiki search --params srsearch="Anvil Carrack"
```

To retrieve a specific wiki page about "Anvil Carrack":

```bash
python client.py call wiki wiki_page --params page="Anvil Carrack"
```

To retrieve a citizen profile by handle:

```bash
python client.py call citizens profile --params handle="KenzoKai"
```

To retrieve an organization profile by SID:

```bash
python client.py call organizations profile --params sid="HMBCREW"
```

To search the Galactapedia for articles about a specific topic:

```bash
python client.py call galactapedia search --params query="Carrack"
```

To retrieve a specific Galactapedia article by ID:

```bash
python client.py call galactapedia article --params articleId="R4ZGyLQaBl-carrack"
```

To browse articles in a specific Galactapedia category:

```bash
python client.py call galactapedia category --params categoryName="spacecraft"
```

### Using the Standalone Scripts

The project includes several standalone scripts that provide a more direct way to interact with the data sources.

#### Wiki Information

```bash
python simple_example.py search "Anvil Carrack"  # Search for articles
python simple_example.py page "Carrack"          # Get a specific page
```

#### Citizen Profiles

```bash
python citizen_lookup.py KenzoKai  # Look up a citizen profile
```

#### Organization Information

```bash
python org_lookup.py HMBCREW          # Look up an organization profile
python org_lookup.py HMBCREW members  # Look up an organization's members
```

#### Galactapedia Information

```bash
python galactapedia_lookup.py search Carrack       # Search for articles about Carrack
python galactapedia_lookup.py article R4ZGyLQaBl-carrack  # Get a specific article by ID
python galactapedia_lookup.py categories           # List all available categories
python galactapedia_lookup.py category spacecraft  # Browse articles in the spacecraft category
```

## Understanding MCP Servers

MCP (Model-Content-Provider) servers are a way to organize and access content from different sources through a standardized interface. In this project:

1. The `server.json` file defines the overall server configuration
2. Each module (wiki, citizens, organizations) provides access to a specific content source
3. Resources within modules define specific API endpoints and their parameters

This modular approach allows you to easily extend the server with additional content sources in the future.

## Data Output

All the scripts save their output to JSON files for easy integration with other applications:

- Wiki searches and pages: Results are displayed in the console
- Citizen profiles: Saved to `<handle>_profile.json` (e.g., `KenzoKai_profile.json`)
- Organization profiles: Saved to `<sid>_profile.json` (e.g., `HMBCREW_profile.json`)
- Organization members: Saved to `<sid>_members.json` (e.g., `HMBCREW_members.json`)
- Galactapedia searches: Saved to `galactapedia_search_<query>.json` (e.g., `galactapedia_search_Carrack.json`)
- Galactapedia articles: Saved to `galactapedia_article_<article_id>.json` (e.g., `galactapedia_article_R4ZGyLQaBl-carrack.json`)
- Galactapedia categories: Saved to `galactapedia_categories.json`
- Galactapedia category articles: Saved to `galactapedia_category_<category_name>.json` (e.g., `galactapedia_category_spacecraft.json`)

1. The `server.json` file defines the overall server configuration
2. Each module (like the wiki module) provides access to a specific content source
3. Resources within modules define specific API endpoints and their parameters

This modular approach allows you to easily extend the server with additional content sources in the future.
