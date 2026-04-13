# lb2obsd

Turn your Letterboxd diary into a linked Obsidian vault.

## Features
- Creates a note for every movie you've watched
- Links actors, directors, genres, and years as Obsidian wikilinks
- Pulls cast, crew, and metadata from TMDB
- Includes your personal rating and review from Letterboxd

## Requirements
- Python 3.8+
- A free [TMDB API key](https://www.themoviedb.org/settings/api)
- A Letterboxd account with csv export
- Obsidian installed locally

## Installation
1. Clone this repo
```bash
   git clone https://github.com/mkedia0/lb2obsd.git
   cd lb2obsd
```
2. Install dependencies
```bash
   pip install -r requirements.txt
```
3. Create a `.env` file based on `.env.example` and add your TMDB API key

## Usage
1. Export your Letterboxd data at [letterboxd.com/settings/data](https://letterboxd.com/settings/data)
2. Run the script
```bash
   python3 main.py
```
3. Enter the paths to your `diary.csv`, `reviews.csv`, and your Obsidian vault when prompted
4. Open Obsidian and hit `Cmd + G` to see your graph!

## Output
Your Obsidian vault will be organized into:
- `movies/` — one note per film with details, cast, and your review
- `actors/` — one note per actor linking to all their movies
- `directors/` — one note per director linking to all their movies
- `genres/` — one note per genre linking to all movies in that genre
- `years/` — one note per year linking to all movies watched that year
