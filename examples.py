"""
Example: Using the batch pipeline programmatically

This example shows how to use the batch pipeline components
directly in Python code without the CLI.
"""

from src.connector import RestApiConnector
from src.loader import DataLoader, LoadType
from src.extractor import Extractor
import json


def example_full_load():
    """Example: Full load from JSONPlaceholder Posts API"""
    print("=" * 60)
    print("Example 1: Full Load")
    print("=" * 60)
    
    # Configure the connector
    config = {
        "base_url": "https://jsonplaceholder.typicode.com",
        "endpoint": "posts",
        "method": "GET",
        "headers": {"Accept": "application/json"},
        "params": {}
    }
    
    # Create components
    connector = RestApiConnector(config)
    loader = DataLoader(output_dir="./data")
    extractor = Extractor(connector, loader)
    
    # Extract and load
    result = extractor.extract(
        source_name="posts_fullload",
        load_type=LoadType.FULL_LOAD
    )
    
    print(json.dumps(result, indent=2))
    print()


def example_incremental_load():
    """Example: Incremental load - only append new records"""
    print("=" * 60)
    print("Example 2: Incremental Load")
    print("=" * 60)
    
    config = {
        "base_url": "https://jsonplaceholder.typicode.com",
        "endpoint": "users",
        "method": "GET",
        "headers": {"Accept": "application/json"},
        "params": {}
    }
    
    connector = RestApiConnector(config)
    loader = DataLoader(output_dir="./data")
    extractor = Extractor(connector, loader)
    
    # First load - full load
    result1 = extractor.extract(
        source_name="users_incremental",
        load_type=LoadType.FULL_LOAD
    )
    print("First extraction (full load):")
    print(f"  Records loaded: {result1['load_metadata']['records_loaded']}")
    
    # Second load - incremental (should add 0 since same data)
    result2 = extractor.extract(
        source_name="users_incremental",
        load_type=LoadType.INCREMENTAL,
        key_column="id"
    )
    print("\nSecond extraction (incremental load):")
    print(f"  Records loaded: {result2['load_metadata']['records_loaded']}")
    print()


def example_upsert_load():
    """Example: Upsert load - update or insert based on key"""
    print("=" * 60)
    print("Example 3: Upsert Load")
    print("=" * 60)
    
    config = {
        "base_url": "https://jsonplaceholder.typicode.com",
        "endpoint": "comments",
        "method": "GET",
        "headers": {"Accept": "application/json"},
        "params": {"_limit": 10}
    }
    
    connector = RestApiConnector(config)
    loader = DataLoader(output_dir="./data")
    extractor = Extractor(connector, loader)
    
    # First load - full load with limited records
    result1 = extractor.extract(
        source_name="comments_upsert",
        load_type=LoadType.FULL_LOAD
    )
    print("First extraction (full load):")
    print(f"  Records loaded: {result1['load_metadata']['records_loaded']}")
    
    # Second load - upsert (updates existing, keeps new)
    result2 = extractor.extract(
        source_name="comments_upsert",
        load_type=LoadType.UPSERT,
        key_column="id"
    )
    print("\nSecond extraction (upsert load):")
    print(f"  Records processed: {result2['load_metadata']['records_processed']}")
    print(f"  Records loaded: {result2['load_metadata']['records_loaded']}")
    print()


def example_paginated_load():
    """Example: Load data with pagination"""
    print("=" * 60)
    print("Example 4: Paginated Load")
    print("=" * 60)
    
    config = {
        "base_url": "https://jsonplaceholder.typicode.com",
        "endpoint": "posts",
        "method": "GET",
        "headers": {"Accept": "application/json"},
        "params": {}
    }
    
    connector = RestApiConnector(config)
    loader = DataLoader(output_dir="./data")
    extractor = Extractor(connector, loader)
    
    # Extract paginated data (limited to 2 pages for demo)
    result = extractor.extract_paginated(
        source_name="posts_paginated",
        load_type=LoadType.FULL_LOAD,
        page_param="_page",
        limit_param="_limit",
        limit=25,
        max_pages=2
    )
    
    print(json.dumps(result, indent=2))
    print()


if __name__ == "__main__":
    example_full_load()
    example_incremental_load()
    example_upsert_load()
    example_paginated_load()
