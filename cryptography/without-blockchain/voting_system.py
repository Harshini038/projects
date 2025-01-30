from flask import Flask, render_template, request, jsonify, session
import os
import json
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-123'  # Fixed secret key for development

# Configuration
REAL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'SOCOFing', 'Real')
VOTERS_FILE = 'voters.json'

# Initialize voters data
def load_voters():
    if os.path.exists(VOTERS_FILE):
        with open(VOTERS_FILE, 'r') as f:
            return json.load(f)
    return {'votes': {}, 'vote_count': {'candidate1': 0, 'candidate2': 0, 'candidate3': 0}}

def save_voters(data):
    with open(VOTERS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Load initial data
voters_data = load_voters()

def verify_user_id(user_id):
    """Verify if the user ID exists in the fingerprint dataset."""
    try:
        print(f"\n=== Starting User ID Verification ===")
        print(f"Verifying user ID: {user_id}")
        print(f"Current working directory: {os.getcwd()}")
        
        # Get absolute path and verify it exists
        abs_real_dir = os.path.abspath(REAL_DIR)
        print(f"Absolute path to REAL_DIR: {abs_real_dir}")
        print(f"Directory exists: {os.path.exists(abs_real_dir)}")
        
        if not os.path.exists(abs_real_dir):
            print(f"Error: Directory does not exist: {abs_real_dir}")
            return False
            
        # Convert to integer to ensure it's a valid number
        try:
            id_num = int(user_id)
            print(f"Successfully converted ID to integer: {id_num}")
        except ValueError:
            print(f"Error: Invalid integer value for user_id: {user_id}")
            return False
        
        if id_num < 1 or id_num > 600:
            print(f"Error: ID {id_num} out of range (1-600)")
            return False
            
        # Format the ID to match the exact filename pattern
        pattern = re.compile(f"^{id_num}__[MF]_(?:Left|Right)_(?:index|little|middle|ring|thumb)_finger\\.(?i:BMP)$")
        print(f"Looking for pattern: {pattern.pattern}")
        
        try:
            # List all files in the directory
            files = os.listdir(abs_real_dir)
            print(f"Successfully listed directory. Found {len(files)} total files")
            
            # Print first few files for debugging
            print(f"Sample of files in directory: {files[:5] if files else 'No files found'}")
            
            # Check for matching files using case-insensitive pattern
            matching_files = [f for f in files if pattern.match(f)]
            print(f"Found {len(matching_files)} matching files: {matching_files[:2]}...")
            
            if len(matching_files) > 0:
                print("=== Verification Successful ===")
                return True
            else:
                print("=== Verification Failed: No matching files found ===")
                print("First few files in directory for comparison:")
                for f in files[:10]:
                    print(f"  - {f}")
                return False
                
        except Exception as e:
            print(f"Error listing directory contents: {str(e)}")
            print(f"Current working directory: {os.getcwd()}")
            return False
            
    except Exception as e:
        print(f"Unexpected error in verify_user_id: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_if_voted(user_id):
    """Check if a user has already voted."""
    return str(user_id) in voters_data['votes']

@app.route('/')
def index():
    try:
        # Clear any existing session data
        session.clear()
        return render_template('index.html', candidates={
            'candidate1': 'Candidate 1',
            'candidate2': 'Candidate 2',
            'candidate3': 'Candidate 3'
        })
    except Exception as e:
        print(f"Error in index route: {str(e)}")
        return "An error occurred", 500

@app.route('/verify', methods=['POST'])
def verify():
    """Handle user verification requests."""
    try:
        print("\n=== Starting Verification Request ===")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Session before verification: {dict(session)}")
        
        user_id = request.form.get('user_id')
        print(f"Received request with user_id: {user_id}")
        print(f"Form data: {dict(request.form)}")
        
        if not user_id:
            print("Error: No user ID provided")
            return jsonify({'success': False, 'message': 'Please enter a User ID'})
        
        # Check if ID exists in dataset
        print("Calling verify_user_id...")
        if not verify_user_id(user_id):
            print("Error: User ID verification failed")
            return jsonify({'success': False, 'message': 'Invalid User ID. Please enter a valid number between 1 and 600.'})
        
        # Check if user has already voted
        print("Checking if user has voted...")
        if check_if_voted(user_id):
            print("Error: User has already voted")
            return jsonify({'success': False, 'message': 'You have already cast your vote!'})
        
        # Store verified ID in session
        session['verified_id'] = user_id
        print(f"Session after storing verified_id: {dict(session)}")
        print("=== Verification Process Complete ===")
        return jsonify({'success': True, 'message': 'Verification successful! You can now cast your vote.'})
        
    except Exception as e:
        print(f"Unexpected error in verify route: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'An unexpected error occurred during verification'})

@app.route('/cast_vote', methods=['POST'])
def cast_vote():
    try:
        if 'verified_id' not in session:
            return jsonify({'success': False, 'message': 'Please verify your ID first'})
        
        user_id = session['verified_id']
        candidate = request.form.get('candidate')
        
        if not candidate:
            return jsonify({'success': False, 'message': 'No candidate selected'})
        
        # Double-check if user hasn't voted
        if check_if_voted(user_id):
            session.pop('verified_id', None)
            return jsonify({'success': False, 'message': 'You have already cast your vote!'})
        
        # Record the vote
        voters_data['votes'][str(user_id)] = {
            'candidate': candidate,
            'timestamp': datetime.now().isoformat()
        }
        voters_data['vote_count'][candidate] = voters_data['vote_count'].get(candidate, 0) + 1
        
        # Save to file
        save_voters(voters_data)
        
        session.pop('verified_id', None)  # Clear verification after voting
        
        return jsonify({'success': True, 'message': 'Vote cast successfully! Redirecting to results...'})
        
    except Exception as e:
        print(f"Unexpected error in cast_vote route: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'An unexpected error occurred during voting'})

@app.route('/results')
def results():
    try:
        results = {
            'candidates': {
                'candidate1': 'Candidate 1',
                'candidate2': 'Candidate 2',
                'candidate3': 'Candidate 3'
            },
            'votes': voters_data['vote_count'],
            'total_votes': sum(voters_data['vote_count'].values())
        }
        return render_template('results.html', results=results)
        
    except Exception as e:
        print(f"Error in results route: {str(e)}")
        return "An error occurred", 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
