# Quick Reference Guide - Batch Pipeline

## 🚀 Getting Started in 5 Minutes

```bash
# 1. Navigate to project
cd /Users/prashantshukla/Desktop/batch-pipeline

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. List available sources
python3 -m src.main list-sources

# 5. Extract data
python3 -m src.main extract --source jsonplaceholder_posts --load-type full_load

# 6. Check results
cat data/jsonplaceholder_posts.json | head -20
```

## 📋 CLI Commands Reference

### List Available Sources
```bash
python3 -m src.main list-sources
```
**Output**: List of all configured data sources

### Extract Data - Full Load
```bash
python3 -m src.main extract \
  --source jsonplaceholder_posts \
  --load-type full_load \
  --output-dir ./data
```
**Result**: Replaces entire file with new data

### Extract Data - Incremental Load
```bash
python3 -m src.main extract \
  --source jsonplaceholder_posts \
  --load-type incremental \
  --key-column id \
  --output-dir ./data
```
**Result**: Appends only new records (by key)

### Extract Data - Upsert Load
```bash
python3 -m src.main extract \
  --source jsonplaceholder_posts \
  --load-type upsert \
  --key-column id \
  --output-dir ./data
```
**Result**: Updates existing, inserts new

### Validate Connection
```bash
python3 -m src.main validate-connection \
  --source jsonplaceholder_posts
```
**Output**: ✓ Connection valid or ✗ Connection failed

## 🐳 Docker Quick Reference

### Build Docker Image
```bash
cd /Users/prashantshukla/Desktop/batch-pipeline
docker build -t batch-pipeline:latest .
```

### Run with Docker
```bash
docker run -v $(pwd)/data:/app/data \
  -v $(pwd)/config:/app/config \
  batch-pipeline:latest \
  extract --source jsonplaceholder_posts
```

### Using Docker Compose
```bash
docker-compose build
docker-compose up
```

## 🐍 Python API Quick Reference

### Basic Usage
```python
from src.connector import RestApiConnector
from src.extractor import Extractor
from src.loader import LoadType

# Configure
config = {
    "base_url": "https://jsonplaceholder.typicode.com",
    "endpoint": "posts"
}

# Extract
connector = RestApiConnector(config)
extractor = Extractor(connector)
result = extractor.extract(
    source_name="posts",
    load_type=LoadType.FULL_LOAD
)
```

### With Incremental Load
```python
result = extractor.extract(
    source_name="posts",
    load_type=LoadType.INCREMENTAL,
    key_column="id"
)
```

### With Pagination
```python
result = extractor.extract_paginated(
    source_name="posts",
    load_type=LoadType.FULL_LOAD,
    limit=100,
    max_pages=5
)
```

## ⚙️ Configuration Quick Reference

### Add New Data Source

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
        "Authorization": "Bearer TOKEN"
      },
      "params": {},
      "timeout": 30
    }
  }
}
```

Then use:
```bash
python3 -m src.main extract --source my_api --load-type full_load
```

## 📊 Load Types Comparison

| Feature | Full Load | Incremental | Upsert |
|---------|-----------|-------------|--------|
| **Action** | Replace all | Append new | Insert/Update |
| **Key Column** | Not needed | Required | Required |
| **Use Case** | Initial load | Append-only | Sync data |
| **Speed** | Fast | Fast | Medium |
| **Data Loss** | Yes | No | No |

## 🔍 Troubleshooting

### Check if Configuration is Valid
```bash
python3 -c "from src.config import Config; c = Config('config/source_config.json'); print('Valid' if c.validate() else 'Invalid')"
```

### Validate Connection to Source
```bash
python3 -m src.main validate-connection --source jsonplaceholder_posts
```

### View Extraction Logs
```bash
# Run with INFO level (default)
python3 -m src.main extract --source jsonplaceholder_posts --load-type full_load

# For more details, check the output
```

### Check Loaded Data
```bash
# View file size
ls -lh data/

# View first records
head -50 data/jsonplaceholder_posts.json

# Count records
python3 -c "import json; print(len(json.load(open('data/jsonplaceholder_posts.json'))))"
```

## 📚 File Locations

| Item | Location |
|------|----------|
| Config | `config/source_config.json` |
| Source Code | `src/` |
| Data Output | `data/` |
| Schemas | `schemas/` |
| Tests | `tests/` |
| Docker File | `Dockerfile` |
| Dependencies | `requirements.txt` |

## 🎯 Common Tasks

### Task: Extract multiple sources
```bash
for source in jsonplaceholder_posts jsonplaceholder_users jsonplaceholder_comments; do
  python3 -m src.main extract --source $source --load-type full_load
done
```

### Task: Schedule with cron
```bash
# Add to crontab
0 2 * * * cd /Users/prashantshukla/Desktop/batch-pipeline && \
  source venv/bin/activate && \
  python3 -m src.main extract --source jsonplaceholder_posts --load-type incremental --key-column id
```

### Task: Run examples
```bash
python3 examples.py
```

### Task: Custom connector template
```python
from src.connector import BaseConnector

class MyConnector(BaseConnector):
    def validate_connection(self) -> bool:
        # Implement validation
        return True
    
    def fetch_data(self, **kwargs):
        # Implement data fetching
        return []

# Use it
connector = MyConnector(config)
extractor = Extractor(connector)
result = extractor.extract(...)
```

## 🔗 Important Links in Documentation

- **Full Guide**: README.md
- **Getting Started**: QUICKSTART.md
- **Architecture**: ARCHITECTURE.md
- **Summary**: PROJECT_SUMMARY.md
- **Checklist**: CHECKLIST.md
- **Files**: FILES_CREATED.md (this file)

## 💡 Tips & Tricks

### Tip 1: Use incremental load for large datasets
```bash
# First run - full load
python3 -m src.main extract --source my_source --load-type full_load

# Subsequent runs - incremental
python3 -m src.main extract --source my_source --load-type incremental --key-column id
```

### Tip 2: Validate before extraction
```bash
python3 -m src.main validate-connection --source my_source && \
python3 -m src.main extract --source my_source --load-type full_load
```

### Tip 3: Use upsert for keeping data synchronized
```bash
# Idempotent - can run multiple times safely
python3 -m src.main extract --source my_source --load-type upsert --key-column id
```

## ❓ FAQ

**Q: Which load type should I use?**
- Full Load: First time, complete refresh needed
- Incremental: Only want to add new records
- Upsert: Need to keep data synchronized

**Q: How do I add authentication?**
A: Add to config:
```json
"headers": {
  "Authorization": "Bearer YOUR_TOKEN"
}
```

**Q: Can I use with a database?**
A: Create a custom connector inheriting from `BaseConnector`

**Q: How do I deploy to production?**
A: Use Docker:
```bash
docker build -t batch-pipeline .
docker run batch-pipeline extract --source my_source
```

## 📞 Support

For issues, check:
1. README.md - Full documentation
2. ARCHITECTURE.md - Design details
3. examples.py - Working examples
4. QUICKSTART.md - Getting started guide

---

**Project Location**: `/Users/prashantshukla/Desktop/batch-pipeline`

**Last Updated**: January 9, 2026
