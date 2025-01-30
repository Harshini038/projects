import os
import cv2
import numpy as np
import hashlib
from tqdm import tqdm
import json
from datetime import datetime
from ecdsa import SigningKey, SECP256k1
import base64

class KeypairGenerator:
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
    
    def generate_private_key_seed(self, endings, bifurcations):
        """Generate a seed for private key using SHA-256."""
        # Create a string representation of minutiae points
        minutiae_str = ""
        
        # Add sorted endings coordinates
        endings_str = ";".join([f"{x},{y}" for x, y in sorted(endings)])
        minutiae_str += f"E:{endings_str}|"
        
        # Add sorted bifurcations coordinates
        bifurcations_str = ";".join([f"{x},{y}" for x, y in sorted(bifurcations)])
        minutiae_str += f"B:{bifurcations_str}"
        
        # Generate SHA-256 hash
        return hashlib.sha256(minutiae_str.encode()).digest()
    
    def generate_keypair(self, private_key_seed):
        """Generate ECDSA keypair from the private key seed."""
        # Create signing key (private key) from the seed
        signing_key = SigningKey.from_string(private_key_seed, curve=SECP256k1)
        
        # Get verifying key (public key)
        verifying_key = signing_key.get_verifying_key()
        
        return {
            'private_key': base64.b64encode(signing_key.to_string()).decode('utf-8'),
            'public_key': base64.b64encode(verifying_key.to_string()).decode('utf-8')
        }
    
    def generate_keypair_for_fingerprint(self, fingerprint_id):
        """Generate keypair for a specific fingerprint ID."""
        # Find the minutiae file
        minutiae_files = [f for f in os.listdir(self.minutiae_dir) if fingerprint_id in f]
        
        if not minutiae_files:
            print(f"No minutiae file found for fingerprint ID: {fingerprint_id}")
            return None
        
        minutiae_path = os.path.join(self.minutiae_dir, minutiae_files[0])
        
        try:
            # Extract minutiae points
            endings, bifurcations = self.extract_minutiae_points(minutiae_path)
            
            # Generate private key seed
            private_key_seed = self.generate_private_key_seed(endings, bifurcations)
            
            # Generate keypair
            keypair = self.generate_keypair(private_key_seed)
            
            # Add metadata
            key_data = {
                'fingerprint_id': fingerprint_id,
                'generated_at': datetime.now().isoformat(),
                'private_key': keypair['private_key'],
                'public_key': keypair['public_key'],
                'minutiae_count': {
                    'endings': len(endings),
                    'bifurcations': len(bifurcations)
                },
                'curve_type': 'SECP256k1'
            }
            
            # Save key data
            output_file = os.path.join(self.keys_dir, f"{fingerprint_id}_keypair.json")
            with open(output_file, 'w') as f:
                json.dump(key_data, f, indent=4)
            
            return key_data
            
        except Exception as e:
            print(f"Error generating keypair for {fingerprint_id}: {str(e)}")
            return None
    
    def generate_keypairs_for_all(self):
        """Generate keypairs for all processed fingerprints."""
        # Get all minutiae files
        minutiae_files = [f for f in os.listdir(self.minutiae_dir) 
                         if f.startswith('min_') and f.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.bmp'))]
        
        successful = 0
        failed = 0
        
        print(f"\nGenerating keypairs for {len(minutiae_files)} fingerprints...")
        for filename in tqdm(minutiae_files):
            # Extract fingerprint ID from filename
            fingerprint_id = filename.replace('min_', '').split('.')[0]
            
            result = self.generate_keypair_for_fingerprint(fingerprint_id)
            if result:
                successful += 1
            else:
                failed += 1
        
        print("\nKeypair Generation Summary:")
        print(f"Successfully generated: {successful} keypairs")
        print(f"Failed: {failed} keypairs")
        print(f"Keypairs are stored in: {self.keys_dir}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate ECDSA keypairs from fingerprint minutiae')
    parser.add_argument('--id', help='Generate keypair for specific fingerprint ID')
    
    args = parser.parse_args()
    generator = KeypairGenerator()
    
    if args.id:
        # Generate keypair for specific fingerprint
        result = generator.generate_keypair_for_fingerprint(args.id)
        if result:
            print(f"\nGenerated keypair for {args.id}:")
            print(f"Private Key: {result['private_key'][:32]}...")
            print(f"Public Key: {result['public_key'][:32]}...")
            print(f"Minutiae Count - Endings: {result['minutiae_count']['endings']}, "
                  f"Bifurcations: {result['minutiae_count']['bifurcations']}")
    else:
        # Generate keypairs for all fingerprints
        generator.generate_keypairs_for_all()

if __name__ == "__main__":
    main()
