#!/usr/bin/env python3
"""
Playwright-based scraper - uses a real browser to avoid detection
"""
from playwright.sync_api import sync_playwright
import time
from typing import Optional, Dict

class PlaywrightScraper:
    """Use Playwright to scrape with a real browser"""
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
    
    def __enter__(self):
        """Context manager entry"""
        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage'
            ]
        )
        
        self.context = self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
        )
        
        self.page = self.context.new_page()
        
        self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def get_page_content(self, url: str, wait_time: int = 3) -> Optional[str]:
        """Navigate to URL and get page content"""
        try:
            print(f"Navigating to {url}")
            
            response = self.page.goto(url, wait_until='networkidle')
            print(f"Response status: {response.status}")
            
            if response.status >= 400:
                print(f"HTTP Error: {response.status}")
                return None
            
            time.sleep(wait_time)
            
            content = self.page.content()
            print(f"Page content: ({len(content)})")
            
            return content
            
        except Exception as e:
            print(f" Could not get page content: {e}")
            return None
    
    def get_match_data(self, url: str) -> Dict:
        """Get table tennis match data from the page"""
        content = self.get_page_content(url)
        if not content:
            return {}
        
        try:
            matches_found = []
            match_links = self.page.query_selector_all('a[href*="table-tennis/match-"]')
            
            print(f"Found {len(match_links)} matches")
            
            for i, link in enumerate(match_links[:5]):
                try:
                    href = link.get_attribute('href')
                    text = link.inner_text().strip()
                    matches_found.append({
                        'text': text,
                        'href': href,
                        'index': i
                    })
                except Exception as e:
                    print(f"Error with link {i}: {e}")
            
            return {
                'total_content_length': len(content),
                'matches_found': len(matches_found),
                'sample_matches': matches_found
            }
            
        except Exception as e:
            print(f"Can't get match data: {e}")
            return {'error': str(e)}

def test_playwright_scraper():
    """Test Playwright scraping approach"""
    print("Testing Playwright Scraper")
    print("=" * 50)
    
    try:
        with PlaywrightScraper() as scraper:
            print("\nTesting AiScore")
            result = scraper.get_match_data("https://www.aiscore.com/table-tennis")
            
            if result:
                print(f"   - Page content: {result.get('total_content_length', 0):,} characters")
                print(f"   - Matches found: {result.get('matches_found', 0)}")
                
                if result.get('sample_matches'):
                    print(f"   - Sample matches:")
                    for match in result['sample_matches'][:3]:
                        print(f"     • {match['text']}")
                        print(f"       URL: {match['href']}")
                else:
                    print(f"   - No matches found")
            else:
                print("Could not retrieve match data.")
                
    except Exception as e:
        print(f"Playwright test failed: {e}")

if __name__ == "__main__":
    test_playwright_scraper()