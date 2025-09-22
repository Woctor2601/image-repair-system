#!/usr/bin/env python3
"""
Military Training Exercise: Reconnaissance Image Reconstruction
Reassemble fragmented surveillance image from training mission.
"""

import os
import sys
from PIL import Image
import zipfile
import argparse

def extract_pieces(zip_path, extract_dir="pieces"):
    """Extract image pieces from ZIP file"""
    print(f"🔓 Extracting pieces from {zip_path}...")
    
    if not os.path.exists(extract_dir):
        os.makedirs(extract_dir)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    
    piece_files = [f for f in os.listdir(extract_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
    print(f"✅ Extracted {len(piece_files)} image pieces")
    return extract_dir, sorted(piece_files, key=lambda x: int(x.split('_')[1].split('.')[0]))

def get_grid_dimensions(num_pieces):
    """Calculate optimal grid dimensions for reconstruction"""
    # Assume square grid for 1000 pieces (could be 40x25, 50x20, etc.)
    import math
    
    # Common factorizations of 1000
    possible_dims = [
        (40, 25),   # 40 wide, 25 tall
        (50, 20),   # 50 wide, 20 tall  
        (25, 40),   # 25 wide, 40 tall
        (20, 50),   # 20 wide, 50 tall
    ]
    
    # Return the most likely dimensions (adjust based on your actual breakdown)
    return possible_dims[0]  # Default to 40x25

def reconstruct_image(pieces_dir, piece_files, output_path="reconstructed_image.png"):
    """Reconstruct the full image from pieces"""
    print(f"🔧 Reconstructing image from {len(piece_files)} pieces...")
    
    if not piece_files:
        print("❌ No image pieces found!")
        return None
    
    # Load first piece to get dimensions
    first_piece = Image.open(os.path.join(pieces_dir, piece_files[0]))
    piece_width, piece_height = first_piece.size
    
    # Calculate grid dimensions
    grid_width, grid_height = get_grid_dimensions(len(piece_files))
    
    # Create blank canvas for reconstruction
    full_width = piece_width * grid_width
    full_height = piece_height * grid_height
    reconstructed = Image.new('RGB', (full_width, full_height))
    
    print(f"📐 Reconstructing {grid_width}x{grid_height} grid")
    print(f"📏 Final image will be {full_width}x{full_height} pixels")
    
    # Place each piece in correct position
    pieces_placed = 0
    for i, piece_file in enumerate(piece_files):
        if i >= grid_width * grid_height:
            break
            
        # Calculate position in grid
        row = i // grid_width
        col = i % grid_width
        
        # Calculate pixel position
        x = col * piece_width
        y = row * piece_height
        
        # Load and place piece
        piece = Image.open(os.path.join(pieces_dir, piece_file))
        reconstructed.paste(piece, (x, y))
        pieces_placed += 1
        
        # Progress indicator
        if pieces_placed % 100 == 0:
            print(f"✨ Placed {pieces_placed}/{len(piece_files)} pieces...")
    
    # Save reconstructed image
    reconstructed.save(output_path)
    print(f"🎉 Reconstruction complete! Saved as: {output_path}")
    print(f"📊 Total pieces placed: {pieces_placed}")
    
    return output_path

def analyze_image(image_path):
    """Analyze the reconstructed image for hidden content"""
    print(f"\n🔍 Analyzing reconstructed image: {image_path}")
    
    try:
        img = Image.open(image_path)
        width, height = img.size
        
        print(f"📏 Image dimensions: {width} x {height}")
        print(f"🎨 Image mode: {img.mode}")
        
        # Check for obvious text/QR codes
        print("\n💡 Analysis Tips:")
        print("   - Look for text overlays or watermarks")
        print("   - Check for QR codes or barcodes") 
        print("   - Examine corners and edges carefully")
        print("   - Try adjusting brightness/contrast if needed")
        print("   - Consider steganography tools for hidden messages")
        
    except Exception as e:
        print(f"❌ Error analyzing image: {e}")

def main():
    parser = argparse.ArgumentParser(description='Reconstruct fragmented surveillance image')
    parser.add_argument('zip_file', help='ZIP file containing image pieces')
    parser.add_argument('-o', '--output', default='mission_intel.png', 
                       help='Output filename for reconstructed image')
    parser.add_argument('--keep-pieces', action='store_true', 
                       help='Keep extracted pieces after reconstruction')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.zip_file):
        print(f"❌ ZIP file not found: {args.zip_file}")
        print("💡 Make sure you downloaded the file correctly:")
        print("   curl -O [URL_TO_ZIP_FILE]")
        sys.exit(1)
    
    print("🎖️  MILITARY INTELLIGENCE RECONSTRUCTION TOOL")
    print("=" * 50)
    
    try:
        # Extract pieces
        pieces_dir, piece_files = extract_pieces(args.zip_file)
        
        # Reconstruct image
        result_path = reconstruct_image(pieces_dir, piece_files, args.output)
        
        if result_path:
            # Analyze result
            analyze_image(result_path)
            
            # Cleanup
            if not args.keep_pieces:
                import shutil
                shutil.rmtree(pieces_dir)
                print(f"🧹 Cleaned up temporary pieces directory")
            
            print(f"\n🎯 MISSION COMPLETE!")
            print(f"📸 Reconstructed image: {args.output}")
            print(f"🔍 Examine the image for your next intelligence briefing...")
            
        else:
            print("❌ Reconstruction failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"💥 Mission failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
