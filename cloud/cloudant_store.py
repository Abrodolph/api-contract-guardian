"""
IBM Cloudant storage module for API Contract Guardian verdicts.
Connects using environment variables: CLOUDANT_URL, CLOUDANT_API_KEY, CLOUDANT_DB_NAME
"""

import os
from typing import Optional
from datetime import datetime, timezone, timedelta
from cloudant.client import Cloudant
from cloudant.error import CloudantException
import uuid


class CloudantStore:
    """Manages verdict storage in IBM Cloudant database."""
    
    def __init__(self):
        """Initialize Cloudant client from environment variables."""
        self.url = os.getenv("CLOUDANT_URL")
        self.api_key = os.getenv("CLOUDANT_API_KEY")
        self.db_name = os.getenv("CLOUDANT_DB_NAME", "verdicts")
        
        self.client = None
        self.db = None
        
        if self.url and self.api_key:
            self._connect()
    
    def _connect(self):
        """Establish connection to Cloudant and get database reference."""
        try:
            self.client = Cloudant.iam(
                account_name=None,
                api_key=self.api_key,
                url=self.url,
                connect=True
            )
            
            # Create database if it doesn't exist
            if self.db_name not in self.client.all_dbs():
                self.db = self.client.create_database(self.db_name)
            else:
                self.db = self.client[self.db_name]
                
        except CloudantException as e:
            print(f"Failed to connect to Cloudant: {e}")
            self.client = None
            self.db = None
    
    def is_connected(self) -> bool:
        """Check if Cloudant connection is active."""
        return self.client is not None and self.db is not None
    
    def save_verdict(self, verdict_json: dict) -> dict:
        """
        Store a verdict document with UUID and ISO timestamp added server-side.
        
        Args:
            verdict_json: Dictionary containing verdict, change_summary, affected_field,
                         blast_radius, and reasoning fields.
        
        Returns:
            The stored document with its _id field.
        
        Raises:
            CloudantException: If storage fails.
        """
        if not self.is_connected():
            raise CloudantException("Not connected to Cloudant")
        
        # Add server-side fields
        doc = {
            "_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **verdict_json
        }
        
        # Store in Cloudant
        result = self.db.create_document(doc)
        
        if not result.exists():
            raise CloudantException("Failed to create document")
        
        return result
    
    def get_all_verdicts(self) -> list[dict]:
        """
        Retrieve all verdict documents sorted newest-first.
        
        Returns:
            List of verdict documents.
        """
        if not self.is_connected():
            raise CloudantException("Not connected to Cloudant")
        
        # Query all documents, sorted by timestamp descending
        selector = {
            "timestamp": {"$exists": True}
        }
        
        docs = self.db.get_query_result(
            selector=selector,
            sort=[{"timestamp": "desc"}]
        )
        
        return [doc for doc in docs]
    
    def get_verdict_by_id(self, id: str) -> Optional[dict]:
        """
        Retrieve a single verdict document by its _id.
        
        Args:
            id: The document _id to retrieve.
        
        Returns:
            The verdict document, or None if not found.
        """
        if not self.is_connected():
            raise CloudantException("Not connected to Cloudant")
        
        try:
            doc = self.db[id]
            return dict(doc)
        except KeyError:
            return None
    
    def get_contract_health(self) -> dict:
        """
        Get counts of BREAKING/SAFE/REVIEW verdicts grouped by day for the last 30 days.
        Used for trend chart visualization.
        
        Returns:
            Dictionary with structure:
            {
                "days": ["2026-05-17", "2026-05-16", ...],
                "breaking": [2, 1, 0, ...],
                "safe": [5, 3, 2, ...],
                "review": [1, 0, 1, ...]
            }
        """
        if not self.is_connected():
            raise CloudantException("Not connected to Cloudant")
        
        # Calculate date range (last 30 days)
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=30)
        
        # Query documents in date range
        selector = {
            "timestamp": {
                "$gte": start_date.isoformat(),
                "$lte": end_date.isoformat()
            }
        }
        
        docs = self.db.get_query_result(selector=selector)
        
        # Initialize counters for each day
        day_counts = {}
        for i in range(31):  # Include today
            day = (end_date - timedelta(days=i)).date().isoformat()
            day_counts[day] = {"BREAKING": 0, "SAFE": 0, "REVIEW": 0}
        
        # Count verdicts by day
        for doc in docs:
            timestamp = doc.get("timestamp", "")
            verdict = doc.get("verdict", "")
            
            if timestamp and verdict:
                day = timestamp[:10]  # Extract YYYY-MM-DD
                if day in day_counts:
                    day_counts[day][verdict] = day_counts[day].get(verdict, 0) + 1
        
        # Convert to chart-friendly format (newest first)
        days = sorted(day_counts.keys(), reverse=True)
        
        return {
            "days": days,
            "breaking": [day_counts[day]["BREAKING"] for day in days],
            "safe": [day_counts[day]["SAFE"] for day in days],
            "review": [day_counts[day]["REVIEW"] for day in days]
        }
    
    def close(self):
        """Close the Cloudant connection."""
        if self.client:
            self.client.disconnect()


# Singleton instance
_store = CloudantStore()


# Public API functions
def save_verdict(verdict_json: dict) -> dict:
    """Store a verdict document. Returns the stored document with its _id."""
    return _store.save_verdict(verdict_json)


def get_all_verdicts() -> list[dict]:
    """Retrieve all verdict documents sorted newest-first."""
    return _store.get_all_verdicts()


def get_verdict_by_id(id: str) -> Optional[dict]:
    """Retrieve a single verdict document by _id."""
    return _store.get_verdict_by_id(id)


def get_contract_health() -> dict:
    """Get verdict counts grouped by day for the last 30 days."""
    return _store.get_contract_health()


def is_cloudant_available() -> bool:
    """Check if Cloudant connection is available."""
    return _store.is_connected()

# Made with Bob
