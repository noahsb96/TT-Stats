from playwright.sync_api import sync_playwright
import time
from typing import Dict, List

class SofaScoreScraper:
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
    
    def __enter__(self):
        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=False,
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
    
    def __exit__(self, *args):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def get_live_matches(self) -> List[Dict]:
        self.page.goto("https://www.sofascore.com/table-tennis", wait_until='domcontentloaded', timeout=60000)
        print("Page loaded")
        time.sleep(5)
        
        print("Checking for Live button")
        live_button = self.page.query_selector('button.bg_status\\.liveHighlight')
        if live_button:
            print("Live button found (likely already active)")
        else:
            print("Live button not found")
        
        print("Looking for live matches")
        time.sleep(3)
        
        matches = []
        match_links = self.page.query_selector_all('a[href*="/table-tennis/match/"][data-id]')
        
        live_match_links = []
        for link in match_links:
            parent_panel = link.evaluate('(element) => element.closest("#tabpanel-h2h")')
            if not parent_panel:
                live_match_links.append(link)
        
        print(f"Found {len(live_match_links)} live match links")
        
        for i, link in enumerate(live_match_links[:5]):
            try:
                player_names = link.query_selector_all('bdi.textStyle_body\\.medium.trunc_true')
                
                if len(player_names) >= 2:
                    text = f"{player_names[0].text_content().strip()} vs {player_names[1].text_content().strip()}"
                else:
                    text = "Could not extract player names"
                
                matches.append({
                    'index': i,
                    'text': text[:100],
                    'element': link
                })
            except Exception as e:
                print(f"Error reading element {i}: {e}")
        
        return matches
    
    def click_first_match(self) -> bool:
        try:
            print("Attempting to click first match")
            
            match_links = self.page.query_selector_all('a[href*="/table-tennis/match/"][data-id]')
            
            live_match_links = []
            for link in match_links:
                parent_panel = link.evaluate('(element) => element.closest("#tabpanel-h2h")')
                if not parent_panel:
                    live_match_links.append(link)
            
            if live_match_links and len(live_match_links) > 0:
                print(f"Found {len(live_match_links)} live matches, clicking first one")
                live_match_links[0].click()
                time.sleep(2)
                return True
            
            print("Could not find any live match links")
            return False
            
        except Exception as e:
            print(f"Error clicking match: {e}")
            return False
    
    def get_current_match_details(self) -> Dict:
        try:
            print("Extracting match details")
            time.sleep(2)
            
            details = {
                'player_1': None,
                'player_2': None,
                'player_1_sets': [],
                'player_2_sets': [],
                'sets_played': 0
            }
            
            player_containers = self.page.query_selector_all('div[style*="position: absolute; bottom: -22px"]')
            
            if len(player_containers) >= 2:
                details['player_1'] = player_containers[0].query_selector('bdi').inner_text().strip()
                details['player_2'] = player_containers[1].query_selector('bdi').inner_text().strip()
                print(f"Players: {details['player_1']} vs {details['player_2']}")
            else:
                all_player_bdi = self.page.query_selector_all('bdi.trunc_true')
                player_candidates = []
                for bdi in all_player_bdi:
                    text = bdi.inner_text().strip()
                    classes = bdi.get_attribute('class')
                    if ('textStyle_body.medium' in classes or 'textStyle_display.medium' in classes) and text:
                        player_candidates.append(text)
                
                if len(player_candidates) >= 2:
                    details['player_1'] = player_candidates[0]
                    details['player_2'] = player_candidates[1]
                    print(f"Players: {details['player_1']} vs {details['player_2']}")
                else:
                    print(f"Found {len(player_candidates)} player candidates (expected 2)")
            
            score_table = self.page.query_selector('table.tbl_fixed.w_100\\%')
            
            if score_table:
                tbody_rows = score_table.query_selector_all('tbody tr')
                
                if len(tbody_rows) >= 2:
                    p1_cells = tbody_rows[0].query_selector_all('td span.textStyle_table\\.medium')
                    details['player_1_sets'] = [cell.inner_text().strip() for cell in p1_cells if cell.inner_text().strip()]
                    
                    p2_cells = tbody_rows[1].query_selector_all('td span.textStyle_table\\.medium')
                    details['player_2_sets'] = [cell.inner_text().strip() for cell in p2_cells if cell.inner_text().strip()]
                    
                    details['sets_played'] = len(details['player_1_sets'])
                    
                    print(f"Scores: P1: {details['player_1_sets']}, P2: {details['player_2_sets']}")
                else:
                    print(f"Found score table but only {len(tbody_rows)} rows (need 2)")
            else:
                print("Could not find score table - may need to wait longer or match hasn't loaded")
            
            return details
            
        except Exception as e:
            print(f"Error extracting match details: {e}")
            return {}
    
    def click_matches_tab(self) -> bool:
        try:
            print("Looking for 'Matches' tab")
            
            matches_tab = self.page.query_selector('button[data-testid="tab-matches"]')
            if matches_tab:
                print("Found 'Matches' tab, clicking")
                matches_tab.click()
                time.sleep(2)
                return True
            else:
                print("Could not find 'Matches' tab")
                return False
                
        except Exception as e:
            print(f"Error clicking Matches tab: {e}")
            return False
    
    def get_h2h_matches(self) -> List[Dict]:
        try:
            print("Extracting H2H match history")
            time.sleep(3)
            
            h2h_panel = self.page.query_selector('div#tabpanel-h2h')
            if not h2h_panel:
                print("Could not find H2H tabpanel")
                return []
            
            print("Found H2H tabpanel")
            
            h2h_matches = []
            match_links = h2h_panel.query_selector_all('a[href*="/table-tennis/match/"][data-id]')
            
            print(f"Found {len(match_links)} match links in H2H panel")
            
            for i, link in enumerate(match_links[:10]):
                try:
                    player_bdi_elements = link.query_selector_all('bdi.textStyle_body\\.medium.trunc_true')
                    score_boxes = link.query_selector_all('div.Flex.jTiCHC.MkeW span.currentScore')
                    match_id = link.get_attribute('data-id')
                    
                    match_data = {
                        'index': i,
                        'match_id': match_id,
                        'player_1': player_bdi_elements[0].text_content().strip() if len(player_bdi_elements) > 0 else 'N/A',
                        'player_2': player_bdi_elements[1].text_content().strip() if len(player_bdi_elements) > 1 else 'N/A',
                        'player_1_score': score_boxes[0].text_content().strip() if len(score_boxes) > 0 else 'N/A',
                        'player_2_score': score_boxes[1].text_content().strip() if len(score_boxes) > 1 else 'N/A'
                    }
                    
                    h2h_matches.append(match_data)
                    
                except Exception as e:
                    print(f"Error reading H2H match {i}: {e}")
            
            return h2h_matches
            
        except Exception as e:
            print(f"Error getting H2H matches: {e}")
            return []
    
    def click_h2h_match(self, match_index: int = 0) -> bool:
        try:
            print(f"Clicking H2H match at index {match_index}")
            
            h2h_panel = self.page.query_selector('div#tabpanel-h2h')
            if not h2h_panel:
                print("Could not find H2H tabpanel")
                return False
            
            match_links = h2h_panel.query_selector_all('a[href*="/table-tennis/match/"][data-id]')
            
            print(f"Found {len(match_links)} H2H matches to choose from")
            
            if match_links and len(match_links) > match_index:
                match_links[match_index].click()
                print(f"Clicked H2H match {match_index}")
                time.sleep(3)
                return True
            else:
                print(f"Could not find H2H match at index {match_index}")
                return False
                
        except Exception as e:
            print(f"Error clicking H2H match: {e}")
            return False

def test_sofascore_scraper():
    print("Testing SofaScore Scraper")
    print("=" * 60)
    
    try:
        with SofaScoreScraper() as scraper:
            print("\nStep 1: Getting live matches")
            live_matches = scraper.get_live_matches()
            
            if live_matches:
                print(f"Found {len(live_matches)} live matches")
                for match in live_matches[:3]:
                    print(f"   - {match['text']}")
            
            print("\nStep 2: Clicking first match")
            if scraper.click_first_match():
                print("Match panel opened")
                
                print("\nStep 3: Extracting match details")
                match_details = scraper.get_current_match_details()
                if match_details:
                    print(f"Match details extracted")
                    print(f"   Players: {match_details.get('player_1')} vs {match_details.get('player_2')}")
                    print(f"   P1 Sets: {match_details.get('player_1_sets')}")
                    print(f"   P2 Sets: {match_details.get('player_2_sets')}")
                    print(f"   Total Sets: {match_details.get('sets_played')}")
                
                print("\nStep 4: Opening H2H matches")
                if scraper.click_matches_tab():
                    print("Matches tab opened")
                    
                    print("\nStep 5: Getting H2H match history")
                    h2h_matches = scraper.get_h2h_matches()
                    if h2h_matches:
                        print(f"Found {len(h2h_matches)} H2H matches")
                        for h2h in h2h_matches[:3]:
                            print(f"   - Match {h2h['match_id']}: {h2h['player_1']} ({h2h['player_1_score']}) vs {h2h['player_2']} ({h2h['player_2_score']})")
                        
                        print("\nStep 6: Clicking second H2H match (index 1) for historical data")
                        if scraper.click_h2h_match(1):
                            h2h_details = scraper.get_current_match_details()
                            if h2h_details:
                                print(f"H2H match details:")
                                print(f"   Players: {h2h_details.get('player_1')} vs {h2h_details.get('player_2')}")
                                print(f"   Detailed scores: P1: {h2h_details.get('player_1_sets')}, P2: {h2h_details.get('player_2_sets')}")
            
            print("\nTest complete! Browser will close in 5 seconds")
            time.sleep(5)
                
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sofascore_scraper()