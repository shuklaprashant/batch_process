"""Main entry point for the batch pipeline"""

import logging
import json
from typing import Optional
import click

from src.config import Config
from src.connector import RestApiConnector
from src.loader import DataLoader, LoadType
from src.extractor import Extractor


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
def cli():
    """Batch Pipeline CLI - Extract and load data with support for various load types"""
    pass


@cli.command()
@click.option('--config', default='config/source_config.json', help='Config file path')
@click.option('--source', required=True, help='Source name to extract from')
@click.option('--load-type', type=click.Choice(['full_load', 'incremental', 'upsert']), 
              default='full_load', help='Type of load operation')
@click.option('--key-column', default=None, help='Key column for incremental/upsert loads')
@click.option('--output-dir', default='./data', help='Output directory for loaded data')
def extract(config: str, source: str, load_type: str, key_column: Optional[str], output_dir: str):
    """Extract data from a configured source and load it"""
    try:
        # Load configuration
        config_obj = Config(config)
        config_obj.validate()
        
        # Get source configuration
        source_config = config_obj.get_source(source)
        
        # Create connector
        connector = RestApiConnector(source_config)
        
        # Create loader
        loader = DataLoader(output_dir)
        
        # Create extractor
        extractor = Extractor(connector, loader)
        
        # Perform extraction
        load_type_enum = LoadType(load_type)
        result = extractor.extract(
            source_name=source,
            load_type=load_type_enum,
            key_column=key_column
        )
        
        # Print result
        click.echo(json.dumps(result, indent=2))
        
        if result["status"] != "success":
            raise click.ClickException("Extraction failed")
    
    except Exception as e:
        logger.error(f"Error: {e}")
        raise click.ClickException(str(e))


@cli.command()
@click.option('--config', default='config/source_config.json', help='Config file path')
def list_sources(config: str):
    """List all configured sources"""
    try:
        config_obj = Config(config)
        sources = config_obj.list_sources()
        click.echo("Configured sources:")
        for source in sources:
            click.echo(f"  - {source}")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise click.ClickException(str(e))


@cli.command()
@click.option('--config', default='config/source_config.json', help='Config file path')
@click.option('--source', required=True, help='Source name')
def validate_connection(config: str, source: str):
    """Validate connection to a data source"""
    try:
        config_obj = Config(config)
        source_config = config_obj.get_source(source)
        connector = RestApiConnector(source_config)
        
        if connector.validate_connection():
            click.echo(f"✓ Connection to {source} is valid")
        else:
            click.echo(f"✗ Connection to {source} failed")
            raise click.ClickException("Connection validation failed")
    
    except Exception as e:
        logger.error(f"Error: {e}")
        raise click.ClickException(str(e))


if __name__ == '__main__':
    cli()
