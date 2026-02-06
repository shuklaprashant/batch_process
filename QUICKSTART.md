# Getting Started with Batch Pipeline

## Quick Start

### 1. Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Your First Extraction

```bash
# List available sources
python3 -m src.main list-sources

# Extract data (full load)
python3 -m src.main extract --source jsonplaceholder_posts --load-type full_load

# Check the output
cat data/jsonplaceholder_posts.json
```

### 3. Try Different Load Types

```bash
# Incremental load (only new records)
python3 -m src.main extract \
  --source jsonplaceholder_posts \
  --load-type incremental \
  --key-column id

# Upsert load (insert or update)
python3 -m src.main extract \
  --source jsonplaceholder_posts \
  --load-type upsert \
  --key-column id
```

## Understanding Load Types

### Full Load
Replaces the entire dataset each time:
```bash
python3 -m src.main extract --source jsonplaceholder_posts --load-type full_load
```
**Use when**: Starting fresh or doing a complete refresh

### Incremental Load
Appends only new records (by unique key):
```bash
python3 -m src.main extract \
  --source jsonplaceholder_posts \
  --load-type incremental \
  --key-column id
```
**Use when**: You only want to add new records, not modify existing ones

### Upsert Load
Updates existing records or inserts new ones:
```bash
python3 -m src.main extract \
  --source jsonplaceholder_posts \
  --load-type upsert \
  --key-column id
```
**Use when**: You need to keep data synchronized with source

## Adding Your Own Data Source

### Step 1: Add to Configuration

Edit `config/source_config.json`:

```json
{
  "sources": {
    "my_api": {
      "type": "rest_api",
      "base_url": "https://api.example.com",
      "endpoint": "data",
      "method": "GET",
      "headers": {
        "Accept": "application/json",
        "Authorization": "Bearer YOUR_TOKEN"
      },
      "params": {},
      "timeout": 30
    }
  }
}
```

### Step 2: Extract Data

```bash
python3 -m src.main extract --source my_api --load-type full_load
```

## Using as a Library

```python
from src.connector import RestApiConnector
from src.loader import DataLoader, LoadType
from src.extractor import Extractor

# Configure
config = {
    "base_url": "https://api.example.com",
    "endpoint": "data"
}

# Create components
connector = RestApiConnector(config)
extractor = Extractor(connector)

# Extract data
result = extractor.extract(
    source_name="my_data",
    load_type=LoadType.FULL_LOAD
)
```

## Docker Usage

```bash
# Build image
docker build -t batch-pipeline:latest .

# Run extraction
docker run -v $(pwd)/data:/app/data \
  -v $(pwd)/config:/app/config \
  batch-pipeline:latest \
  extract --source jsonplaceholder_posts

# Or use docker-compose
docker-compose up
```

## Examples

Run the examples to see all features in action:

```bash
python3 examples.py
```

## Next Steps

1. **Add your first API** - Configure a custom data source
2. **Test load types** - Try each load type with your data
3. **Create a custom connector** - Extend `BaseConnector` for databases or files
4. **Build a pipeline** - Combine multiple extractions in a single job
5. **Deploy with Docker** - Containerize your pipeline for production

## Common Issues

**Connection failed?**
```bash
python3 -m src.main validate-connection --source jsonplaceholder_posts
```

**No data returned?**
- Check API endpoint is correct
- Verify parameters in configuration
- Check API response format

**Wrong key column?**
- Ensure key column name matches your data
- Key values must be unique for upsert/incremental loads
