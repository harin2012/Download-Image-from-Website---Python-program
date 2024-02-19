import tkinter as tk
from tkinter import filedialog
import time
import threading
from PIL import Image, ImageTk
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import requests
import io


def download_images(url, img_tags, name, download_path, count, downloaded_urls, min_images, max_images):
    for img_tag in img_tags:
        if count >= max_images:  # Check if the count exceeds the maximum limit
            return count  # Exit if maximum limit reached
        img_url = urljoin(url, img_tag['src'])
        if img_url not in downloaded_urls:
            img_name = img_tag.get('alt', '')
            if name.lower() in img_name.lower():
                img_data = requests.get(img_url).content
                # Construct full file path
                file_path = os.path.join(
                    download_path, f"{img_name}_{count}.jpg")
                # Write image data to file
                with open(file_path, 'wb') as f:
                    f.write(img_data)
                count += 1
                # Add URL to set of downloaded URLs
                downloaded_urls.add(img_url)
                # Update download counter label
                counter_label.config(
                    text=f"Images downloaded: {count}/{max_images}")
                # Preview image in GUI
                show_image(img_data)
    return count


def show_image(img_data):
    image = Image.open(io.BytesIO(img_data))
    image.thumbnail((200, 200))
    photo = ImageTk.PhotoImage(image)
    image_label.config(image=photo)
    image_label.image = photo  # Keep a reference to the image to prevent garbage collection


def download_process():
    global stop_flag
    stop_flag = False  # Initialize stop flag
    url = url_entry.get()
    name = name_entry.get()
    download_path = path_entry.get()
    # Minimum number of images to download
    min_images = int(min_images_entry.get())
    max_images = int(max_images_entry.get())
    # Cap max_images to at least min_images
    max_images = max(min_images, max_images)

    # Initialize Chrome WebDriver
    driver = webdriver.Chrome()
    driver.get(url)

    # Scroll down the page to load more images and download them
    last_height = 0
    count = 0
    downloaded_urls = set()
    while True:
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Adjust sleep time as needed
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height or count >= max_images or stop_flag:
            break
        last_height = new_height

        # Get page source after scrolling
        page_source = driver.page_source

        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')
        img_tags = soup.find_all('img')

        count = download_images(
            url, img_tags, name, download_path, count, downloaded_urls, min_images, max_images)

    driver.quit()  # Close the WebDriver

    print(f"{count} images downloaded successfully!")


def process():
    global download_thread
    download_thread = threading.Thread(target=download_process)
    download_thread.start()


def stop():
    global stop_flag
    stop_flag = True


def exit_app():
    if download_thread and download_thread.is_alive():
        stop()
        download_thread.join()
    root.destroy()


def browse_button():
    folder_path = filedialog.askdirectory()
    path_entry.delete(0, tk.END)
    path_entry.insert(0, folder_path)


# Create the main window
root = tk.Tk()
root.title("Image Downloader")

# URL Entry
url_label = tk.Label(root, text="Enter website URL:")
url_label.grid(row=0, column=0)
url_entry = tk.Entry(root, width=50)
url_entry.grid(row=0, column=1, padx=5, pady=5)

# Name Entry
name_label = tk.Label(root, text="Enter person's name:")
name_label.grid(row=1, column=0)
name_entry = tk.Entry(root, width=50)
name_entry.grid(row=1, column=1, padx=5, pady=5)

# Download Path Entry
path_label = tk.Label(root, text="Select download path:")
path_label.grid(row=2, column=0)
path_entry = tk.Entry(root, width=50)
path_entry.grid(row=2, column=1, padx=5, pady=5)
browse_button = tk.Button(root, text="Browse", command=browse_button)
browse_button.grid(row=2, column=2)

# Minimum Images Entry
min_images_label = tk.Label(root, text="Minimum number of images:")
min_images_label.grid(row=3, column=0)
min_images_entry = tk.Entry(root, width=10)
min_images_entry.grid(row=3, column=1, padx=5, pady=5)
min_images_entry.insert(0, "300")  # Default value

# Maximum Images Entry
max_images_label = tk.Label(root, text="Maximum number of images:")
max_images_label.grid(row=4, column=0)
max_images_entry = tk.Entry(root, width=10)
max_images_entry.grid(row=4, column=1, padx=5, pady=5)

# Process Button
process_button = tk.Button(root, text="Process", command=process)
process_button.grid(row=5, column=1, pady=10)

# Stop Button
stop_button = tk.Button(root, text="Stop", command=stop)
stop_button.grid(row=5, column=0, pady=10)

# Exit Button
exit_button = tk.Button(root, text="Exit", command=exit_app)
exit_button.grid(row=5, column=2, pady=10)

# Download Counter Label
counter_label = tk.Label(root, text="Images downloaded: 0/300")
counter_label.grid(row=6, column=1)

# Image Preview Label
image_label = tk.Label(root)
image_label.grid(row=7, column=1, pady=10)

stop_flag = False  # Flag to stop the process
download_thread = None

root.mainloop()
