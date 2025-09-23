# backend_api/app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import pickle
import os
import requests # Library to make HTTP requests for downloading files

# --- 1. Initialize Flask App ---
app = Flask(__name__)
CORS(app) # Enable Cross-Origin Resource Sharing

# --- 2. Download and Load Models on Startup ---

# Define the local directory where models will be stored
MODELS_DIR = 'models'
os.makedirs(MODELS_DIR, exist_ok=True) # Ensure the 'models' directory exists

# --- IMPORTANT: PASTE YOUR GOOGLE DRIVE DIRECT DOWNLOAD LINKS HERE ---
# These links are placeholders. You must replace them with your own.
FILE_URLS = {
    "books_df.pkl": "https://drive.google.com/uc?export=download&id=1x99l6OUMuedncQkET77gX4PmnRl6AtW5",
    "similarity.pkl": "https://drive.google.com/uc?export=download&id=1lV72ypO0Mmf1iXXdwJqEPFDjBZ3n8OTI",
    "author_stats.pkl": "https://drive.google.com/uc?export=download&id=1oEWrlxpCaw30nN2J5RcuHqBXIpAtdV9h",
    "genre_stats.pkl": "https://drive.google.com/uc?export=download&id=1iVXWFlDZsBU2tsmh3YTq0qIcBDJorYZ8",
    "rating_dist_data.pkl": "https://drive.google.com/uc?export=download&id=1zz7XbPf2z3frCCoUeMJggTJ0EDFTVEl7"
}

# Helper function to download a file from a URL
def download_file(url, local_filename):
    print(f"Downloading {local_filename} from cloud storage...")
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status() # Will raise an error for bad status codes
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"✅ Downloaded {local_filename} successfully.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error downloading {local_filename}: {e}")
        # In a real-world scenario, you might want to handle this more gracefully
        # For this project, we'll exit if a crucial file can't be downloaded.
        exit()

# On startup, check if each model file exists. If not, download it.
for filename, url in FILE_URLS.items():
    local_path = os.path.join(MODELS_DIR, filename)
    if not os.path.exists(local_path):
        download_file(url, local_path)
    else:
        print(f"✅ {filename} already exists locally.")

# Now, load the files into memory
try:
    books_df = pd.read_pickle(os.path.join(MODELS_DIR, 'books_df.pkl'))
    similarity_matrix = pickle.load(open(os.path.join(MODELS_DIR, 'similarity.pkl'),'rb'))
    author_stats = pickle.load(open(os.path.join(MODELS_DIR, 'author_stats.pkl'),'rb'))
    genre_stats = pickle.load(open(os.path.join(MODELS_DIR, 'genre_stats.pkl'),'rb'))
    rating_dist_data = pickle.load(open(os.path.join(MODELS_DIR, 'rating_dist_data.pkl'),'rb'))
    print("✅ All models and stats loaded into memory successfully.")
except FileNotFoundError as e:
    print(f"❌ CRITICAL ERROR: Could not load model file {e}. The application cannot start.")
    exit()

# --- 3. API Endpoints ---

@app.route('/books', methods=['GET'])
def get_book_titles():
    """Provides a list of all book titles for search autocomplete."""
    return jsonify(books_df['book'].tolist())

@app.route('/stats', methods=['GET'])
def get_stats():
    """Provides pre-calculated analytics data for the dashboard."""
    top_authors = [{"author": index, "ratings": int(value)} for index, value in author_stats.items()]
    top_genres = [{"genre": index, "count": int(value)} for index, value in genre_stats.items()]
    rating_distribution = {"ratings": rating_dist_data.index.tolist(), "counts": rating_dist_data.values.tolist()}
    
    return jsonify({
        "top_authors": top_authors,
        "top_genres": top_genres,
        "rating_distribution": rating_distribution
    })

@app.route('/recommend', methods=['GET'])
def recommend():
    """Generates book recommendations based on a given book title."""
    book_title = request.args.get('title')
    if not book_title:
        return jsonify({"error": "A 'title' query parameter is required."}), 400

    # Find the book in the dataframe (case-insensitive)
    matching_books = books_df[books_df['book'].str.lower() == book_title.lower()]
    if matching_books.empty:
        return jsonify({"error": f"Book '{book_title}' not found in the dataset."}), 404

    book_index = matching_books.index[0]
    
    # Get similarity scores and sort them to find the most similar books
    sorted_scores = sorted(list(enumerate(similarity_matrix[book_index])), reverse=True, key=lambda x: x[1])
    
    recommended_books = []
    # Get top 5 recommendations (index 0 is the book itself, so we skip it)
    for i in sorted_scores[1:6]:
        book_data = books_df.iloc[i[0]]
        recommended_books.append({
            "book": book_data['book'],
            "author": book_data['author'],
            "avg_rating": round(book_data['avg_rating'], 2),
            "num_ratings": int(book_data['num_ratings']),
            "genres": book_data['genres'],
            "url": book_data.get('url', '#') # Use '#' as a fallback if URL is missing
        })
        
    return jsonify(recommended_books)

# Note: The if __name__ == '__main__': block is removed for deployment.
# Gunicorn (the production server) will be used to run this 'app' object.
