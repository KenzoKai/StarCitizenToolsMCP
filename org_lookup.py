"""
Organization Lookup Example - Demonstrates how to retrieve organization information from RSI website
"""

import requests
import json
import sys
import re
import textwrap
from bs4 import BeautifulSoup

def get_organization_profile(sid):
    """Retrieve an organization's profile from the RSI website"""
    print(f"Looking up organization profile for: {sid}")
    
    url = f"https://robertsspaceindustries.com/en/orgs/{sid}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        org_data = {}
        
        # Extract organization name and SID
        name_elem = soup.select_one("#organization h1")
        if name_elem:
            full_name = name_elem.text.strip()
            org_data["name"] = re.sub(r'\s*/\s*.*$', '', full_name)  # Remove SID part
            
            # Extract SID
            sid_elem = name_elem.select_one(".symbol")
            if sid_elem:
                org_data["sid"] = sid_elem.text.strip()
        
        # Extract logo
        logo_elem = soup.select_one(".logo img")
        if logo_elem and logo_elem.has_attr('src'):
            logo_src = logo_elem['src']
            # Make sure it's a full URL
            if logo_src.startswith('/'):
                logo_src = f"https://robertsspaceindustries.com{logo_src}"
            org_data["logo"] = logo_src
        
        # Extract banner
        banner_elem = soup.select_one(".banner img")
        if banner_elem and banner_elem.has_attr('src'):
            banner_src = banner_elem['src']
            # Make sure it's a full URL
            if banner_src.startswith('/'):
                banner_src = f"https://robertsspaceindustries.com{banner_src}"
            org_data["banner"] = banner_src
        
        # Extract background image
        bg_elem = soup.select_one("#post-background")
        if bg_elem and bg_elem.has_attr('style'):
            style = bg_elem['style']
            bg_match = re.search(r"url\('([^']+)'\)", style)
            if bg_match:
                bg_src = bg_match.group(1)
                # Make sure it's a full URL
                if bg_src.startswith('/'):
                    bg_src = f"https://robertsspaceindustries.com{bg_src}"
                org_data["background"] = bg_src
        
        # Extract member count
        count_elem = soup.select_one(".logo .count")
        if count_elem:
            org_data["memberCount"] = count_elem.text.strip()
        
        # Extract organization model
        model_elem = soup.select_one(".tags .model")
        if model_elem:
            org_data["model"] = model_elem.text.strip()
        
        # Extract commitment level
        commitment_elem = soup.select_one(".tags .commitment")
        if commitment_elem:
            org_data["commitment"] = commitment_elem.text.strip()
        
        # Extract roleplay status
        roleplay_elem = soup.select_one(".tags .roleplay")
        if roleplay_elem:
            org_data["roleplay"] = roleplay_elem.text.strip()
        
        # Extract primary focus
        primary_focus_elem = soup.select_one(".focus .primary img")
        if primary_focus_elem and primary_focus_elem.has_attr('alt'):
            org_data["primaryFocus"] = primary_focus_elem['alt']
        
        # Extract secondary focus
        secondary_focus_elem = soup.select_one(".focus .secondary img")
        if secondary_focus_elem and secondary_focus_elem.has_attr('alt'):
            org_data["secondaryFocus"] = secondary_focus_elem['alt']
        
        # Extract short description
        desc_elem = soup.select_one(".join-us .body")
        if desc_elem:
            org_data["description"] = desc_elem.text.strip()
        
        # Extract history
        history_elem = soup.select_one("#tab-history .markitup-text")
        if history_elem:
            org_data["history"] = history_elem.text.strip()
        
        # Extract manifesto
        manifesto_elem = soup.select_one("#tab-manifesto .markitup-text")
        if manifesto_elem:
            org_data["manifesto"] = manifesto_elem.text.strip()
        
        # Extract charter
        charter_elem = soup.select_one("#tab-charter .markitup-text")
        if charter_elem:
            org_data["charter"] = charter_elem.text.strip()
        
        # Extract cover image
        cover_elem = soup.select_one(".content.block.cover img")
        if cover_elem and cover_elem.has_attr('src'):
            cover_src = cover_elem['src']
            # Make sure it's a full URL
            if cover_src.startswith('/'):
                cover_src = f"https://robertsspaceindustries.com{cover_src}"
            org_data["cover"] = cover_src
        
        return org_data
        
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving organization profile: {e}")
        return None

def get_organization_members(sid):
    """Retrieve an organization's members list from the RSI website"""
    print(f"Looking up members for organization: {sid}")
    
    url = f"https://robertsspaceindustries.com/en/orgs/{sid}/members"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        members = []
        
        # Find all member items
        member_items = soup.select(".member-item")
        for item in member_items:
            member_data = {}
            
            # Extract handle - try multiple possible selectors
            handle_elem = None
            
            # Try different possible selectors for the handle
            handle_selectors = [
                ".nick .value",                # Original selector
                ".member-info .nick",          # Alternative selector
                ".member-info a",              # Direct link to member profile
                "a.membercard-profile",        # Another possible link format
                ".name",                       # Simple name class
                "h3"                           # Generic heading that might contain the name
            ]
            
            for selector in handle_selectors:
                handle_elem = item.select_one(selector)
                if handle_elem and handle_elem.text.strip():
                    member_data["handle"] = handle_elem.text.strip()
                    break
            
            # If we still don't have a handle, try to extract it from href attribute
            if "handle" not in member_data:
                link_elem = item.select_one("a[href*='/citizens/']")
                if link_elem and link_elem.has_attr('href'):
                    # Extract handle from URL path
                    href = link_elem['href']
                    handle_match = re.search(r'/citizens/([^/]+)', href)
                    if handle_match:
                        member_data["handle"] = handle_match.group(1)
            
            # Extract rank
            rank_elem = item.select_one(".rank .value") or item.select_one(".member-rank")
            if rank_elem:
                member_data["rank"] = rank_elem.text.strip()
            
            # Extract stars (rank level)
            stars_elem = item.select_one(".stars")
            if stars_elem and stars_elem.has_attr('class'):
                stars_class = ' '.join(stars_elem['class'])
                stars_match = re.search(r'stars-(\d+)', stars_class)
                if stars_match:
                    member_data["stars"] = int(stars_match.group(1))
            
            # Extract avatar
            avatar_elem = item.select_one(".thumb img") or item.select_one(".member-thumb img")
            if avatar_elem and avatar_elem.has_attr('src'):
                avatar_src = avatar_elem['src']
                # Make sure it's a full URL
                if avatar_src.startswith('/'):
                    avatar_src = f"https://robertsspaceindustries.com{avatar_src}"
                member_data["avatar"] = avatar_src
            
            members.append(member_data)
        
        return members
        
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving organization members: {e}")
        return None

def display_organization(org_data):
    """Display the organization profile in a formatted way"""
    if not org_data:
        print("No organization data available.")
        return
    
    print("\n" + "="*80)
    print(f"Organization: {org_data.get('name', 'Unknown')}")
    print("="*80)
    
    print(f"SID: {org_data.get('sid', 'Unknown')}")
    print(f"Member Count: {org_data.get('memberCount', 'Unknown')}")
    
    if "model" in org_data or "commitment" in org_data or "roleplay" in org_data:
        print("\nOrganization Type:")
        if "model" in org_data:
            print(f"- Model: {org_data['model']}")
        if "commitment" in org_data:
            print(f"- Commitment: {org_data['commitment']}")
        if "roleplay" in org_data:
            print(f"- Roleplay: {org_data['roleplay']}")
    
    if "primaryFocus" in org_data or "secondaryFocus" in org_data:
        print("\nFocus Areas:")
        if "primaryFocus" in org_data:
            print(f"- Primary: {org_data['primaryFocus']}")
        if "secondaryFocus" in org_data:
            print(f"- Secondary: {org_data['secondaryFocus']}")
    
    if "logo" in org_data or "banner" in org_data or "background" in org_data or "cover" in org_data:
        print("\nMedia:")
        if "logo" in org_data:
            print(f"- Logo: {org_data['logo']}")
        if "banner" in org_data:
            print(f"- Banner: {org_data['banner']}")
        if "background" in org_data:
            print(f"- Background: {org_data['background']}")
        if "cover" in org_data:
            print(f"- Cover: {org_data['cover']}")
    
    if "description" in org_data:
        print("\nDescription:")
        try:
            desc_text = org_data["description"].strip()
            wrapped_desc = textwrap.fill(desc_text, width=80)
            print(wrapped_desc)
        except Exception:
            print(org_data["description"])
    
    # Don't display full history, manifesto, and charter in the console output
    # as they can be very long. Just indicate if they're available.
    print("\nDetailed Information Available:")
    print(f"- History: {'Available' if 'history' in org_data else 'Not available'}")
    print(f"- Manifesto: {'Available' if 'manifesto' in org_data else 'Not available'}")
    print(f"- Charter: {'Available' if 'charter' in org_data else 'Not available'}")
    
    print("\n" + "="*80)

def display_members(members):
    """Display the organization members in a formatted way"""
    if not members:
        print("No member data available.")
        return
    
    print("\n" + "="*80)
    print(f"Organization Members ({len(members)})")
    print("="*80)
    
    for i, member in enumerate(members, 1):
        print(f"{i}. {member.get('handle', 'Unknown')}")
        if "rank" in member:
            stars = "★" * member.get('stars', 0)
            print(f"   Rank: {member['rank']} {stars}")
        if "avatar" in member:
            print(f"   Avatar: {member['avatar']}")
        print()
    
    print("="*80)

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Profile: python org_lookup.py <org_sid>")
        print("  Members: python org_lookup.py <org_sid> members")
        print("Example: python org_lookup.py HMBCREW")
        return
    
    sid = sys.argv[1]
    
    if len(sys.argv) > 2 and sys.argv[2].lower() == "members":
        # Get and display members
        members = get_organization_members(sid)
        if members:
            display_members(members)
            
            # Save members to JSON file
            filename = f"{sid}_members.json"
            with open(filename, 'w') as f:
                json.dump(members, f, indent=2)
            print(f"Members saved to {filename}")
    else:
        # Get and display organization profile
        org_data = get_organization_profile(sid)
        if org_data:
            display_organization(org_data)
            
            # Save profile to JSON file
            filename = f"{sid}_profile.json"
            with open(filename, 'w') as f:
                json.dump(org_data, f, indent=2)
            print(f"Profile saved to {filename}")

if __name__ == "__main__":
    main()
