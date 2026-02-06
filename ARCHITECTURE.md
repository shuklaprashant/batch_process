# Batch Pipeline Architecture

## Overview

Batch Pipeline is an extensible data extraction and loading framework inspired by Meltano. It provides a modular, configuration-driven approach to building batch ETL/ELT pipelines with support for multiple load types.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Configuration                           │
│                   (source_config.json)                       │
└────────────────────────────────────────────────────────────┬┘
                                                               │
                    ┌───────────────────────────────────────┴─┐
                    │                                         │
              ┌─────▼──────┐                         ┌────────▼─────┐
              │   Config   │                         │   CLI/Main   │
              │   Manager  │                         │              │
              └─────┬──────┘                         └────────┬─────┘
                    │                                         │
         ┌──────────┴───────────────────────────────────────┐
         │                                                  │
    ┌────▼────────┐                              ┌────────▼──────┐
    │  Connector  │                              │   Extractor   │
    │ (Data Source)                              │  (Orchestrator)
    │             │                              │                │
    │ • REST API  │                              │ • Validation   │
    │ • Database  │◄──────────────────────────────┤ • Extraction  │
    │ • File      │                              │ • Loading      │
    │ • Custom    │                              │ • Logging      │
    └────┬────────┘                              └────────┬──────┘
         │                                                │
         │                                                │
         │     Records (List[Dict])                       │
         │     ◄──────────────────────────────────────────┤
         │                                                │
         └──────────────────────┬──────────────────────────┘
                                │
                           ┌────▼──────────┐
                           │    Loader     │
                           │               │
                           │ • Full Load   │
                           │ • Incremental │
                           │ • Upsert      │
                           └────┬──────────┘
                                │
                                │ JSON Files
                                │
                           ┌────▼──────────┐
                           │  Data Storage  │
                           │  (./data/)     │
                           └────────────────┘
```

## Core Components

### 1. Configuration Manager (`config.py`)

**Responsibility**: Load and manage pipeline configuration

**Key Features**:
- Load JSON configuration files
- Validate configuration structure
- Provide easy access to source definitions
- Support for multiple sources in single config

**Usage**:
```python
config = Config("config/source_config.json")
source_config = config.get_source("jsonplaceholder_posts")
```

### 2. Connectors (`connector.py`)

**Responsibility**: Abstract data source connectivity

**Architecture**:
- `BaseConnector`: Abstract base class defining connector interface
- `RestApiConnector`: Implementation for REST APIs
- Extensible design for custom connectors

**Key Features**:
- Connection validation
- Flexible data fetching
- Pagination support
- Customizable headers, params, authentication
- Error handling and logging

**Extensibility**:
```python
class DatabaseConnector(BaseConnector):
    def validate_connection(self) -> bool:
        # Implement database connection validation
        pass
    
    def fetch_data(self, **kwargs):
        # Implement database query
        pass
```

### 3. Data Loader (`loader.py`)

**Responsibility**: Load data using different load type strategies

**Load Types**:

#### Full Load
- Replaces entire file with new data
- Use: Initial loads, complete refreshes
- Implementation: Overwrite file completely

#### Incremental Load
- Appends only new records (by unique key)
- Use: Append-only scenarios
- Implementation: Compare keys, add only new records

#### Upsert Load
- Insert new records, update existing ones
- Use: Synchronization scenarios
- Implementation: Merge on key, update/insert as needed

**Key Features**:
- Configurable key columns
- Atomic operations
- Detailed logging of load operations
- Error handling and recovery

### 4. Extractor (`extractor.py`)

**Responsibility**: Orchestrate extraction workflow

**Key Features**:
- Coordinate connector and loader
- Validate connections before extraction
- Handle extraction lifecycle
- Support pagination
- Track extraction history
- Comprehensive error handling

**Workflow**:
1. Validate connector connection
2. Fetch data from source
3. Load data using specified strategy
4. Record metadata and status
5. Return results

### 5. CLI Interface (`main.py`)

**Responsibility**: Provide command-line interface

**Commands**:
- `extract`: Extract and load data
- `list-sources`: Show configured sources
- `validate-connection`: Test source connectivity

**Design**:
- Click-based CLI framework
- Supports multiple output formats
- Detailed logging and error messages

## Data Flow

### Extraction Process

```
1. CLI Request (extract --source X --load-type Y)
   │
   ├─► Load Configuration
   │   └─► Get source config
   │
   ├─► Create Connector
   │   └─► RestApiConnector with config
   │
   ├─► Create Extractor
   │   └─► Initialize with connector
   │
   ├─► Validate Connection
   │   └─► connector.validate_connection()
   │
   ├─► Fetch Data
   │   └─► connector.fetch_data()
   │       └─► Returns List[Dict]
   │
   ├─► Load Data
   │   └─► loader.load_data(records, filename, load_type, key_column)
   │       ├─► Full Load: Replace file
   │       ├─► Incremental: Append new records
   │       └─► Upsert: Insert/update by key
   │
   └─► Return Results
       └─► Metadata with record counts and status
```

## Configuration Structure

```json
{
  "pipeline": {
    "name": "Pipeline Name",
    "version": "0.1.0"
  },
  "sources": {
    "source_name": {
      "type": "rest_api",
      "base_url": "https://api.example.com",
      "endpoint": "data",
      "method": "GET",
      "headers": {},
      "params": {},
      "timeout": 30
    }
  },
  "load_config": {
    "default_load_type": "full_load",
    "output_directory": "./data"
  }
}
```

## Design Patterns

### 1. Strategy Pattern
- LoadType strategies (FullLoad, Incremental, Upsert)
- Different algorithms for different load requirements

### 2. Template Method Pattern
- BaseConnector defines interface
- Subclasses implement specific behavior

### 3. Factory Pattern
- Configuration-driven connector creation
- Extensible source management

### 4. Observer Pattern
- Extraction history tracking
- Status monitoring

## Extension Points

### Adding New Connectors

Implement the `BaseConnector` interface:
```python
class CustomConnector(BaseConnector):
    def validate_connection(self) -> bool:
        pass
    
    def fetch_data(self, **kwargs) -> List[Dict[str, Any]]:
        pass
```

### Adding New Load Types

Extend the `LoadType` enum and loader logic:
```python
class LoadType(Enum):
    CUSTOM_LOAD = "custom_load"
```

### Custom Loaders

Subclass `DataLoader` for specialized output formats:
```python
class ParquetLoader(DataLoader):
    def load_data(self, records, filename, load_type):
        # Load to Parquet instead of JSON
        pass
```

## Dependencies

- **requests**: HTTP client for REST API
- **pydantic**: Data validation
- **click**: CLI framework
- **pyyaml/json**: Configuration parsing

## Performance Considerations

### Pagination
- Use `extract_paginated()` for large datasets
- Configurable page size and limits

### Memory Management
- Streams data processing
- No full dataset in memory
- Configurable batch processing

### Connection Pooling
- Reuse HTTP connections
- Configurable timeouts

## Error Handling

- Connection validation before operations
- Graceful degradation
- Detailed error logging
- Extraction history for debugging

## Testing Strategy

### Unit Tests
- Connector functionality
- Loader operations
- Configuration management

### Integration Tests
- End-to-end extraction
- Load type validation
- Error scenarios

### Docker Tests
- Image building
- Container execution
- Volume mounting

## Future Enhancements

1. **Database Connectors**
   - PostgreSQL, MySQL, MongoDB
   - Direct database-to-database loading

2. **File Format Support**
   - Parquet, CSV, Avro
   - Schema validation

3. **Scheduling**
   - Cron-based execution
   - DAG workflows (similar to Airflow)

4. **Data Quality**
   - Schema validation
   - Data profiling
   - Quality metrics

5. **Metadata Management**
   - Data lineage
   - Column-level metadata
   - Transformation tracking

6. **Transformation Pipeline**
   - dbt integration
   - Custom transformations
   - Predefined recipes

## Related Projects

- **Meltano**: Open-source data integration tool
- **Airbyte**: Data integration platform
- **Dbt**: Data transformation tool
- **Apache Airflow**: Workflow orchestration
