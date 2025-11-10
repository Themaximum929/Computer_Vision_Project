"""Script to collect poster dataset via web scraping"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from src.scraper import PosterScraper

def main():
    scraper = PosterScraper(output_dir="data/posters")
    
    print("Starting poster data collection...")
    print("This will scrape movie posters from IMDB")
    
    # Get movie IDs
    movie_ids = scraper.get_top_movie_ids(count=25)
    print(f"Collecting {len(movie_ids)} posters...")
    
    # Scrape posters with genre labels
    posters, metadata = scraper.scrape_imdb_posters(movie_ids)
    
    print(f"\nData collection complete!")
    print(f"Collected {len(posters)} posters")
    print(f"Saved to: data/posters/")
    print(f"\nGenre distribution:")
    genre_counts = {}
    for item in metadata:
        for genre in item['genres']:
            genre_counts[genre] = genre_counts.get(genre, 0) + 1
    for genre, count in sorted(genre_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {genre}: {count}")

if __name__ == "__main__":
    main()
