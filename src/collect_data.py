"""Data collection script for poster dataset"""
from src.scraper import PosterScraper

def main():
    print("="*60)
    print("POSTER DATA COLLECTION")
    print("="*60)
    
    scraper = PosterScraper(output_dir="data/posters")
    
    # Get diverse movie IDs
    movie_ids = scraper.get_top_movie_ids(count=50)
    
    print(f"\nCollecting {len(movie_ids)} movie posters...")
    print("This will take approximately 1-2 minutes...\n")
    
    posters, metadata = scraper.scrape_imdb_posters(movie_ids)
    
    print("\n" + "="*60)
    print(f"✓ Successfully collected {len(posters)} posters")
    print(f"✓ Saved to data/posters/")
    print(f"✓ Metadata saved to data/posters/metadata.json")
    print("="*60)
    
    # Print genre distribution
    genre_counts = {}
    for item in metadata:
        for genre in item['genres']:
            genre_counts[genre] = genre_counts.get(genre, 0) + 1
    
    print("\nGenre Distribution:")
    for genre, count in sorted(genre_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {genre}: {count}")

if __name__ == "__main__":
    main()
