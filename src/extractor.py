"""Main Extractor class - orchestrates data extraction process"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.connector import BaseConnector
from src.loader import DataLoader, LoadType


class Extractor:
    """
    Main extractor class that orchestrates data extraction from a source
    and loads it using specified load type
    """
    
    def __init__(self, 
                 connector: BaseConnector,
                 loader: Optional[DataLoader] = None):
        """
        Initialize extractor
        
        Args:
            connector: Data source connector
            loader: Data loader (creates default if not provided)
        """
        self.connector = connector
        self.loader = loader or DataLoader()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.extraction_history = []
    
    def extract(self,
                source_name: str,
                load_type: LoadType = LoadType.FULL_LOAD,
                key_column: Optional[str] = None,
                **connector_kwargs) -> Dict[str, Any]:
        """
        Extract data from source and load it
        
        Args:
            source_name: Name of the source for file naming
            load_type: Type of load operation
            key_column: Key column for upsert/incremental loads
            **connector_kwargs: Additional arguments for connector.fetch_data
        
        Returns:
            Extraction result with metadata
        """
        self.logger.info(f"Starting extraction from {source_name}")
        
        result = {
            "source_name": source_name,
            "status": "pending",
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "extraction_metadata": {},
            "load_metadata": {}
        }
        
        try:
            # Validate connection
            if not self.connector.validate_connection():
                raise Exception("Connection validation failed")
            
            # Extract data
            self.logger.info(f"Fetching data from {source_name}")
            records = self.connector.fetch_data(**connector_kwargs)
            
            result["extraction_metadata"] = {
                "records_fetched": len(records),
                "timestamp": datetime.now().isoformat()
            }
            
            if not records:
                self.logger.warning(f"No records fetched from {source_name}")
                result["status"] = "completed_with_no_data"
            else:
                # Load data
                load_result = self.loader.load_data(
                    records=records,
                    filename=source_name,
                    load_type=load_type,
                    key_column=key_column
                )
                
                result["load_metadata"] = load_result
                result["status"] = "success"
            
        except Exception as e:
            self.logger.error(f"Extraction failed: {e}")
            result["status"] = "failed"
            result["error"] = str(e)
        
        finally:
            result["end_time"] = datetime.now().isoformat()
            self.extraction_history.append(result)
        
        return result
    
    def extract_paginated(self,
                         source_name: str,
                         load_type: LoadType = LoadType.FULL_LOAD,
                         key_column: Optional[str] = None,
                         page_param: str = "page",
                         limit_param: str = "limit",
                         limit: int = 100,
                         max_pages: Optional[int] = None) -> Dict[str, Any]:
        """
        Extract paginated data from source
        
        Args:
            source_name: Name of the source
            load_type: Type of load operation
            key_column: Key column for upsert/incremental loads
            page_param: Name of page parameter
            limit_param: Name of limit parameter
            limit: Records per page
            max_pages: Maximum pages to fetch
        
        Returns:
            Extraction result
        """
        self.logger.info(f"Starting paginated extraction from {source_name}")
        
        result = {
            "source_name": source_name,
            "status": "pending",
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "extraction_metadata": {},
            "load_metadata": {},
            "pagination": {
                "page_param": page_param,
                "limit_param": limit_param,
                "limit": limit,
                "max_pages": max_pages
            }
        }
        
        try:
            # Validate connection
            if not self.connector.validate_connection():
                raise Exception("Connection validation failed")
            
            # Extract paginated data
            self.logger.info(f"Fetching paginated data from {source_name}")
            records = self.connector.fetch_paginated_data(
                page_param=page_param,
                limit_param=limit_param,
                limit=limit,
                max_pages=max_pages
            )
            
            result["extraction_metadata"] = {
                "records_fetched": len(records),
                "timestamp": datetime.now().isoformat()
            }
            
            if not records:
                self.logger.warning(f"No records fetched from {source_name}")
                result["status"] = "completed_with_no_data"
            else:
                # Load data
                load_result = self.loader.load_data(
                    records=records,
                    filename=source_name,
                    load_type=load_type,
                    key_column=key_column
                )
                
                result["load_metadata"] = load_result
                result["status"] = "success"
        
        except Exception as e:
            self.logger.error(f"Extraction failed: {e}")
            result["status"] = "failed"
            result["error"] = str(e)
        
        finally:
            result["end_time"] = datetime.now().isoformat()
            self.extraction_history.append(result)
        
        return result
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get extraction history"""
        return self.extraction_history
