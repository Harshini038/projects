import os
import cv2
import numpy as np
import hashlib
from tqdm import tqdm
import json
from datetime import datetime

class KeyGenerator:
    def __init__(self):
        self.minutiae_dir = os.path.join('processed_images', 'minutiae')
        self.keys_dir = os.path.join('generated_keys')
        
        # Create keys directory if it doesn't exist
        if not os.path.exists(self.keys_dir):
            os.makedirs(self.keys_dir)
    
    def extract_minutiae_points(self, image_path):
        """Extract minutiae points from processed image."""
        # Read the minutiae image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Initialize lists for different types of minutiae
        endings = []
        bifurcations = []
        
        # Scan the image for colored circles (minutiae markers)
        height, width = img.shape[:2]
        for y in range(height):
            for x in range(width):
                pixel = img[y, x]
                # Red pixels indicate ridge endings
                if np.array_equal(pixel, [0, 0, 255]):
                    endings.append((x, y))
                # Blue pixels indicate bifurcations
                elif np.array_equal(pixel, [255, 0, 0]):
                    bifurcations.append((x, y))
        
        return endings, bifurcations
    
    def generate_private_key(self, endings, bifurcations):
        """Generate a 256-bit private key using SHA-256."""
        # Create a string representation of minutiae points
        minutiae_str = ""
        
        # Add sorted endings coordinates
        endings_str = ";".join([f"{x},{y}" for x, y in sorted(endings)])
        minutiae_str += f"E:{endings_str}|"
        
        # Add sorted bifurcations coordinates
        bifurcations_str = ";".join([f"{x},{y}" for x, y in sorted(bifurcations)])
        minutiae_str += f"B:{bifurcations_str}"
        
        # Generate SHA-256 hash
        sha256_hash = hashlib.sha256(minutiae_str.encode()).hexdigest()
        
        return {
            'private_key': sha256_hash,
            'minutiae_count': {
                'endings': len(endings),
                'bifurcations': len(bifurcations)
            }
        }
    
    def generate_key_for_fingerprint(self, fingerprint_id):
        """Generate private key for a specific fingerprint ID."""
        # Find the minutiae file
        minutiae_files = [f for f in os.listdir(self.minutiae_dir) if fingerprint_id in f]
        
        if not minutiae_files:
            print(f"No minutiae file found for fingerprint ID: {fingerprint_id}")
            return None
        
        minutiae_path = os.path.join(self.minutiae_dir, minutiae_files[0])
        
        try:
            # Extract minutiae points
            endings, bifurcations = self.extract_minutiae_points(minutiae_path)
            
            # Generate private key
            key_data = self.generate_private_key(endings, bifurcations)
            
            # Add metadata
            key_data['fingerprint_id'] = fingerprint_id
            key_data['generated_at'] = datetime.now().isoformat()
            
            # Save key data
            output_file = os.path.join(self.keys_dir, f"{fingerprint_id}_key.json")
            with open(output_file, 'w') as f:
                json.dump(key_data, f, indent=4)
            
            return key_data
            
        except Exception as e:
            print(f"Error generating key for {fingerprint_id}: {str(e)}")
            return None
    
    def generate_keys_for_all(self):
        """Generate private keys for all processed fingerprints."""
        # Get all minutiae files
        minutiae_files = [f for f in os.listdir(self.minutiae_dir) 
                         if f.startswith('min_') and f.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.bmp'))]
        
        successful = 0
        failed = 0
        
        print(f"\nGenerating private keys for {len(minutiae_files)} fingerprints...")
        for filename in tqdm(minutiae_files):
            # Extract fingerprint ID from filename
            fingerprint_id = filename.replace('min_', '').split('.')[0]
            
            result = self.generate_key_for_fingerprint(fingerprint_id)
            if result:
                successful += 1
            else:
                failed += 1
        
        print("\nKey Generation Summary:")
        print(f"Successfully generated: {successful} keys")
        print(f"Failed: {failed} keys")
        print(f"Keys are stored in: {self.keys_dir}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate private keys from fingerprint minutiae')
    parser.add_argument('--id', help='Generate key for specific fingerprint ID')
    
    args = parser.parse_args()
    generator = KeyGenerator()
    
    if args.id:
        # Generate key for specific fingerprint
        result = generator.generate_key_for_fingerprint(args.id)
        if result:
            print(f"\nGenerated private key for {args.id}:")
            print(f"Private Key: {result['private_key']}")
            print(f"Minutiae Count - Endings: {result['minutiae_count']['endings']}, "
                  f"Bifurcations: {result['minutiae_count']['bifurcations']}")
    else:
        # Generate keys for all fingerprints
        generator.generate_keys_for_all()

if __name__ == "__main__":
    main()
