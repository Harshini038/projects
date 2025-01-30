import os
import cv2
import matplotlib.pyplot as plt
import argparse

class FingerprintViewer:
    def __init__(self):
        self.original_dir = os.path.join('SOCOFing', 'Real')
        self.preprocessed_dir = os.path.join('processed_images', 'preprocessed')
        self.minutiae_dir = os.path.join('processed_images', 'minutiae')
    
    def find_image_by_id(self, fingerprint_id):
        """Find image filename containing the given ID."""
        for filename in os.listdir(self.original_dir):
            if fingerprint_id in filename:
                return filename
        return None
    
    def check_processed_files(self, filename):
        """Check if preprocessed files exist for the given filename."""
        prep_path = os.path.join(self.preprocessed_dir, f'prep_{filename}')
        min_path = os.path.join(self.minutiae_dir, f'min_{filename}')
        
        if not os.path.exists(prep_path) or not os.path.exists(min_path):
            return False
        return True
    
    def view_fingerprint(self, fingerprint_id):
        """Display original, preprocessed, and minutiae images for a fingerprint."""
        # Find the image file
        filename = self.find_image_by_id(fingerprint_id)
        if not filename:
            print(f"No fingerprint found with ID: {fingerprint_id}")
            return False
        
        # Check if processed files exist
        if not self.check_processed_files(filename):
            print(f"Processed files not found for ID: {fingerprint_id}")
            print("Please run preprocess_dataset.py first to process the images.")
            return False
        
        try:
            # Read images
            original = cv2.imread(os.path.join(self.original_dir, filename))
            preprocessed = cv2.imread(os.path.join(self.preprocessed_dir, f'prep_{filename}'))
            minutiae = cv2.imread(os.path.join(self.minutiae_dir, f'min_{filename}'))
            
            # Convert from BGR to RGB for proper display
            original = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
            minutiae = cv2.cvtColor(minutiae, cv2.COLOR_BGR2RGB)
            
            # Create figure
            fig, axes = plt.subplots(1, 3, figsize=(15, 5))
            fig.suptitle(f'Fingerprint Analysis - ID: {fingerprint_id}')
            
            # Display images
            axes[0].imshow(original)
            axes[0].set_title('Original')
            axes[0].axis('off')
            
            axes[1].imshow(preprocessed, cmap='gray')
            axes[1].set_title('Preprocessed')
            axes[1].axis('off')
            
            axes[2].imshow(minutiae)
            axes[2].set_title('Minutiae Features\n(Red: Ridge Endings, Blue: Bifurcations)')
            axes[2].axis('off')
            
            plt.tight_layout()
            plt.show()
            return True
            
        except Exception as e:
            print(f"Error viewing fingerprint: {str(e)}")
            return False

def main():
    parser = argparse.ArgumentParser(description='View processed fingerprint images')
    parser.add_argument('--id', required=True, help='Fingerprint ID to view')
    
    args = parser.parse_args()
    viewer = FingerprintViewer()
    viewer.view_fingerprint(args.id)

if __name__ == "__main__":
    main()
