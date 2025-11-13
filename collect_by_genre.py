"""Collect posters organized by genre from the start"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from src.scraper import PosterScraper

# 20 IMDB codes per genre
GENRE_MOVIE_IDS = {
    "action": [
        "tt0468569", "tt0167260", "tt0120737", "tt0076759", "tt0133093",
        "tt4154796", "tt2911666", "tt4154756", "tt0816692", "tt1375666",
        "tt0109830", "tt0088763", "tt2488496", "tt1825683", "tt1877830",
        "tt0120815", "tt0361748", "tt5013056", "tt0317248", "tt0245429"
    ],
    "scifi": [
        "tt0076759", "tt0133093", "tt0816692", "tt1375666", "tt0088763",
        "tt2488496", "tt0078748", "tt0080684", "tt2543164", "tt0816692",
        "tt1454468", "tt0816692", "tt2380307", "tt0245429", "tt0347149",
        "tt1049413", "tt0119698", "tt5311514", "tt2458948", "tt2397167"
    ],
    "fantasy": [
        "tt0167260", "tt0120737", "tt0167261", "tt0245429", "tt0347149",
        "tt1049413", "tt0119698", "tt5311514", "tt2458948", "tt2397167",
        "tt3416828", "tt2119532", "tt4633694", "tt1302006", "tt0361748",
        "tt0317248", "tt4574334", "tt2380307", "tt6751668", "tt7286456"
    ],
    "horror": [
        "tt0081505", "tt0078748", "tt0073486", "tt0137523", "tt0114369",
        "tt2380307", "tt1457767", "tt1764234", "tt7798634", "tt6644200",
        "tt4574334", "tt0078748", "tt0081505", "tt0073486", "tt0137523",
        "tt0114369", "tt1457767", "tt1764234", "tt7798634", "tt6644200"
    ],
    "romance": [
        "tt0038650", "tt0110413", "tt0034583", "tt0043014", "tt0112573",
        "tt3783958", "tt5311514", "tt2338151", "tt2543164", "tt1838556",
        "tt8079248", "tt0110413", "tt3783958", "tt5311514", "tt2338151",
        "tt2543164", "tt1838556", "tt8079248", "tt0038650", "tt0034583"
    ],
    "comedy": [
        "tt0050083", "tt0057012", "tt0105236", "tt0087843", "tt0095327",
        "tt11032374", "tt1987680", "tt2126355", "tt2283362", "tt8065792",
        "tt2380307", "tt0050083", "tt0057012", "tt0105236", "tt0087843",
        "tt0095327", "tt11032374", "tt1987680", "tt2126355", "tt2283362"
    ],
    "drama": [
        "tt0111161", "tt0068646", "tt0071562", "tt0108052", "tt0110912",
        "tt7286456", "tt5311514", "tt2380307", "tt0816692", "tt8079248",
        "tt0073486", "tt0137523", "tt0114369", "tt6751668", "tt4574334",
        "tt0111161", "tt0068646", "tt0071562", "tt0108052", "tt0110912"
    ],
    "thriller": [
        "tt0114369", "tt0137523", "tt0073486", "tt0081505", "tt0078748",
        "tt6644200", "tt7798634", "tt1764234", "tt1457767", "tt2380307",
        "tt0468569", "tt0114369", "tt0137523", "tt0073486", "tt0081505",
        "tt0078748", "tt6644200", "tt7798634", "tt1764234", "tt1457767"
    ]
}

def main():
    print("="*60)
    print("GENRE-SPECIFIC POSTER COLLECTION")
    print("="*60)
    
    base_dir = Path("data/posters_by_genre")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    for genre, movie_ids in GENRE_MOVIE_IDS.items():
        print(f"\n[{genre.upper()}] Collecting {len(movie_ids)} posters...")
        
        genre_dir = base_dir / genre
        scraper = PosterScraper(output_dir=str(genre_dir))
        
        posters, metadata = scraper.scrape_imdb_posters(movie_ids)
        
        print(f"  ✓ Collected {len(posters)} {genre} posters")
    
    print("\n" + "="*60)
    print("✓ All genres collected!")
    print("="*60)
    
    # Print summary
    print("\nGenre Summary:")
    for genre in GENRE_MOVIE_IDS.keys():
        genre_dir = base_dir / genre
        if genre_dir.exists():
            images = list(genre_dir.glob("*.jpg")) + list(genre_dir.glob("*.png"))
            print(f"  {genre}: {len(images)} posters")
    
    print("\nNext step: Train genre-specific LoRAs")
    print("  python train_genre_loras.py")

if __name__ == "__main__":
    main()
