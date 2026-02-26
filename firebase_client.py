"""
Firebase Firestore client for state management and real-time data streaming.
CRITICAL: All database and state management MUST use this module.
"""
import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin.exceptions import FirebaseError
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import json
from google.api_core.exceptions import GoogleAPIError

class FirebaseClient:
    """Singleton Firebase Firestore client with error handling"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseClient, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, config):
        if not self._initialized:
            self.config = config
            self._initialize_firebase()
            self._initialized = True
    
    def _initialize_firebase(self) -> None:
        """Initialize Firebase Admin SDK with error handling"""
        try:
            # Initialize with credentials
            cred = credentials.Certificate(self.config.firebase.credentials_path)
            firebase_admin.initialize_app(cred, {
                'projectId': self.config.firebase.project_id
            })
            self.db = firestore.client()
            logging.info(f"Firebase initialized for project: {self.config.firebase.project_id}")
            
            # Test connection
            self._test_connection()
            
        except FileNotFoundError as