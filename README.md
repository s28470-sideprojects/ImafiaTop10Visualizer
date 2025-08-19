


# Imafia Top 10 Visualizer

A tool to fetch tournament results from imafia.org and create an animated visualization of how the Top 10 players change from round to round.

## Input
- Use a tournament link in the following format:  
  https://imafia.org/tournament/&lt;TOURNAMENT_ID&gt;

## Usage
1. Install dependencies (preferably in a virtual environment):
   ```bash
   pip install -r requirements.txt
   ```

2. Run the script with a tournament link:
   ```bash
   python src/fetch_and_create_video.py "https://imafia.org/tournament/367"
   ```

## Output
- The parsed tournament data is saved in the `data/` folder as a CSV file.  
- The animated video is saved in `data/`.  