"""Data source connectors for extracting data from various sources"""

import requests
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class BaseConnector(ABC):
    """Abstract base class for data source connectors"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def fetch_data(self, **kwargs) -> List[Dict[str, Any]]:
        """Fetch data from the source"""
        pass
    
    @abstractmethod
    def validate_connection(self) -> bool:
        """Validate connection to the data source"""
        pass


class RestApiConnector(BaseConnector):
    """Connector for REST API data sources"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get("base_url")
        self.endpoint = config.get("endpoint")
        self.method = config.get("method", "GET")
        self.headers = config.get("headers", {})
        self.params = config.get("params", {})
        self.auth = config.get("auth")
        self.timeout = config.get("timeout", 30)
    
    def validate_connection(self) -> bool:
        """Validate connection to the REST API"""
        try:
            url = f"{self.base_url}/{self.endpoint}"
            response = requests.head(url, timeout=self.timeout, headers=self.headers)
            is_valid = response.status_code < 400
            self.logger.info(f"Connection validation: {is_valid}")
            return is_valid
        except Exception as e:
            self.logger.error(f"Connection validation failed: {e}")
            return False
    
    def fetch_data(self, 
                   params_override: Optional[Dict[str, Any]] = None,
                   **kwargs) -> List[Dict[str, Any]]:
        """
        Fetch data from REST API
        
        Args:
            params_override: Override default params for this request
            **kwargs: Additional parameters to pass to the request
        
        Returns:
            List of records from the API
        """
        url = f"{self.base_url}/{self.endpoint}"
        params = {**self.params, **(params_override or {})}
        
        try:
            response = requests.request(
                method=self.method,
                url=url,
                headers=self.headers,
                params=params,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Handle different API response formats
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # Try common response wrapper keys
                for key in ["data", "records", "items", "results"]:
                    if key in data:
                        items = data[key]
                        return items if isinstance(items, list) else [items]
                # If no wrapper found, return as single item
                return [data]
            else:
                self.logger.warning(f"Unexpected response type: {type(data)}")
                return []
        
        except requests.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            raise
    
    def fetch_paginated_data(self,
                            page_param: str = "page",
                            limit_param: str = "limit",
                            limit: int = 100,
                            max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetch data with pagination support
        
        Args:
            page_param: Name of the page parameter
            limit_param: Name of the limit parameter
            limit: Records per page
            max_pages: Maximum pages to fetch (None for all)
        
        Returns:
            Combined list of all records
        """
        all_records = []
        page = 1
        
        while True:
            if max_pages and page > max_pages:
                break
            
            params_override = {
                page_param: page,
                limit_param: limit
            }
            
            try:
                records = self.fetch_data(params_override=params_override)
                if not records:
                    break
                
                all_records.extend(records)
                self.logger.info(f"Fetched {len(records)} records from page {page}")
                page += 1
            
            except Exception as e:
                self.logger.error(f"Error fetching page {page}: {e}")
                break
        
        return all_records
