# backend/app/api/articles.py

from flask import Blueprint, request, jsonify
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

# Initialize Flask Blueprint
articles_bp = Blueprint('articles', __name__)

# MongoDB Connection (replace with your actual connection string and credentials)
# For demonstration, using a placeholder. In a real application, use environment variables.
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'ai_news_db')

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
articles_collection = db.articles
categories_collection = db.categories # Assuming categories collection exists for lookups

@articles_bp.route('/ingest', methods=['POST'])
def ingest_article():
    """
    API endpoint to ingest articles from trusted sources.
    Parses content, extracts metadata, and stores in MongoDB.
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    # --- Data Validation and Extraction ---
    required_fields = ['title', 'full_content_url', 'publication_date', 'source']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"error": f"Missing or empty required field: {field}"}), 400

    try:
        # Convert publication_date string to datetime object
        publication_date = datetime.fromisoformat(data['publication_date'].replace('Z', '+00:00'))
    except ValueError:
        return jsonify({"error": "Invalid publication_date format. Use ISO 8601 (e.g., YYYY-MM-DDTHH:MM:SSZ)"}), 400

    # Extract optional fields with default empty values
    summary = data.get('summary', '')
    image_url = data.get('image_url', '')
    source_url = data.get('source_url', '')
    keywords = data.get('keywords', [])
    category_names = data.get('categories', []) # Expecting a list of category names

    # Resolve category names to ObjectIds
    category_ids = []
    if category_names:
        # In a real scenario, you'd query the categories_collection to get ObjectIds
        # For this example, we'll simulate finding them or creating placeholders
        for cat_name in category_names:
            category = categories_collection.find_one({"name": cat_name})
            if category:
                category_ids.append(category['_id'])
            else:
                # Optionally, create new categories or log a warning for unknown categories
                print(f"Warning: Category '{cat_name}' not found. Skipping or creating placeholder.")
                # For demonstration, let's add a placeholder ObjectId if not found
                # In a real app, you might want to enforce existing categories or create them
                category_ids.append(ObjectId()) # Placeholder for demonstration

    # Construct the article document based on the MongoDB schema
    article_doc = {
        "title": data['title'],
        "summary": summary,
        "full_content_url": data['full_content_url'],
        "image_url": image_url,
        "publication_date": publication_date,
        "source": data['source'],
        "source_url": source_url,
        "category_ids": category_ids,
        "keywords": keywords,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    # --- Store in MongoDB ---
    try:
        # Check for duplicate article based on full_content_url to prevent re-ingestion
        if articles_collection.find_one({"full_content_url": article_doc["full_content_url"]}):
            return jsonify({"message": "Article already exists", "url": article_doc["full_content_url"]}), 200

        result = articles_collection.insert_one(article_doc)
        return jsonify({"message": "Article ingested successfully", "article_id": str(result.inserted_id)}), 201
    except Exception as e:
        print(f"Error ingesting article: {e}")
        return jsonify({"error": "Internal server error during article ingestion"}), 500

# Example of how to integrate this blueprint into a Flask app (e.g., in app.py)
'''
# from flask import Flask
# from app.api.articles import articles_bp
#
# app = Flask(__name__)
# app.register_blueprint(articles_bp, url_prefix='/articles')
#
# if __name__ == '__main__':
#     app.run(debug=True)
'''