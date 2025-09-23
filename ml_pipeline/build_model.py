# ml_pipeline/build_model.py

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
import re

print("🚀 Starting the advanced model building process...")

# --- 1. Load the New Dataset ---
try:
    # IMPORTANT: Update this to the name of your new CSV file.
    df = pd.read_csv('jealousleopard-goodreads-books/books.csv', thousands=',')
    print("✅ New dataset loaded successfully.")
except FileNotFoundError:
    print("❌ Error: books.csv not found. Please place it in the ml_pipeline folder and update the filename.")
    exit()

# --- 2. Preprocess and Clean Data ---
# Standardize column names to be lowercase and free of spaces
df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

# Define the columns we expect to use
required_columns = ['book', 'author', 'description', 'genres', 'avg_rating', 'num_ratings']
for col in required_columns:
    if col not in df.columns:
        print(f"❌ Error: Required column '{col}' not found in the dataset.")
        exit()

# Handle missing values in key text fields
df.dropna(subset=['book', 'author', 'description', 'genres'], inplace=True)

# Clean the genres column by removing special characters and extra spaces
def clean_genres(genres_str):
    # The genres seem to be in a string like "['Fiction', 'Dystopian']"
    # We'll extract the words.
    if isinstance(genres_str, str):
        return ' '.join(re.findall(r"\w+", genres_str))
    return ''
df['genres'] = df['genres'].apply(clean_genres)

print(f"⚙️ Processing {len(df)} books after cleaning.")

# --- 3. Feature Engineering for Recommendations (Upgraded) ---
# Create a rich 'tags' field by combining all relevant text data
df['tags'] = df['book'] + ' ' + df['author'] + ' ' + df['description'] + ' ' + df['genres']

# Use TF-IDF to convert the text 'tags' into numerical vectors
tfidf = TfidfVectorizer(stop_words='english', max_features=5000)
tfidf_matrix = tfidf.fit_transform(df['tags'])

print("📐 Calculating cosine similarity based on rich features...")
similarity_matrix = cosine_similarity(tfidf_matrix)

# --- 4. Calculate Advanced Insights ---
print("📊 Calculating new advanced insights...")

# Top 20 Most Popular Authors (by total number of ratings)
author_stats = df.groupby('author')['num_ratings'].sum().sort_values(ascending=False).head(20)

# Top 20 Most Frequent Genres
# We need to split the genre strings and count each one
all_genres = df['genres'].str.split(expand=True).stack()
genre_stats = all_genres.value_counts().head(20)

# Data for Rating Distribution Histogram
rating_dist_data = df['avg_rating'].value_counts().sort_index()

print("✅ Insights calculated successfully.")

# --- 5. Save All Artifacts ---
# This is the corrected block. Replace the old code with this.

os.makedirs('../backend_api/models', exist_ok=True)

pickle.dump(similarity_matrix, open('../backend_api/models/similarity.pkl', 'wb'))
pickle.dump(df, open('../backend_api/models/books_df.pkl', 'wb'))
pickle.dump(author_stats, open('../backend_api/models/author_stats.pkl', 'wb'))
pickle.dump(genre_stats, open('../backend_api/models/genre_stats.pkl', 'wb'))
pickle.dump(rating_dist_data, open('../backend_api/models/rating_dist_data.pkl', 'wb')) # This line was likely incomplete

print("💾 All new model artifacts and stats have been saved successfully.")