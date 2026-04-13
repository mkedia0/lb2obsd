import os
import requests
from dotenv import load_dotenv
import csv

load_dotenv()

TMDB_API_KEY = os.getenv('TMDB_API_KEY')

def search_movie(title, year):
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": title,
        "year": year
    }
    response = requests.get(url, params=params)
    results = response.json()["results"]
    if results:
        return results[0]["id"]
    else:
        return None 
    
def get_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {"api_key": TMDB_API_KEY}
    response = requests.get(url, params=params)
    details = response.json()
    
    credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits"
    credits_response = requests.get(credits_url, params=params)
    details["credits"] = credits_response.json()
    
    return details

def extract_info(details):
    title = details.get("title", "Unknown Title")
    release_date = details.get("release_date", "")[:4]
    overview = details.get("overview", "")
    genres = [g["name"] for g in details.get("genres", [])]
    runtime = details.get("runtime", "")
    credits = details.get("credits", {})

    cast = [c["name"] for c in credits.get("cast", [])][:5]
    director = next((c["name"] for c in credits.get("crew", []) if c["job"] == "Director"), "")

    return{
        "title": title,
        "release_year": release_date,
        "overview": overview,
        "genres": genres,
        "runtime": runtime,
        "cast": cast,
        "directors": [director] if director else []
    }

def create_note(info, rating, review, watched_date):
    directors = " ".join([f"[[{d}]]" for d in info["directors"]])
    cast = " ".join([f"[[{c}]]" for c in info["cast"]])
    genres = " ".join([f"[[{g}]]" for g in info["genres"]])

    note = f"""# {info['title']} ({info['release_year']})

## Details
- **Year**; [[{info["release_year"]}]]
- **Genres**: {genres}
- **Runtime**: {info["runtime"]} minutes
- **Director**: {directors}
- **Cast**: {cast}
- **Watched**: {watched_date}
- **Rating**: {rating}/5

## Overview
{info['overview']}

## My Review
{review}
"""
    return note

def load_reviews(reviews_csv_path):
    reviews = {}
    try:
        with open(reviews_csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row["Name"], row["Year"])
                reviews[key] = row.get("Review", "")
    except FileNotFoundError:
        print("No reviews file found, skipping...")
    return reviews

def create_entity_notes(entity_movies, output_path, folder_name):
    folder_path = os.path.join(output_path, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    
    for entity, movies in entity_movies.items():
        movie_links = "\n".join([f"- [[movies/{m}]]" for m in movies])
        note = f"# {entity}\n\n## Movies\n{movie_links}\n"
        
        filename = f"{entity.replace('/', '-')}.md"
        filepath = os.path.join(folder_path, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(note)


def process_csv(csv_path, reviews_csv_path, output_path):
    os.makedirs(output_path, exist_ok=True)
    reviews = load_reviews(reviews_csv_path)
    
    actor_movies = {}
    director_movies = {}
    genre_movies = {}
    year_movies = {}

    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row["Name"]
            year = row["Year"]
            rating = row.get("Rating", "")
            review = reviews.get((title, year), "")
            watched_date = row.get("Watched Date", row.get("Date", ""))

            print(f"Processing {title}...")

            movie_id = search_movie(title, year)
            if not movie_id:
                print(f"Movie not found: {title} ({year})")
                continue
            details = get_movie_details(movie_id)
            info = extract_info(details)
            for actor in info["cast"]:
                actor_movies.setdefault(actor, []).append(info["title"])
            for director in info["directors"]:
                director_movies.setdefault(director, []).append(info["title"])
            for genre in info["genres"]:
                genre_movies.setdefault(genre, []).append(info["title"])
            year_movies.setdefault(info["release_year"], []).append(info["title"])

            note = create_note(info, rating, review, watched_date)

            movies_path = os.path.join(output_path, "movies")
            os.makedirs(movies_path, exist_ok=True)
            filename = f"{title.replace('/', '-')}.md"
            filepath = os.path.join(movies_path, filename)

            with open(filepath, 'w', encoding='utf-8') as out:
                out.write(note)
            
            print(f"Created note for {title} at {filepath}")
    
    create_entity_notes(actor_movies, output_path, "actors")
    create_entity_notes(director_movies, output_path, "directors")
    create_entity_notes(genre_movies, output_path, "genres")
    create_entity_notes(year_movies, output_path, "years")


if __name__ == "__main__":
    csv_path = input("Enter path to your Letterboxd diary.csv file: ")
    reviews_csv_path = input("Enter path to your Letterboxd reviews.csv file (or leave blank if not available): ")
    output_path = input("Enter path to save Obsidian notes: ")
    process_csv(csv_path, reviews_csv_path, output_path)
            
    