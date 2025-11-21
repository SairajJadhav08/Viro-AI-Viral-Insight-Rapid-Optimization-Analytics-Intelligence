"""
Script to fix _store_results method to use raw SQL instead of ORM
This avoids the created_at column issue
"""
# This is a helper script - the actual fix will be in processing_service.py

