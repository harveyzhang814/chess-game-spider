#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LiveChessCloud Tournament Scraper
================================

A web scraper tool for extracting complete chess tournament data from LiveChessCloud website.

Features:
1. Extract tournament metadata (tournament.json)
2. Extract round pairing tables (index.json) 
3. Extract complete game moves (game-{id}.json?poll)

Author: Chess Game Spider
Date: 2024
"""

import os
import json
import time
import requests
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging
from urllib.parse import urljoin
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LiveChessCloudScraper:
    """LiveChessCloud tournament data scraper class"""
    
    def __init__(self, match_id: str, base_url: str = "https://1.pool.livechesscloud.com"):
        """
        Initialize the scraper
        
        Args:
            match_id: Tournament ID (UUID format)
            base_url: API base URL
        """
        self.match_id = match_id
        self.base_url = base_url
        self.session = requests.Session()
        
        # Set request headers to simulate browser access
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Referer': 'https://view.livechesscloud.com',
            'Origin': 'https://view.livechesscloud.com',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        
        # Create data storage directories
        self.data_dir = Path("data/raw_data")
        self.tournament_dir = self.data_dir / "tournament"
        self.rounds_dir = self.data_dir / "rounds"
        self.games_dir = self.data_dir / "games"
        
        self._create_directories()
        
        # Request configuration
        self.request_delay = 1.0  # Request interval (seconds)
        self.max_retries = 3      # Maximum retry attempts
        
    def _create_directories(self):
        """Create data storage directory structure"""
        for directory in [self.tournament_dir, self.rounds_dir, self.games_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")
    
    def _make_request(self, url: str, retries: int = None) -> Optional[Dict[str, Any]]:
        """
        Send HTTP request and handle exceptions
        
        Args:
            url: Request URL
            retries: Retry count, defaults to self.max_retries
            
        Returns:
            Response JSON data, returns None on failure
        """
        if retries is None:
            retries = self.max_retries
            
        for attempt in range(retries + 1):
            try:
                logger.info(f"Requesting URL: {url} (attempt {attempt + 1}/{retries + 1})")
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # Check response content
                if not response.content:
                    logger.warning(f"Empty response: {url}")
                    return None
                    
                data = response.json()
                logger.info(f"Successfully retrieved data: {url}")
                
                # Request interval to avoid rate limiting
                time.sleep(self.request_delay)
                return data
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed (attempt {attempt + 1}): {url} - {e}")
                if attempt < retries:
                    wait_time = (attempt + 1) * 2  # Incremental wait time
                    logger.info(f"Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Reached maximum retry attempts, abandoning request: {url}")
                    return None
                    
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing failed: {url} - {e}")
                return None
            except Exception as e:
                logger.error(f"Unknown error: {url} - {e}")
                return None
    
    def _save_json(self, data: Dict[str, Any], filepath: Path) -> bool:
        """
        Save JSON data to file
        
        Args:
            data: Data to save
            filepath: File path
            
        Returns:
            Returns True on successful save, False on failure
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Data saved: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save file: {filepath} - {e}")
            return False
    
    def fetch_tournament_info(self) -> Optional[Dict[str, Any]]:
        """
        Get tournament metadata
        
        Returns:
            Tournament info dictionary, returns None on failure
        """
        url = f"{self.base_url}/get/{self.match_id}/tournament.json"
        data = self._make_request(url)
        
        if data:
            filepath = self.tournament_dir / "info.json"
            if self._save_json(data, filepath):
                return data
        
        return None
    
    def fetch_round_index(self, round_number: int) -> Optional[Dict[str, Any]]:
        """
        Get pairing table for specified round
        
        Args:
            round_number: Round number
            
        Returns:
            Round pairing info, returns None on failure
        """
        url = f"{self.base_url}/get/{self.match_id}/round-{round_number}/index.json"
        data = self._make_request(url)
        
        if data:
            filepath = self.rounds_dir / f"round_{round_number}_index.json"
            if self._save_json(data, filepath):
                return data
        
        return None
    
    def fetch_game_detail(self, round_number: int, game_number: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed moves for specified game
        
        Args:
            round_number: Round number
            game_number: Game number
            
        Returns:
            Game detailed info, returns None on failure
        """
        url = f"{self.base_url}/get/{self.match_id}/round-{round_number}/game-{game_number}.json?poll"
        data = self._make_request(url)
        
        if data:
            filepath = self.games_dir / f"round_{round_number}_game_{game_number}.json"
            if self._save_json(data, filepath):
                return data
        
        return None
    
    def scrape_tournament(self) -> bool:
        """
        Main method to scrape complete tournament data
        
        Returns:
            Returns True on successful scraping, False on failure
        """
        logger.info(f"Starting tournament data scraping: {self.match_id}")
        
        # 1. Get tournament metadata
        logger.info("Step 1: Getting tournament metadata")
        tournament_info = self.fetch_tournament_info()
        if not tournament_info:
            logger.error("Unable to get tournament metadata, terminating scraping")
            return False
        
        # 2. Get round information
        rounds = tournament_info.get('rounds', [])
        total_rounds = len(rounds)
        logger.info(f"Tournament has {total_rounds} rounds")
        
        # 3. Iterate through each round to get pairing tables and game details
        for round_num in range(1, total_rounds + 1):
            logger.info(f"Step 2.{round_num}: Processing round {round_num}")
            print(f"\n\033[1;36m[Round Progress] Round {round_num}/{total_rounds}\033[0m", flush=True)
            
            # Get round pairing table
            round_index = self.fetch_round_index(round_num)
            if not round_index:
                logger.warning(f"Unable to get round {round_num} pairing table, skipping")
                continue
            
            # Get all games in this round
            pairings = round_index.get('pairings', [])
            total_games = len(pairings)
            logger.info(f"Round {round_num} has {total_games} games")
            
            # Progress bar initialization
            bar_width = 40
            for game_num in range(1, total_games + 1):
                # Print progress bar
                progress = game_num / total_games
                filled_len = int(bar_width * progress)
                bar = '█' * filled_len + '-' * (bar_width - filled_len)
                sys.stdout.write(f"\r  [Game Progress] Game {game_num}/{total_games} |{bar}| {progress*100:5.1f}%")
                sys.stdout.flush()
                
                game_detail = self.fetch_game_detail(round_num, game_num)
                if not game_detail:
                    logger.warning(f"Unable to get round {round_num} game {game_num} details")
                # Optional: display game status
                # else:
                #     status = game_detail.get('status', 'unknown')
                #     sys.stdout.write(f" Status:{status}")
            sys.stdout.write("\n")
            sys.stdout.flush()
        
        logger.info("Tournament data scraping completed!")
        print("\n\033[1;32mAll scraping completed!\033[0m")
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get scraping statistics
        
        Returns:
            Statistics dictionary
        """
        stats = {
            'tournament_files': len(list(self.tournament_dir.glob('*.json'))),
            'round_files': len(list(self.rounds_dir.glob('*.json'))),
            'game_files': len(list(self.games_dir.glob('*.json'))),
            'total_files': 0
        }
        stats['total_files'] = stats['tournament_files'] + stats['round_files'] + stats['game_files']
        return stats


def main():
    """Main function"""
    # Configuration parameters
    MATCH_ID = "43056032-65e9-4a86-98d0-484aa2572c6d"  # Example tournament ID
    
    try:
        # Create scraper instance
        scraper = LiveChessCloudScraper(MATCH_ID)
        
        # Start scraping
        success = scraper.scrape_tournament()
        
        if success:
            # Display statistics
            stats = scraper.get_statistics()
            logger.info("Scraping statistics:")
            logger.info(f"  Tournament info files: {stats['tournament_files']}")
            logger.info(f"  Round files: {stats['round_files']}")
            logger.info(f"  Game files: {stats['game_files']}")
            logger.info(f"  Total files: {stats['total_files']}")
        else:
            logger.error("Scraping failed")
            
    except KeyboardInterrupt:
        logger.info("User interrupted scraping")
    except Exception as e:
        logger.error(f"Program execution error: {e}")


if __name__ == "__main__":
    main() 