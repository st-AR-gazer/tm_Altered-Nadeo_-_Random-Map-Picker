import os
import requests

def download_csv():
    password = os.getenv("WRBOT_API_PASSWORD")
    if not password:
        raise ValueError("WRBOT_API_PASSWORD is not set in environment variables.")

    url = f"https://tmapi.the418.gg/wrbot_api/data.csv?password={password}"

    response = requests.get(url)

    if response.status_code == 200:
        with open("data.csv", "wb") as file:
            file.write(response.content)
        print("File downloaded successfully as data.csv")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")

if __name__ == "__main__":
    download_csv()
