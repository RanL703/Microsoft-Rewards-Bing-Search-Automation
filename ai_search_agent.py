#!/usr/bin/env python3
"""
Microsoft Rewards Agent - AI-Powered Search Automation
Combines Microsoft Edge automation with Google's Gemini AI for intelligent search automation.
"""

import os
import sys
import time
import random
import logging
import csv
from datetime import datetime
from typing import List, Optional, Tuple
import traceback

# Third-party imports
try:
    from selenium import webdriver
    from selenium.webdriver.edge.service import Service
    from selenium.webdriver.edge.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.common.exceptions import TimeoutException
    from webdriver_manager.microsoft import EdgeChromiumDriverManager
    
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    
    from colorama import init, Fore
    from fake_useragent import UserAgent
    from dotenv import load_dotenv
    
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Please install requirements: pip install -r requirements.txt")
    sys.exit(1)

# Initialize colorama for Windows
init(autoreset=True)

class AISearchAgent:
    """AI-powered search automation agent using Microsoft Edge and Google Gemini."""
    
    def __init__(self, config_file: str = ".env"):
        """Initialize the search agent with configuration."""
        self.load_config(config_file)
        self.setup_logging()
        self.driver: Optional[webdriver.Edge] = None
        self.ai_client = None
        self.search_history: List[str] = []
        self.user_agent = UserAgent()
        self.session_start_time = datetime.now()
        
        # Search parameters
        self.search_params = {
            "categories": [
                "technology", "current events", "pop culture", "science",
                "entertainment", "sports", "health", "travel", "food",
                "history", "nature", "space", "education", "business"
            ],
            "query_types": [
                "question", "fact", "news search", "definition",
                "how to", "what is", "why does", "comparison"
            ],
            "complexity_levels": ["simple", "detailed", "comprehensive"]
        }
        
        # Initialize components
        self._initialize_gemini()
        self._initialize_browser()
        self._setup_csv_logging()

    def load_config(self, config_file: str) -> None:
        """Load configuration from environment file."""
        load_dotenv(config_file)
        
        self.config = {
            'gemini_api_key': os.getenv('GEMINI_API_KEY'),
            'edge_driver_path': os.getenv('EDGE_DRIVER_PATH', 'auto'),
            'debug_mode': os.getenv('DEBUG_MODE', 'False').lower() == 'true',
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'max_cycles': int(os.getenv('MAX_SEARCH_CYCLES', '10')),
            'min_delay': int(os.getenv('MIN_DELAY', '5')),
            'max_delay': int(os.getenv('MAX_DELAY', '45'))
        }
        
        if not self.config['gemini_api_key'] or self.config['gemini_api_key'] == 'your_gemini_api_key_here':
            raise ValueError("GEMINI_API_KEY not set in .env file")

    def setup_logging(self) -> None:
        """Setup logging configuration."""
        log_level = getattr(logging, self.config['log_level'].upper())
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('search_agent.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _initialize_gemini(self) -> None:
        """Initialize Google Gemini AI client."""
        try:
            genai.configure(api_key=self.config['gemini_api_key'])
            
            # Configure safety settings
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
            
            # Initialize the model
            self.ai_client = genai.GenerativeModel(
                model_name="gemini-2.0-flash-lite",
                safety_settings=safety_settings
            )
            
            self.logger.info(f"{Fore.GREEN}[OK] Gemini AI initialized successfully")
            
        except Exception as e:
            self.logger.error(f"{Fore.RED}[FAIL] Failed to initialize Gemini AI: {e}")
            raise

    def _initialize_browser(self) -> None:
        """Initialize Microsoft Edge browser with optimal settings."""
        try:
            # Edge options for stealth and performance
            edge_options = Options()
            edge_options.add_argument("--disable-blink-features=AutomationControlled")
            edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            edge_options.add_experimental_option('useAutomationExtension', False)
            edge_options.add_argument("--disable-extensions")
            edge_options.add_argument("--no-sandbox")
            edge_options.add_argument("--disable-dev-shm-usage")
            edge_options.add_argument("--disable-gpu")
            edge_options.add_argument("--window-size=800,600")
            edge_options.add_argument(f"--user-agent={self.user_agent.random}")
            
            # Set up driver service
            if self.config['edge_driver_path'] == 'auto':
                service = Service(EdgeChromiumDriverManager().install())
            else:
                service = Service(self.config['edge_driver_path'])
            
            # Initialize driver
            self.driver = webdriver.Edge(service=service, options=edge_options)
            
            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.logger.info(f"{Fore.GREEN}[OK] Microsoft Edge initialized successfully")
            
        except Exception as e:
            self.logger.error(f"{Fore.RED}[FAIL] Failed to initialize Edge browser: {e}")
            raise

    def _setup_csv_logging(self) -> None:
        """Setup CSV logging for search results."""
        self.csv_filename = f"search_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(self.csv_filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                'timestamp', 'generated_query', 'search_url', 
                'response_status', 'execution_time', 'category', 'query_type'
            ])
        
        self.logger.info(f"{Fore.CYAN}[LOG] CSV logging initialized: {self.csv_filename}")

    def generate_search_query(self) -> Tuple[str, str, str]:
        """Generate an AI-powered search query using Gemini."""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # Select random parameters
                category = random.choice(self.search_params["categories"])
                query_type = random.choice(self.search_params["query_types"])
                complexity = random.choice(self.search_params["complexity_levels"])
                
                # Create context-aware prompt
                history_context = ""
                if self.search_history:
                    recent_searches = self.search_history[-3:]  # Last 3 searches
                    history_context = f"Recent search topics: {', '.join(recent_searches)}. "
                
                prompt = f"""
                {history_context}Generate a {complexity} {query_type} about {category} that would be suitable for a Bing search.
                
                Requirements:
                - Make it naturally human-like and interesting
                - 3-15 words maximum
                - Avoid repetition of recent topics
                - Be specific enough to get good search results
                - Safe for general audiences
                
                Category: {category}
                Type: {query_type}
                Complexity: {complexity}
                
                Respond with ONLY the search query, nothing else.
                """
                
                response = self.ai_client.generate_content(prompt)
                query = response.text.strip().strip('"').strip("'")
                  # Validate query
                if self._validate_query(query):
                    self.search_history.append(query)
                    if len(self.search_history) > 20:  # Keep only recent history
                        self.search_history = self.search_history[-20:]
                    
                    self.logger.info(f"{Fore.YELLOW}[AI] Generated query: {query}")
                    return query, category, query_type
                
            except Exception as e:
                self.logger.warning(f"{Fore.YELLOW}[WARNING] Query generation attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        # Fallback query
        fallback_query = f"what is {random.choice(self.search_params['categories'])}"
        self.logger.warning(f"{Fore.YELLOW}[WARNING] Using fallback query: {fallback_query}")
        return fallback_query, "general", "fallback"

    def _validate_query(self, query: str) -> bool:
        """Validate generated search query."""
        if not query or len(query) < 3:
            return False
        
        if len(query) > 100:  # Too long
            return False
            
        # Check for problematic content
        forbidden_terms = ['explicit', 'illegal', 'hack', 'crack']
        if any(term in query.lower() for term in forbidden_terms):
            return False
            
        return True

    def execute_search(self, query: str) -> Tuple[bool, str, float]:
        """Execute search on Bing with human-like behavior."""
        start_time = time.time()
        
        try:
            # Navigate to Bing
            self.logger.info(f"{Fore.BLUE}[WEB] Navigating to Bing...")
            self.driver.get("https://www.bing.com")
            
            # Wait for page to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "sb_form_q"))
            )
            
            # Find search box
            search_box = self.driver.find_element(By.ID, "sb_form_q")
            
            # Clear any existing text
            search_box.clear()
            
            # Simulate human-like typing
            self._human_like_typing(search_box, query)
            
            # Random delay before submitting
            time.sleep(random.uniform(0.5, 2.0))
            
            # Submit search (randomly choose between Enter key or clicking search button)
            if random.choice([True, False]):
                search_box.send_keys(Keys.RETURN)
            else:
                search_button = self.driver.find_element(By.ID, "search_icon")
                search_button.click()
            
            # Wait for results
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "b_results"))
            )
            
            # Random mouse movement and scrolling
            self._simulate_human_behavior()
            
            execution_time = time.time() - start_time
            current_url = self.driver.current_url
            
            self.logger.info(f"{Fore.GREEN}[OK] Search completed successfully in {execution_time:.2f}s")
            return True, current_url, execution_time
            
        except TimeoutException:
            self.logger.error(f"{Fore.RED}[TIMEOUT] Search timeout for query: {query}")
            return False, "timeout", time.time() - start_time
            
        except Exception as e:
            self.logger.error(f"{Fore.RED}[FAIL] Search failed: {e}")
            return False, f"error: {str(e)}", time.time() - start_time

    def _human_like_typing(self, element, text: str) -> None:
        """Simulate human-like typing with variable speeds and occasional mistakes."""
        for char in text:
            element.send_keys(char)
            # Variable typing speed
            time.sleep(random.uniform(0.05, 0.15))
            
            # Occasional pause (like thinking)
            if random.random() < 0.1:
                time.sleep(random.uniform(0.2, 0.8))

    def _simulate_human_behavior(self) -> None:
        """Simulate human browsing behavior."""
        try:
            actions = ActionChains(self.driver)
            
            # Random mouse movements
            for _ in range(random.randint(2, 5)):
                x_offset = random.randint(-100, 100)
                y_offset = random.randint(-100, 100)
                actions.move_by_offset(x_offset, y_offset)
            
            actions.perform()
            
            # Random scrolling
            scroll_distance = random.randint(300, 800)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
            
            time.sleep(random.uniform(1, 3))
            
            # Scroll back up sometimes
            if random.random() < 0.3:
                self.driver.execute_script(f"window.scrollBy(0, -{scroll_distance // 2});")
            
        except Exception as e:
            self.logger.debug(f"Human behavior simulation failed: {e}")

    def _log_search_result(self, query: str, category: str, query_type: str, 
                          success: bool, url: str, execution_time: float) -> None:
        """Log search result to CSV file."""
        timestamp = datetime.now().isoformat()
        status = "success" if success else "failed"
        
        with open(self.csv_filename, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                timestamp, query, url, status, f"{execution_time:.2f}",
                category, query_type
            ])

    def _random_delay(self) -> None:
        """Implement random delay between searches."""
        delay = random.randint(self.config['min_delay'], self.config['max_delay'])
        self.logger.info(f"{Fore.CYAN}[WAIT] Waiting {delay} seconds before next search...")
          # Show countdown
        for remaining in range(delay, 0, -1):
            print(f"\r{Fore.CYAN}[WAIT] Next search in: {remaining:2d}s", end="", flush=True)
            time.sleep(1)
        print()  # New line after countdown

    def _recover_from_browser_crash(self) -> bool:
        """Attempt to recover from browser crashes."""
        try:
            self.logger.warning(f"{Fore.YELLOW}[RECOVER] Attempting browser recovery...")
            
            if self.driver:
                try:
                    self.driver.quit()
                except Exception:
                    pass
            
            time.sleep(5)  # Wait before reinitialization
            self._initialize_browser()
            return True
        except Exception as e:
            self.logger.error(f"{Fore.RED}[FAIL] Browser recovery failed: {e}")
            return False

    def run(self, cycles: Optional[int] = None) -> None:
        """Main execution loop for the search agent."""
        if cycles is None:
            cycles = self.config['max_cycles']
        
        self.logger.info(f"{Fore.MAGENTA}[START] Starting AI Search Agent - {cycles} cycles planned")
        print(f"\n{Fore.MAGENTA}{'='*60}")
        print(f"{Fore.MAGENTA}[AGENT] Microsoft Rewards Agent - AI Search Automation")
        print(f"{Fore.MAGENTA}{'='*60}")
        print(f"{Fore.CYAN}[INFO] Cycles: {cycles}")
        print(f"{Fore.CYAN}[TIME] Delay Range: {self.config['min_delay']}-{self.config['max_delay']}s")
        print(f"{Fore.CYAN}[LOG] Log File: {self.csv_filename}")
        print(f"{Fore.MAGENTA}{'='*60}\n")
        
        successful_searches = 0
        failed_searches = 0
        
        for cycle in range(1, cycles + 1):
            try:
                print(f"\n{Fore.MAGENTA}[CYCLE] Cycle {cycle}/{cycles}")
                print(f"{Fore.BLUE}{'─'*40}")
                
                # Generate AI query
                query, category, query_type = self.generate_search_query()
                
                # Execute search
                success, url, execution_time = self.execute_search(query)
                  # Log result
                self._log_search_result(query, category, query_type, success, url, execution_time)
                
                if success:
                    successful_searches += 1
                    print(f"{Fore.GREEN}[SUCCESS] Success: {query}")
                else:
                    failed_searches += 1
                    print(f"{Fore.RED}[FAIL] Failed: {query}")
                
                # Progress summary
                print(f"{Fore.CYAN}[PROGRESS] Progress: {successful_searches}/{cycle} successful")
                
                # Random delay before next cycle (except for the last cycle)
                if cycle < cycles:
                    self._random_delay()
                
            except KeyboardInterrupt:
                self.logger.info(f"{Fore.YELLOW}[WARNING] User interrupted execution")
                break
                
            except Exception as e:
                self.logger.error(f"{Fore.RED}[FAIL] Cycle {cycle} failed: {e}")
                failed_searches += 1
                
                # Attempt browser recovery
                if "driver" in str(e).lower() or "session" in str(e).lower():
                    if not self._recover_from_browser_crash():
                        self.logger.error(f"{Fore.RED}[FAIL] Cannot continue - browser recovery failed")
                        break
        
        # Final summary
        self._print_final_summary(successful_searches, failed_searches, cycles)

    def _print_final_summary(self, successful: int, failed: int, total_planned: int) -> None:
        """Print execution summary."""
        total_executed = successful + failed
        success_rate = (successful / total_executed * 100) if total_executed > 0 else 0
        session_duration = datetime.now() - self.session_start_time
        
        print(f"\n{Fore.MAGENTA}{'='*60}")
        print(f"{Fore.MAGENTA}[SUMMARY] EXECUTION SUMMARY")
        print(f"{Fore.MAGENTA}{'='*60}")
        print(f"{Fore.GREEN}[SUCCESS] Successful searches: {successful}")
        print(f"{Fore.RED}[FAIL] Failed searches: {failed}")
        print(f"{Fore.CYAN}[STATS] Success rate: {success_rate:.1f}%")
        print(f"{Fore.CYAN}[TIME] Session duration: {session_duration}")
        print(f"{Fore.CYAN}[LOG] Results logged to: {self.csv_filename}")
        print(f"{Fore.MAGENTA}{'='*60}\n")

    def cleanup(self) -> None:
        """Clean up resources."""
        try:
            if self.driver:
                self.driver.quit()
                self.logger.info(f"{Fore.GREEN}[OK] Browser cleanup completed")
        except Exception as e:
            self.logger.warning(f"{Fore.YELLOW}[WARNING] Cleanup warning: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()


def main():
    """Main entry point."""
    try:
        with AISearchAgent() as agent:
            agent.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[WARNING] Program interrupted by user")
    except Exception as e:
        print(f"\n{Fore.RED}[FATAL] Fatal error: {e}")
        if agent.config.get('debug_mode'):
            traceback.print_exc()
    finally:
        print(f"\n{Fore.CYAN}[EXIT] AI Search Agent terminated")


if __name__ == "__main__":
    main()
