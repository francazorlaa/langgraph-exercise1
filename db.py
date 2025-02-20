import os
import logging
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environmental variables
load_dotenv()

# Logging level and format
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test the connection
def get_database():
    try: 
        # Get MongoDB URI from environment variables
        MONGO_URI = os.getenv("MONGODB_URI")
        # Create a MongoDB client 
        client = MongoClient(MONGO_URI)
        # The ismaster command is cheap and does not require auth
        client.admin.command('ismaster')

        # Using logger
        db = client['test']
        logger.info("Connected to MongoDB")
        return db
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        raise
