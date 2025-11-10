"""Web scraper for poster datasets"""
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from PIL import Image
from io import BytesIO
import time
from tqdm import tqdm

class PosterScraper:
    def __init__(self, output_dir="data/posters"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    def scrape_imdb_posters(self, movie_ids, max_count=100):
        """Scrape movie posters from IMDB with genre labels"""
        posters = []
        metadata = []
        
        for i, movie_id in enumerate(tqdm(movie_ids[:max_count], desc="Scraping posters")):
            try:
                url = f"https://www.imdb.com/title/{movie_id}/"
                response = requests.get(url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Get poster image
                img_tag = soup.find('img', class_='ipc-image')
                if img_tag and 'src' in img_tag.attrs:
                    img_url = img_tag['src']
                    img_response = requests.get(img_url, timeout=10)
                    img = Image.open(BytesIO(img_response.content)).convert('RGB')
                    img = img.resize((512, 768), Image.Resampling.LANCZOS)
                    
                    # Extract genres
                    genres = []
                    genre_tags = soup.find_all('a', class_='ipc-chip')
                    for tag in genre_tags[:3]:  # Get top 3 genres
                        genre_text = tag.get_text(strip=True)
                        if genre_text and len(genre_text) < 20:
                            genres.append(genre_text.lower())
                    
                    # Save with genre prefix
                    genre_str = "_".join(genres[:2]) if genres else "general"
                    save_path = self.output_dir / f"{genre_str}_{movie_id}.jpg"
                    img.save(save_path, quality=95)
                    
                    posters.append(str(save_path))
                    metadata.append({"id": movie_id, "genres": genres, "path": str(save_path)})
                    
                time.sleep(1)
            except Exception as e:
                print(f"\nError scraping {movie_id}: {e}")
        
        # Save metadata
        import json
        with open(self.output_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\nSuccessfully scraped {len(posters)} posters with genres")
        return posters, metadata
    
    def get_top_movie_ids(self, count=100):
        """Get diverse movie IDs across genres"""
        movie_ids = [
        # Action/Adventure
        "tt0468569",  # The Dark Knight (2008)
        "tt0167260",  # LOTR: Two Towers (2002)
        "tt0120737",  # LOTR: Fellowship (2001)
        "tt0076759",  # Star Wars: A New Hope (1977)
        "tt0133093",  # The Matrix (1999)
        "tt4154796",  # Avengers: Endgame (2019)
        "tt2911666",  # John Wick (2014)
        "tt6751668",  # Parasite (2019)
        "tt4154756",  # Avengers: Infinity War (2018)
        "tt4574334",  # Stranger Things (2016–)

        # Drama
        "tt0111161",  # Shawshank Redemption (1994)
        "tt0068646",  # The Godfather (1972)
        "tt0071562",  # Godfather Part II (1974)
        "tt0108052",  # Schindler's List (1993)
        "tt0110912",  # Pulp Fiction (1994)
        "tt7286456",  # Joker (2019)
        "tt5311514",  # Your Name (2016)
        "tt2380307",  # Coco (2017)
        "tt0816692",  # Interstellar (2014)
        "tt8079248",  # Little Women (2019)

        # Horror/Thriller
        "tt0081505",  # The Shining (1980)
        "tt0078748",  # Alien (1979)
        "tt0073486",  # One Flew Over the Cuckoo's Nest (1975)
        "tt0137523",  # Fight Club (1999)
        "tt0114369",  # Se7en (1995)
        "tt2380307",  # The Conjuring (2013)
        "tt1457767",  # The Conjuring 2 (2016)
        "tt1764234",  # The Ritual (2017)
        "tt7798634",  # Midsommar (2019)
        "tt6644200",  # A Quiet Place (2018)

        # Sci-Fi
        "tt0080684",  # The Empire Strikes Back (1980)
        "tt0816692",  # Interstellar (2014)
        "tt1375666",  # Inception (2010)
        "tt0109830",  # Forrest Gump (1994)
        "tt0088763",  # Back to the Future (1985)
        "tt4154796",  # Avengers: Endgame (2019)
        "tt2488496",  # Star Wars: The Force Awakens (2015)
        "tt1825683",  # Black Panther (2018)
        "tt1877830",  # The Batman (2022)
        "tt2543164",  # Arrival (2016)

        # Romance
        "tt0038650",  # It's a Wonderful Life (1946)
        "tt0110413",  # Léon: The Professional (1994)
        "tt0034583",  # Casablanca (1942)
        "tt0043014",  # Sunset Blvd. (1950)
        "tt0112573",  # Braveheart (1995)
        "tt3783958",  # La La Land (2016)
        "tt5311514",  # Your Name (2016)
        "tt2338151",  # About Time (2013)
        "tt2543164",  # Arrival (2016)
        "tt1838556",  # Before Midnight (2013)

        # Comedy
        "tt0050083",  # 12 Angry Men (1957)
        "tt0057012",  # Dr. Strangelove (1964)
        "tt0105236",  # Reservoir Dogs (1992)
        "tt0087843",  # Once Upon a Time in America (1984)
        "tt0095327",  # Cinema Paradiso (1988)
        "tt11032374", # Dolemite Is My Name (2019)
        "tt1987680",  # The Intouchables (2011)
        "tt2126355",  # Me, Earl and the Dying Girl (2015)
        "tt2283362",  # Jumanji: Welcome to the Jungle (2017)
        "tt8065792",  # Deadpool 2 (2018)

        # Fantasy
        "tt0167261",  # LOTR: Return of the King (2003)
        "tt0317248",  # City of God (2002)
        "tt0120815",  # Saving Private Ryan (1998)
        "tt0245429",  # Spirited Away (2001)
        "tt0361748",  # Inglourious Basterds (2009)
        "tt3416828",  # The Shape of Water (2017)
        "tt5013056",  # Dunkirk (2017)
        "tt2119532",  # Eternal Sunshine of the Spotless Mind (2004)
        "tt4633694",  # Spider-Man: Into the Spider-Verse (2018)
        "tt1302006",  # The Secret World of Arrietty (2010)

        # Anime
        "tt0245429",  # Spirited Away (2001)
        "tt0347149",  # Howl's Moving Castle (2004)
        "tt0095327",  # Cinema Paradiso (1988)
        "tt1049413",  # Ponyo (2008)
        "tt0119698",  # Princess Mononoke (1997)
        "tt5311514",  # Your Name (2016)
        "tt2458948",  # Wolf Children (2012)
        "tt2397167",  # The Wind Rises (2013)
        "tt6095088",  # A Silent Voice (2016)
        "tt2380307",  # Coco (2017)
        ]
        return movie_ids[:count]