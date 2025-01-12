1. Requirements

Before you start, make sure you have:

    Python 3 installed on your Mac. (Python often comes pre-installed on macOS, but if you don’t have it, I’ll guide you through installing it.)

2. Setting Up the CarScraper Tool

Follow these steps to set up everything needed to run CarScraper.
Step 1: Open Terminal


    You can open Terminal directly in the folder where the CarScraper files are located:

       1) Right-click inside the folder containing the CarScraper files.

       2) In the context menu, choose Services and then New Terminal at Folder. This will open a Terminal window directly in that folder.

Step 2: Make the Script Executable

    1) Run this command in Terminal:

            chmod +x run_car_scraper.sh

    This command makes the script executable so it can be run directly.

Step 3: Run the Setup and Start the CarScraper Tool

    1) Run the following command in Terminal:

        ./run_car_scraper.sh

The first time you run this command, it will:

    1) Create a Virtual Environment: This is like a separate workspace to install the required libraries for CarScraper.
    2) Install Necessary Libraries: It will download and install the required tools.
    3) Set Up Playwright Browsers: Playwright, which is used to load web pages, will install the browser files it needs.

Starting the CarScraper Tool:

    1) Once setup is complete, the CarScraper graphical window will appear.

    In this window, you can:
        1) Enter the URL of the car listing you want to scrape.
        2) Select the location where you’d like to save the report.
        3) Click the "Generate PDF" button to start scraping.

3. Running the Script in the Future

Now that everything is set up, you won’t need to repeat the setup steps. To run CarScraper in the future:

    1) Open Terminal as told in step one.
    2) Run the script:

                        ./run_car_scraper.sh

This command will start the tool right away.



4. Troubleshooting

Here are solutions to common issues you might encounter:

    Python Not Installed:

        If Terminal shows “command not found” when you try to run Python commands, you may need to install Python. Visit Python’s website and download the latest version for macOS. Install it, then try running the script again.

    Timeout Errors with Playwright:

        If the scraping process takes too long and fails, it could be due to slow internet. Restart the process by re-running ./run_car_scraper.sh.

    Permission Issues:

        If you see permission errors, make sure you followed Step 3 to make run_car_scraper.sh executable. If issues persist, try running:

        sudo ./run_car_scraper.sh

        It will ask for your Mac password, which is normal.

You’re all set! Follow this guide step-by-step, and you should have the CarScraper tool up and running on your Mac in no time. Enjoy using the CarScraper!

If you still have any questions or problem just feel free to contact me. :)
