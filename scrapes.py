import time
import os
import pandas as pd
from bs4 import BeautifulSoup
import requests

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

# Older method using pd.read_html -- prone to 429 responses
def MLS_gk_scrape_per_table():

    delay = 20   # Avoid 429
    baseurl = "https://fbref.com/en/squads/"
    teamIDs = [
        "cb8b86a2/Inter-Miami-Stats",
        "529ba333/Columbus-Crew-Stats",
        "e9ea41b2/FC-Cincinnati-Stats",
        "46ef01d0/Orlando-City-Stats",
        "eb57545a/Charlotte-FC-Stats",
        "64e81410/New-York-City-FC-Stats",
        "69a0fb10/New-York-Red-Bulls-Stats",
        "fc22273c/CF-Montreal-Stats",
        "1ebc1a5b/Atlanta-United-Stats",
        "44117292/DC-United-Stats",
        "130f43fa/Toronto-FC-Stats",
        "46024eeb/Philadelphia-Union-Stats",
        "35f1b818/Nashville-SC-Stats",
        "3c079def/New-England-Revolution-Stats",
        "f9940243/Chicago-Fire-Stats",
        "81d817a3/Los-Angeles-FC-Stats",
        "d8b46897/LA-Galaxy-Stats",
        "f7d86a43/Real-Salt-Lake-Stats",
        "6218ebd4/Seattle-Sounders-FC-Stats",
        "0d885416/Houston-Dynamo-Stats",
        "99ea75a6/Minnesota-United-Stats",
        "415b4465/Colorado-Rapids-Stats",
        "ab41cb90/Vancouver-Whitecaps-FC-Stats",
        "d076914e/Portland-Timbers-Stats",
        "b918956d/Austin-FC-Stats",
        "15cf8f40/FC-Dallas-Stats",
        "bd97ac1f/St-Louis-City-Stats",
        "4acb0537/Sporting-Kansas-City-Stats",
        "ca460650/San-Jose-Earthquakes-Stats"
    ]
    
    gklist = []

    print("Retreiving MLS GK stats from 2024...")

    for i in range(len(teamIDs)):
        time.sleep(delay)

        # Retrieve GA and SoTA
        sotadf = pd.read_html(baseurl + teamIDs[i], attrs={"id":"stats_keeper_22"})[0]
        sotadf = sotadf.droplevel(0, axis=1)
        sotadf = sotadf.drop(sotadf[(sotadf.Player == 'Squad Total')].index)
        sotadf = sotadf.drop(sotadf[(sotadf.Player == 'Opponent Total')].index)
        sotadf = sotadf.loc[:, ['Player', 'GA', 'SoTA']]

        time.sleep(delay)

        # Retrieve PSxG
        psxgdf = pd.read_html(baseurl + teamIDs[i], attrs={"id":"stats_keeper_adv_22"})[0]
        psxgdf = psxgdf.droplevel(0, axis=1)
        psxgdf = psxgdf.drop(psxgdf[(psxgdf.Player == 'Squad Total')].index)
        psxgdf = psxgdf.drop(psxgdf[(psxgdf.Player == 'Opponent Total')].index)
        psxgdf = psxgdf.loc[:, ['PSxG']]

        # Concatenate
        team_gk_df = pd.concat([sotadf, psxgdf], axis = 1)

        for row in team_gk_df.values.tolist():
            gklist.append(row)
    
    full_gk_df = pd.DataFrame(gklist)
    full_gk_df.columns = ['Player', 'GA', 'SoTA', 'PSxG']

    return full_gk_df

def mls_gk_scrape(filename):

    delay = 10   # Avoid 429
    baseurl = "https://fbref.com/en/squads/"
    teamids = [
        "cb8b86a2/Inter-Miami-Stats",
        "529ba333/Columbus-Crew-Stats",
        "e9ea41b2/FC-Cincinnati-Stats",
        "46ef01d0/Orlando-City-Stats",
        "eb57545a/Charlotte-FC-Stats",
        "64e81410/New-York-City-FC-Stats",
        "69a0fb10/New-York-Red-Bulls-Stats",
        "fc22273c/CF-Montreal-Stats",
        "1ebc1a5b/Atlanta-United-Stats",
        "44117292/DC-United-Stats",
        "130f43fa/Toronto-FC-Stats",
        "46024eeb/Philadelphia-Union-Stats",
        "35f1b818/Nashville-SC-Stats",
        "3c079def/New-England-Revolution-Stats",
        "f9940243/Chicago-Fire-Stats",
        "81d817a3/Los-Angeles-FC-Stats",
        "d8b46897/LA-Galaxy-Stats",
        "f7d86a43/Real-Salt-Lake-Stats",
        "6218ebd4/Seattle-Sounders-FC-Stats",
        "0d885416/Houston-Dynamo-Stats",
        "99ea75a6/Minnesota-United-Stats",
        "415b4465/Colorado-Rapids-Stats",
        "ab41cb90/Vancouver-Whitecaps-FC-Stats",
        "d076914e/Portland-Timbers-Stats",
        "b918956d/Austin-FC-Stats",
        "15cf8f40/FC-Dallas-Stats",
        "bd97ac1f/St-Louis-City-Stats",
        "4acb0537/Sporting-Kansas-City-Stats",
        "ca460650/San-Jose-Earthquakes-Stats"
    ]

    all_data_ls = []

    # len(teamids)

    for i in range(len(teamids)):

        print(f"Retrieving '{teamids[i]}'...")

        # Retrieve page and tables
        page = requests.get(baseurl + teamids[i]).text
        soup = BeautifulSoup(page, 'html.parser')
        gktable = soup.find('table', id='stats_keeper_22')
        agktable = soup.find('table', id='stats_keeper_adv_22')

        # Exclude unnecessary top and bottom rows
        gkrows = gktable.find_all('tr')[2:-2]
        agkrows = agkrows = agktable.find_all('tr')[2:-2]

        # Retrieve stats from goalkeeping table
        for i in range(len(gkrows)):
            row_ls = []
            
            # Player name
            row_ls.append(gkrows[i].find('th').text)

            # Rest of player data
            for td in gkrows[i].find_all('td')[:-1]:
                row_ls.append(td.text.replace(",", ""))

            # Retrieve PSxG from advanced goalkeeping table
            row_ls.append(agkrows[i].find_all('td')[9].text)
            
            all_data_ls.append(row_ls)

        time.sleep(delay)

    # Make df
    df = pd.DataFrame(all_data_ls)
    df.columns = [
        'Player', 'Nation', 'Pos', 'Age', 'MP', 'Starts', 'Min', '90s', 'GA', 'GA90', 'SoTA', 'Saves', 
        'Save%', 'W', 'D', 'L', 'CS', 'CS%', 'PKatt', 'PKA', 'PKsv', 'PKm', 'Save%', 'PSxG'
    ]

    # Drop unnecessary rows
    # Edit this to keep whichever stats you want
    df = df.loc[:, ['Player', 'Min', '90s', 'GA', 'SoTA', 'PSxG']]

    df['Min'] = df['Min'].astype(int)
    df['90s'] = df['90s'].astype(float)
    df['GA'] = df['GA'].astype(int)
    df['SoTA'] = df['SoTA'].astype(int)
    df['PSxG'] = df['PSxG'].astype(float)

    # Add some custom metrics
    df['GSAA'] = (round(df['PSxG'] - df['GA'], 3))
    df['GSAA%'] = (round((df['GSAA'] / df['SoTA']) * 100, 3))

    # Write
    df.to_csv(filename, index=False)

    return

def fotmob_league_scrape():

    # Choose the league URL
    league_url = 'https://www.fotmob.com/leagues/47/overview/premier-league'
    base_team_url = 'https://www.fotmob.com/teams/'
    base_url = 'https://fotmob.com'
    
    # Set up chrome driver
    if not os.path.exists('./DRIVERPATH.txt'):
        print('Error: DRIVERPATH.txt could not be found.')
        return
    else:
        with open('./DRIVERPATH.txt', 'r') as file:
            driverpath = file.readline()

            if not driverpath:
                print('Error: DRIVERPATH.txt is empty.')
                return

    service = Service(executable_path=f'{driverpath + '/chromedriver.exe'}')
    driver = webdriver.Chrome(service=service)
    driver.get(league_url)
    driver.implicitly_wait(5)

    # Find each team in league and then find keeper
    teams = driver.find_elements(By.CLASS_NAME, "exhos731")

    team_urls = []
    gk_urls = []

    # Isolate the url for each team
    for i in range(6,7):
        team_urls.append(teams[i].get_attribute('href')[29:])
    

    # On each team page retrieve GK
    for url in team_urls:
        driver.get(base_team_url + url)
        gkdiv = driver.find_elements(By.CLASS_NAME, "ejpepe01")[-1]
        gk_urls.append(gkdiv.find_element(By.TAG_NAME, 'a').get_attribute('href'))
        time.sleep(3)

    driver.quit()

    # Use BeautifulSoup from this point onwards for scraping player stats
    all_gk_bs_data = []
    
    for i in range(len(gk_urls)):
        page = requests.get(gk_urls[i]).text
        soup = BeautifulSoup(page, 'html.parser')

        # Retrieve column headers, i.e. stat names
        headers_raw = soup.find_all('div', class_ = 'css-2duihq-StatTitle e1uibvo11')
        headers_ls = ['Player'] + [header.text for header in headers_raw]

        # Loop for each player

        player_data = []

        # Retrieve name
        player_data.append(soup.find('h1', class_='css-zt63wq-PlayerNameCSS eopqf5x1').text)

        # Retrieve stats
        data_raw = soup.find_all('div', class_='css-jb6lgd-StatValue e1uibvo12')
        player_data += [data.text for data in data_raw]

        if len(player_data) == 14:
            player_data = player_data[0:6] + [0,0,0] + player_data[6:]

        all_gk_bs_data.append(player_data)

    for row in all_gk_bs_data:
        print(row)

    # Figure out solution for different stats

    # df = pd.DataFrame(all_gk_data)
    # df.columns = headers_ls

    # print(df)

    # df.to_csv(filename, index=False)