import logging
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionError, OperationFailure

logger = logging.getLogger(__name__)


class MongoDBHandler:
    def __init__(
        self,
        connection_string="mongodb://localhost:27017/",
        database_name="job_scraper",
    ):
        """Initialize MongoDB connection"""
        try:
            self.client = MongoClient(connection_string)
            self.db = self.client[database_name]
            self.jobs_collection = self.db.jobs

            # Create indexes
            self.jobs_collection.create_index([("url", 1)], unique=True)
            self.jobs_collection.create_index([("title", 1), ("company", 1)])

            logger.info("Successfully connected to MongoDB")
        except ConnectionError as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise

    def save_job(self, job_data):
        """Save a single job to MongoDB"""
        try:
            # Add timestamp if not present
            if "scraped_at" not in job_data:
                job_data["scraped_at"] = datetime.now().isoformat()

            # Use URL as unique identifier
            if "url" in job_data:
                result = self.jobs_collection.update_one(
                    {"url": job_data["url"]}, {"$set": job_data}, upsert=True
                )
                return result.upserted_id or result.modified_count
            else:
                result = self.jobs_collection.insert_one(job_data)
                return result.inserted_id
        except Exception as e:
            logger.error(f"Error saving job to MongoDB: {str(e)}")
            return None

    def save_jobs(self, jobs):
        """Save multiple jobs to MongoDB"""
        try:
            successful_saves = 0
            for job in jobs:
                if self.save_job(job):
                    successful_saves += 1

            logger.info(
                f"Successfully saved {successful_saves} out of {len(jobs)} jobs"
            )
            return successful_saves
        except Exception as e:
            logger.error(f"Error saving jobs to MongoDB: {str(e)}")
            return 0

    def get_job_by_url(self, url):
        """Retrieve a job by its URL"""
        try:
            return self.jobs_collection.find_one({"url": url})
        except Exception as e:
            logger.error(f"Error retrieving job by URL: {str(e)}")
            return None

    def get_jobs_by_query(self, query=None, limit=100):
        """Retrieve jobs matching a query"""
        try:
            return list(self.jobs_collection.find(query or {}).limit(limit))
        except Exception as e:
            logger.error(f"Error retrieving jobs: {str(e)}")
            return []

    def close(self):
        """Close MongoDB connection"""
        try:
            self.client.close()
            logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {str(e)}")
