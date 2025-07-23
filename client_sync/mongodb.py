"""
MongoDB connection utility for Django project.
Uses pymongo for direct MongoDB access.
"""

from pymongo import MongoClient
from decouple import config
import logging

logger = logging.getLogger(__name__)

class MongoDBConnection:
    """MongoDB connection manager"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB"""
        try:
            # Get MongoDB configuration from environment
            mongo_user = config('MONGO_USER', default='client_sync_user')
            mongo_password = config('MONGO_PASSWORD', default='client_sync_password')
            mongo_host = config('MONGO_HOST', default='localhost')
            mongo_port = config('MONGO_PORT', default='27017')
            mongo_db = config('MONGO_DB', default='client_sync_mongo')
            
            # Create connection string
            connection_string = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/"
            
            # Connect to MongoDB
            self.client = MongoClient(connection_string)
            self.db = self.client[mongo_db]
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def get_collection(self, collection_name):
        """Get a MongoDB collection"""
        if not self.db:
            self._connect()
        return self.db[collection_name]
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

# Global MongoDB connection instance
mongodb = MongoDBConnection()

def get_mongodb_collection(collection_name):
    """Helper function to get a MongoDB collection"""
    return mongodb.get_collection(collection_name)

def close_mongodb_connection():
    """Helper function to close MongoDB connection"""
    mongodb.close() 