# Batch Pipeline

A production-ready batch data extraction and loading pipeline with support for multiple load types and extensible connector architecture.

## Features

- 🔌 **Extensible Connector Architecture** - Easy to add new data sources (REST API, databases, files, etc.)
- 📦 **Multiple Load Types** - Full Load, Incremental, and Upsert support
- 🐳 **Docker Support** - Containerized for easy deployment
- ⚙️ **Configuration-Driven** - JSON-based configuration for sources
- 📝 **Comprehensive Logging** - Built-in logging for monitoring and debugging
- 🔄 **Pagination Support** - Handle large datasets with pagination
- 🛡️ **Error Handling** - Robust error handling and recovery

## Project Structure

```
batch-pipeline/
├── config/                 # Configuration files
│   └── source_config.json # Source definitions
├── data/                   # Output directory for loaded data
├── schemas/               # JSON schemas for validation
├── src/
│   ├── __init__.py
│   ├── main.py           # CLI entry point
│   ├── extractor.py      # Main extractor orchestrator
│   ├── connector.py      # Data source connectors
│   ├── loader.py         # Data loaders with load type support
│   └── config.py         # Configuration management
├── tests/                # Unit tests
├── Dockerfile            # Docker image definition
├── docker-compose.yml    # Docker Compose configuration
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Installation

### Local Setup

```bash
# Clone or navigate to the project
cd batch-pipeline

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Docker Setup

```bash
# Build the Docker image
docker build -t batch-pipeline:latest .

# Or use Docker Compose
docker-compose build
```

## Usage

### List Configured Sources

```bash
python -m src.main list-sources
```

### Extract Data - Full Load

Load entire dataset, replacing existing data:

```bash
python -m src.main extract \
  --source jsonplaceholder_posts \
  --load-type full_load
```

### Extract Data - Incremental Load

Append only new records (records not in existing file):

```bash
python -m src.main extract \
  --source jsonplaceholder_posts \
  --load-type incremental \
  --key-column id
```

### Extract Data - Upsert Load

Insert new records or update existing ones based on key:

```bash
python -m src.main extract \
  --source jsonplaceholder_posts \
  --load-type upsert \
  --key-column id
```

### Validate Connection

Test connectivity to a data source:

```bash
python -m src.main validate-connection --source jsonplaceholder_posts
```

### Using Docker

```bash
# Build and run
docker-compose up --build

# Or run with specific command
docker run -v $(pwd)/data:/app/data \
  -v $(pwd)/config:/app/config \
  batch-pipeline:latest \
  extract --source jsonplaceholder_posts
```

## Configuration

Edit `config/source_config.json` to add new sources:

```json
{
  "sources": {
    "your_source_name": {
      "type": "rest_api",
      "base_url": "https://api.example.com",
      "endpoint": "data",
      "method": "GET",
      "headers": {},
      "params": {},
      "timeout": 30
    }
  }
}
```

## Extending the Pipeline

### Creating a Custom Connector

```python
from src.connector import BaseConnector

class CustomConnector(BaseConnector):
    def validate_connection(self) -> bool:
        # Implement connection validation
        pass
    
    def fetch_data(self, **kwargs):
        # Implement data fetching
        return []
```

### Creating a Custom Loader

```python
from src.loader import DataLoader

class CustomLoader(DataLoader):
    def load_data(self, records, filename, load_type, key_column=None):
        # Implement custom loading logic
        pass
```

## Load Types Explained

### Full Load
- **Use Case**: Initial data load or when you need complete refresh
- **Behavior**: Replaces entire file with new data
- **Example**: `--load-type full_load`

### Incremental Load
- **Use Case**: Append-only scenarios where only new records matter
- **Behavior**: Appends only records that don't exist in the file (based on key)
- **Example**: `--load-type incremental --key-column id`
- **Requires**: `--key-column` parameter

### Upsert Load
- **Use Case**: Synchronize records with updates from source
- **Behavior**: Insert new records, update existing ones based on key
- **Example**: `--load-type upsert --key-column id`
- **Requires**: `--key-column` parameter

## Logging

Logs are printed to console with timestamps and log levels. Control with environment variable:

```bash
export LOG_LEVEL=DEBUG
python -m src.main extract --source jsonplaceholder_posts
```

## Development

Run tests:

```bash
pytest tests/
```

Format code:

```bash
black src/
```

Lint code:

```bash
pylint src/
```

## API Reference

### Extractor

```python
from src.connector import RestApiConnector
from src.extractor import Extractor
from src.loader import LoadType

connector = RestApiConnector(config)
extractor = Extractor(connector)

# Simple extraction
result = extractor.extract(
    source_name="my_source",
    load_type=LoadType.FULL_LOAD
)

# Paginated extraction
result = extractor.extract_paginated(
    source_name="my_source",
    load_type=LoadType.INCREMENTAL,
    key_column="id",
    page_param="page",
    limit_param="limit",
    limit=100,
    max_pages=10
)
```

### RestApiConnector

```python
from src.connector import RestApiConnector

connector = RestApiConnector({
    "base_url": "https://api.example.com",
    "endpoint": "data",
    "headers": {"Authorization": "Bearer token"}
})

# Validate connection
if connector.validate_connection():
    # Fetch data
    data = connector.fetch_data()
    
    # Fetch paginated data
    data = connector.fetch_paginated_data(
        page_param="page",
        limit_param="limit",
        limit=100
    )
```

## Best Practices

1. **Use Incremental Load** for large datasets to minimize processing time
2. **Use Upsert Load** for data synchronization scenarios
3. **Configure appropriate timeouts** for API connections
4. **Use key columns** that uniquely identify records
5. **Monitor logs** for extraction issues
6. **Validate connections** before running extractions
7. **Test with small datasets** before processing large volumes

## Troubleshooting

### Connection Failed
```bash
python -m src.main validate-connection --source your_source
```

### No Records Returned
- Check API endpoint and credentials
- Verify API parameters in configuration
- Check API response format compatibility

### Upsert Not Working as Expected
- Ensure `key_column` values are unique
- Verify key column name matches your data

## Contributing

1. Create a new branch for features
2. Add tests for new functionality
3. Update README with new features
4. Submit pull request

## License

MIT License
