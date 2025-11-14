#!/usr/bin/env python3
"""
Test Setup Script
Verify that all dependencies are installed correctly
"""

import sys

def test_imports():
    """Test all required imports"""
    print("Testing required packages...\n")

    packages = {
        'selenium': 'selenium',
        'bs4': 'beautifulsoup4',
        'lxml': 'lxml',
        'pandas': 'pandas',
        'requests': 'requests',
    }

    all_ok = True

    for module, package in packages.items():
        try:
            __import__(module)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - NOT INSTALLED")
            all_ok = False

    return all_ok


def test_chrome_driver():
    """Test Chrome WebDriver"""
    print("\nTesting Chrome WebDriver...\n")

    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome(options=options)
        driver.get("https://www.google.com")
        driver.quit()

        print("✓ Chrome WebDriver working")
        return True

    except Exception as e:
        print(f"✗ Chrome WebDriver error: {e}")
        print("\nTroubleshooting:")
        print("1. Install Chrome: https://www.google.com/chrome/")
        print("2. Install ChromeDriver: pip install webdriver-manager")
        return False


def main():
    """Run all tests"""
    print("="*60)
    print(" "*15 + "Setup Verification Test")
    print("="*60 + "\n")

    # Test imports
    imports_ok = test_imports()

    # Test Chrome driver
    driver_ok = test_chrome_driver()

    # Summary
    print("\n" + "="*60)
    if imports_ok and driver_ok:
        print("✓ All tests passed! You're ready to scrape.")
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        sys.exit(1)
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
