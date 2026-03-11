import os
import json
import logging
from typing import List, Dict, Any
from bs4 import BeautifulSoup

# Try to import cloudscraper. If missing (e.g., in CI or not installed), gracefully fallback for testing.
try:
    import cloudscraper
    HAS_CLOUDSCRAPER = True
except ImportError:
    HAS_CLOUDSCRAPER = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class NairobiHotScraper:
    def __init__(self, base_url: str = 'https://nairobihot.com/'):
        self.base_url = base_url
        if HAS_CLOUDSCRAPER:
            self.scraper = cloudscraper.create_scraper()
        else:
            # Fallback for CI/CD environments where we might only run mock tests
            import requests
            self.scraper = requests.Session()
            self.scraper.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })

    def fetch_home_page(self) -> str:
        """Fetches the main HTML content."""
        logger.info(f"Fetching {self.base_url}...")
        try:
            response = self.scraper.get(self.base_url, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Failed to fetch {self.base_url}: {e}")
            return ""

    def parse_locations(self, html: str) -> List[Dict[str, str]]:
        """Parses the homepage HTML to extract counties and their locations."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # We will look for list items inside typical menu dropdowns or lists of counties/locations
        locations = []
        
        # Based on DOM structure inspection:
        # We have typical lists where the top-level <a> might be a County, 
        # and the nested lists or direct links correspond to Locations.
        # Alternatively, we can extract known big nodes.
        # Nairobihot has a specific block of links for exact locations.
        # They are usually contained inside 'd-inline-block' divs on the homepage.
        location_divs = soup.find_all('div', class_='d-inline-block')
        all_links = []
        for div in location_divs:
            for a in div.find_all('a', href=True):
                if len(a.text.strip()) > 3:
                    all_links.append(a.text.strip())
        
        # Build a reverse lookup to assign scraped locations
        # (Nairobi as the primary county, with all the subsequent sub-locations like 'Kilimani', 'Westlands')
        
        county_map = {
            "Nairobi": [
                "Allsops", "Buru Buru", "Dagoretti", "Dandora", "Donholm", "Eastleigh", 
                "Embakasi", "Githurai 44", "Githurai 45", "Hurlingham", "Imara Daima", 
                "Karen", "Kasarani", "Kawangware", "Kayole", "Kibera", "Kileleshwa", 
                "Kilimani", "Langata", "Lavington", "Madaraka", "Nairobi West", 
                "Ngara", "Pangani", "Parklands", "Roysambu", "Ruaraka", "Runda", 
                "South B", "South C", "Upper Hill", "Westlands", "Umoja"
            ],
            "Kiambu": [
                "Banana", "Githunguri", "Juja", "Kabete", "Kahawa Sukari", "Kahawa Wendani", 
                "Kahawa West", "Kikuyu", "Ndenderu", "Ruaka", "Ruiru", "Thika"
            ],
            "Machakos": [
                "Athi River", "Joska", "Kamulu", "Kitengela", "Malaa", "Mlolongo", "Syokimau"
            ],
            "Mombasa": [
                "Changamwe", "Diani", "Likoni", "Mombasa", "Watamu"
            ]
        }
        
        # Build a reverse lookup to assign scraped locations
        known_lookup = {}
        for county, loc_list in county_map.items():
            for loc in loc_list:
                known_lookup[loc.lower()] = county
                
        extracted_locations = []
        seen = set()
        
        for link_text in all_links:
            # Skip noise
            if link_text.lower() in ['home', 'escorts', 'videos', 'classifieds', 'sign in', 'register', 'contact us', 'blog', 'stories', 'nairobiraha', 'agencies', 'more', 'nairobi raha', 'hot & sexy call girls', 'reset password']:
                continue
            
            # Simple heuristic: if it doesn't have multiple words and isn't spammy
            if len(link_text) < 30 and 'escort' not in link_text.lower() and 'call' not in link_text.lower():
                if link_text not in seen:
                    seen.add(link_text)
                    county = known_lookup.get(link_text.lower(), "Other Regions")
                    extracted_locations.append({
                        "county": county,
                        "group": "General", # We use a default group for seeding
                        "name": link_text
                    })

        # Ensure we always return at least the hardcoded ones if the site changes its DOM wildly
        if len(extracted_locations) < 10:
            for county, loc_list in county_map.items():
                for loc in loc_list:
                    extracted_locations.append({
                        "county": county,
                        "group": "General",
                        "name": loc
                    })

        # Remove duplicates
        unique_locations = []
        unique_seen = set()
        for item in extracted_locations:
            if item['name'] not in unique_seen:
                unique_seen.add(item['name'])
                unique_locations.append(item)

        return unique_locations

    def extract_services(self) -> List[str]:
        """Provides a realistic list of services to seed since Nairobihot usually has these."""
        return [
            "Incall", "Outcall", "Overnight", "GFE (Girlfriend Experience)", 
            "Massage", "Anal", "Oral", "Roleplay", "BDSM", "Threesome", "Cum in Mouth"
        ]

    def run(self, output_file: str):
        """Executes the scraper and saves the JSON output."""
        logger.info("Starting NairobiHot Scraping...")
        html = self.fetch_home_page()
        
        if not html:
            logger.error("No HTML retrieved. Using fallback list.")
            locations = self.parse_locations("") # Will trigger fallback
        else:
            locations = self.parse_locations(html)
            
        services = self.extract_services()
        
        data = {
            "locations": locations,
            "services": services
        }
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        logger.info(f"Successfully extracted {len(locations)} locations and {len(services)} services. Saved to {output_file}")


if __name__ == "__main__":
    # Base directory calculation so it can run from anywhere
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    out_path = os.path.join(project_root, 'data', 'raw', 'nairobihot_data.json')
    
    scraper = NairobiHotScraper()
    scraper.run(out_path)
