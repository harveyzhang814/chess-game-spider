#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PGN Generator
============

Reads all tournament data from the data folder and generates PGN files containing complete header information and game moves.
All games from each round are placed in one PGN file, including standard format header information and game moves.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PGNGenerator:
    """PGN Generator"""
    
    def __init__(self, data_dir: str = "data/raw_data"):
        """
        Initialize PGN generator
        
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
    
    def get_player_name(self, player_data: Dict[str, Any]) -> str:
        """Get complete player name"""
        fname = player_data.get('fname', '') or ''
        mname = player_data.get('mname', '') or ''
        lname = player_data.get('lname', '') or ''
        
        # Combine name parts
        name_parts = []
        if fname.strip():
            name_parts.append(fname.strip())
        if mname.strip():
            name_parts.append(mname.strip())
        if lname.strip():
            name_parts.append(lname.strip())
        
        return ' '.join(name_parts) if name_parts else 'Unknown'
    
    def format_time_chessbase(self, time_str: str) -> str:
        """
        Convert raw time string (e.g., 1518+2) to chessbase format {[%clk hh:mm:ss]}
        """
        # Only take main time part (remove + increment)
        if '+' in time_str:
            main_time = time_str.split('+')[0]
        else:
            main_time = time_str
        try:
            seconds = int(main_time)
        except Exception:
            return ''
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{{[%clk {h:02d}:{m:02d}:{s:02d}]}}"

    def format_moves_with_time(self, moves_data: Any) -> str:
        """
        Format move sequence with chessbase time tags
        Each turn on one line: 1.Nf3 {[%clk 00:25:18]} 2.d5 {[%clk 00:25:17]}
        """
        if not moves_data:
            return ""
        
        moves_list = []
        if isinstance(moves_data, list):
            moves_list = moves_data
        elif isinstance(moves_data, str):
            moves_list = moves_data.split()
        else:
            return str(moves_data)
        
        if not moves_list:
            return ""
        
        # Reorganize moves, group every two moves (white + black)
        formatted_moves = []
        i = 0
        move_number = 1
        
        while i < len(moves_list):
            move_line = f"{move_number}."
            
            # White move
            if i < len(moves_list):
                white_move = moves_list[i]
                if isinstance(white_move, str) and ' ' in white_move:
                    move_part, time_part = white_move.split(' ', 1)
                    clk = self.format_time_chessbase(time_part)
                    move_line += f"{move_part} {clk}"
                else:
                    move_line += str(white_move)
                i += 1
            
            # Black move
            if i < len(moves_list):
                move_line += " "
                black_move = moves_list[i]
                if isinstance(black_move, str) and ' ' in black_move:
                    move_part, time_part = black_move.split(' ', 1)
                    clk = self.format_time_chessbase(time_part)
                    move_line += f"{move_part} {clk}"
                else:
                    move_line += str(black_move)
                i += 1
            
            formatted_moves.append(move_line)
            move_number += 1
        
        return '\n'.join(formatted_moves)
    
    def format_time_control(self, timecontrol_str: str) -> str:
        """
        Format time control to standard format, e.g., [TimeControl "2500+10"]
        """
        if not timecontrol_str or timecontrol_str == "Unknown":
            return "2500+10"  # Default value
        
        # Try to parse "25m+10s" format
        try:
            if 'm' in timecontrol_str and 's' in timecontrol_str:
                # Remove all spaces
                timecontrol_str = timecontrol_str.replace(' ', '')
                # Split minutes and seconds
                if '+' in timecontrol_str:
                    main_part, increment_part = timecontrol_str.split('+')
                    # Extract minutes
                    minutes = int(main_part.replace('m', ''))
                    # Extract increment seconds
                    increment = int(increment_part.replace('s', ''))
                    # Convert to seconds format
                    return f"{minutes*60}+{increment}"
                else:
                    # Only main time, no increment
                    minutes = int(timecontrol_str.replace('m', ''))
                    return f"{minutes*60}"
        except:
            pass
        
        # If already in correct format (e.g., "1500+10"), return directly
        if '+' in timecontrol_str and timecontrol_str.replace('+', '').isdigit():
            return timecontrol_str
        
        return "2500+10"  # Default value

    def generate_game_pgn(self, round_number: int, game_number: int, 
                         tournament_info: Dict[str, Any], 
                         round_data: Dict[str, Any]) -> Optional[str]:
        """
        Generate PGN format for single game
        
        Args:
            round_number: Round number
            game_number: Game number
            tournament_info: Tournament information
            round_data: Round data
            
        Returns:
            PGN format string, returns None on failure
        """
        # Get game data
        game_data = self.load_game_data(round_number, game_number)
        if not game_data:
            return None
        
        # Get pairing information
        pairings = round_data.get('pairings', [])
        if game_number > len(pairings):
            return None
        
        pairing = pairings[game_number - 1]
        white = pairing.get('white', {})
        black = pairing.get('black', {})
        result = pairing.get('result', '*')
        
        # Get player names
        white_name = self.get_player_name(white)
        black_name = self.get_player_name(black)
        
        # Get FIDE ID
        white_fideid = white.get('fideid', '')
        black_fideid = black.get('fideid', '')
        
        # Format time control
        timecontrol = self.format_time_control(tournament_info.get("timecontrol", "Unknown"))
        
        # Build PGN header information
        pgn_headers = [
            f'[Event "{tournament_info.get("name", "Unknown Tournament")}"]',
            f'[Site "{tournament_info.get("location", "Unknown")}, {tournament_info.get("country", "")}"]',
            f'[Date "{round_data.get("date", "????.??.??")}"]',
            f'[Round "{round_number}"]',
            f'[White "{white_name}"]',
            f'[Black "{black_name}"]',
            f'[Result "{result}"]',
            f'[TimeControl "{timecontrol}"]',
            f'[WhiteFideId "{white_fideid}"]' if white_fideid else '',
            f'[BlackFideId "{black_fideid}"]' if black_fideid else '',
            f'[EventDate "{round_data.get("date", "????.??.??")}"]',
            f'[EventType "tournament"]',
            f'[Source "LiveChessCloud"]'
        ]
        
        # Filter empty strings
        pgn_headers = [header for header in pgn_headers if header]
        
        # Get move sequence
        moves = game_data.get('moves', '')
        formatted_moves = self.format_moves_with_time(moves)
        
        # Combine PGN
        pgn = '\n'.join(pgn_headers) + '\n\n' + formatted_moves + ' ' + result + '\n\n'
        
        return pgn
    
    def generate_round_pgn(self, round_number: int) -> Optional[str]:
        """
        Generate PGN file for specified round
        
        Args:
            round_number: Round number
            
        Returns:
            PGN content string, returns None on failure
        """
        # Load tournament information
        tournament_info = self.load_tournament_info()
        if not tournament_info:
            logger.error("Unable to load tournament information")
            return None
        
        # Load round data
        round_data = self.load_round_data(round_number)
        if not round_data:
            logger.error(f"Unable to load round {round_number} data")
            return None
        
        # Get all games in this round
        pairings = round_data.get('pairings', [])
        total_games = len(pairings)
        
        if total_games == 0:
            logger.warning(f"Round {round_number} has no game data")
            return None
        
        logger.info(f"Generating round {round_number} PGN, {total_games} games total")
        
        # Generate PGN for each game
        pgn_content = []
        for game_num in range(1, total_games + 1):
            game_pgn = self.generate_game_pgn(round_number, game_num, tournament_info, round_data)
            if game_pgn:
                pgn_content.append(game_pgn)
                logger.info(f"  Game {game_num} PGN generated successfully")
            else:
                logger.warning(f"  Game {game_num} PGN generation failed")
        
        return '\n'.join(pgn_content)
    
    def generate_tournament_pgn(self) -> bool:
        """
        Generate complete tournament PGN file
        
        Returns:
            Returns True on successful generation, False on failure
        """
        # Create output directory
        output_dir = Path("data/pgn_format")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "tournament.pgn"
        
        # Load tournament information
        tournament_info = self.load_tournament_info()
        if not tournament_info:
            logger.error("Unable to load tournament information")
            return False
        
        tournament_name = tournament_info.get('name', 'Unknown Tournament')
        total_rounds = len(tournament_info.get('rounds', []))
        
        logger.info(f"Starting tournament PGN file generation: {tournament_name}")
        logger.info(f"Total rounds: {total_rounds}")
        
        all_pgn_content = []
        success_count = 0
        
        for round_num in range(1, total_rounds + 1):
            logger.info(f"Processing round {round_num}/{total_rounds}")
            
            # Generate round PGN
            pgn_content = self.generate_round_pgn(round_num)
            if pgn_content:
                all_pgn_content.append(pgn_content)
                success_count += 1
                logger.info(f"Round {round_num} PGN generated successfully")
            else:
                logger.warning(f"Round {round_num} PGN generation failed")
        
        if all_pgn_content:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(all_pgn_content))
                logger.info(f"Tournament PGN file saved: {output_file}")
                logger.info(f"Contains {success_count}/{total_rounds} rounds of data")
                return True
            except Exception as e:
                logger.error(f"Failed to save tournament PGN file: {e}")
                return False
        else:
            logger.error("No successfully generated PGN content")
            return False


def main():
    """Main function"""
    generator = PGNGenerator()
    
    print("🎯 PGN Generator Started")
    print("=" * 50)
    
    try:
        # Check if data directory exists
        if not generator.data_dir.exists():
            print("❌ Data directory does not exist, please run the scraper first")
            return
        
        # Generate tournament PGN file
        print("📁 Generating tournament PGN file...")
        success = generator.generate_tournament_pgn()
        
        print("\n" + "=" * 50)
        if success:
            print("✅ PGN generation completed!")
            print("📄 Tournament PGN file saved at: data/pgn_format/tournament.pgn")
        else:
            print("⚠️ PGN generation partially completed, please check logs")
            
    except KeyboardInterrupt:
        print("\n⚠️ User interrupted generation")
    except Exception as e:
        print(f"\n❌ Error occurred during generation: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 