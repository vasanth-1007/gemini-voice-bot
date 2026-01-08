#!/usr/bin/env python3
"""
Test script for image extraction support
Verifies that image-heavy SOPs can be processed
"""
import sys
from pathlib import Path
from colorama import Fore, Style, init

init(autoreset=True)

def print_header(text):
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{text:^60}")
    print(f"{'='*60}{Style.RESET_ALL}\n")

def check_image_dependencies():
    """Check if image processing dependencies are installed"""
    print(f"{Fore.YELLOW}Checking image processing dependencies...{Style.RESET_ALL}")
    
    required_packages = {
        'fitz': 'PyMuPDF',
        'PIL': 'Pillow'
    }
    
    all_installed = True
    for import_name, package_name in required_packages.items():
        try:
            if import_name == 'fitz':
                import fitz
            else:
                from PIL import Image
            print(f"{Fore.GREEN}✓ {package_name}{Style.RESET_ALL}")
        except ImportError:
            print(f"{Fore.RED}✗ {package_name} not installed{Style.RESET_ALL}")
            all_installed = False
    
    return all_installed

def check_image_extractor():
    """Check if ImageExtractor module is available"""
    print(f"\n{Fore.YELLOW}Checking ImageExtractor module...{Style.RESET_ALL}")
    
    try:
        from src.sop_loader.image_extractor import ImageExtractor
        print(f"{Fore.GREEN}✓ ImageExtractor module available{Style.RESET_ALL}")
        return True
    except ImportError as e:
        print(f"{Fore.RED}✗ ImageExtractor module error: {e}{Style.RESET_ALL}")
        return False

def check_sop_pdfs():
    """Check if there are PDF files in sops folder"""
    print(f"\n{Fore.YELLOW}Checking for PDF files in sops/...{Style.RESET_ALL}")
    
    sop_path = Path('sops')
    if not sop_path.exists():
        print(f"{Fore.RED}✗ sops/ folder not found{Style.RESET_ALL}")
        return False
    
    pdf_files = list(sop_path.glob('*.pdf'))
    
    if pdf_files:
        print(f"{Fore.GREEN}✓ Found {len(pdf_files)} PDF file(s){Style.RESET_ALL}")
        for pdf in pdf_files:
            print(f"  - {pdf.name}")
        return True
    else:
        print(f"{Fore.YELLOW}⚠ No PDF files found in sops/{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}  Note: Image extraction works with PDF files only{Style.RESET_ALL}")
        return False

def test_basic_image_extraction():
    """Test basic image extraction functionality"""
    print(f"\n{Fore.YELLOW}Testing image extraction...{Style.RESET_ALL}")
    
    try:
        # Check if we can import required modules
        from src.sop_loader.image_extractor import ImageExtractor
        from config import Config
        import fitz
        
        # Check for API key
        config = Config()
        if not config.google_api_key or 'your_' in config.google_api_key.lower():
            print(f"{Fore.YELLOW}⚠ API key not configured - skipping live test{Style.RESET_ALL}")
            print(f"{Fore.GREEN}✓ Module structure is correct{Style.RESET_ALL}")
            return True
        
        # Check for PDF files
        sop_path = Path('sops')
        pdf_files = list(sop_path.glob('*.pdf'))
        
        if not pdf_files:
            print(f"{Fore.YELLOW}⚠ No PDF files to test - skipping extraction test{Style.RESET_ALL}")
            print(f"{Fore.GREEN}✓ Module structure is correct{Style.RESET_ALL}")
            return True
        
        # Test extraction on first PDF
        test_pdf = pdf_files[0]
        print(f"\n{Fore.CYAN}Testing with: {test_pdf.name}{Style.RESET_ALL}")
        
        # Initialize extractor
        extractor = ImageExtractor(api_key=config.google_api_key)
        
        # Try to extract images (without analyzing)
        print(f"  Extracting images...")
        images = extractor.extract_images_from_pdf(test_pdf)
        
        if images:
            print(f"{Fore.GREEN}✓ Successfully extracted {len(images)} image(s){Style.RESET_ALL}")
            for img in images[:3]:  # Show first 3
                print(f"  - Page {img.page_number}: {img.width}x{img.height}px")
            if len(images) > 3:
                print(f"  ... and {len(images) - 3} more")
        else:
            print(f"{Fore.YELLOW}⚠ No images found in PDF (might be text-only){Style.RESET_ALL}")
        
        print(f"{Fore.GREEN}✓ Image extraction working correctly{Style.RESET_ALL}")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}✗ Error during test: {e}{Style.RESET_ALL}")
        return False

def main():
    """Run all image support checks"""
    print_header("IMAGE SUPPORT VERIFICATION")
    
    checks = {
        "Image Dependencies": check_image_dependencies(),
        "ImageExtractor Module": check_image_extractor(),
        "PDF Files Available": check_sop_pdfs(),
        "Basic Extraction Test": test_basic_image_extraction()
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
        print(f"{'🎉 IMAGE SUPPORT READY! 🎉':^60}")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        print(f"{Fore.CYAN}Your bot can now process image-heavy SOPs!{Style.RESET_ALL}\n")
        print(f"{Fore.YELLOW}What happens when you load SOPs:{Style.RESET_ALL}")
        print(f"  1. Text is extracted from all documents")
        print(f"  2. Images are detected in PDF files")
        print(f"  3. Each image is analyzed with Gemini Vision")
        print(f"  4. Image descriptions are added to searchable index")
        print(f"  5. You can ask questions about visual content!\n")
        return 0
    else:
        print(f"{Fore.RED}{'='*60}")
        print(f"{'⚠ SETUP INCOMPLETE ⚠':^60}")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        
        # Provide specific guidance
        if not checks["Image Dependencies"]:
            print(f"{Fore.CYAN}To install image dependencies:{Style.RESET_ALL}")
            print(f"  pip install PyMuPDF Pillow\n")
        
        if not checks["PDF Files Available"]:
            print(f"{Fore.CYAN}To test image extraction:{Style.RESET_ALL}")
            print(f"  Add PDF files with images to the sops/ folder\n")
        
        print(f"{Fore.YELLOW}Note: The bot will still work with text-only documents{Style.RESET_ALL}\n")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Test cancelled{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}Error during test: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
