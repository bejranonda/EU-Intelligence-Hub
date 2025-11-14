#!/usr/bin/env python3
"""
Post-Startup Health Check Script
Run this after starting Docker services to verify everything is working
"""

import sys
import time
import requests
import subprocess
from pathlib import Path

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

class HealthChecker:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.services_status = {}

    def check_docker_services(self):
        """Check if Docker services are running"""
        print_header("Docker Services Status")

        try:
            result = subprocess.run(
                ['docker', 'compose', 'ps', '--format', 'json'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                print_error("Failed to get Docker service status")
                self.issues.append("Docker services not accessible")
                return False

            import json
            services = []

            # Parse line-by-line JSON (docker compose ps outputs JSONL)
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        services.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass

            if not services:
                print_warning("No Docker services found")
                print_info("Run: docker compose up -d")
                self.warnings.append("No services running")
                return False

            required_services = [
                'postgres', 'redis', 'backend',
                'celery_worker', 'celery_beat', 'frontend'
            ]

            for service_name in required_services:
                matching = [s for s in services if service_name in s.get('Service', '').lower()]

                if matching:
                    service = matching[0]
                    state = service.get('State', 'unknown')

                    if state == 'running':
                        print_success(f"{service_name}: Running")
                        self.services_status[service_name] = 'running'
                    else:
                        print_error(f"{service_name}: {state}")
                        self.services_status[service_name] = state
                        self.issues.append(f"{service_name} not running")
                else:
                    print_error(f"{service_name}: Not found")
                    self.services_status[service_name] = 'not found'
                    self.issues.append(f"{service_name} not found")

            return all(v == 'running' for v in self.services_status.values())

        except subprocess.TimeoutExpired:
            print_error("Docker command timed out")
            self.issues.append("Docker not responding")
            return False
        except FileNotFoundError:
            print_error("Docker not installed or not in PATH")
            self.issues.append("Docker not available")
            return False
        except Exception as e:
            print_error(f"Error checking Docker services: {e}")
            self.issues.append(f"Docker check failed: {e}")
            return False

    def check_backend_api(self):
        """Check if backend API is responsive"""
        print_header("Backend API Health Check")

        api_url = "http://localhost:8000"

        try:
            # Basic health check
            print_info("Checking /health endpoint...")
            response = requests.get(f"{api_url}/health", timeout=10)

            if response.status_code == 200:
                print_success("Backend API is responding")
                print_info(f"Response: {response.json()}")
            else:
                print_error(f"Health check failed with status {response.status_code}")
                self.issues.append(f"Backend health check: {response.status_code}")
                return False

            # Detailed health check
            print_info("\nChecking /api/health/detailed endpoint...")
            response = requests.get(f"{api_url}/api/health/detailed", timeout=10)

            if response.status_code == 200:
                health_data = response.json()

                print_info("\nComponent Health:")
                for component, status in health_data.items():
                    if isinstance(status, dict):
                        comp_status = status.get('status', 'unknown')
                        if comp_status == 'healthy':
                            print_success(f"  {component}: {comp_status}")
                        else:
                            print_warning(f"  {component}: {comp_status}")
                            self.warnings.append(f"{component}: {comp_status}")
                    else:
                        print_info(f"  {component}: {status}")

                # Check database specifically
                db_health = health_data.get('database', {})
                if db_health.get('status') == 'healthy':
                    print_success("\nDatabase connection is healthy")
                else:
                    print_error("\nDatabase connection issues detected")
                    self.issues.append("Database not healthy")

                # Check redis
                redis_health = health_data.get('redis', {})
                if redis_health.get('status') == 'healthy':
                    print_success("Redis connection is healthy")
                else:
                    print_warning("Redis connection issues detected")
                    self.warnings.append("Redis not healthy")

                return True
            else:
                print_warning("Detailed health check not available")
                return True  # Not critical

        except requests.ConnectionError:
            print_error(f"Cannot connect to backend at {api_url}")
            print_info("Make sure backend service is running")
            self.issues.append("Backend not accessible")
            return False
        except requests.Timeout:
            print_error("Backend API request timed out")
            self.issues.append("Backend timeout")
            return False
        except Exception as e:
            print_error(f"Backend health check failed: {e}")
            self.issues.append(f"Backend check error: {e}")
            return False

    def check_database_content(self):
        """Check if database has data"""
        print_header("Database Content Check")

        api_url = "http://localhost:8000"

        try:
            # Check keywords
            print_info("Checking keywords in database...")
            response = requests.get(f"{api_url}/api/keywords/?page=1&page_size=10", timeout=10)

            if response.status_code == 200:
                data = response.json()
                keyword_count = data.get('pagination', {}).get('total', 0)

                if keyword_count > 0:
                    print_success(f"Found {keyword_count} keywords in database")
                    print_info("Sample keywords:")
                    for kw in data.get('results', [])[:3]:
                        print(f"  - {kw.get('keyword_en')} (ID: {kw.get('id')})")
                else:
                    print_warning("No keywords found in database")
                    print_info("You need to add keywords via the frontend or admin panel")
                    self.warnings.append("No keywords in database")

            # Check articles
            print_info("\nChecking articles in database...")
            response = requests.get(f"{api_url}/api/search/articles?page=1&page_size=10", timeout=10)

            if response.status_code == 200:
                data = response.json()
                article_count = data.get('pagination', {}).get('total', 0)

                if article_count > 0:
                    print_success(f"Found {article_count} articles in database")
                    print_info("Sample articles:")
                    for article in data.get('results', [])[:3]:
                        print(f"  - {article.get('title', 'N/A')[:60]}...")
                        print(f"    Source: {article.get('source', 'N/A')}, "
                              f"Sentiment: {article.get('sentiment', {}).get('overall', 'N/A')}")
                else:
                    print_warning("No articles found in database")
                    print_info("\nThis is why keyword search returns no results!")
                    print_info("\nTo populate the database:")
                    print_info("1. Add keywords via frontend (http://localhost:3000)")
                    print_info("2. Approve keywords in admin panel")
                    print_info("3. Wait for Celery worker to process (check logs)")
                    print_info("4. Or wait for hourly scraping job")
                    self.warnings.append("No articles in database")

                return article_count > 0

        except Exception as e:
            print_error(f"Database content check failed: {e}")
            self.issues.append(f"DB content check: {e}")
            return False

    def check_celery_workers(self):
        """Check if Celery workers are processing tasks"""
        print_header("Celery Workers Check")

        try:
            # Check celery worker logs
            result = subprocess.run(
                ['docker', 'compose', 'logs', '--tail', '50', 'celery_worker'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                logs = result.stdout

                if 'ready' in logs.lower() or 'connected' in logs.lower():
                    print_success("Celery worker is connected and ready")
                else:
                    print_warning("Celery worker status unclear")

                # Check for recent task processing
                if 'task' in logs.lower() and 'received' in logs.lower():
                    print_success("Celery worker has processed tasks recently")
                else:
                    print_info("No recent task activity detected")
                    print_info("This is normal if no keywords have been triggered yet")

            # Check celery beat scheduler
            result = subprocess.run(
                ['docker', 'compose', 'logs', '--tail', '30', 'celery_beat'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                logs = result.stdout

                if 'scheduler' in logs.lower() and 'started' in logs.lower():
                    print_success("Celery beat scheduler is running")
                else:
                    print_warning("Celery beat scheduler status unclear")

            return True

        except Exception as e:
            print_warning(f"Could not check Celery workers: {e}")
            self.warnings.append("Celery check failed")
            return False

    def check_frontend(self):
        """Check if frontend is accessible"""
        print_header("Frontend Accessibility Check")

        frontend_url = "http://localhost:3000"

        try:
            print_info(f"Checking {frontend_url}...")
            response = requests.get(frontend_url, timeout=10)

            if response.status_code == 200:
                print_success("Frontend is accessible")
                print_info(f"Open in browser: {frontend_url}")
                return True
            else:
                print_error(f"Frontend returned status {response.status_code}")
                self.issues.append(f"Frontend status: {response.status_code}")
                return False

        except requests.ConnectionError:
            print_error(f"Cannot connect to frontend at {frontend_url}")
            print_info("Make sure frontend service is running")
            self.issues.append("Frontend not accessible")
            return False
        except Exception as e:
            print_error(f"Frontend check failed: {e}")
            self.issues.append(f"Frontend error: {e}")
            return False

    def generate_report(self):
        """Generate final health report"""
        print_header("Health Check Summary")

        total_checks = 6
        issues_count = len(self.issues)
        warnings_count = len(self.warnings)

        print(f"\n{Colors.BOLD}Results:{Colors.RESET}")
        print(f"{Colors.GREEN}Total Checks: {total_checks}{Colors.RESET}")
        print(f"{Colors.RED}Critical Issues: {issues_count}{Colors.RESET}")
        print(f"{Colors.YELLOW}Warnings: {warnings_count}{Colors.RESET}")

        if self.issues:
            print(f"\n{Colors.BOLD}{Colors.RED}✗ Critical Issues:{Colors.RESET}")
            for issue in self.issues:
                print(f"  • {issue}")

        if self.warnings:
            print(f"\n{Colors.BOLD}{Colors.YELLOW}⚠ Warnings:{Colors.RESET}")
            for warning in self.warnings:
                print(f"  • {warning}")

        if not self.issues and not self.warnings:
            print(f"\n{Colors.BOLD}{Colors.GREEN}✓ ALL SYSTEMS OPERATIONAL{Colors.RESET}")
            print(f"\n{Colors.GREEN}{'=' * 70}{Colors.RESET}")
            print(f"{Colors.GREEN}Your EU Intelligence Hub is fully operational!{Colors.RESET}")
            print(f"{Colors.GREEN}{'=' * 70}{Colors.RESET}\n")
            print_info("You can now:")
            print_info("  • Access frontend: http://localhost:3000")
            print_info("  • Access API docs: http://localhost:8000/docs")
            print_info("  • View Grafana: http://localhost:3001")
            print_info("  • Add keywords and search for articles")
        elif not self.issues:
            print(f"\n{Colors.BOLD}{Colors.YELLOW}⚠ SYSTEM OPERATIONAL WITH WARNINGS{Colors.RESET}")
            print_info("\nThe system is functional but needs attention to warnings.")
        else:
            print(f"\n{Colors.BOLD}{Colors.RED}✗ SYSTEM HAS CRITICAL ISSUES{Colors.RESET}")
            print_info("\nPlease fix the critical issues before using the system.")
            print_info("\nCommon fixes:")
            print_info("  • Restart services: docker compose restart")
            print_info("  • Check logs: docker compose logs [service_name]")
            print_info("  • Rebuild: docker compose up -d --build")

        print(f"\n{Colors.BOLD}{'=' * 70}{Colors.RESET}\n")

        return len(self.issues) == 0

def main():
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║              System Health Check Utility                     ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    print(f"{Colors.RESET}")

    print_info("This script checks if all services are running and healthy.")
    print_info("Run this AFTER starting Docker services with: docker compose up -d\n")

    time.sleep(1)

    checker = HealthChecker()

    # Run all checks
    checker.check_docker_services()
    checker.check_backend_api()
    checker.check_database_content()
    checker.check_celery_workers()
    checker.check_frontend()

    # Generate final report
    success = checker.generate_report()

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
