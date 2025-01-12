from playwright.sync_api import sync_playwright, TimeoutError
from urllib.parse import urlparse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io
import requests
import time
import json
from urllib.parse import urlparse
from time import sleep
from PIL import Image






import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QComboBox, QDialog,QTextEdit,QScrollArea,QHBoxLayout,QGroupBox
)
from threading import Thread

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QComboBox, QDialog
)
from PyQt5.QtCore import QThread, pyqtSignal
import os

# Worker class to handle the scraping in a separate thread
class MultiScraperThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, url_data_pairs, save_path):
        super().__init__()
        self.url_data_pairs = url_data_pairs
        self.save_path = save_path

    def run(self):
        try:
            all_scrapers = []
            
            # Create and run scrapers for each URL
            for url, additional_data in self.url_data_pairs:
                self.progress.emit(f"Processing {url}...")
                scraper = get_scraper(url)
                scraper.scrape()
                scraper.data.update(additional_data)
                all_scrapers.append(scraper)

            # Use first car's name for the filename
            first_car_name = all_scrapers[0].car_name.replace("/", "_").replace("\\", "_")
            filename = os.path.join(self.save_path, f"{first_car_name}.pdf")
            BaseScraper.generate_combined_pdf(self,all_scrapers, filename)
            self.finished.emit(filename)
        except Exception as e:
            self.error.emit(str(e))

class MultiCarScraperGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.url_entries = []
        self.additional_data = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Multi-Car Scraper")
        self.setGeometry(100, 100, 600, 400)

        # Main layout
        self.main_layout = QVBoxLayout()

        # Scroll area for URLs
        scroll = QWidget()
        self.scroll_layout = QVBoxLayout(scroll)
        
        # Add first URL entry
        self.add_url_entry()

        # Add URL button
        add_url_button = QPushButton("Add Another URL (Max 6)")
        add_url_button.clicked.connect(self.add_url_entry)
        self.scroll_layout.addWidget(add_url_button)

        # Save Location
        self.save_location_label = QLabel("Select Save Location for PDF:")
        self.scroll_layout.addWidget(self.save_location_label)
        self.save_location_button = QPushButton("Browse")
        self.save_location_button.clicked.connect(self.select_save_location)
        self.scroll_layout.addWidget(self.save_location_button)
        self.save_path = None

        # Generate PDF Button
        self.generate_button = QPushButton("Generate Combined PDF")
        self.generate_button.clicked.connect(self.start_pdf_generation)
        self.scroll_layout.addWidget(self.generate_button)

        # Status Label
        self.status_label = QLabel("")
        self.scroll_layout.addWidget(self.status_label)

        # Add scroll area to main layout
        scroll_area = QScrollArea()
        scroll_area.setWidget(scroll)
        scroll_area.setWidgetResizable(True)
        self.main_layout.addWidget(scroll_area)

        self.setLayout(self.main_layout)

    def add_url_entry(self):
        if len(self.url_entries) >= 6:
            QMessageBox.warning(self, "Warning", "Maximum 6 URLs allowed")
            return

        # Create a horizontal layout for URL entry and remove button
        url_layout = QHBoxLayout()
        
        # URL Entry
        url_entry = QLineEdit()
        url_entry.setPlaceholderText(f"Enter URL #{len(self.url_entries) + 1}")
        url_layout.addWidget(url_entry)

        # Remove button
        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(lambda: self.remove_url_entry(url_layout))
        url_layout.addWidget(remove_button)

        # Insert the new URL entry before the "Add URL" button
        self.scroll_layout.insertLayout(len(self.url_entries), url_layout)
        self.url_entries.append(url_layout)

    def remove_url_entry(self, url_layout):
        # Remove the URL entry from the layout and the list
        self.url_entries.remove(url_layout)
        
        # Delete all widgets in the layout
        while url_layout.count():
            item = url_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Delete the layout itself
        url_layout.deleteLater()

    def select_save_location(self):
        self.save_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if self.save_path:
            self.status_label.setText(f"Save Location Selected: {self.save_path}")

    def get_url_entries(self):
        urls = []
        for url_layout in self.url_entries:
            url_widget = url_layout.itemAt(0).widget()
            if isinstance(url_widget, QLineEdit) and url_widget.text().strip():
                urls.append(url_widget.text().strip())
        return urls

    def show_additional_inputs(self, urls):
        dialog = QDialog(self)
        dialog.setWindowTitle("Additional Information")
        dialog.setGeometry(100, 100, 600, 400)
        
        # Create a scroll area
        scroll = QScrollArea(dialog)
        scroll.setWidgetResizable(True)
        
        # Create a widget to hold all inputs
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)

        all_additional_data = []

        for url in urls:
            # Group box for each URL
            group = QGroupBox(f"Additional Info for {url[:50]}...")
            group_layout = QVBoxLayout()

            url_data = {"url": url}

            if "sbtjapan" in url or "beforward" in url:
                # Total Price
                total_price_label = QLabel("Total Price ($)")
                group_layout.addWidget(total_price_label)
                total_price_entry = QLineEdit()
                group_layout.addWidget(total_price_entry)
                url_data["total_price_entry"] = total_price_entry

                # Island Dropdown
                island_label = QLabel("Select Island")
                group_layout.addWidget(island_label)
                island_dropdown = QComboBox()
                island_dropdown.addItems(["Abaco", "Nassau", "Freeport", "Exuma", "Eleuthera", 
                                        "Spanish Wells", "Bimini", "Andros", "Long Island", 
                                        "Chub Cay", "Green Turtle Cays", "Nassau", ""])
                group_layout.addWidget(island_dropdown)
                url_data["island_dropdown"] = island_dropdown

                # Half Down Option
                half_down_label = QLabel("Half Down ($)")
                group_layout.addWidget(half_down_label)
                half_down_entry = QLineEdit()
                group_layout.addWidget(half_down_entry)
                url_data["half_down_entry"] = half_down_entry

            elif "iaai" in url or "manheim" in url:
                # Parts Input
                parts_label = QLabel("Enter Parts (one per line):")
                group_layout.addWidget(parts_label)
                parts_text_edit = QTextEdit()
                parts_text_edit.setMaximumHeight(100)
                group_layout.addWidget(parts_text_edit)
                url_data["parts_text_edit"] = parts_text_edit

                # Repair Estimates
                repair_bh_label = QLabel("Estimated Parts Repair BH ($):")
                group_layout.addWidget(repair_bh_label)
                repair_bh_entry = QLineEdit()
                group_layout.addWidget(repair_bh_entry)
                url_data["repair_bh_entry"] = repair_bh_entry

                repair_us_label = QLabel("Estimated Parts Repair US ($):")
                group_layout.addWidget(repair_us_label)
                repair_us_entry = QLineEdit()
                group_layout.addWidget(repair_us_entry)
                url_data["repair_us_entry"] = repair_us_entry

            group.setLayout(group_layout)
            layout.addWidget(group)
            all_additional_data.append(url_data)

        scroll_widget.setLayout(layout)
        scroll.setWidget(scroll_widget)

        # Add scroll area and buttons to dialog
        dialog_layout = QVBoxLayout(dialog)
        dialog_layout.addWidget(scroll)
        
        button_box = QHBoxLayout()
        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(lambda: self.submit_additional_inputs(dialog, all_additional_data))
        button_box.addWidget(submit_button)
        dialog_layout.addLayout(button_box)

        dialog.setLayout(dialog_layout)
        dialog.exec_()

    def submit_additional_inputs(self, dialog, all_data):
        self.additional_data = []
        for url_data in all_data:
            url = url_data["url"]
            additional_info = {}

            if "sbtjapan" in url or "beforward" in url:
                additional_info["Total Price"] = url_data["total_price_entry"].text() + " $"
                additional_info["Island"] = url_data["island_dropdown"].currentText()
                additional_info["Half Down"] = url_data["half_down_entry"].text()
            elif "iaai" in url or "manheim" in url:
                additional_info["Parts"] = url_data["parts_text_edit"].toPlainText().strip().split("\n")
                additional_info["Estimated Parts Repair BH"] = url_data["repair_bh_entry"].text() + " $"
                additional_info["Estimated Parts Repair US"] = url_data["repair_us_entry"].text() + " $"

            self.additional_data.append((url, additional_info))
        dialog.accept()

    def start_pdf_generation(self):
        urls = self.get_url_entries()
        if not urls:
            QMessageBox.critical(self, "Error", "Please enter at least one URL.")
            return
        if not self.save_path:
            QMessageBox.critical(self, "Error", "Please select a save location.")
            return

        # Show additional inputs dialog
        self.show_additional_inputs(urls)

        # Create a combined scraper thread
        self.scraper_thread = MultiScraperThread(self.additional_data, self.save_path)
        self.scraper_thread.finished.connect(self.on_pdf_generated)
        self.scraper_thread.error.connect(self.on_error)
        self.scraper_thread.progress.connect(self.update_progress)

        self.status_label.setText("Generating PDF... Please wait.")
        self.scraper_thread.start()

    def update_progress(self, message):
        self.status_label.setText(message)

    def on_pdf_generated(self, filename):
        self.status_label.setText("PDF generated successfully!")
        QMessageBox.information(self, "Success", f"Combined PDF generated successfully at {filename}")

    def on_error(self, error_message):
        self.status_label.setText("Error generating PDF.")
        QMessageBox.critical(self, "Error", f"An error occurred: {error_message}")



class BaseScraper:
    def __init__(self, url,crop_size):
        self.crop_size = crop_size
        self.url = url
        self.data = {}
        self.images = []
        self.car_name = "Car Report"

    def scrape(self):
        """Method to be implemented by each subclass for site-specific scraping."""
        raise NotImplementedError("Subclasses must implement this method")


    def generate_combined_pdf(self, scrapers, filename):
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter

        for idx, scraper in enumerate(scrapers):
            y_position = height - 50

            # Add logo
            logo_path = "lux_official_logo.png"
            try:
                logo = ImageReader(logo_path)
                logo_width, logo_height = logo.getSize()
                aspect_ratio = logo_height / logo_width
                display_width = 200
                display_height = display_width * aspect_ratio
                c.drawImage(logo, (width - display_width) / 2, y_position - display_height, 
                            width=display_width, height=display_height)
                y_position -= display_height + 40
            except Exception as e:
                print(f"Error loading logo: {e}")

            # Add Car Name as Heading
            c.setFont("Helvetica-Bold", 22)
            c.drawCentredString(width / 2, y_position, scraper.car_name)
            y_position -= 40

            # Prepare data for two-column layout
            keys = list(scraper.data.keys())
            values = list(scraper.data.values())
            mid_point = len(keys) // 2
            left_keys, right_keys = keys[:mid_point], keys[mid_point:]
            left_values, right_values = values[:mid_point], values[mid_point:]

            c.setFont("Helvetica", 12)
            x_left, x_right = 10, width / 2 + 10
            y_position -= 20

            # Populate columns with extra formatting for Parts and Estimated Repairs
            for i in range(max(len(left_keys), len(right_keys))):
                if i < len(left_keys):
                    key, value = left_keys[i], left_values[i]
                    key = key.replace(":", "")
                    if type(value) == str:
                        value = value.replace(":", "")
                    if key == "Title/Sale Doc Notes":
                        continue
                    if key == "Parts":
                        if value[0] != "":
                            y_position -= 20
                            c.setFillColorRGB(1, 0, 0)
                            c.drawString(x_left, y_position, "Parts:")
                            c.setFont("Helvetica", 12)
                            for part in value:
                                y_position -= 15
                                c.drawString(x_left + 20, y_position, f"- {part}")
                            y_position -= 20
                    elif key in ["Estimated Parts Repair BH", "Estimated Parts Repair US"]:
                        if value != " $":
                            y_position -= 40
                            c.setFillColorRGB(1, 0, 0)
                            c.drawString(x_left, y_position, f"{key}: {value}")
                    else:
                        c.setFillColorRGB(0, 0, 0)
                        c.drawString(x_left, y_position, f"{key}: {value}")

                if i < len(right_keys):
                    key, value = right_keys[i], right_values[i]
                    key = key.replace(":", "")
                    if type(value) == str:
                        value = value.replace(":", "")
                    if key == "Title/Sale Doc Notes":
                        continue
                    if key == "Parts":
                        if value[0] != "":
                            c.setFillColorRGB(1, 0, 0)
                            c.drawString(x_right, y_position, "Parts:")
                            c.setFont("Helvetica", 12)
                            for part in value:
                                y_position -= 15
                                c.drawString(x_right + 20, y_position, f"- {part}")
                            y_position -= 20
                    elif key in ["Estimated Parts Repair BH", "Estimated Parts Repair US"]:
                        if value != " $":
                            y_position -= 40
                            c.setFillColorRGB(1, 0, 0)
                            c.drawString(x_right, y_position, f"{key}: {value}")
                        y_position -= 20
                    else:
                        c.setFillColorRGB(0, 0, 0)
                        c.drawString(x_right, y_position, f"{key}: {value}")
                        y_position -= 20

                if y_position < 50:  # Check if we need a new page
                    c.showPage()
                    y_position = height - 50

            # Add a new page before processing images
            c.showPage()
            y_position = height - 40

            # Process images for current car
            images_per_page = 2  # Number of images per page
            current_image_on_page = 0

            for img_idx, img_url in enumerate(scraper.images):
                try:
                    img_content = requests.get(img_url).content
                    with io.BytesIO(img_content) as img_stream:
                        with Image.open(img_stream) as img:
                            # Crop image if needed
                            img_width, img_height = img.size
                            if scraper.crop_size > 0:
                                cropped_img = img.crop((0, 0, img_width, img_height - scraper.crop_size))
                            else:
                                cropped_img = img

                            # Convert cropped image to ImageReader
                            image_reader = ImageReader(cropped_img)

                            # Calculate display size with aspect ratio
                            aspect_ratio = cropped_img.height / cropped_img.width
                            img_display_width = width - 100
                            img_display_height = img_display_width * aspect_ratio

                            # Start a new page if this is first image or we've reached the images per page limit
                            if current_image_on_page == 0:
                                if img_idx > 0:  # Don't start a new page for the first image
                                    c.showPage()
                                y_position = height - 40

                            # Position and draw the image
                            c.drawImage(image_reader, 50, y_position - img_display_height,
                                      width=img_display_width, height=img_display_height)

                            y_position -= img_display_height + 20
                            current_image_on_page += 1

                            # Reset counter if we've reached images per page limit
                            if current_image_on_page >= images_per_page:
                                current_image_on_page = 0

                except Exception as e:
                    print(f"Failed to load or crop image {img_url}: {e}")
                    continue

            # Add a new page after each car (except the last one)
            if idx < len(scrapers) - 1:
                c.showPage()

        # Save the final PDF
        c.save()

class CopartScraper(BaseScraper): 
    def __init__(self,url,crop_size):
        super().__init__(url,crop_size)
    def scrape(self):
        # try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False,args=[
                        "--window-position=-10000,-10000",  # Position window off-screen
                        "--disable-blink-features=AutomationControlled",
                    ])
            try:
                context = browser.new_context()
                page = context.new_page()
                page.goto(self.url, wait_until="domcontentloaded", timeout=10000)
                time.sleep(5)
                try:
                    

                    car_info_div = page.wait_for_selector("div.tab-content.f-g1.d-f", timeout=10000)
                    if not car_info_div:
                        print("NOt found")
                        car_info_div = page.query_selector("div[ng-if='!showCopartSelectCode']")
                    car_info = car_info_div.query_selector_all("div[ng-if*='lotDetails']")
                        
                    self.car_name = page.query_selector("h1").inner_text()
                    current_bid_div = page.query_selector("div[ng-if*='dynamiclotDetails.firstBid']")

                    for div in car_info:
                        label = div.query_selector("label").inner_text()
                        value = div.query_selector("span").inner_text()
                        if "View Report " in value:
                            continue
                        self.data[label] = value
                    
                    if current_bid_div:
                        current_bid_element = current_bid_div.query_selector("span.bid-price")
                        if(current_bid_element):
                            self.data["Current Bid"] = current_bid_element.inner_text()

                    # Handle images with pagination
                    self.extract_images_with_pagination(page)


                    

                except Exception as e:
                    print(f"First structure failed: {e}")

                # Second structure fallback
                    try:
                        page.wait_for_selector("div.lot-details-section.vehicle-info", timeout=10000)
                        car_info = page.query_selector_all("div.lot-details-info")
                        self.car_name = page.query_selector("h1").inner_text()

                        current_bid_element = page.query_selector("h1.p-mt-0.amount.bidding-heading.p-d-inline-block.p-position-relative.separate-currency-symbol.ng-star-inserted")
                        if(current_bid_element):
                            self.data["Current Bid"] = current_bid_element.inner_text()

                        for div in car_info:
                            label = div.query_selector("label").inner_text()
                            value = div.query_selector("span").inner_text()
                            self.data[label] = value

                        # Handle images with pagination
                        self.extract_images_with_pagination(page)
                    except Exception as e:
                        print(f"Second structure failed: {e}")
                    finally:
                        browser.close()
            except TimeoutError:
                print("TimeoutError on Copart site")
        
        return self.data

    def extract_images(self, page):
        image_elements = page.query_selector_all("div.small-container.martop img")
        self.images = [img.get_attribute("src").replace("_thb.jpg", "_ful.jpg") for img in image_elements]

    def extract_images_with_pagination(self, page):
        for _ in range(5):
            image_elements = page.query_selector_all("div.p-galleria-thumbnail-items img")
            self.images.extend([
                img.get_attribute("src").replace("_thb.jpg", "_ful.jpg")
                for img in image_elements
            ])
            next_button = page.query_selector("span.lot-details-sprite.thumbnail-next-image-icon.p-position-absolute.p-cursor-pointer")
            if next_button:
                next_button.click()
                time.sleep(0.5)
        self.images = list(dict.fromkeys(self.images))  # Remove duplicates




class IAAIScraper(BaseScraper):
    def __init__(self,url,crop_size,cookies_path="iaai.json"):
        super().__init__(url,crop_size)
        self.cookies_path = cookies_path

    def save_cookies(self, page):
        try:
            cookies = page.context.cookies()
            with open(self.cookies_path, "w") as file:
                json.dump(cookies, file)
            print("Cookies saved successfully.")
        except Exception as e:
            print(f"Error saving cookies: {e}")

    def load_cookies(self, page):
        try:
            with open(self.cookies_path, "r") as file:
                cookies = json.load(file)
                page.context.add_cookies(cookies)
            print("Cookies loaded successfully.")
        except FileNotFoundError:
            print("No cookies file found, proceeding with login.")

    def check_login_required(self, page):
        profile_div = page.wait_for_selector("div.profile")
        logged_in = True if profile_div.query_selector("div.header__avatar-name") else False
        return not logged_in

    def handle_login(self, playwright):
        # Launch browser in visible mode for user login
        browser = playwright.chromium.launch(
                            headless=False,
                            args=[
                                "--disable-blink-features=AutomationControlled",
                                "--disable-web-security",
                                "--disable-features=IsolateOrigins,site-per-process",
                                "--disable-site-isolation-trials",
                            ]
                        )
                        
                        # Create a new browser context with a custom user-agent and viewport

        page = browser.new_page()
        page.goto("https://login.iaai.com/Identity/Account/Login?ReturnUrl=%2Fconnect%2Fauthorize%2Fcallback%3Fclient_id%3DAuctionCenterPortal%26redirect_uri%3Dhttps%253A%252F%252Fwww.iaai.com%252Fsignin-oidc%26response_type%3Dcode%26scope%3Dopenid%2520profile%2520email%2520phone%2520offline_access%2520BuyerProfileClaims%26code_challenge%3De0lc9yinf_BWkFZ0eGroXcCB9v_8opa2fq_AhPQOVvM%26code_challenge_method%3DS256%26response_mode%3Dform_post%26nonce%3D638721827358411961.MDIwNTM5NjQtMzZiOS00MzUwLTk2MDYtMDBiMDJmZWY5NDBjZWMzY2NkMzItZjExZi00MDg1LWJhOGUtYmFmMDFlZDJiNmVj%26state%3DCfDJ8NCW8OcYZ55Nml5GPUzf9CwG9VD2Zw6gduoU0vnrQ8tFZgVBFef5YRCU1_LoTDVq03CEXz76kdpNp-g_iDW6w2odhlC1AFvhr56GcWURuXCRxE1ApQymcPveST57hTwQ3z1G0RiEd6x96HUrRUoqbG2brQ3DeHT5KVovavPwJYWiPtqQ3dYnpzhokZw-SkrqtuRkC1bAY9knDUd-dwMUWGcYmnFCE9eEbExO9o3N0oA7LA9IGAptFBaMMlJkp1thYZ-XWVk71I2yEq4zOKMPhS723j--6GYMOga5TzBqgwiH5Br5S72g5Vjn3SC--WwKg56lITGL-PwBbFRvzfnwazHJcwNE9spuLKIIVKvzCNMwtZPPvEuPuZ_hDddvoxcoLbhczerdiZEKNUNJLSnPcDXS6TeacmIOrTWoNK8ENpdnn7nPE0tfY2sQKHAB7CDyENyHwV2HtfvpCVe1Tub48dP4V0V6zNyrvWL1ZF2riJlq")

        # Inform user and wait for login
        
        time.sleep(90)  # Give user time to log in

        # Save cookies after login
        self.save_cookies(page)
        browser.close()

    def scrape(self):
        with sync_playwright() as playwright:
            try:
                browser = playwright.chromium.launch(headless=False,args=[
                            "--window-position=-10000,-10000",  # Position window off-screen
                            "--disable-blink-features=AutomationControlled",
                        ])



                # Load cookies if available

                page = browser.new_page()
                self.load_cookies(page)
                page.goto(self.url, wait_until="domcontentloaded", timeout=10000)


                if self.check_login_required(page):
                    browser.close()
                    self.handle_login(playwright)
                    browser = playwright.chromium.launch(headless=False,args=[
                            "--window-position=-10000,-10000",  # Position window off-screen
                            "--disable-blink-features=AutomationControlled",
                        ])
                        
                        # Create a new browser context with a custom user-agent and viewport

                    page = browser.new_page()
                    self.load_cookies(page)
                    page.goto(self.url, wait_until="domcontentloaded", timeout=10000)


                    
                
                try:
                    page.wait_for_selector("div.data-container", timeout=5000)
                    self.save_cookies(page)
                    self.car_name = page.query_selector("h1").inner_text()

                    # Scrape data as soon as it's available
                    car_info_tables = page.query_selector_all("ul.data-list.data-list--details")
                    for table in car_info_tables:
                        rows = table.query_selector_all("li")
                        for row in rows:
                            spans = row.query_selector_all("span")
                            anchor = row.query_selector_all("a")
                            if len(spans) < 2:
                                if(len(anchor)>0 and len(spans)>0):
                                    key=spans[0].inner_text().strip()
                                    value = anchor[0].inner_text().strip()


                                    self.data[key] = value
                                    continue
                                else:
                                    continue
                            
                            key = spans[0].inner_text().strip()
                            value = spans[1].inner_text().strip()
                            to_leave = ["Branch:","Vehicle Location:","Time Left to Buy:","Pick up location:","Payment is due:","Pick up by:","Pre-bid Closes:","My Max Bid:","Selling Branch:","Restraint System:","Exterior/Interior:","Options:","Manufactued in:","Vehicle Class:","Lane/Run #:","Aisle/Stall:"]
                            if key in to_leave:
                                continue
                            if key=="Start Code:":

                                    value = page.query_selector("span[id='startcodeengine_novideo']")
                                    
                                    if value:
                                            value = value.inner_text().strip()
                                            self.data[key] = value
                                    else:
                                            value = ""

                            self.data[key] = value

                    current_bid_div = page.query_selector("div.action-area__secondary-info")
                    if(current_bid_div):
                        lis = current_bid_div.query_selector_all("li")
                        for li in lis:
                            if "Current Bid" in li.inner_text():
                                current_bid_element = li
                            else:
                                current_bid_element = None
                        
                        if current_bid_element:
                            spans = current_bid_element.query_selector_all("span")
                            if(len(spans)>1):
                                self.data["Current Bid"] = spans[1].inner_text()
                            

                            

                    image_elements = page.query_selector_all("img")
                    for img in image_elements:
                        if(img.get_attribute('src') is not None and img.get_attribute('src')[0:21]=="https://vis.iaai.com/"):
                            self.images.append(img.get_attribute('src').replace("161", "845").replace("120", "633"))


                    print("Scraping completed.")
                except TimeoutError:
                    print("Main content not loaded in time.")
                finally:
                    browser.close()
            except TimeoutError:
                print("Timeout occurred for IAAI Scraper.")
                browser.close()

    
class BeForwardScrper(BaseScraper):
    def __init__(self,url,crop_size):
        super().__init__(url,crop_size)
    def scrape(self):
        with sync_playwright() as playwright:


                browser = playwright.chromium.launch(headless=False,args=[
                        "--window-position=-10000,-10000",  # Position window off-screen
                        "--disable-blink-features=AutomationControlled",
                    ])
                
                # Open a new page in the connected browser
                page = browser.new_page()

                
                # Go to the desired URL
                page.goto(self.url, wait_until="domcontentloaded", timeout=10000)
                # page.wait_for_selector("h1",timeout=10000)
                car_name_element = page.query_selector("div.car-info-flex-box")
                if car_name_element:
                    car_name = car_name_element.query_selector("h1")
                    if car_name:
                        self.car_name = car_name.inner_text()
                # self.data['Price'] = page.query_selector("span.price.ip-usd-price").inner_text()
                car_info_div = page.query_selector("div.cf.specs-area")
                car_info_table = car_info_div.query_selector("table.specification")
                rows = car_info_table.query_selector_all('tr')
                for row in rows:
                    
                    keys = row.query_selector_all('th')
                    values = row.query_selector_all('td')

                    self.data[keys[0].inner_text()] = values[0].inner_text()
                    if(len(keys)==2 and len(values)==2):
                        self.data[keys[1].inner_text()] = values[1].inner_text()
                image_next_button = page.query_selector("img[id='fn-vehicle-detail-images-slider-next']")


                while(True):
                    image_next_button.click()
                    image = "https:" + page.query_selector("img[id='mainImage']").get_attribute('src').replace("\n"," ")
                    if(image in self.images):
                        break
                    self.images.append(image)
                    



                browser.close()
                # Check for CAPTCHA

class SBTJapanScraper(BaseScraper):
    def __init__(self,url,crop_size):
        super().__init__(url,crop_size)
    def scrape(self):
        
        with sync_playwright() as playwright:



                browser = playwright.chromium.launch(headless=False,args=[
                        "--window-position=-10000,-10000",  # Position window off-screen
                        "--disable-blink-features=AutomationControlled",
                    ])
                

                page = browser.new_page()

                page.goto(self.url+"?currency=2")

                car_name_element = page.query_selector('div.content')
                if car_name_element:
                    car_name = car_name_element.query_selector("h2")
                    if car_name:
                        self.car_name = car_name.inner_text()
                car_details_divs = page.query_selector_all("div.carDetails")
                if(len(car_details_divs)>1):
                    car_details_div = car_details_divs[1]
                else:
                    car_details_div = car_details_divs[0]

                car_details_table = car_details_div.query_selector("table.tabA")
                
                
                rows = car_details_table.query_selector_all("tr")
                # self.data["Price: "] = page.query_selector("span[id='fob']").inner_text()
                for row in rows:
                    key = row.query_selector_all("th")
                    value = row.query_selector_all("td")

                    self.data[key[0].inner_text()] = value[0].inner_text()
                    self.data[key[1].inner_text()] = value[1].inner_text()

                

                image_div = page.query_selector("div.photoBox")
                images = image_div.query_selector_all("img")
                for img in images:
                    if(img.get_attribute('src')[-3:]=='640'):
                        self.images.append(img.get_attribute('src'))
                

                

                browser.close()


                


class ManheimScraper(BaseScraper):
    def __init__(self, url, crop_size, cookies_path="cookies.json"):
        super().__init__(url,crop_size)
        self.cookies_path = cookies_path
        self.images = []

    def save_cookies(self, page):
        try:
            cookies = page.context.cookies()
            with open(self.cookies_path, "w") as file:
                json.dump(cookies, file)
            print("Cookies saved successfully.")
        except Exception as e:
            print(f"Error saving cookies: {e}")

    def load_cookies(self, page):
        try:
            with open(self.cookies_path, "r") as file:
                cookies = json.load(file)
                page.context.add_cookies(cookies)
            print("Cookies loaded successfully.")
        except FileNotFoundError:
            print("No cookies file found, proceeding with login.")

    def check_login_required(self, page):
        sign_in = page.query_selector("h1")
        return sign_in and sign_in.inner_text() == "SIGN IN"

    def handle_login(self, playwright):
        # Launch browser in visible mode for user login
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://auth.manheim.com/as/authorization.oauth2?adaptor=manheim_customer&client_id=smzbeqp277av7kx8jmx3syk9&redirect_uri=https%3A%2F%2Fhome.manheim.com%2Fcallback&response_type=code&scope=email+profile+openid+offline_access&state=%2Flogin")

        # Inform user and wait for login
        
        time.sleep(100)  # Give user time to log in

        # Save cookies after login
        self.save_cookies(page)
        browser.close()
    def scrape_auction_details(self,page):
        auction_info_element = page.query_selector("div.BidWidget__col1")
        details_mapping = {
            "Status":"span[data-test-id='status-label']",
            "Current Bid":"span.bid-widget__value.current-price",
            "Time Left": "span.bboEndStartTime"
  
                    }

                    # Extract data with handling for missing elements
        for key, selector in details_mapping.items():
            element = auction_info_element.query_selector(selector)
            if element:

                    self.data[key] = element.inner_text() 
      
        
        
    def scrape_car_details(self, page):
        car_name_element = page.query_selector("span.ListingTitle__title")
        if car_name_element:
            self.car_name = car_name_element.inner_text()
            print("Car Name:", self.car_name)

        car_details_element = page.query_selector("div[data-test-id='collapse-overview']")
        if car_details_element:
            columns = car_details_element.query_selector_all("div.dont-break-columns")
            for column in columns:
                key = column.query_selector("div.dt.collapsible-top-label")
                value = column.query_selector("div.dd,.collapsible-bottom-value")
                to_leave = ["BODY STYLE","TOP TYPE","FACILITATION","ORG MFG BASIC WARRANTY","MSRP"]
                if key and value:
                    if(key.inner_text() in to_leave):
                        continue
                    else:
                        self.data[key.inner_text()] = value.inner_text()



    def scrape_images(self, page):
        image_element = page.query_selector("div[id='fyusion-prism-viewer']")
        next_button = image_element.query_selector("a.svfy_a_next")
        for _ in range(30):
            img = image_element.query_selector("img.svfy_img")
            if img:
                img_src = img.get_attribute('src')
                if img_src not in self.images:
                    self.images.append(img_src)
                else:
                    break
            if next_button:
                next_button.click()
                time.sleep(1)
            else:
                break

    def scrape(self):
        with sync_playwright() as playwright:
            # Start browser off-screen
            browser = playwright.chromium.launch(headless=False,args=[
                        "--window-position=-10000,-10000",  # Position window off-screen
                        "--disable-blink-features=AutomationControlled",
                    ])
            page = browser.new_page()
            self.load_cookies(page)
            page.goto(self.url)

            try:
                # Check if login is required
                if self.check_login_required(page):
                    browser.close()  # Close off-screen browser
                    self.handle_login(playwright)  # Relaunch on-screen for login
                    # Re-launch off-screen after login
                    browser = playwright.chromium.launch(headless=False,args=[
                            "--window-position=-10000,-10000",  # Position window off-screen
                            "--disable-blink-features=AutomationControlled",
                        ])
                    page = browser.new_page()
                    self.load_cookies(page)
                    page.goto(self.url)

                # Scrape data after login
                
                page.wait_for_selector("div[id='fyusion-prism-viewer']")
                self.scrape_auction_details(page)
                self.scrape_car_details(page)
                self.scrape_images(page)

            except Exception as e:
                print(f"An error occurred during scraping: {e}")
            finally:
                browser.close()


          



def get_scraper(url):
    domain = urlparse(url).netloc
    if "copart.com" in domain:
        return CopartScraper(url,0)
    elif "iaai.com" in domain:
        return IAAIScraper(url,15)
    elif "beforward" in domain:
        return BeForwardScrper(url,25)
    elif "sbtjapan" in domain:
        return SBTJapanScraper(url,45)
    elif "manheim" in domain:
        return ManheimScraper(url,0)
    else:
        raise ValueError("Unsupported site")

# # Example Usage

# Main application
def main():
    app = QApplication(sys.argv)
    gui = MultiCarScraperGUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()







                
        

