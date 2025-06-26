# 🕸️ LiveChessCloud Tournament Scraper

A Python tool for scraping LiveChessCloud chess tournament data and generating standard PGN format files.

## 🎯 Features

- ✅ Scrape tournament metadata (tournament.json)
- ✅ Scrape round pairing tables (index.json)
- ✅ Scrape complete game moves (game-{id}.json?poll)
- ✅ Automatically create data directory structure
- ✅ Comprehensive exception handling and retry mechanisms
- ✅ Request rate limiting to avoid IP blocking
- ✅ Detailed logging
- ✅ Configurable parameters
- ✅ **PGN Format Conversion** - Generate standard PGN files
- ✅ **Time Tag Support** - ChessBase format time tags
- ✅ **UTF-8 Encoding** - Standard encoding format

## 📁 Project Structure

```
chess-game-spider/
├── main.py              # Main scraper program
├── generate_pgn.py      # PGN format generator
├── config.py            # Configuration file
├── requirements.txt     # Python dependencies
├── README.md           # Project documentation
├── USAGE.md            # Usage instructions
├── docs/               # Documentation directory
│   └── prd.md         # Product requirements document
├── data/               # Data storage directory (auto-created)
│   ├── raw_data/       # Scraper raw data
│   │   ├── tournament/ # Tournament information
│   │   ├── rounds/     # Round pairing tables
│   │   └── games/      # Game details
│   └── pgn_format/     # PGN format output
│       └── tournament.pgn # Complete tournament PGN file
└── scraper.log         # Log file (auto-created)
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Scraper to Collect Data

```bash
python main.py
```

### 3. Generate PGN Format Files

```bash
python generate_pgn.py
```

### 4. Customize Tournament ID

Edit the `MATCH_ID` variable in `main.py`:

```python
MATCH_ID = "your-match-id-here"
```

## 📊 Data Flow

```
LiveChessCloud API → Raw JSON Data → PGN Format Files
     ↓                    ↓              ↓
  Scraper Program    data/raw_data/   data/pgn_format/
  (main.py)                              tournament.pgn
```

## ⚙️ Configuration

### Main Configuration Parameters (config.py)

- **Request Interval**: `REQUEST_CONFIG['delay']` - Controls request frequency
- **Retry Count**: `REQUEST_CONFIG['max_retries']` - Number of retry attempts
- **Timeout**: `API_CONFIG['timeout']` - Request timeout settings
- **Data Directory**: `DATA_CONFIG['base_dir']` - Data storage location

### Development Mode Configuration

```python
DEBUG_CONFIG = {
    'verbose': True,     # Detailed logging
    'dry_run': False,    # Dry run mode
    'max_rounds': 3,     # Limit number of rounds (for testing)
    'max_games': 5,      # Limit number of games (for testing)
}
```

## 📊 Data Formats

### Raw Data Format

#### Tournament Information (raw_data/tournament/info.json)
```json
{
  "id": "tournament_short_name",
  "name": "Full Tournament Name",
  "location": "City",
  "country": "XX",
  "timecontrol": "25m+10s",
  "rounds": [
    {"count": 10, "live": false},
    {"count": 10, "live": true}
  ]
}
```

#### Round Pairings (raw_data/rounds/round_X_index.json)
```json
{
  "date": "2024-01-01",
  "pairings": [
    {
      "white": {"lname": "Player1", "fideid": "123456"},
      "black": {"lname": "Player2", "fideid": "789012"},
      "result": "1-0",
      "live": false
    }
  ]
}
```

#### Game Details (raw_data/games/round_X_game_Y.json)
```json
{
  "moves": "1.e4 e5 2.Nf3 Nc6...",
  "initialFen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "players": {...},
  "status": "finished"
}
```

### PGN Format Output

The generated `data/pgn_format/tournament.pgn` file contains:

- **Standard PGN Headers**: Event, Site, Date, Round, White, Black, Result, TimeControl
- **Standard Move Format**: One line per turn, including white and black moves
- **Time Tags**: ChessBase format `{[%clk hh:mm:ss]}`
- **UTF-8 Encoding**: Standard encoding format

Example PGN format:
```
[Event "Tournament Name"]
[Site "City"]
[Date "2024.01.01"]
[Round "1"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]
[TimeControl "1500+10"]

1.Nf3 {[%clk 00:25:18]} d5 {[%clk 00:25:17]} 2.g3 {[%clk 00:25:27]} Nf6 {[%clk 00:25:16]}
```

## 🔧 Advanced Usage

### Custom Scraper Instance

```python
from main import LiveChessCloudScraper

# Create scraper instance
scraper = LiveChessCloudScraper(
    match_id="your-match-id",
    base_url="https://1.pool.livechesscloud.com"
)

# Get tournament information only
tournament_info = scraper.fetch_tournament_info()

# Get specific round
round_data = scraper.fetch_round_index(round_number=1)

# Get specific game
game_data = scraper.fetch_game_detail(round_number=1, game_number=1)
```

### Custom PGN Generation

```python
from generate_pgn import PGNGenerator

# Create PGN generator
pgn_gen = PGNGenerator(data_dir="data/raw_data")

# Generate PGN file
success = pgn_gen.generate_tournament_pgn()
```

### Batch Process Multiple Tournaments

```python
match_ids = [
    "43056032-65e9-4a86-98d0-484aa2572c6d",
    "another-match-id",
    "third-match-id"
]

for match_id in match_ids:
    scraper = LiveChessCloudScraper(match_id)
    success = scraper.scrape_tournament()
    print(f"Tournament {match_id}: {'Success' if success else 'Failed'}")
```

## 🛡️ Exception Handling

The project includes comprehensive exception handling mechanisms:

- **Network Errors**: Automatic retry with incremental wait times
- **JSON Parsing Errors**: Skip corrupted data
- **File Save Errors**: Log error details
- **User Interruption**: Graceful exit
- **PGN Generation Errors**: Detailed error logging and recovery mechanisms

## 📝 Logging

The log file `scraper.log` contains:

- Request status and responses
- Error information and retry records
- Data save status
- Scraping statistics
- PGN generation progress and errors

## 🔮 Extension Features

The project is designed with an extensible architecture for future additions:

- Database storage
- Web interface
- Real-time monitoring
- Win rate statistical analysis
- Multiple PGN format support

## ⚠️ Important Notes

1. **Request Frequency**: Maintain at least 1-second intervals to avoid rate limiting
2. **Data Integrity**: Some games may not be retrievable due to network issues
3. **Storage Space**: Large tournaments may generate many JSON files
4. **PGN Format**: Generated PGN files comply with chess standards
5. **Legal Compliance**: Please respect website terms of service and robots.txt

## 📄 License

This project is for learning and research purposes only.

## 🤝 Contributing

Issues and Pull Requests are welcome!

---

**Author**: Chess Game Spider  
**Version**: 2.0.0  
**Updated**: 2024 