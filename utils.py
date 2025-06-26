#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LiveChessCloud Scraper Utilities
================================

Utility function collection containing data analysis, PGN conversion, and other functionality.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class ChessDataAnalyzer:
    """Chess data analyzer"""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize analyzer
        
        Args:
            data_dir: Data directory path
        """
        self.data_dir = Path(data_dir)
        self.tournament_dir = self.data_dir / "tournament"
        self.rounds_dir = self.data_dir / "rounds"
        self.games_dir = self.data_dir / "games"
    
    def load_tournament_info(self) -> Optional[Dict[str, Any]]:
        """Load tournament information"""
        try:
            info_file = self.tournament_dir / "info.json"
            if info_file.exists():
                with open(info_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load tournament info: {e}")
        return None
    
    def load_round_data(self, round_number: int) -> Optional[Dict[str, Any]]:
        """Load specified round data"""
        try:
            round_file = self.rounds_dir / f"round_{round_number}_index.json"
            if round_file.exists():
                with open(round_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load round {round_number} data: {e}")
        return None
    
    def load_game_data(self, round_number: int, game_number: int) -> Optional[Dict[str, Any]]:
        """Load specified game data"""
        try:
            game_file = self.games_dir / f"round_{round_number}_game_{game_number}.json"
            if game_file.exists():
                with open(game_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load round {round_number} game {game_number} data: {e}")
        return None
    
    def get_tournament_summary(self) -> Dict[str, Any]:
        """Get tournament summary information"""
        tournament_info = self.load_tournament_info()
        if not tournament_info:
            return {}
        
        summary = {
            'name': tournament_info.get('name', 'Unknown'),
            'location': tournament_info.get('location', 'Unknown'),
            'country': tournament_info.get('country', 'Unknown'),
            'timecontrol': tournament_info.get('timecontrol', 'Unknown'),
            'total_rounds': len(tournament_info.get('rounds', [])),
            'rounds_info': []
        }
        
        # Statistics for each round
        for i, round_info in enumerate(tournament_info.get('rounds', []), 1):
            round_data = self.load_round_data(i)
            if round_data:
                pairings = round_data.get('pairings', [])
                summary['rounds_info'].append({
                    'round': i,
                    'date': round_data.get('date', 'Unknown'),
                    'total_games': len(pairings),
                    'finished_games': len([p for p in pairings if p.get('result')]),
                    'live_games': len([p for p in pairings if p.get('live')])
                })
        
        return summary
    
    def get_player_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get player statistics"""
        players = {}
        tournament_info = self.load_tournament_info()
        
        if not tournament_info:
            return players
        
        total_rounds = len(tournament_info.get('rounds', []))
        
        for round_num in range(1, total_rounds + 1):
            round_data = self.load_round_data(round_num)
            if not round_data:
                continue
            
            for pairing in round_data.get('pairings', []):
                # Process white player
                white = pairing.get('white', {})
                white_name = white.get('lname', 'Unknown')
                if white_name not in players:
                    players[white_name] = {
                        'fideid': white.get('fideid'),
                        'games_as_white': 0,
                        'games_as_black': 0,
                        'wins': 0,
                        'losses': 0,
                        'draws': 0,
                        'total_games': 0
                    }
                
                players[white_name]['games_as_white'] += 1
                players[white_name]['total_games'] += 1
                
                # Process black player
                black = pairing.get('black', {})
                black_name = black.get('lname', 'Unknown')
                if black_name not in players:
                    players[black_name] = {
                        'fideid': black.get('fideid'),
                        'games_as_white': 0,
                        'games_as_black': 0,
                        'wins': 0,
                        'losses': 0,
                        'draws': 0,
                        'total_games': 0
                    }
                
                players[black_name]['games_as_black'] += 1
                players[black_name]['total_games'] += 1
                
                # Statistics for results
                result = pairing.get('result', '')
                if result == '1-0':
                    players[white_name]['wins'] += 1
                    players[black_name]['losses'] += 1
                elif result == '0-1':
                    players[black_name]['wins'] += 1
                    players[white_name]['losses'] += 1
                elif result == '1/2-1/2':
                    players[white_name]['draws'] += 1
                    players[black_name]['draws'] += 1
        
        return players


class PGNConverter:
    """PGN format converter"""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize converter
        
        Args:
            data_dir: Data directory path
        """
        self.data_dir = Path(data_dir)
        self.analyzer = ChessDataAnalyzer(data_dir)
    
    def convert_game_to_pgn(self, round_number: int, game_number: int) -> Optional[str]:
        """
        Convert single game to PGN format
        
        Args:
            round_number: Round number
            game_number: Game number
            
        Returns:
            PGN format string, returns None on failure
        """
        game_data = self.analyzer.load_game_data(round_number, game_number)
        round_data = self.analyzer.load_round_data(round_number)
        
        if not game_data or not round_data:
            return None
        
        # Get pairing information
        pairings = round_data.get('pairings', [])
        if game_number > len(pairings):
            return None
        
        pairing = pairings[game_number - 1]
        white = pairing.get('white', {})
        black = pairing.get('black', {})
        result = pairing.get('result', '*')
        
        # Build PGN header
        pgn_headers = [
            f'[Event "{self._get_tournament_name()}"]',
            f'[Site "{self._get_tournament_location()}"]',
            f'[Date "{round_data.get("date", "????.??.??")}"]',
            f'[Round "{round_number}"]',
            f'[White "{white.get("lname", "Unknown")}"]',
            f'[Black "{black.get("lname", "Unknown")}"]',
            f'[Result "{result}"]',
            f'[TimeControl "{self._get_time_control()}"]',
            f'[FEN "{game_data.get("initialFen", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")}"]'
        ]
        
        # Get move sequence
        moves = game_data.get('moves', '')
        
        # Combine PGN
        pgn = '\n'.join(pgn_headers) + '\n\n' + moves + ' ' + result + '\n\n'
        
        return pgn
    
    def convert_tournament_to_pgn(self, output_file: str = "tournament.pgn") -> bool:
        """
        Convert entire tournament to PGN file
        
        Args:
            output_file: Output filename
            
        Returns:
            Returns True on successful conversion, False on failure
        """
        try:
            tournament_info = self.analyzer.load_tournament_info()
            if not tournament_info:
                logger.error("Unable to load tournament information")
                return False
            
            total_rounds = len(tournament_info.get('rounds', []))
            pgn_content = []
            
            for round_num in range(1, total_rounds + 1):
                round_data = self.analyzer.load_round_data(round_num)
                if not round_data:
                    continue
                
                total_games = len(round_data.get('pairings', []))
                
                for game_num in range(1, total_games + 1):
                    game_pgn = self.convert_game_to_pgn(round_num, game_num)
                    if game_pgn:
                        pgn_content.append(game_pgn)
                        logger.info(f"Converted round {round_num} game {game_num} to PGN")
            
            # Save PGN file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(pgn_content))
            
            logger.info(f"PGN file saved: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"PGN conversion failed: {e}")
            return False
    
    def _get_tournament_name(self) -> str:
        """Get tournament name"""
        tournament_info = self.analyzer.load_tournament_info()
        return tournament_info.get('name', 'Unknown Tournament') if tournament_info else 'Unknown Tournament'
    
    def _get_tournament_location(self) -> str:
        """Get tournament location"""
        tournament_info = self.analyzer.load_tournament_info()
        if tournament_info:
            location = tournament_info.get('location', 'Unknown')
            country = tournament_info.get('country', '')
            return f"{location}, {country}" if country else location
        return 'Unknown'
    
    def _get_time_control(self) -> str:
        """Get time control"""
        tournament_info = self.analyzer.load_tournament_info()
        return tournament_info.get('timecontrol', 'Unknown') if tournament_info else 'Unknown'


def print_tournament_summary():
    """Print tournament summary"""
    analyzer = ChessDataAnalyzer()
    summary = analyzer.get_tournament_summary()
    
    if not summary:
        print("Unable to get tournament summary information")
        return
    
    print("=" * 60)
    print(f"Tournament Name: {summary['name']}")
    print(f"Tournament Location: {summary['location']}, {summary['country']}")
    print(f"Time Control: {summary['timecontrol']}")
    print(f"Total Rounds: {summary['total_rounds']}")
    print("=" * 60)
    
    print("\nRound Details:")
    for round_info in summary['rounds_info']:
        print(f"Round {round_info['round']} ({round_info['date']}): "
              f"{round_info['finished_games']}/{round_info['total_games']} games completed, "
              f"{round_info['live_games']} live games")


def print_player_statistics():
    """Print player statistics"""
    analyzer = ChessDataAnalyzer()
    players = analyzer.get_player_statistics()
    
    if not players:
        print("Unable to get player statistics")
        return
    
    print("=" * 80)
    print("Player Statistics")
    print("=" * 80)
    
    # Sort by total games
    sorted_players = sorted(players.items(), key=lambda x: x[1]['total_games'], reverse=True)
    
    for name, stats in sorted_players:
        total = stats['total_games']
        wins = stats['wins']
        losses = stats['losses']
        draws = stats['draws']
        
        if total > 0:
            win_rate = (wins + draws * 0.5) / total * 100
            print(f"{name:20} | Total: {total:2d} | Wins: {wins:2d} | Losses: {losses:2d} | "
                  f"Draws: {draws:2d} | Win Rate: {win_rate:5.1f}%")


if __name__ == "__main__":
    # Example usage
    print("=== Tournament Summary ===")
    print_tournament_summary()
    
    print("\n=== Player Statistics ===")
    print_player_statistics()
    
    print("\n=== PGN Conversion ===")
    converter = PGNConverter()
    success = converter.convert_tournament_to_pgn()
    if success:
        print("PGN conversion completed!")
    else:
        print("PGN conversion failed!") 