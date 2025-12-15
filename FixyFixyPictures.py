#!/usr/bin/env python3
"""
Military Training Exercise: Reconnaissance Image Reconstruction
Reassemble fragmented surveillance image from training mission.
"""

import os
import sys
import re
from PIL import Image
import zipfile
import argparse
import shutil


def find_image_files(directory):
    """Recursively find all image files in directory"""
    image_files = []
    for root, dirs, files in os.walk(directory):
        # Skip Mac OS metadata directories
        if '__MACOSX' in root:
            continue
        for f in files:
            if f.endswith(('.png', '.jpg', '.jpeg')) and not f.startswith('._'):
                image_files.append(os.path.join(root, f))
    return image_files


def extract_number_from_filename(filepath):
    """Extract the numeric portion from a filename like strip_0245.png"""
    filename = os.path.basename(filepath)
    # Match patterns like: strip_0245.png, piece_123.png, 0245.png, etc.
    match = re.search(r'(\d+)', filename)
    if match:
        return int(match.group(1))
    return 0


def extract_pieces(input_path, extract_dir="pieces"):
    """Extract image pieces from ZIP file or locate them in a directory"""
    print(f"Processing input: {input_path}...")
    
    # Clean up any existing extract directory
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    os.makedirs(extract_dir)
    
    # Check if input is a ZIP file or directory
    if zipfile.is_zipfile(input_path):
        print(f"Detected ZIP file, extracting...")
        with zipfile.ZipFile(input_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        search_dir = extract_dir
    elif os.path.isdir(input_path):
        print(f"Detected directory, scanning for images...")
        search_dir = input_path
    else:
        print(f"Input is neither a ZIP file nor a directory: {input_path}")
        return None, []
    
    # Find all image files recursively
    image_files = find_image_files(search_dir)
    
    # Sort by the numeric portion of the filename
    image_files.sort(key=extract_number_from_filename)
    
    print(f"Found {len(image_files)} image pieces")
    
    # Validate numbering
    if image_files:
        numbers = [extract_number_from_filename(f) for f in image_files]
        print(f"Numbering range: {min(numbers):04d} to {max(numbers):04d}")
        
        # Check for gaps
        expected = set(range(min(numbers), max(numbers) + 1))
        actual = set(numbers)
        missing = expected - actual
        if missing:
            print(f"Warning: Missing {len(missing)} pieces: {sorted(missing)[:10]}{'...' if len(missing) > 10 else ''}")
    
    return search_dir, image_files


def determine_grid_layout(piece_files):
    """Determine grid layout based on piece dimensions"""
    if not piece_files:
        return 1, 1
    
    # Load first piece to get dimensions
    first_piece = Image.open(piece_files[0])
    piece_width, piece_height = first_piece.size
    first_piece.close()
    
    num_pieces = len(piece_files)
    
    print(f"Piece dimensions: {piece_width} x {piece_height}")
    
    # If pieces are 1 pixel wide (vertical strips), stitch horizontally
    if piece_width == 1:
        print(f"Detected vertical strips - stitching horizontally")
        return num_pieces, 1  # All pieces in one row
    
    # If pieces are 1 pixel tall (horizontal strips), stitch vertically
    if piece_height == 1:
        print(f"Detected horizontal strips - stitching vertically")
        return 1, num_pieces  # All pieces in one column
    
    # For square-ish pieces, calculate optimal grid
    import math
    sqrt_pieces = int(math.sqrt(num_pieces))
    
    # Try to find factors close to square root
    for cols in range(sqrt_pieces, 0, -1):
        if num_pieces % cols == 0:
            rows = num_pieces // cols
            return cols, rows
    
    # Fallback: assume 40x25 for 1000 pieces
    if num_pieces == 1000:
        return 40, 25
    
    return sqrt_pieces, sqrt_pieces


def reconstruct_image(piece_files, output_path="reconstructed_image.png"):
    """Reconstruct the full image from pieces"""
    print(f"🔧 Reconstructing image from {len(piece_files)} pieces...")
    
    if not piece_files:
        print("No image pieces found!")
        return None
    
    # Load first piece to get dimensions
    first_piece = Image.open(piece_files[0])
    piece_width, piece_height = first_piece.size
    first_piece.close()
    
    # Determine grid layout
    grid_cols, grid_rows = determine_grid_layout(piece_files)
    
    # Create blank canvas for reconstruction
    full_width = piece_width * grid_cols
    full_height = piece_height * grid_rows
    
    # Use RGBA if source images have alpha channel
    sample = Image.open(piece_files[0])
    mode = sample.mode if sample.mode in ('RGB', 'RGBA') else 'RGB'
    sample.close()
    
    reconstructed = Image.new(mode, (full_width, full_height))
    
    print(f"Grid layout: {grid_cols} columns x {grid_rows} rows")
    print(f"Final image: {full_width} x {full_height} pixels")
    
    # Place each piece in correct position
    pieces_placed = 0
    for i, piece_file in enumerate(piece_files):
        if i >= grid_cols * grid_rows:
            print(f"Warning: More pieces than grid cells, stopping at {i}")
            break
        
        # Calculate position in grid (row-major order)
        row = i // grid_cols
        col = i % grid_cols
        
        # Calculate pixel position
        x = col * piece_width
        y = row * piece_height
        
        # Load and place piece
        piece = Image.open(piece_file)
        reconstructed.paste(piece, (x, y))
        piece.close()
        pieces_placed += 1
        
        # Progress indicator
        if pieces_placed % 200 == 0:
            print(f"Placed {pieces_placed}/{len(piece_files)} pieces...")
    
    # Save reconstructed image
    reconstructed.save(output_path)
    print(f"Reconstruction complete! Saved as: {output_path}")
    print(f"Total pieces placed: {pieces_placed}")
    
    return output_path


def analyze_image(image_path):
    """Analyze the reconstructed image"""
    print(f"\n Analyzing reconstructed image: {image_path}")
    
    try:
        img = Image.open(image_path)
        width, height = img.size
        
        print(f"Image dimensions: {width} x {height}")
        print(f"Image mode: {img.mode}")
        
        print("\n Analysis Tips:")
        print("   - Look for text overlays or watermarks")
        print("   - Check for QR codes or barcodes")
        print("   - Examine corners and edges carefully")
        print("   - Try adjusting brightness/contrast if needed")
        
        img.close()
        
    except Exception as e:
        print(f"Error analyzing image: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Reconstruct fragmented surveillance image',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s riddle_strips.zip           # Process a ZIP file
  %(prog)s ./extracted_images/         # Process an existing directory
  %(prog)s data.zip -o result.png      # Custom output filename
        """
    )
    parser.add_argument('input_path', 
                       help='ZIP file or directory containing image pieces')
    parser.add_argument('-o', '--output', default='mission_intel.png',
                       help='Output filename for reconstructed image')
    parser.add_argument('--keep-pieces', action='store_true',
                       help='Keep extracted pieces after reconstruction')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_path):
        print(f"Input not found: {args.input_path}")
        sys.exit(1)
    
    print("IMAGE INTELLIGENCE RECONSTRUCTION TOOL")
    print("=" * 50)
    
    try:
        # Extract/locate pieces
        pieces_dir, piece_files = extract_pieces(args.input_path)
        
        if not piece_files:
            print("No image pieces found!")
            sys.exit(1)
        
        # Validate we have expected count
        expected_count = 1000
        if len(piece_files) != expected_count:
            print(f"Warning: Expected {expected_count} pieces, found {len(piece_files)}")
        else:
            print(f"Confirmed: {len(piece_files)} pieces (000-999)")
        
        # Reconstruct image
        result_path = reconstruct_image(piece_files, args.output)
        
        if result_path:
            # Analyze result
            analyze_image(result_path)
            
            # Cleanup extracted files (only if we extracted from ZIP)
            if not args.keep_pieces and os.path.exists("pieces"):
                shutil.rmtree("pieces")
                print(f"🧹 Cleaned up temporary pieces directory")
            
            print(f"\n MISSION COMPLETE!")
            print(f"Reconstructed image: {args.output}")
            print(f" Examine the image for your next intelligence briefing...")
            
        else:
            print(" Reconstruction failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f" Mission failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
