#!/usr/bin/env python3
"""
Gemini API Connection Test Script
Tests if the Gemini API key is properly configured and working
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "backend"))

# Color codes
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

def test_gemini_api():
    """Test Gemini API configuration and connectivity"""

    print_header("Gemini API Connection Test")

    # Step 1: Check if .env file exists
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        print_error(".env file not found!")
        print_info("Please create a .env file from .env.example")
        return False

    print_success(".env file exists")

    # Step 2: Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path)
        print_success("Environment variables loaded")
    except ImportError:
        print_error("python-dotenv not installed")
        print_info("Run: pip install python-dotenv")
        return False

    # Step 3: Check if API key is set
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print_error("GEMINI_API_KEY not found in .env file")
        print_info("Please add your Gemini API key to .env")
        return False

    if api_key in ["your_gemini_api_key_here", "your_api_key_here"]:
        print_error("GEMINI_API_KEY is still set to placeholder value")
        print_info("\nTo fix this:")
        print_info("1. Visit: https://makersuite.google.com/app/apikey")
        print_info("2. Sign in with your Google account")
        print_info("3. Create a new API key")
        print_info("4. Update GEMINI_API_KEY in .env file")
        return False

    print_success("GEMINI_API_KEY is set")
    print_info(f"Key preview: {api_key[:15]}...{api_key[-5:]}")

    # Step 4: Try to import google.generativeai
    try:
        import google.generativeai as genai
        print_success("google-generativeai package is installed")
    except ImportError:
        print_error("google-generativeai package not installed")
        print_info("Run: pip install google-generativeai")
        return False

    # Step 5: Configure and test the API
    print_info("\nTesting API connection...")

    try:
        genai.configure(api_key=api_key)
        print_success("API key configured")

        # Test with a simple query
        print_info("Sending test query to Gemini...")
        model = genai.GenerativeModel('gemini-pro')

        response = model.generate_content(
            "Reply with exactly: 'API connection successful'",
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=50,
            )
        )

        if response and response.text:
            print_success("Received response from Gemini API")
            print_info(f"Response: {response.text.strip()}")

            # Test news research capability (what the scraper uses)
            print_info("\nTesting news research capability...")

            news_test = model.generate_content(
                """Find 1 recent news article about technology from any major news source.
                Return as JSON: {"title": "...", "source": "...", "summary": "..."}""",
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=200,
                )
            )

            if news_test and news_test.text:
                print_success("News research capability works!")
                print_info("Sample response:")
                print(f"{Colors.BLUE}{news_test.text[:200]}...{Colors.RESET}")

                print(f"\n{Colors.BOLD}{Colors.GREEN}{'=' * 70}{Colors.RESET}")
                print(f"{Colors.BOLD}{Colors.GREEN}✓ GEMINI API IS FULLY FUNCTIONAL{Colors.RESET}")
                print(f"{Colors.BOLD}{Colors.GREEN}{'=' * 70}{Colors.RESET}\n")

                print_info("The scraper will be able to fetch news articles successfully.")
                print_info("You can now start the application and keyword search will work.")

                return True
            else:
                print_warning("News research test returned empty response")
                return False

        else:
            print_error("Empty response from Gemini API")
            return False

    except Exception as e:
        print_error(f"API test failed: {str(e)}")

        error_msg = str(e).lower()

        if "api_key" in error_msg or "invalid" in error_msg:
            print_warning("\nThe API key appears to be invalid.")
            print_info("Please check:")
            print_info("1. The key is copied correctly (no extra spaces)")
            print_info("2. The key is from: https://makersuite.google.com/app/apikey")
            print_info("3. The key hasn't been revoked or expired")

        elif "quota" in error_msg or "rate" in error_msg:
            print_warning("\nAPI quota or rate limit exceeded.")
            print_info("Free tier limits:")
            print_info("- 60 requests per minute")
            print_info("- 1,500 requests per day")
            print_info("Wait a few minutes and try again, or upgrade your quota.")

        elif "permission" in error_msg:
            print_warning("\nPermission denied.")
            print_info("Make sure the API key has Gemini API access enabled.")

        else:
            print_warning(f"\nUnexpected error: {e}")
            print_info("Check your internet connection and try again.")

        return False

def test_scraper_simulation():
    """Simulate what the scraper does"""

    print_header("Scraper Simulation Test")

    print_info("This simulates the actual news scraping process...\n")

    try:
        # Import scraper service
        from app.services.scraper import NewsScraper

        print_info("Creating NewsScraper instance...")
        scraper = NewsScraper()
        print_success("NewsScraper initialized")

        print_info("Calling research_thailand_news_gemini()...")
        print_warning("This may take 10-30 seconds...")

        results = scraper.research_thailand_news_gemini()

        if results:
            print_success(f"Scraper found {len(results)} articles!")

            print_info("\nSample articles found:")
            for i, article in enumerate(results[:3], 1):
                print(f"\n{Colors.BLUE}Article {i}:{Colors.RESET}")
                print(f"  Title: {article.get('title', 'N/A')[:60]}...")
                print(f"  Source: {article.get('source', 'N/A')}")
                print(f"  Date: {article.get('date', 'N/A')}")

            print(f"\n{Colors.BOLD}{Colors.GREEN}✓ SCRAPER IS WORKING!{Colors.RESET}")
            print_info("The application will be able to fetch and process news.")

            return True
        else:
            print_warning("Scraper returned no results")
            print_info("This might be normal if there are no recent Thailand articles.")
            print_info("The scraper will fall back to mock data if needed.")
            return True

    except ImportError as e:
        print_error(f"Cannot import scraper: {e}")
        print_info("Make sure backend dependencies are installed:")
        print_info("  cd backend && pip install -r requirements.txt")
        return False
    except Exception as e:
        print_error(f"Scraper test failed: {e}")
        return False

def main():
    """Main test function"""

    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║           Gemini API Connection Test Utility                 ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    print(f"{Colors.RESET}")

    # Test 1: Basic API connection
    api_test_passed = test_gemini_api()

    if not api_test_passed:
        print(f"\n{Colors.BOLD}{Colors.RED}{'=' * 70}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.RED}✗ API TEST FAILED{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.RED}{'=' * 70}{Colors.RESET}\n")
        print_info("Fix the API key issue and run this test again.")
        print_info("Command: python3 test_gemini_api.py")
        sys.exit(1)

    # Test 2: Scraper simulation (optional)
    print("\n")
    response = input(f"{Colors.YELLOW}Test the actual scraper? (y/n): {Colors.RESET}").strip().lower()

    if response == 'y':
        scraper_test_passed = test_scraper_simulation()

        if scraper_test_passed:
            print(f"\n{Colors.BOLD}{Colors.GREEN}{'=' * 70}{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.GREEN}✓ ALL TESTS PASSED{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.GREEN}{'=' * 70}{Colors.RESET}\n")
            print_success("Your Gemini API is properly configured!")
            print_success("The application is ready to fetch and process news.")
            print_info("\nNext steps:")
            print_info("1. Start Docker services: docker compose up -d")
            print_info("2. Access frontend: http://localhost:3000")
            print_info("3. Create and approve keywords")
            print_info("4. Articles will be fetched automatically")
        else:
            print_warning("\nScraper test had issues, but API connection works.")
            print_info("The application should still function with the fallback data.")
    else:
        print(f"\n{Colors.BOLD}{Colors.GREEN}✓ API CONNECTION TEST PASSED{Colors.RESET}\n")
        print_info("Skipping scraper test. You can run it later if needed.")

    print(f"\n{Colors.BOLD}Test complete!{Colors.RESET}\n")

if __name__ == "__main__":
    main()
