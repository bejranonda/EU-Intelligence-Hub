#!/usr/bin/env python3
"""
Comprehensive Project Validation Script
Validates all connections, configurations, and dependencies for the EU-Intelligence-Hub project
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import socket

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(80)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.RESET}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

class ProjectValidator:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.issues = []
        self.warnings = []
        self.successes = []

    def check_env_file(self) -> bool:
        """Check if .env file exists and has required variables"""
        print_header("1. Environment Configuration Check")

        env_file = self.project_root / '.env'
        if not env_file.exists():
            print_error(".env file not found!")
            self.issues.append("Missing .env file")
            return False

        print_success(".env file exists")

        # Check for required environment variables
        required_vars = [
            'GEMINI_API_KEY',
            'POSTGRES_USER',
            'POSTGRES_PASSWORD',
            'POSTGRES_DB',
            'DATABASE_URL',
            'REDIS_URL',
            'SECRET_KEY',
            'ADMIN_USERNAME',
            'ADMIN_PASSWORD'
        ]

        env_content = env_file.read_text()
        missing_vars = []
        placeholder_vars = []

        for var in required_vars:
            if f"{var}=" not in env_content:
                missing_vars.append(var)
            elif f"{var}=your_" in env_content or f"{var}=change_this" in env_content:
                placeholder_vars.append(var)

        if missing_vars:
            print_error(f"Missing environment variables: {', '.join(missing_vars)}")
            self.issues.append(f"Missing variables: {', '.join(missing_vars)}")
            return False

        if placeholder_vars:
            print_warning(f"Placeholder values detected: {', '.join(placeholder_vars)}")
            print_warning("Please update these with actual values!")
            self.warnings.append(f"Placeholder values: {', '.join(placeholder_vars)}")

        print_success(f"All {len(required_vars)} required environment variables are defined")
        self.successes.append("Environment configuration complete")
        return True

    def check_python_environment(self) -> bool:
        """Check Python version and backend dependencies"""
        print_header("2. Python Environment Check")

        # Check Python version
        python_version = sys.version.split()[0]
        print_info(f"Python version: {python_version}")

        if sys.version_info < (3, 11):
            print_error(f"Python 3.11+ required, found {python_version}")
            self.issues.append(f"Python version too old: {python_version}")
            return False

        print_success(f"Python {python_version} is compatible (3.11+ required)")

        # Check if backend requirements.txt exists
        requirements_file = self.project_root / 'backend' / 'requirements.txt'
        if not requirements_file.exists():
            print_error("backend/requirements.txt not found!")
            self.issues.append("Missing requirements.txt")
            return False

        print_success("requirements.txt found")

        # Check if virtual environment is recommended
        if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print_warning("Not running in a virtual environment (recommended but not required)")
            self.warnings.append("No virtual environment detected")

        # Try to import critical packages
        critical_packages = {
            'fastapi': 'FastAPI',
            'sqlalchemy': 'SQLAlchemy',
            'psycopg2': 'psycopg2 (PostgreSQL driver)',
            'redis': 'redis-py',
            'celery': 'Celery',
            'google.generativeai': 'Google Generative AI'
        }

        missing_packages = []
        for module, name in critical_packages.items():
            try:
                __import__(module)
                print_success(f"{name} is installed")
            except ImportError:
                print_error(f"{name} is NOT installed")
                missing_packages.append(name)

        if missing_packages:
            print_warning(f"\nMissing packages: {', '.join(missing_packages)}")
            print_info("Run: cd backend && pip install -r requirements.txt")
            self.warnings.append(f"Missing Python packages: {', '.join(missing_packages)}")
        else:
            self.successes.append("All critical Python packages installed")

        return True

    def check_nodejs_environment(self) -> bool:
        """Check Node.js version and frontend dependencies"""
        print_header("3. Node.js Environment Check")

        # Check Node.js version
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            node_version = result.stdout.strip()
            print_info(f"Node.js version: {node_version}")

            version_num = int(node_version.lstrip('v').split('.')[0])
            if version_num < 18:
                print_error(f"Node.js 18+ required, found {node_version}")
                self.issues.append(f"Node.js version too old: {node_version}")
                return False

            print_success(f"Node.js {node_version} is compatible (18+ required)")
        except FileNotFoundError:
            print_error("Node.js is not installed!")
            self.issues.append("Node.js not found")
            return False

        # Check if package.json exists
        package_json = self.project_root / 'frontend' / 'package.json'
        if not package_json.exists():
            print_error("frontend/package.json not found!")
            self.issues.append("Missing package.json")
            return False

        print_success("package.json found")

        # Check if node_modules exists
        node_modules = self.project_root / 'frontend' / 'node_modules'
        if not node_modules.exists():
            print_warning("node_modules not found - dependencies not installed")
            print_info("Run: cd frontend && npm install")
            self.warnings.append("Frontend dependencies not installed")
        else:
            print_success("node_modules directory exists")
            self.successes.append("Frontend dependencies installed")

        return True

    def check_docker_environment(self) -> bool:
        """Check if Docker is available"""
        print_header("4. Docker Environment Check")

        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            docker_version = result.stdout.strip()
            print_info(f"Docker version: {docker_version}")
            print_success("Docker is installed")

            # Check docker compose
            result = subprocess.run(['docker', 'compose', 'version'], capture_output=True, text=True)
            compose_version = result.stdout.strip()
            print_info(f"Docker Compose version: {compose_version}")
            print_success("Docker Compose is installed")

            # Check running containers
            result = subprocess.run(
                ['docker', 'ps', '--filter', 'name=euint', '--format', '{{.Names}}\t{{.Status}}'],
                capture_output=True,
                text=True
            )

            if result.stdout.strip():
                print_info("\nRunning containers:")
                for line in result.stdout.strip().split('\n'):
                    if line:
                        name, status = line.split('\t', 1)
                        print_info(f"  - {name}: {status}")
                print_success("Docker containers are running")
                self.successes.append("Docker environment ready")
                return True
            else:
                print_warning("No Docker containers are currently running")
                print_info("Run: docker compose up -d")
                self.warnings.append("Docker containers not running")
                return False

        except FileNotFoundError:
            print_warning("Docker is not installed or not in PATH")
            print_info("This project requires Docker for full functionality")
            print_info("Install Docker: https://docs.docker.com/get-docker/")
            self.warnings.append("Docker not available")
            return False

    def check_port_availability(self) -> bool:
        """Check if required ports are available or in use"""
        print_header("5. Port Availability Check")

        required_ports = {
            5432: 'PostgreSQL',
            6379: 'Redis',
            8000: 'Backend API',
            3000: 'Frontend',
            9090: 'Prometheus',
            3001: 'Grafana'
        }

        all_available = True
        for port, service in required_ports.items():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()

            if result == 0:
                print_success(f"Port {port} ({service}) is in use - service may be running")
            else:
                print_warning(f"Port {port} ({service}) is available but service not running")
                all_available = False

        if all_available:
            self.successes.append("All required ports have services running")
        else:
            self.warnings.append("Some services are not running")

        return True

    def check_database_connection(self) -> bool:
        """Check PostgreSQL database connection"""
        print_header("6. Database Connection Check")

        try:
            import psycopg2
            from dotenv import load_dotenv

            load_dotenv(self.project_root / '.env')

            db_url = os.getenv('DATABASE_URL')
            if not db_url:
                print_error("DATABASE_URL not found in .env")
                self.issues.append("Missing DATABASE_URL")
                return False

            # Try to connect
            try:
                # Parse connection string
                # postgresql://user:pass@host:port/db
                if db_url.startswith('postgresql://'):
                    print_info("Attempting to connect to PostgreSQL...")
                    # Try connection with timeout
                    conn = psycopg2.connect(db_url, connect_timeout=5)
                    cursor = conn.cursor()
                    cursor.execute('SELECT version();')
                    version = cursor.fetchone()[0]
                    print_success("Successfully connected to PostgreSQL")
                    print_info(f"Database version: {version}")

                    # Check for pgvector extension
                    cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
                    if cursor.fetchone():
                        print_success("pgvector extension is installed")
                    else:
                        print_warning("pgvector extension not found - required for semantic search")
                        self.warnings.append("Missing pgvector extension")

                    cursor.close()
                    conn.close()
                    self.successes.append("Database connection successful")
                    return True

            except psycopg2.OperationalError as e:
                print_error(f"Cannot connect to PostgreSQL: {e}")
                print_info("Make sure PostgreSQL is running (docker compose up postgres)")
                self.issues.append("PostgreSQL connection failed")
                return False

        except ImportError:
            print_warning("psycopg2 not installed - cannot test database connection")
            print_info("Run: pip install psycopg2-binary")
            self.warnings.append("psycopg2 not installed")
            return False

    def check_redis_connection(self) -> bool:
        """Check Redis connection"""
        print_header("7. Redis Connection Check")

        try:
            import redis
            from dotenv import load_dotenv

            load_dotenv(self.project_root / '.env')

            redis_url = os.getenv('REDIS_URL')
            if not redis_url:
                print_error("REDIS_URL not found in .env")
                self.issues.append("Missing REDIS_URL")
                return False

            try:
                print_info("Attempting to connect to Redis...")
                client = redis.from_url(redis_url, socket_timeout=5, socket_connect_timeout=5)
                client.ping()
                print_success("Successfully connected to Redis")

                # Get Redis info
                info = client.info()
                print_info(f"Redis version: {info['redis_version']}")
                print_info(f"Connected clients: {info['connected_clients']}")

                client.close()
                self.successes.append("Redis connection successful")
                return True

            except redis.ConnectionError as e:
                print_error(f"Cannot connect to Redis: {e}")
                print_info("Make sure Redis is running (docker compose up redis)")
                self.issues.append("Redis connection failed")
                return False

        except ImportError:
            print_warning("redis-py not installed - cannot test Redis connection")
            print_info("Run: pip install redis")
            self.warnings.append("redis-py not installed")
            return False

    def check_backend_api(self) -> bool:
        """Check if backend API is accessible"""
        print_header("8. Backend API Check")

        try:
            import requests

            api_url = "http://localhost:8000"

            try:
                print_info(f"Checking API at {api_url}/health...")
                response = requests.get(f"{api_url}/health", timeout=5)

                if response.status_code == 200:
                    print_success("Backend API is responding")
                    print_info(f"Health check: {response.json()}")
                    self.successes.append("Backend API is accessible")

                    # Check detailed health
                    try:
                        response = requests.get(f"{api_url}/api/health/detailed", timeout=5)
                        if response.status_code == 200:
                            health_data = response.json()
                            print_info("\nDetailed Health Check:")
                            for key, value in health_data.items():
                                if isinstance(value, dict):
                                    status = value.get('status', 'unknown')
                                    if status == 'healthy':
                                        print_success(f"  {key}: {status}")
                                    else:
                                        print_warning(f"  {key}: {status}")
                    except:
                        pass

                    return True
                else:
                    print_error(f"API returned status code: {response.status_code}")
                    self.issues.append(f"API health check failed: {response.status_code}")
                    return False

            except requests.ConnectionError:
                print_error(f"Cannot connect to backend API at {api_url}")
                print_info("Make sure the backend is running:")
                print_info("  - Docker: docker compose up backend")
                print_info("  - Manual: cd backend && uvicorn app.main:app --reload")
                self.issues.append("Backend API not accessible")
                return False

        except ImportError:
            print_warning("requests library not installed - cannot test API")
            print_info("Run: pip install requests")
            self.warnings.append("requests library not installed")
            return False

    def check_gemini_api_key(self) -> bool:
        """Check if Gemini API key is configured"""
        print_header("9. Google Gemini API Check")

        from dotenv import load_dotenv
        load_dotenv(self.project_root / '.env')

        api_key = os.getenv('GEMINI_API_KEY')

        if not api_key or api_key == 'your_gemini_api_key_here':
            print_error("GEMINI_API_KEY is not configured!")
            print_info("This is REQUIRED for the application to work")
            print_info("\nTo get a Gemini API key:")
            print_info("1. Visit: https://makersuite.google.com/app/apikey")
            print_info("2. Sign in with your Google account")
            print_info("3. Create a new API key")
            print_info("4. Update GEMINI_API_KEY in .env file")
            self.issues.append("GEMINI_API_KEY not configured")
            return False

        print_success("GEMINI_API_KEY is configured")
        print_info(f"Key starts with: {api_key[:10]}...")

        # Try to validate the key
        try:
            import google.generativeai as genai

            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-pro')

                print_info("Testing API key with a simple query...")
                response = model.generate_content("Say 'API key is valid' if you can read this.")

                print_success("Gemini API key is valid and working!")
                print_info(f"Test response: {response.text[:50]}...")
                self.successes.append("Gemini API configured and working")
                return True

            except Exception as e:
                print_error(f"Gemini API key validation failed: {e}")
                print_warning("The key may be invalid or rate limited")
                self.warnings.append("Gemini API validation failed")
                return False

        except ImportError:
            print_warning("google-generativeai not installed - cannot validate API key")
            print_info("Run: pip install google-generativeai")
            self.warnings.append("Cannot validate Gemini API key")
            return False

    def check_file_structure(self) -> bool:
        """Check if all required files and directories exist"""
        print_header("10. File Structure Check")

        required_paths = {
            'backend/app/main.py': 'Backend main application file',
            'backend/app/database.py': 'Database configuration',
            'backend/app/config.py': 'Application configuration',
            'backend/init_db.sql': 'Database initialization script',
            'backend/requirements.txt': 'Python dependencies',
            'frontend/package.json': 'Frontend dependencies',
            'frontend/src/App.tsx': 'Frontend main component',
            'docker-compose.yml': 'Docker Compose configuration',
            '.env': 'Environment variables'
        }

        all_exist = True
        for path, description in required_paths.items():
            full_path = self.project_root / path
            if full_path.exists():
                print_success(f"{description}: {path}")
            else:
                print_error(f"Missing {description}: {path}")
                self.issues.append(f"Missing file: {path}")
                all_exist = False

        if all_exist:
            self.successes.append("All required files present")

        return all_exist

    def generate_report(self):
        """Generate final validation report"""
        print_header("VALIDATION REPORT")

        print(f"\n{Colors.BOLD}Summary:{Colors.RESET}")
        print(f"{Colors.GREEN}Successes: {len(self.successes)}{Colors.RESET}")
        print(f"{Colors.YELLOW}Warnings: {len(self.warnings)}{Colors.RESET}")
        print(f"{Colors.RED}Critical Issues: {len(self.issues)}{Colors.RESET}")

        if self.successes:
            print(f"\n{Colors.BOLD}{Colors.GREEN}✓ What's Working:{Colors.RESET}")
            for success in self.successes:
                print(f"  • {success}")

        if self.warnings:
            print(f"\n{Colors.BOLD}{Colors.YELLOW}⚠ Warnings:{Colors.RESET}")
            for warning in self.warnings:
                print(f"  • {warning}")

        if self.issues:
            print(f"\n{Colors.BOLD}{Colors.RED}✗ Critical Issues:{Colors.RESET}")
            for issue in self.issues:
                print(f"  • {issue}")

            print(f"\n{Colors.BOLD}Recommended Actions:{Colors.RESET}")

            if any('GEMINI_API_KEY' in issue for issue in self.issues):
                print("\n1. Configure Gemini API Key (CRITICAL):")
                print("   - Get key from: https://makersuite.google.com/app/apikey")
                print("   - Update .env file with your actual API key")

            if any('Docker' in str(self.warnings) for warning in self.warnings):
                print("\n2. Install Docker:")
                print("   - Visit: https://docs.docker.com/get-docker/")
                print("   - After installation, run: docker compose up -d")

            if any('PostgreSQL' in issue for issue in self.issues):
                print("\n3. Start PostgreSQL:")
                print("   - Run: docker compose up -d postgres")

            if any('Redis' in issue for issue in self.issues):
                print("\n4. Start Redis:")
                print("   - Run: docker compose up -d redis")

            if any('Backend API' in issue for issue in self.issues):
                print("\n5. Start Backend:")
                print("   - Run: docker compose up -d backend")

            if any('packages' in str(self.warnings) for warning in self.warnings):
                print("\n6. Install Python dependencies:")
                print("   - Run: cd backend && pip install -r requirements.txt")

            if any('Frontend' in str(self.warnings) for warning in self.warnings):
                print("\n7. Install Frontend dependencies:")
                print("   - Run: cd frontend && npm install")
        else:
            print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 All critical checks passed!{Colors.RESET}")
            print("\nYou can start the application with:")
            print("  docker compose up -d")

        print(f"\n{Colors.BOLD}{'=' * 80}{Colors.RESET}\n")

        # Return exit code
        return 0 if len(self.issues) == 0 else 1

def main():
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("""
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║                                                                       ║
    ║         EU Intelligence Hub - Project Validation Script              ║
    ║                                                                       ║
    ╚═══════════════════════════════════════════════════════════════════════╝
    """)
    print(f"{Colors.RESET}")

    validator = ProjectValidator()

    # Run all checks
    validator.check_env_file()
    validator.check_python_environment()
    validator.check_nodejs_environment()
    validator.check_docker_environment()
    validator.check_port_availability()
    validator.check_database_connection()
    validator.check_redis_connection()
    validator.check_backend_api()
    validator.check_gemini_api_key()
    validator.check_file_structure()

    # Generate final report
    exit_code = validator.generate_report()
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
