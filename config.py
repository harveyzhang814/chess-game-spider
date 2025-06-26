#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LiveChessCloud Scraper Configuration
===================================

Scraper configuration file containing all configurable parameters.
"""

# API Configuration
API_CONFIG = {
    'base_url': 'https://1.pool.livechesscloud.com',
    'timeout': 30,  # Request timeout (seconds)
}

# Request Configuration
REQUEST_CONFIG = {
    'delay': 1.0,        # Request interval (seconds)
    'max_retries': 3,    # Maximum retry attempts
    'retry_delay': 2,    # Retry interval multiplier
}

# Request Headers Configuration
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://view.livechesscloud.com',
    'Origin': 'https://view.livechesscloud.com',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
}

# Data Storage Configuration
DATA_CONFIG = {
    'base_dir': 'data',
    'tournament_dir': 'tournament',
    'rounds_dir': 'rounds', 
    'games_dir': 'games',
    'encoding': 'utf-8',
    'indent': 2,
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'file': 'scraper.log',
    'max_bytes': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5,
}

# Example Tournament ID (for testing)
EXAMPLE_MATCH_ID = "43056032-65e9-4a86-98d0-484aa2572c6d"

# Development Mode Configuration
DEBUG_CONFIG = {
    'verbose': True,     # Detailed log output
    'dry_run': False,    # Dry run mode (don't save files)
    'max_rounds': None,  # Limit maximum number of rounds (for testing)
    'max_games': None,   # Limit maximum games per round (for testing)
} 