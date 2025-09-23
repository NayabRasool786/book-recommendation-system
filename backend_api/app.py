# backend_api/app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import pickle

app = Flask(__name__)
CORS(app)

# --- 1. Load All Pre-computed Models and Stats ---
try:
    books_df = pd.read_pickle('models/books_df.pkl')
    similarity_matrix = pickle.load(open('models/similarity.pkl','rb'))
    author_stats = pickle.load(open('models/author_stats.pkl','rb'))
    genre_stats = pickle.load(open('models/genre_stats.pkl','rb'))
    rating_dist_data = pickle.load(open('models/rating_dist_data.pkl','rb'))
    print("✅ All new models and stats loaded successfully.")
except FileNotFoundError:
    print("❌ Error: Model files not found. Please run the new build_model.py script first.")
    exit()

# --- 2. API Endpoints ---
@app.route('/books', methods=['GET'])
def get_book_titles():
    # The column is now 'book'
    return jsonify(books_df['book'].tolist())

@app.route('/stats', methods=['GET'])
def get_stats():
    # Prepare the stats data for JSON response
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
    # Get the book title from the frontend request
    book_title = request.args.get('title')
    if not book_title:
        return jsonify({"error": "A 'title' query parameter is required."}), 400

    # Find the book in the 'book' column (case-insensitive)
    matching_books = books_df[books_df['book'].str.lower() == book_title.lower()]
    
    if matching_books.empty:
        return jsonify({"error": f"Book '{book_title}' not found in the dataset."}), 404

    # Get the index of the matched book to find it in the similarity matrix
    book_index = matching_books.index[0]
    
    # Get similarity scores and sort them
    sorted_scores = sorted(list(enumerate(similarity_matrix[book_index])), reverse=True, key=lambda x: x[1])
    
    # Get the top 5 most similar books (starting from index 1 to exclude the book itself)
    recommended_books = []
    for i in sorted_scores[1:6]:
        book_data = books_df.iloc[i[0]]
        recommended_books.append({
            "book": book_data['book'],
            "author": book_data['author'],
            "avg_rating": round(book_data['avg_rating'], 2),
            "num_ratings": int(book_data['num_ratings']),
            "genres": book_data['genres'],
            "url": book_data.get('url', '#')
        })
        
    return jsonify(recommended_books)



if __name__ == '__main__':
    app.run(port=5000, debug=True)