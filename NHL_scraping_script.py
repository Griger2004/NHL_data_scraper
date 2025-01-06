import os
import time
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuration
load_dotenv()
DOWNLOADS_PATH = os.getenv('DOWNLOADS_PATH')
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
COMBINED_CSV_PATH = os.path.join(SCRIPT_PATH, 'combined.csv')
BASE_URL = 'https://www.nhl.com/stats/teams?aggregate=0&report=daysbetweengames&reportType=game&dateFrom=2024-10-04&dateTo=2025-01-02&gameType=2&sort=a_gameDate&page={}&pageSize=100'

# Setup Chrome options for automatic download
chrome_options = Options()
chrome_options.add_experimental_option('prefs', {
    'download.default_directory': DOWNLOADS_PATH,
    'download.prompt_for_download': False,
    'download.directory_upgrade': True,
    'safebrowsing.enabled': True
})

# Initialize the WebDriver
service = Service('chromedriver.exe')
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.maximize_window()

try:
    combined_data = pd.DataFrame()  # Initialize an empty DataFrame for combining data

    # Loop through pages
    for page in range(0, 13):
        url = BASE_URL.format(page)
        driver.get(url)

        # Wait for the export link to be present and clickable
        export_link = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/main/div/div/div/div[2]/div/div[2]/div/main/div[2]/h4/a'))
        )
        # Scroll to the element if necessary
        driver.execute_script("arguments[0].scrollIntoView(true);", export_link)
        export_link.click()
        time.sleep(5)  # Wait for the file to download

        # Process the downloaded file
        downloaded_file = os.path.join(DOWNLOADS_PATH, 'Days between Games.xlsx')
        if os.path.exists(downloaded_file):
            data = pd.read_excel(downloaded_file)
            combined_data = pd.concat([combined_data, data], ignore_index=True)
            os.remove(downloaded_file)  # Remove the downloaded file after processing

    # Save the combined data as a CSV file
    if os.path.exists('Days between Games.xlsx'):
        os.remove('Days between Games.xlsx')
    combined_data.to_csv(COMBINED_CSV_PATH, index=False)
    print(f"Combined CSV saved at: {COMBINED_CSV_PATH}")

finally:
    driver.quit()

# Step 2: Find Home or Away Team from Hockey Reference

hockey_ref_url = 'https://www.hockey-reference.com/leagues/NHL_2025_games.html'
hockey_ref_dfs = pd.read_html(hockey_ref_url)
hockey_ref_dfs[0].to_csv('nhl_ref_data.csv', index=False)

# Step 3: Combine the two dataframes and filter

nhl_data = pd.read_csv('combined.csv')
nhl_ref_data = pd.read_csv('nhl_ref_data.csv')

def add_home_column(final_df, temp_df):
    # step 1: loop thorugh the temp df
    # step 2: get display a second df from the main where the dates match the temp df
    # step 3: loop through the second df until 'Team' matches 'Home' and 'Date' matches 'Date' in the temp df
    # step 4: add the 'Home' column to the main df for that row with the value of 1
    for i in range(len(temp_df)):  # Iterate over rows in temp_df
        temp_date = temp_df['Date'][i]
        new_df = final_df[final_df['Game Date'] == temp_date]
        
        for j in range(len(new_df)):
            if new_df['Team'].iloc[j] == temp_df['Home'].iloc[i]:
                if 'Home' not in final_df.columns:
                    final_df['Home'] = 0
                
                # Update the specific row in the original df
                final_df.loc[new_df.index[j], 'Home'] = 1
    
    return final_df

final_nhl_data = add_home_column(nhl_data, nhl_ref_data)
final_nhl_data = final_nhl_data.dropna()

final_nhl_data.rename(columns={'OT':'OT Losses','GD/GP':'Net Goals','Shots/GP':'Shots For','SA/GP':'Shots Against','SD/GP':'Shot Diff'}, inplace=True)
final_nhl_data['Winner'] = final_nhl_data.apply(lambda row: row['Team'] if row['Net Goals'] > 0 else row['Opp Team'], axis=1)

nhl_team_abbr = {
    'ANA' : 'Anaheim Ducks',
    'BOS' : 'Boston Bruins',
    'BUF' : 'Buffalo Sabres',
    'CAR' : 'Carolina Hurricanes',
    'CBJ' : 'Columbus Blue Jackets',
    'CGY' : 'Calgary Flames',
    'CHI' : 'Chicago Blackhawks',
    'COL' : 'Colorado Avalanche',
    'DAL' : 'Dallas Stars',
    'DET' : 'Detroit Red Wings',
    'EDM' : 'Edmonton Oilers',
    'FLA' : 'Florida Panthers',
    'LAK' : 'Los Angeles Kings',
    'MIN' : 'Minnesota Wild',
    'MTL' : 'Montreal Canadiens',
    'NJD' : 'New Jersey Devils',
    'NSH' : 'Nashville Predators',
    'NYI' : 'New York Islanders',
    'NYR' : 'New York Rangers',
    'OTT' : 'Ottawa Senators',
    'PHI' : 'Philadelphia Flyers',
    'PIT' : 'Pittsburgh Penguins',
    'SJS' : 'San Jose Sharks',
    'SEA' : 'Seattle Kraken',
    'STL' : 'St. Louis Blues',
    'TBL' : 'Tampa Bay Lightning',
    'TOR' : 'Toronto Maple Leafs',
    'UTA' : 'Utah Hockey Club',
    'VAN' : 'Vancouver Canucks',
    'VGK' : 'Vegas Golden Knights',
    'WPG' : 'Winnipeg Jets',
    'WSH' : 'Washington Capitals'
}

final_nhl_data['Opp Team'] = final_nhl_data['Opp Team'].apply(lambda abbr: nhl_team_abbr.get(abbr, abbr))
final_nhl_data['Winner'] = final_nhl_data['Winner'].apply(lambda abbr: nhl_team_abbr.get(abbr, abbr))

final_nhl_data.drop(columns=['W', 'L', 'T', 'GP', 'OT Losses', 'P', 'P%'], inplace=True)
final_nhl_data.to_csv('final_nhl_data.csv', index=False)

# Step 4: Remove the other temp csv files
os.remove('nhl_ref_data.csv')
os.remove('combined.csv')






