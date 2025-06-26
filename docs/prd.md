# 🕸️ LiveChessCloud Tournament Scraper - API Reference

This document outlines the structure and usage of three primary HTTP GET requests for scraping chess tournament data from LiveChessCloud. The endpoints allow fetching tournament metadata, round pairing summaries, and individual game move data.

---

## 1️⃣ Tournament Metadata

### **URL Pattern**
```
GET https://1.pool.livechesscloud.com/get/{match_id}/tournament.json
```

### **Example**
```
GET https://1.pool.livechesscloud.com/get/43056032-65e9-4a86-98d0-484aa2572c6d/tournament.json
```

### **Response Fields**
- `id`: tournament short name
- `name`: full tournament name
- `location`: city
- `country`: ISO 2-letter country code
- `timecontrol`: game time format (e.g., "25m+10s")
- `rounds`: list of round summaries
  - `count`: number of games in that round
  - `live`: whether the round is currently live
- `eboards`: list of board IDs (optional)

### **Purpose**
Used to:
- Identify how many rounds the tournament has
- Determine how many games per round to scrape

---

## 2️⃣ Round Pairings (Index)

### **URL Pattern**
```
GET https://1.pool.livechesscloud.com/get/{match_id}/round-{round_number}/index.json
```

### **Example**
```
GET https://1.pool.livechesscloud.com/get/43056032-65e9-4a86-98d0-484aa2572c6d/round-9/index.json
```

### **Response Fields**
- `date`: round date
- `pairings`: array of pairing objects
  - `white` / `black`: each contains:
    - `lname`: last name of the player
    - `fideid`: FIDE ID (if available)
  - `result`: game result (`"1-0"`, `"0-1"`, `"1/2-1/2"`)
  - `live`: boolean (if game is live-streamed)

### **Purpose**
Used to:
- List all player matchups per round
- Extract player names, FIDE IDs, and results
- Determine how many games exist in each round

---

## 3️⃣ Game Detail (Moves and FEN)

### **URL Pattern**
```
GET https://1.pool.livechesscloud.com/get/{match_id}/round-{round_number}/game-{game_number}.json?poll
```

### **Example**
```
GET https://1.pool.livechesscloud.com/get/43056032-65e9-4a86-98d0-484aa2572c6d/round-9/game-3.json?poll
```

### **Response Fields**
- `moves`: PGN-style move string
- `initialFen`: starting FEN (usually standard FEN)
- `players`: player metadata
- `status`: game status (e.g. `finished`, `ongoing`)
- Other technical fields like timestamps, board info, etc.

### **Purpose**
Used to:
- Extract full move history
- Reconstruct the board using FEN and PGN
- Store or convert to PGN for analysis

---

## 🔧 Technical Notes

- **HTTP Method**: All requests are `GET`
- **Headers Required**:
  ```
  User-Agent: Mozilla/5.0
  Referer: https://view.livechesscloud.com
  Origin: https://view.livechesscloud.com
  ```

- **Rate Limiting**:
  - Add 0.5–1s `sleep` between requests to avoid throttling
  - Retry on 429 or 5xx errors

- **Error Handling**:
  - Missing or invalid games may return empty JSON or non-200 status
  - Validate with `.get("moves")` or status code check

---

## 📁 Recommended File Structure

```
data/
├── tournament/
│   └── info.json
├── rounds/
│   ├── round_1_index.json
│   ├── round_2_index.json
│   └── ...
├── games/
│   ├── round_1_game_1.json
│   ├── round_1_game_2.json
│   └── ...
```

---

## ✅ Suggested Workflow

1. Fetch `tournament.json` to get total rounds and game counts.
2. For each round, fetch `round-{n}/index.json` to get pairings.
3. For each pairing, fetch `game-{m}.json?poll` for game details.
4. Store all data in JSON files for post-processing or PGN conversion.

---

## 📌 Example Match ID

For testing:

```
match_id = 43056032-65e9-4a86-98d0-484aa2572c6d
```

---