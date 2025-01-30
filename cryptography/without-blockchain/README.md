# Fingerprint Authentication System

A robust fingerprint authentication system built with Python that processes, analyzes, and authenticates fingerprint images using advanced computer vision techniques.

## Features

- Fingerprint image preprocessing and enhancement
- Minutiae extraction and feature detection
- Secure fingerprint matching and authentication
- Web-based interface for easy interaction
- Support for real fingerprint datasets

## Prerequisites

- Python 3.7+
- OpenCV
- NumPy
- Flask
- Other dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fingerprint-authentication-system.git
cd fingerprint-authentication-system
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

- `preprocess_dataset.py`: Handles fingerprint image preprocessing and feature extraction
- `view_fingerprint.py`: Manages fingerprint visualization and authentication
- `templates/`: Contains web interface HTML templates
- `processed_images/`: Directory for storing processed fingerprint images
- `voters.json`: Configuration file for voter data

## Usage

1. Place your fingerprint dataset in the `SOCOFing/Real` directory
2. Run the preprocessing script:
```bash
python preprocess_dataset.py
```
3. Start the web interface:
```bash
python view_fingerprint.py
```
4. Access the application through your web browser at `http://localhost:5000`

## Features in Detail

- **Image Preprocessing**: Implements advanced preprocessing techniques including:
  - Grayscale conversion
  - Otsu's thresholding
  - Skeletonization
  - Minutiae extraction

- **Authentication System**: Secure fingerprint matching using:
  - Feature point detection
  - Minutiae matching
  - ECDSA for secure signature verification

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to the SOCOFing dataset for providing fingerprint samples
- OpenCV and scikit-image communities for their excellent computer vision libraries
