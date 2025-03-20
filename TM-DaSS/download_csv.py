import os
import subprocess
import requests
from dotenv import load_dotenv

def get_github_secret(secret_name, repo):
    load_dotenv()
    
    password = os.getenv(secret_name)
    if password:
        return password

    gh_path = r"C:\Program Files\GitHub CLI\gh.exe"
    try:
        result = subprocess.run(
            [gh_path, "secret", "get", secret_name, "-R", repo],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error fetching secret '{secret_name}': {e}")
        return None

def download_csv():
    repo = "st-AR-gazer/tm_Altered-Nadeo_-_Random-Map-Picker"
    password = get_github_secret("WRBOT_API_PASSWORD", repo)
    
    if not password:
        raise ValueError("Failed to fetch WRBOT_API_PASSWORD.")

    url = f"https://tmapi.the418.gg/wrbot_api/data.csv?password={password}"
    response = requests.get(url)

    if response.status_code == 200:
        os.makedirs("data", exist_ok=True)
        file_path = os.path.join("TM-DaSS", "data", "data.csv")
        with open(file_path, "wb") as file:
            file.write(response.content)
        print(f"File downloaded successfully as {file_path}")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")

if __name__ == "__main__":
    download_csv()
