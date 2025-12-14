# Test script to help debug font import crashes
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core import analyze_font, validate_font, create_preview_pixmap

def test_font(font_path):
    """Test a single font file to see what causes crashes"""
    print(f"\n{'='*60}")
    print(f"Testing: {font_path}")
    print(f"{'='*60}")
    
    # Test 1: File exists
    print(f"1. File exists: {os.path.exists(font_path)}")
    
    # Test 2: Validate
    try:
        valid = validate_font(font_path)
        print(f"2. Validation: {valid}")
    except Exception as e:
        print(f"2. Validation FAILED: {e}")
        valid = False
    
    # Test 3: Analyze
    try:
        data = analyze_font(font_path)
        print(f"3. Analysis: {data}")
    except Exception as e:
        print(f"3. Analysis FAILED: {e}")
        data = {'name': os.path.basename(font_path), 'error': str(e)}
    
    # Test 4: Preview
    try:
        pixmap = create_preview_pixmap(font_path)
        print(f"4. Preview: {'Success' if pixmap else 'Failed (returned None)'}")
    except Exception as e:
        print(f"4. Preview FAILED: {e}")
    
    print(f"{'='*60}\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Test specific font
        test_font(sys.argv[1])
    else:
        print("Usage: python test_fonts.py <font_file_path>")
        print("Or drag a TTF/OTF file here to test it")
