"""
Citizen Lookup Example - Demonstrates how to retrieve citizen profiles from RSI website
"""

import requests
import json
import sys
import re
from bs4 import BeautifulSoup

def get_citizen_profile(handle):
    """Retrieve a citizen's profile from the RSI website"""
    print(f"Looking up citizen profile for: {handle}")
    
    url = f"https://robertsspaceindustries.com/en/citizens/{handle}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        profile_data = {}
        
        # Extract avatar image
        avatar_img = soup.select_one(".profile .thumb img")
        if avatar_img and avatar_img.has_attr('src'):
            avatar_src = avatar_img['src']
            # Make sure it's a full URL
            if avatar_src.startswith('/'):
                avatar_src = f"https://robertsspaceindustries.com{avatar_src}"
            profile_data["avatar"] = avatar_src
        
        # Extract profile info from the main profile section
        profile_section = soup.select_one(".profile")
        if profile_section:
            # Extract citizen name
            name_elem = profile_section.select_one(".info .entry:nth-child(1) .value")
            if name_elem:
                profile_data["name"] = name_elem.text.strip()
            
            # Extract handle
            handle_elem = profile_section.select_one(".info .entry:nth-child(2) .value")
            if handle_elem:
                profile_data["handle"] = handle_elem.text.strip()
            
            # Extract rank
            rank_elem = profile_section.select_one(".info .entry:nth-child(3) .value")
            if rank_elem:
                profile_data["rank"] = rank_elem.text.strip()
            
            # Extract rank image
            rank_img = profile_section.select_one(".info .entry:nth-child(3) .icon img")
            if rank_img and rank_img.has_attr('src'):
                profile_data["rankImage"] = rank_img['src']
        
        # Extract info from the second left column (enlisted, location, fluency)
        # Note: There are multiple .left-col elements, we need the one that's not inside .profile
        left_cols = soup.select("div.left-col")
        if len(left_cols) > 1:  # The second one contains the enlisted, location, fluency info
            left_col = left_cols[1]  # Use the second left-col div
            entries = left_col.select(".entry")
            
            for entry in entries:
                label = entry.select_one(".label")
                value = entry.select_one(".value")
                
                if label and value:
                    label_text = label.text.strip().lower()
                    value_text = value.text.strip()
                    
                    if "enlisted" in label_text:
                        profile_data["enlisted"] = value_text
                    elif "location" in label_text:
                        profile_data["location"] = re.sub(r'\s+', ' ', value_text)
                    elif "fluency" in label_text:
                        profile_data["fluency"] = value_text
        
        # Extract bio
        bio_elem = soup.select_one(".right-col .entry.bio .value")
        if bio_elem:
            profile_data["bio"] = bio_elem.text.strip()
        
        # Extract main organization info if available
        main_org_elem = soup.select_one(".main-org .info .entry:nth-child(1) .value")
        if main_org_elem:
            profile_data["mainOrg"] = main_org_elem.text.strip()
            
            # Extract SID
            org_sid_elem = soup.select_one(".main-org .info .entry:nth-child(2) .value")
            if org_sid_elem:
                profile_data["mainOrgSID"] = org_sid_elem.text.strip()
            
            # Extract org rank
            org_rank_elem = soup.select_one(".main-org .info .entry:nth-child(3) .value")
            if org_rank_elem:
                profile_data["mainOrgRank"] = org_rank_elem.text.strip()
            
            # Extract org logo
            org_logo = soup.select_one(".main-org .thumb img")
            if org_logo and org_logo.has_attr('src'):
                profile_data["mainOrgLogo"] = org_logo['src']
        
        return profile_data
        
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving citizen profile: {e}")
        return None

def display_profile(profile):
    """Display the citizen profile in a formatted way"""
    if not profile:
        print("No profile data available.")
        return
    
    print("\n" + "="*50)
    print(f"Citizen Profile: {profile.get('name', 'Unknown')}")
    print("="*50)
    
    print(f"Handle: {profile.get('handle', 'Unknown')}")
    if "avatar" in profile:
        print(f"Avatar: {profile['avatar']}")
    print(f"Rank: {profile.get('rank', 'Unknown')}")
    if "rankImage" in profile:
        print(f"Rank Image: {profile['rankImage']}")

    
    print("\nEnlistment & Personal Info:")
    print(f"- Enlisted: {profile.get('enlisted', 'Unknown')}")
    print(f"- Location: {profile.get('location', 'Unknown')}")
    print(f"- Fluency: {profile.get('fluency', 'Unknown')}")
    
    if "mainOrg" in profile:
        print("\nMain Organization:")
        print(f"- Name: {profile.get('mainOrg', 'Unknown')}")
        print(f"- SID: {profile.get('mainOrgSID', 'Unknown')}")
        print(f"- Rank: {profile.get('mainOrgRank', 'Unknown')}")
        if "mainOrgLogo" in profile:
            print(f"- Logo: {profile['mainOrgLogo']}")
    
    if "bio" in profile:
        print("\nBio:")
        # Print the bio with proper formatting
        try:
            bio_text = profile["bio"].strip()
            # Wrap the text to 80 characters per line
            import textwrap
            wrapped_bio = textwrap.fill(bio_text, width=80)
            print(wrapped_bio)
        except Exception as e:
            # Fallback if text wrapping fails
            print(profile["bio"])
    
    print("\n" + "="*50)

def main():
    if len(sys.argv) != 2:
        print("Usage: python citizen_lookup.py <handle>")
        print("Example: python citizen_lookup.py KenzoKai")
        return
    
    handle = sys.argv[1]
    profile = get_citizen_profile(handle)
    
    if profile:
        display_profile(profile)
        
        # Save profile to JSON file
        filename = f"{handle}_profile.json"
        with open(filename, 'w') as f:
            json.dump(profile, f, indent=2)
        print(f"Profile saved to {filename}")

if __name__ == "__main__":
    main()
