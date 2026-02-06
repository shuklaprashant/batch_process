"""Unit tests for the batch pipeline"""

import pytest
from src.connector import RestApiConnector
from src.loader import DataLoader, LoadType
from src.extractor import Extractor
from src.config import Config
