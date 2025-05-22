import json
import requests
import argparse
import os
import sys
from requests.exceptions import RequestException, Timeout, ConnectionError

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
        
        # Build the URL
        base_url = module.get('baseUrl', '')
        path = resource.get('path', '/')
        url = f"{base_url}{path}"
        
        # Prepare parameters
        request_params = {}
        for param in resource.get('parameters', []):
            param_name = param['name']
            if param_name in params:
                request_params[param_name] = params[param_name]
            elif 'default' in param:
                request_params[param_name] = param['default']
            elif param.get('required', False):
                print(f"Missing required parameter: {param_name}")
                return None
        
        # Make the request
        method = resource.get('method', 'GET')
        print(f"Making {method} request to {url} with parameters: {request_params}")
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, params=request_params, timeout=10)
            elif method.upper() == 'POST':
                response = requests.post(url, json=request_params, timeout=10)
            else:
                print(f"Unsupported method: {method}")
                return None
            
            response.raise_for_status()
            return response.json()
        except Timeout:
            print("Error: Request timed out. The server took too long to respond.")
            return None
        except ConnectionError:
            print("Error: Connection failed. Please check your internet connection.")
            return None
        except RequestException as e:
            print(f"Error making request: {e}")
            return None
        except json.JSONDecodeError:
            print("Error: Could not parse the response as JSON.")
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
