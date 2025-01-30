import os
import cv2
import numpy as np
from tqdm import tqdm
from skimage.morphology import skeletonize
from skimage.util import img_as_ubyte

class FingerprintPreprocessor:
    def __init__(self):
        self.input_dir = os.path.join('SOCOFing', 'Real')
        self.preprocessed_dir = os.path.join('processed_images', 'preprocessed')
        self.minutiae_dir = os.path.join('processed_images', 'minutiae')
        
        # Create output directories
        for dir_path in [self.preprocessed_dir, self.minutiae_dir]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
    
    def preprocess_image(self, image):
        """Preprocess fingerprint image using Otsu's thresholding."""
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(image, (5, 5), 0)
        
        # Apply Otsu's thresholding
        _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    
    def get_crossing_number(self, values):
        """Calculate crossing number for minutiae detection."""
        crossings = 0
        for i in range(8):
            crossings += abs(int(values[i]) - int(values[(i + 1) % 8]))
        return crossings // 2
    
    def extract_minutiae(self, skeleton_img):
        """Extract minutiae features using crossing number method."""
        minutiae_img = cv2.cvtColor(img_as_ubyte(skeleton_img), cv2.COLOR_GRAY2BGR)
        minutiae_points = {'endings': [], 'bifurcations': []}
        
        rows, cols = skeleton_img.shape
        
        # Scan through the image (excluding border pixels)
        for i in range(1, rows - 1):
            for j in range(1, cols - 1):
                if skeleton_img[i, j] == 1:  # Ridge pixel
                    values = [
                        skeleton_img[i-1, j],   # P1
                        skeleton_img[i-1, j+1], # P2
                        skeleton_img[i, j+1],   # P3
                        skeleton_img[i+1, j+1], # P4
                        skeleton_img[i+1, j],   # P5
                        skeleton_img[i+1, j-1], # P6
                        skeleton_img[i, j-1],   # P7
                        skeleton_img[i-1, j-1]  # P8
                    ]
                    
                    cn = self.get_crossing_number(values)
                    
                    if cn == 1:  # Ridge ending
                        cv2.circle(minutiae_img, (j, i), 3, (0, 0, 255), -1)
                        minutiae_points['endings'].append((j, i))
                    elif cn == 3:  # Bifurcation
                        cv2.circle(minutiae_img, (j, i), 3, (255, 0, 0), -1)
                        minutiae_points['bifurcations'].append((j, i))
        
        return minutiae_img, minutiae_points
    
    def process_single_image(self, image_path):
        """Process a single fingerprint image."""
        # Read image
        original = cv2.imread(image_path)
        if original is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Preprocess
        preprocessed = self.preprocess_image(original)
        
        # Skeletonize
        _, binary = cv2.threshold(preprocessed, 127, 1, cv2.THRESH_BINARY)
        skeleton = skeletonize(binary)
        
        # Extract minutiae
        minutiae_img, minutiae_points = self.extract_minutiae(skeleton)
        
        # Save results
        filename = os.path.basename(image_path)
        cv2.imwrite(os.path.join(self.preprocessed_dir, f'prep_{filename}'), preprocessed)
        cv2.imwrite(os.path.join(self.minutiae_dir, f'min_{filename}'), minutiae_img)
        
        return len(minutiae_points['endings']), len(minutiae_points['bifurcations'])
    
    def process_dataset(self):
        """Process entire dataset and display statistics."""
        image_files = [f for f in os.listdir(self.input_dir) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.bmp'))]
        
        total_endings = 0
        total_bifurcations = 0
        processed_count = 0
        
        print(f"\nProcessing {len(image_files)} images...")
        for filename in tqdm(image_files):
            try:
                input_path = os.path.join(self.input_dir, filename)
                endings, bifurcations = self.process_single_image(input_path)
                
                total_endings += endings
                total_bifurcations += bifurcations
                processed_count += 1
            except Exception as e:
                print(f"\nError processing {filename}: {str(e)}")
        
        print("\nFeature Extraction Summary:")
        print(f"Successfully processed {processed_count} images")
        print(f"Total Ridge Endings detected: {total_endings}")
        print(f"Total Bifurcations detected: {total_bifurcations}")
        print(f"Average Ridge Endings per image: {total_endings/processed_count:.2f}")
        print(f"Average Bifurcations per image: {total_bifurcations/processed_count:.2f}")

if __name__ == "__main__":
    preprocessor = FingerprintPreprocessor()
    preprocessor.process_dataset()
