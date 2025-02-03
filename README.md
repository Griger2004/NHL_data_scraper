# NHL_data_scraper

This is the data collection script which will be used in my prediction model

## steps

1. use `final_nhl_data_2024.csv` as your initial starting spot. Depending on when you come accross it, it will be out of date
2. before you run the updating_games.ipynb

    * Make sure to install all dependencies from `requirements.txt` by activating you python virtual environment and running
      `pip install -r requirements.txt`
   * In the second cell, there are 2 base links where data will be exported from. Copy and paste those urls into your browser and change the date to testerday's date.
   * Take note of the last day there is data for in `final_nhl_data_2024.csv` and the last page of the data. Those and all pages in between will need to be exported. Make sure to change that in the next few cells.
   * IMPORTANT: Currently, you can only scrape one page and the script moves on. What you need to do is implement a for loop that exports the data from every page that you are missing
  
3. Run the script and check if all data is present in the updated `final_nhl_data_2024.csv` file
