"""All the classes used in "scrapping_script.py"
"""

####################################################
# Import BeautifulSoup in order to fetch HTML code #
####################################################
from bs4 import BeautifulSoup

#########################################################
# Import requests package in order to make web requests #
#########################################################
import requests

##################################################################
# Import pandas package in order to manipulate data in csv files #
##################################################################
import pandas as pd

class InstantGamingScraper:
    """Class to scrap prices from Instant Gaming
    """

    def __init__(self, num_pages: int):
        # Set the numbers of pages
        self.num_pages = num_pages
        # User-Agent header to simulate a web browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

    def fetch_data(self):
        """This function fetch data
        """
        
        # Create empty lists to store the scraped data
        links = []
        titles = []
        prices = []
        final_prices = []

        # Number of titles we want to skip at the beginning
        skip = 4

        # Loop through pages 1 to 134
        for page in range(1, self.num_pages+1):
            # Base URL that will change at every turn of the loop
            url = f"https://www.instant-gaming.com/fr/rechercher/?type%5B0%5D=steam&page={page}"

            # Fetch the page
            result = requests.get(url, headers=self.headers, timeout=60)
            doc = BeautifulSoup(result.text, "html.parser")

            # Fetch the games pages's link and add it to the CSV file
            links += [link.get("href") for link in doc.find_all("a", class_="cover")]

            # Fetch the games's title
            page_titles = [title.text for title in doc.find_all("span", class_="title")]
            # Add the titles in the CSV file skipping the 4 first ones 
            titles += page_titles[skip:]

            #Fetch the games's price and check if there is price. If not, it says so.
            information_divs = doc.find_all("div", class_="information")
            for i, div in enumerate(information_divs):
                if i == len(information_divs) - 1:
                    continue
                price_div = div.find("div", class_="price")
                if price_div:
                    price = float(price_div.text.replace(',', '.').split('€')[0])
                    # Add 20 % for the TVA
                    final_price = round(price * 1.2, 2)
                else:
                    price = "Pas de prix"
                    final_price = "Pas de prix"
                # Add the prices to the csv file
                prices.append(price)
                final_prices.append(final_price)

        return titles, prices, final_prices, links

    def save_to_csv(self, titles, prices, final_prices, links):
        """This function send the data to a csv file
        """
        
        # Create a pandas DataFrame from the scraped data
        data = {'Title': titles, 'Price': prices, 'Final Price': final_prices, 'Link': links}
        df = pd.DataFrame(data)

        # Save the DataFrame to a CSV file
        df.to_csv('game_prices.csv', index=False)
        print('Données sauvegardés dans "game_prices.csv"')

    def execute_scrap(self):
        """This function execute the scrap function
        """
        
        titles, prices, final_prices, links, = self.fetch_data()
        self.save_to_csv(titles, prices, final_prices, links,)

class DataSearcher:
    """Class to search for specific games in the list
    """

    def __init__(self, research):
        self.research = research

    def fetch_csv(self):
        """This function fetches the data from a CSV file using pandas
        """
        # Read the CSV file into a pandas dataframe
        df = pd.read_csv('game_prices.csv') # pylint: disable=C0103

        # Extract the data into separate lists
        titles = df['Title'].tolist()
        prices = df['Price'].tolist()
        final_prices = df['Final Price'].tolist()
        links = df['Link'].tolist()

        return titles, prices, final_prices, links

    def search(self, research):
        """This function search for a game by name
        """

        # Fetch the data
        titles, prices, final_prices, links = self.fetch_csv()

        # Create a list of matching games
        matching_games = []
        for i, title in enumerate(titles):
            if research.lower() in title.lower():
                matching_games.append((title, prices[i], final_prices[i], links[i]))

        # Display the matching games
        if len(matching_games) == 0:
            print("Aucun jeu correspondant trouvé.")
        else:
            print(f"Voici les {len(matching_games)} jeux correspondants :")
            for game_match in matching_games:
                print(f"Titre : {game_match[0]}")
                print(f"Prix : {game_match[1]}€")
                print(f"Prix final : {game_match[2]}€")
                print(f"Lien : {game_match[3]}")
                print()
