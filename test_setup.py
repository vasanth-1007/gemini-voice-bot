#!/usr/bin/env python3
"""
Quick test script to verify setup and configuration
Run this before starting the main application
"""
import sys
from pathlib import Path
from colorama import Fore, Style, init

init(autoreset=True)

def print_header(text):
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{text:^60}")
    print(f"{'='*60}{Style.RESET_ALL}\n")

def check_python_version():
    """Check Python version"""
    print(f"{Fore.YELLOW}Checking Python version...{Style.RESET_ALL}")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"{Fore.GREEN}✓ Python {version.major}.{version.minor}.{version.micro}{Style.RESET_ALL}")
        return True
    else:
        print(f"{Fore.RED}✗ Python 3.8+ required, found {version.major}.{version.minor}{Style.RESET_ALL}")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print(f"\n{Fore.YELLOW}Checking dependencies...{Style.RESET_ALL}")
    
    required_packages = [
        'google.generativeai',
        'chromadb',
        'sentence_transformers',
        'sounddevice',
        'numpy',
        'PyPDF2',
        'docx',
        'loguru',
        'pydantic',
        'colorama'
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            if package == 'docx':
                __import__('docx')
            else:
                __import__(package.replace('.', '/').split('/')[0])
            print(f"{Fore.GREEN}✓ {package}{Style.RESET_ALL}")
        except ImportError:
            print(f"{Fore.RED}✗ {package} not installed{Style.RESET_ALL}")
            all_installed = False
    
    return all_installed

def check_env_file():
    """Check if .env file exists and has API key"""
    print(f"\n{Fore.YELLOW}Checking configuration...{Style.RESET_ALL}")
    
    env_path = Path('.env')
    if not env_path.exists():
        print(f"{Fore.RED}✗ .env file not found{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}  → Copy .env.example to .env and add your API key{Style.RESET_ALL}")
        return False
    
    print(f"{Fore.GREEN}✓ .env file exists{Style.RESET_ALL}")
    
    # Check if API key is set
    with open(env_path, 'r') as f:
        content = f.read()
        if 'GOOGLE_API_KEY=' in content and 'your_gemini_api_key_here' not in content:
            # Check if it's not empty
            for line in content.split('\n'):
                if line.startswith('GOOGLE_API_KEY='):
                    key = line.split('=', 1)[1].strip()
                    if key and len(key) > 10:
                        print(f"{Fore.GREEN}✓ API key configured{Style.RESET_ALL}")
                        return True
    
    print(f"{Fore.RED}✗ API key not configured properly{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}  → Add your Gemini API key to .env file{Style.RESET_ALL}")
    return False

def check_sop_folder():
    """Check if SOP folder exists and has files"""
    print(f"\n{Fore.YELLOW}Checking SOP folder...{Style.RESET_ALL}")
    
    sop_path = Path('sops')
    if not sop_path.exists():
        print(f"{Fore.RED}✗ sops/ folder not found{Style.RESET_ALL}")
        return False
    
    print(f"{Fore.GREEN}✓ sops/ folder exists{Style.RESET_ALL}")
    
    # Check for files
    files = list(sop_path.glob('*'))
    doc_files = [f for f in files if f.suffix.lower() in ['.pdf', '.docx', '.txt']]
    
    if doc_files:
        print(f"{Fore.GREEN}✓ Found {len(doc_files)} document(s){Style.RESET_ALL}")
        for f in doc_files[:5]:  # Show first 5
            print(f"  - {f.name}")
        if len(doc_files) > 5:
            print(f"  ... and {len(doc_files) - 5} more")
        return True
    else:
        print(f"{Fore.YELLOW}⚠ No documents in sops/ folder{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}  → Add PDF, DOCX, or TXT files to sops/ folder{Style.RESET_ALL}")
        return False

def check_folder_structure():
    """Check if all required folders exist"""
    print(f"\n{Fore.YELLOW}Checking folder structure...{Style.RESET_ALL}")
    
    required_folders = [
        'src',
        'src/sop_loader',
        'src/retrieval',
        'src/gemini_integration',
        'src/voice_handler',
        'sops'
    ]
    
    all_exist = True
    for folder in required_folders:
        folder_path = Path(folder)
        if folder_path.exists():
            print(f"{Fore.GREEN}✓ {folder}/{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ {folder}/ missing{Style.RESET_ALL}")
            all_exist = False
    
    return all_exist

def main():
    """Run all checks"""
    print_header("GEMINI VOICE BOT - SETUP VERIFICATION")
    
    checks = {
        "Python Version": check_python_version(),
        "Dependencies": check_dependencies(),
        "Folder Structure": check_folder_structure(),
        "Configuration": check_env_file(),
        "SOP Documents": check_sop_folder()
    }
    
    # Summary
    print_header("SUMMARY")
    
    passed = sum(checks.values())
    total = len(checks)
    
    for check_name, result in checks.items():
        status = f"{Fore.GREEN}✓ PASS{Style.RESET_ALL}" if result else f"{Fore.RED}✗ FAIL{Style.RESET_ALL}"
        print(f"{check_name:.<40} {status}")
    
    print(f"\n{Fore.CYAN}Results: {passed}/{total} checks passed{Style.RESET_ALL}\n")
    
    if passed == total:
        print(f"{Fore.GREEN}{'='*60}")
        print(f"{'🎉 ALL CHECKS PASSED! 🎉':^60}")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        print(f"{Fore.CYAN}You're ready to run the application!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Run: python main.py{Style.RESET_ALL}\n")
        return 0
    else:
        print(f"{Fore.RED}{'='*60}")
        print(f"{'⚠ SETUP INCOMPLETE ⚠':^60}")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        print(f"{Fore.YELLOW}Please fix the issues above before running the application.{Style.RESET_ALL}\n")
        
        # Provide specific guidance
        if not checks["Dependencies"]:
            print(f"{Fore.CYAN}To install dependencies:{Style.RESET_ALL}")
            print(f"  pip install -r requirements.txt\n")
        
        if not checks["Configuration"]:
            print(f"{Fore.CYAN}To configure API key:{Style.RESET_ALL}")
            print(f"  1. Copy .env.example to .env")
            print(f"  2. Get your API key from: https://makersuite.google.com/app/apikey")
            print(f"  3. Add it to .env file\n")
        
        if not checks["SOP Documents"]:
            print(f"{Fore.CYAN}To add SOP documents:{Style.RESET_ALL}")
            print(f"  Copy your PDF, DOCX, or TXT files to the sops/ folder\n")
        
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Setup check cancelled{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}Error during setup check: {e}{Style.RESET_ALL}")
        sys.exit(1)
