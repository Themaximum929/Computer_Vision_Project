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
    
    def scrape_imdb_posters(self, movie_ids, max_count=160):
        """Scrape movie posters from IMDB with genre labels"""
        posters = []
        metadata = []
        
        # Get genre mapping from movie IDs
        genre_map = self._get_genre_mapping()
        
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
                    
                    # Get genre from manual mapping
                    genre = genre_map.get(movie_id, "general")
                    
                    # Save with genre prefix
                    save_path = self.output_dir / f"{genre}_{movie_id}.jpg"
                    img.save(save_path, quality=95)
                    
                    posters.append(str(save_path))
                    metadata.append({"id": movie_id, "genres": [genre], "path": str(save_path)})
                    
                time.sleep(1)
            except Exception as e:
                print(f"\nError scraping {movie_id}: {e}")
        
        # Save metadata
        import json
        with open(self.output_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\nSuccessfully scraped {len(posters)} posters with genres")
        return posters, metadata
    
    def _get_genre_mapping(self):
        """Map movie IDs to genres based on collection categories"""
        genre_map = {}
        
        # Action/Adventure
        action_ids = ["tt0468569", "tt0167260", "tt0120737", "tt0076759", "tt0133093", 
                      "tt4154796", "tt2911666", "tt6751668", "tt4154756", "tt4574334",
                      "tt0364989", "tt0117571", "tt0848228", "tt0398286", "tt0993846",
                      "tt0206634", "tt0816692", "tt1877830", "tt0107290", "tt2906216"]
        for mid in action_ids:
            genre_map[mid] = "action"
        
        # Drama
        drama_ids = ["tt0111161", "tt0068646", "tt0071562", "tt0108052", "tt0110912",
                     "tt7286456", "tt5311514", "tt8079248", "tt0209144", "tt0109830",
                     "tt0084649", "tt0118799", "tt0114369", "tt1291584", "tt0102926",
                     "tt0120689", "tt0245712", "tt1049413", "tt0347149"]
        for mid in drama_ids:
            genre_map[mid] = "drama"
        
        # Horror/Thriller
        horror_ids = ["tt0081505", "tt0078748", "tt0137523", "tt1457767", "tt1764234",
                      "tt7798634", "tt6644200", "tt0360717", "tt0104057", "tt1870216",
                      "tt0381681", "tt0208092", "tt2121382", "tt2294629", "tt0993846",
                      "tt0083658", "tt0463854", "tt0105026"]
        for mid in horror_ids:
            genre_map[mid] = "horror"
        
        # Sci-Fi
        scifi_ids = ["tt0080684", "tt1375666", "tt0088763", "tt2488496", "tt1825683",
                     "tt2543164", "tt0437086", "tt0114709", "tt0116765", "tt0407304",
                     "tt0119654", "tt1622547", "tt0090605", "tt0091251", "tt0816711"]
        for mid in scifi_ids:
            genre_map[mid] = "scifi"
        
        # Romance
        romance_ids = ["tt0038650", "tt0110413", "tt0034583", "tt0043014", "tt0112573",
                       "tt3783958", "tt2338151", "tt1838556", "tt1074638", "tt0120363",
                       "tt0482571", "tt0167404", "tt0119346", "tt0480249", "tt0093058",
                       "tt0091763", "tt0086879"]
        for mid in romance_ids:
            genre_map[mid] = "romance"
        
        # Comedy
        comedy_ids = ["tt0050083", "tt0057012", "tt0105236", "tt0087843", "tt0095327",
                      "tt11032374", "tt1987680", "tt2126355", "tt2283362", "tt8065792",
                      "tt0095953", "tt0073195", "tt0100976", "tt0120815", "tt0114746"]
        for mid in comedy_ids:
            genre_map[mid] = "comedy"
        
        # Fantasy
        fantasy_ids = ["tt0167261", "tt0245429", "tt0120815", "tt0361748", "tt3416828",
                       "tt5013056", "tt2119532", "tt4633694", "tt1302006", "tt1130884",
                       "tt0167264", "tt0120735", "tt0103064", "tt0317705", "tt0120903",
                       "tt0112462", "tt0105121", "tt0248916", "tt0295297"]
        for mid in fantasy_ids:
            genre_map[mid] = "fantasy"
        
        # Anime
        anime_ids = ["tt0119698", "tt2458948", "tt2397167", "tt6095088", "tt4925292",
                     "tt0435761", "tt4834206", "tt2467690", "tt2250192", "tt0094625",
                     "tt2414224", "tt0061722", "tt0423731", "tt0318871", "tt10648342"]
        for mid in anime_ids:
            genre_map[mid] = "anime"
        
        return genre_map
    
    def get_top_movie_ids(self, count=100):
        """Get diverse movie IDs across genres"""
        movie_ids = [

            # Action/Adventure (20)
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
            "tt0364989",  # Jurassic Park (1993)
            "tt0117571",  # Gladiator (2000)
            "tt0848228",  # The Avengers (2012)
            "tt0398286",  # Batman Begins (2005)
            "tt0993846",  # The Wolf of Wall Street (2013)
            "tt0206634",  # Gladiator (2000)
            "tt0816692",  # Interstellar (2014) (also sci-fi but often included action)
            "tt1877830",  # The Batman (2022)
            "tt0107290",  # Jurassic Park (1993)
            "tt2906216",  # A Whisker Away (2020) (if you want to cross anime/adventure)

            # Drama (20)
            "tt0111161",  # Shawshank Redemption (1994)
            "tt0068646",  # The Godfather (1972)
            "tt0071562",  # Godfather Part II (1974)
            "tt0108052",  # Schindler's List (1993)
            "tt0110912",  # Pulp Fiction (1994)
            "tt7286456",  # Joker (2019)
            "tt5311514",  # Your Name (2016) (removed from here if strictly anime)
            "tt0816692",  # Interstellar (2014)
            "tt8079248",  # Little Women (2019)
            "tt0209144",  # Memento (2000)
            "tt0109830",  # Forrest Gump (1994)
            "tt0084649",  # Once Upon a Time in America (1984)
            "tt0118799",  # Life is Beautiful (1997)
            "tt0114369",  # Se7en (1995) (close to thriller, often drama)
            "tt1291584",  # The Social Network (2010)
            "tt0102926",  # The Silence of the Lambs (1991)
            "tt0120689",  # The Green Mile (1999)
            "tt0245712",  # Amélie (2001)
            "tt1049413",  # Ponyo (2008) (anime but dramatic)
            "tt0347149",  # Howl's Moving Castle (2004) (anime/fantasy/drama)

            # Horror/Thriller (20)
            "tt0081505",  # The Shining (1980)
            "tt0078748",  # Alien (1979)
            "tt0137523",  # Fight Club (1999)
            "tt0114369",  # Se7en (1995)
            "tt1457767",  # The Conjuring 2 (2016)
            "tt1764234",  # The Ritual (2017)
            "tt7798634",  # Midsommar (2019)
            "tt6644200",  # A Quiet Place (2018)
            "tt0360717",  # The Babadook (2014)
            "tt0104057",  # Silence of the Lambs (1991)
            "tt1870216",  # The Cabin in the Woods (2011)
            "tt0111161",  # The Sixth Sense (1999)
            "tt0381681",  # 28 Days Later (2002)
            "tt0208092",  # Session 9 (2001)
            "tt2121382",  # Sinister (2012)
            "tt2294629",  # It Follows (2014)
            "tt0993846",  # The Babadook (2014)
            "tt0083658",  # The Thing (1982)
            "tt0463854",  # Saw (2004)
            "tt0105026",  # Misery (1990)

            # Sci-Fi (20)
            "tt0080684",  # The Empire Strikes Back (1980)
            "tt0816692",  # Interstellar (2014)
            "tt1375666",  # Inception (2010)
            "tt0088763",  # Back to the Future (1985)
            "tt4154796",  # Avengers: Endgame (2019)
            "tt2488496",  # Star Wars: The Force Awakens (2015)
            "tt1825683",  # Black Panther (2018)
            "tt1877830",  # The Batman (2022)
            "tt2543164",  # Arrival (2016)
            "tt0437086",  # Guardians of the Galaxy (2014)
            "tt0114709",  # Toy Story (1995)
            "tt0116765",  # Toy Story 2 (1999)
            "tt2294629",  # The Martian (2015)
            "tt0407304",  # Minority Report (2002)
            "tt0119654",  # Independence Day (1996)
            "tt1622547",  # Twilight Saga: Eclipse (2010)
            "tt0090605",  # Aliens (1986)
            "tt0091251",  # Blade Runner (1982)
            "tt0078748",  # Alien (1979)
            "tt0816711",  # Ex Machina (2014)

            # Romance (20)
            "tt0038650",  # It's a Wonderful Life (1946)
            "tt0110413",  # Léon: The Professional (1994)
            "tt0034583",  # Casablanca (1942)
            "tt0043014",  # Sunset Blvd. (1950)
            "tt0112573",  # Braveheart (1995)
            "tt3783958",  # La La Land (2016)
            "tt2338151",  # About Time (2013)
            "tt1838556",  # Before Midnight (2013)
            "tt1074638",  # Atonement (2007)
            "tt0111161",  # 500 Days of Summer (2009)
            "tt0120363",  # Romeo + Juliet (1996)
            "tt0078748",  # Pride & Prejudice (2005)
            "tt0482571",  # Eternal Sunshine of the Spotless Mind (2004)
            "tt0167404",  # Moulin Rouge! (2001)
            "tt0119346",  # Titanic (1997)
            "tt0480249",  # The Notebook (2004)
            "tt0381681",  # About Time (2013)
            "tt0093058",  # When Harry Met Sally (1989)
            "tt0091763",  # Dirty Dancing (1987)
            "tt0086879",  # Amélie (2001)

            # Comedy (20)
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
            "tt0086879",  # Amadeus (1984)
            "tt0095953",  # Groundhog Day (1993)
            "tt0110912",  # The Big Lebowski (1998)
            "tt0073195",  # Annie Hall (1977)
            "tt0100976",  # Home Alone (1990)
            "tt0398286",  # Meet the Parents (2000)
            "tt0120815",  # The 40-Year-Old Virgin (2005)
            "tt0111161",  # Superbad (2007)
            "tt0114746",  # Ferris Bueller's Day Off (1986)
            "tt0480249",  # Tropic Thunder (2008)

            # Fantasy (20)
            "tt0167261",  # LOTR: Return of the King (2003)
            "tt0245429",  # Spirited Away (2001)
            "tt0120815",  # Saving Private Ryan (1998)
            "tt0361748",  # Inglourious Basterds (2009)
            "tt3416828",  # The Shape of Water (2017)
            "tt5013056",  # Dunkirk (2017)
            "tt2119532",  # Eternal Sunshine of the Spotless Mind (2004)
            "tt4633694",  # Spider-Man: Into the Spider-Verse (2018)
            "tt1302006",  # The Secret World of Arrietty (2010)
            "tt1130884",  # The Hobbit: An Unexpected Journey (2012)
            "tt0167264",  # LOTR: The Return of the King (2003)
            "tt0120689",  # The Green Mile (1999)
            "tt0120735",  # LOTR: The Fellowship of the Ring (2001)
            "tt0103064",  # Edward Scissorhands (1990)
            "tt0317705",  # The Lion King (1994)
            "tt0120903",  # The Nightmare Before Christmas (1993)
            "tt0112462",  # Beauty and the Beast (1991)
            "tt0105121",  # Aladdin (1992)
            "tt0248916",  # Harry Potter and the Sorcerer's Stone (2001)
            "tt0295297",  # Harry Potter and the Chamber of Secrets (2002)

            # Anime (20)
            "tt0245429",  # Spirited Away (2001)
            "tt0347149",  # Howl's Moving Castle (2004)
            "tt1049413",  # Ponyo (2008)
            "tt0119698",  # Princess Mononoke (1997)
            "tt2458948",  # Wolf Children (2012)
            "tt2397167",  # The Wind Rises (2013)
            "tt6095088",  # A Silent Voice (2016)
            "tt4925292",  # Your Lie in April (2016)
            "tt2906216",  # A Whisker Away (2020)
            "tt0435761",  # Your Name (2016)
            "tt4834206",  # Weathering with You (2019)
            "tt2467690",  # My Neighbor Totoro (1988)
            "tt2250192",  # Neon Genesis Evangelion: The End of Evangelion (1997)
            "tt7286456",  # Joker (2019) (remove if strict anime)
            "tt0094625",  # Akira (1988)
            "tt2414224",  # The Garden of Words (2013)
            "tt0061722",  # Nausicaä of the Valley of the Wind (1984)
            "tt0423731",  # Paprika (2006)
            "tt0318871",  # Ghost in the Shell (1995)
            "tt10648342", # Belle (2021)
        ]
        return movie_ids[:count]