import json
import argparse
import os
import sys
import importlib.util

# Import specialized modules dynamically when needed
def import_module_from_file(module_name, file_path):
    """Import a module from file path dynamically"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class MCPClient:
    def __init__(self, server_config_path):
        try:
            # Load server configuration
            with open(server_config_path, 'r') as f:
                self.server_config = json.load(f)
            
            # Load module configurations
            self.modules = {}
            for module_info in self.server_config.get('modules', []):
                module_path = os.path.join(os.path.dirname(server_config_path), module_info['source'])
                with open(module_path, 'r') as f:
                    self.modules[module_info['name']] = json.load(f)
        except FileNotFoundError as e:
            print(f"Error: Could not find file: {e.filename}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in configuration file: {e}")
            sys.exit(1)
    
    def list_modules(self):
        """List all available modules"""
        print(f"Available modules in {self.server_config['name']}:")
        for name, module in self.modules.items():
            print(f"- {name}: {module.get('description', 'No description')}")
    
    def list_resources(self, module_name):
        """List all resources in a specific module"""
        if module_name not in self.modules:
            print(f"Module '{module_name}' not found")
            return
        
        module = self.modules[module_name]
        print(f"Resources in module '{module_name}':")
        for resource in module.get('resources', []):
            print(f"- {resource['name']}: {resource.get('description', 'No description')}")
            print(f"  Method: {resource.get('method', 'GET')}, Path: {resource.get('path', '/')}")
            print("  Parameters:")
            for param in resource.get('parameters', []):
                required = "Required" if param.get('required', False) else "Optional"
                default = f", Default: {param.get('default')}" if 'default' in param else ""
                print(f"    - {param['name']} ({param.get('type', 'string')}): {required}{default}")
                print(f"      {param.get('description', 'No description')}")
            print()
    
    def call_resource(self, module_name, resource_name, params=None):
        """Call a specific resource with parameters"""
        if params is None:
            params = {}
        
        if module_name not in self.modules:
            print(f"Module '{module_name}' not found")
            return None
        
        module = self.modules[module_name]
        resource = None
        for res in module.get('resources', []):
            if res['name'] == resource_name:
                resource = res
                break
        
        if not resource:
            print(f"Resource '{resource_name}' not found in module '{module_name}'")
            return None
        
        # Use specialized lookup scripts based on the module
        if module_name == 'citizens' and resource_name == 'profile':
            # Use citizen_lookup.py for citizen profiles
            return self._call_citizen_lookup(params)
        
        elif module_name == 'organizations':
            # Use org_lookup.py for organization profiles and members
            return self._call_org_lookup(resource_name, params)
        
        elif module_name == 'galactapedia':
            # Use galactapedia_lookup.py for Galactapedia resources
            return self._call_galactapedia_lookup(resource_name, params)
        
        elif module_name == 'wiki':
            # Use simple_example.py for wiki resources
            return self._call_wiki_lookup(resource_name, params)
        
        else:
            print(f"No specialized handler for module '{module_name}', resource '{resource_name}'")
            return None
    
    def _call_citizen_lookup(self, params):
        """Use citizen_lookup.py to retrieve citizen profiles"""
        if 'handle' not in params:
            print("Error: Missing required parameter 'handle'")
            return None
        
        handle = params['handle']
        print(f"Using citizen_lookup.py to retrieve profile for: {handle}")
        
        # Import the citizen_lookup module
        citizen_module = import_module_from_file('citizen_lookup', 'citizen_lookup.py')
        if not citizen_module:
            print("Error: Could not import citizen_lookup.py")
            return None
        
        # Call the get_citizen_profile function
        try:
            profile = citizen_module.get_citizen_profile(handle)
            if profile:
                # Save to JSON file (this is done in the main function of citizen_lookup.py)
                # but we'll do it here for consistency
                with open(f"{handle}_profile.json", 'w') as f:
                    json.dump(profile, f, indent=2)
                return profile
            else:
                print(f"Error: Could not retrieve profile for {handle}")
                return None
        except Exception as e:
            print(f"Error calling get_citizen_profile: {e}")
            return None
    
    def _call_org_lookup(self, resource_name, params):
        """Use org_lookup.py to retrieve organization profiles and members"""
        if 'sid' not in params:
            print("Error: Missing required parameter 'sid'")
            return None
        
        sid = params['sid']
        print(f"Using org_lookup.py to retrieve {resource_name} for organization: {sid}")
        
        # Import the org_lookup module
        org_module = import_module_from_file('org_lookup', 'org_lookup.py')
        if not org_module:
            print("Error: Could not import org_lookup.py")
            return None
        
        try:
            if resource_name == 'profile':
                # Call the get_organization_profile function
                org_data = org_module.get_organization_profile(sid)
                if org_data:
                    # Save to JSON file
                    with open(f"{sid}_profile.json", 'w') as f:
                        json.dump(org_data, f, indent=2)
                    return org_data
            elif resource_name == 'members':
                # Call the get_organization_members function
                members = org_module.get_organization_members(sid)
                if members:
                    # Save to JSON file
                    with open(f"{sid}_members.json", 'w') as f:
                        json.dump(members, f, indent=2)
                    return members
            else:
                print(f"Error: Unsupported resource '{resource_name}' for organizations module")
                return None
        except Exception as e:
            print(f"Error calling org_lookup functions: {e}")
            return None
    
    def _call_galactapedia_lookup(self, resource_name, params):
        """Use galactapedia_lookup.py to retrieve Galactapedia resources"""
        # Import the galactapedia_lookup module
        galactapedia_module = import_module_from_file('galactapedia_lookup', 'galactapedia_lookup.py')
        if not galactapedia_module:
            print("Error: Could not import galactapedia_lookup.py")
            return None
        
        try:
            # Create a GalactapediaClient instance
            client = galactapedia_module.GalactapediaClient()
            
            if resource_name == 'search':
                if 'query' not in params:
                    print("Error: Missing required parameter 'query'")
                    return None
                query = params['query']
                print(f"Using galactapedia_lookup.py to search for: {query}")
                return client.search_articles(query)
            
            elif resource_name == 'article':
                if 'articleId' not in params:
                    print("Error: Missing required parameter 'articleId'")
                    return None
                article_id = params['articleId']
                print(f"Using galactapedia_lookup.py to retrieve article: {article_id}")
                return client.get_article(article_id)
            
            elif resource_name == 'category':
                if 'categoryName' not in params:
                    print("Error: Missing required parameter 'categoryName'")
                    return None
                category_name = params['categoryName']
                print(f"Using galactapedia_lookup.py to retrieve category: {category_name}")
                return client.get_category(category_name)
            
            elif resource_name == 'categories':
                print("Using galactapedia_lookup.py to retrieve all categories")
                return client.get_categories()
            
            else:
                print(f"Error: Unsupported resource '{resource_name}' for galactapedia module")
                return None
        except Exception as e:
            print(f"Error calling galactapedia_lookup functions: {e}")
            return None
    
    def _call_wiki_lookup(self, resource_name, params):
        """Use simple_example.py to retrieve wiki resources"""
        # Import the simple_example module
        wiki_module = import_module_from_file('simple_example', 'simple_example.py')
        if not wiki_module:
            print("Error: Could not import simple_example.py")
            return None
        
        try:
            if resource_name == 'search':
                if 'srsearch' not in params:
                    print("Error: Missing required parameter 'srsearch'")
                    return None
                query = params['srsearch']
                print(f"Using simple_example.py to search wiki for: {query}")
                return wiki_module.search_wiki(query)
            
            elif resource_name == 'wiki_page':
                if 'page' not in params:
                    print("Error: Missing required parameter 'page'")
                    return None
                page = params['page']
                print(f"Using simple_example.py to retrieve wiki page: {page}")
                return wiki_module.get_wiki_page(page)
            
            else:
                print(f"Error: Unsupported resource '{resource_name}' for wiki module")
                return None
        except Exception as e:
            print(f"Error calling simple_example functions: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(description='MCP Client')
    parser.add_argument('--server', default='server.json', help='Path to server configuration file')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # List modules command
    subparsers.add_parser('list-modules', help='List all available modules')
    
    # List resources command
    list_resources_parser = subparsers.add_parser('list-resources', help='List all resources in a module')
    list_resources_parser.add_argument('module', help='Module name')
    
    # Call resource command
    call_parser = subparsers.add_parser('call', help='Call a resource')
    call_parser.add_argument('module', help='Module name')
    call_parser.add_argument('resource', help='Resource name')
    call_parser.add_argument('--params', nargs='+', help='Parameters in the format key=value')
    
    args = parser.parse_args()
    
    # Create client
    client = MCPClient(args.server)
    
    if args.command == 'list-modules':
        client.list_modules()
    elif args.command == 'list-resources':
        client.list_resources(args.module)
    elif args.command == 'call':
        params = {}
        if args.params:
            for param in args.params:
                key, value = param.split('=', 1)
                params[key] = value
        
        result = client.call_resource(args.module, args.resource, params)
        if result:
            print("\nResponse:")
            print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
