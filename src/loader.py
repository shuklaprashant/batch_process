"""Data loader with support for different load types"""

import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from enum import Enum
from datetime import datetime


class LoadType(Enum):
    """Supported load types for data loading"""
    FULL_LOAD = "full_load"
    INCREMENTAL = "incremental"
    UPSERT = "upsert"


class DataLoader:
    """Loads data to local storage with support for multiple load types"""
    
    def __init__(self, output_dir: str = "./data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def load_data(self,
                  records: List[Dict[str, Any]],
                  filename: str,
                  load_type: LoadType = LoadType.FULL_LOAD,
                  key_column: Optional[str] = None) -> Dict[str, Any]:
        """
        Load data using the specified load type
        
        Args:
            records: List of records to load
            filename: Output filename (without extension)
            load_type: Type of load operation
            key_column: Column to use as key for upsert/incremental operations
        
        Returns:
            Load metadata with record counts
        """
        file_path = self.output_dir / f"{filename}.json"
        metadata = {
            "filename": filename,
            "load_type": load_type.value,
            "timestamp": datetime.now().isoformat(),
            "records_processed": len(records),
            "records_loaded": 0
        }
        
        try:
            if load_type == LoadType.FULL_LOAD:
                metadata["records_loaded"] = self._full_load(records, file_path)
            
            elif load_type == LoadType.INCREMENTAL:
                if not key_column:
                    raise ValueError("key_column is required for incremental load")
                metadata["records_loaded"] = self._incremental_load(
                    records, file_path, key_column
                )
            
            elif load_type == LoadType.UPSERT:
                if not key_column:
                    raise ValueError("key_column is required for upsert load")
                metadata["records_loaded"] = self._upsert_load(
                    records, file_path, key_column
                )
            
            self.logger.info(
                f"Load completed: {metadata['records_loaded']} records loaded "
                f"({load_type.value}) to {file_path}"
            )
            return metadata
        
        except Exception as e:
            self.logger.error(f"Load failed: {e}")
            metadata["error"] = str(e)
            return metadata
    
    def _full_load(self, records: List[Dict[str, Any]], file_path: Path) -> int:
        """
        Full load: Replace entire file with new data
        
        Returns:
            Number of records loaded
        """
        with open(file_path, "w") as f:
            json.dump(records, f, indent=2, default=str)
        return len(records)
    
    def _incremental_load(self,
                          records: List[Dict[str, Any]],
                          file_path: Path,
                          key_column: str) -> int:
        """
        Incremental load: Append new records that don't exist in file
        
        Returns:
            Number of records loaded
        """
        existing_records = self._read_existing(file_path)
        existing_keys = {rec.get(key_column) for rec in existing_records}
        
        new_records = [
            rec for rec in records
            if rec.get(key_column) not in existing_keys
        ]
        
        combined = existing_records + new_records
        
        with open(file_path, "w") as f:
            json.dump(combined, f, indent=2, default=str)
        
        self.logger.info(
            f"Incremental load: {len(new_records)} new records added "
            f"(existing: {len(existing_records)})"
        )
        return len(new_records)
    
    def _upsert_load(self,
                     records: List[Dict[str, Any]],
                     file_path: Path,
                     key_column: str) -> int:
        """
        Upsert load: Insert new records or update existing ones based on key
        
        Returns:
            Number of records loaded (inserted + updated)
        """
        existing_records = self._read_existing(file_path)
        
        # Create a map of existing records by key
        existing_map = {
            rec.get(key_column): rec
            for rec in existing_records
        }
        
        records_upserted = 0
        
        # Upsert new records
        for record in records:
            key_value = record.get(key_column)
            if key_value in existing_map:
                existing_map[key_value].update(record)
                self.logger.debug(f"Updated record with key: {key_value}")
            else:
                existing_map[key_value] = record
                records_upserted += 1
                self.logger.debug(f"Inserted record with key: {key_value}")
        
        combined = list(existing_map.values())
        
        with open(file_path, "w") as f:
            json.dump(combined, f, indent=2, default=str)
        
        self.logger.info(
            f"Upsert load: {records_upserted} new records inserted, "
            f"{len(records) - records_upserted} records updated"
        )
        return len(records)
    
    def _read_existing(self, file_path: Path) -> List[Dict[str, Any]]:
        """Read existing records from file"""
        if not file_path.exists():
            return []
        
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                return data if isinstance(data, list) else [data]
        except json.JSONDecodeError:
            self.logger.warning(f"Could not parse existing file: {file_path}")
            return []
