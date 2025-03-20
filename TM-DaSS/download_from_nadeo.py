import requests
import time
import json
import os
import base64
import argparse



parser = argparse.ArgumentParser(description="Fetch map data from Nadeo online services.")
parser.add_argument('-v', '--verbose', action='store_true', help="Enable verbose output.")
args = parser.parse_args()
verbose = args.verbose



def encode_credentials(username, password):
    credentials = f"{username}:{password}"
    return base64.b64encode(credentials.encode('ascii')).decode('ascii')

def get_access_token(username, password):
    url = "https://prod.trackmania.core.nadeo.online/v2/authentication/token/basic"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {encode_credentials(username, password)}",
        "User-Agent": "I'm downloading all the Altered Nadeo maps to keep a plugin project up to date, this should only happen once, maybe twice a month on average, if you see this and have any questions or concerns please contact me, thank you!",
        "From": "@ar___ on discord (or ar@xjk.yt through e-mail, though discord is preferred :D)",
    }
    body = {"audience": "NadeoServices"}
    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 200:
        token = response.json()['accessToken']
        if verbose:
            print(f"Token obtained: {token}")
        return token
    else:
        if verbose:
            print(f"Error obtaining token: {response.status_code}")
        return None



def fetch_map_info(uid_batch, access_token):
    url = f"https://prod.trackmania.core.nadeo.online/maps/?mapUidList={','.join(uid_batch)}"
    headers = {'Authorization': f'nadeo_v1 t={access_token}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        if verbose:
            print(f"Error fetching data for batch: {response.status_code}")
        return None



def read_uids(file_path):
    if not os.path.exists(file_path):
        if verbose:
            print(f"File not found: {file_path}")
        return set()
    with open(file_path, 'r') as file:
        if verbose:
            print(f"Reading UIDs from {file_path}")
        return set(line.strip() for line in file)



def write_processed_uids(file_path, uids):
    if verbose:
        print(f"Writing processed UIDs to {file_path}")
    with open(file_path, 'a') as file:
        for uid in uids:
            file.write(uid + '\n')



def split_into_batches(uids, max_length, max_uid_count=220):
    batch = []
    current_length = 0
    for uid in uids:
        added_length = len(uid) + 1
        if current_length + added_length > max_length or len(batch) >= max_uid_count:
            yield batch
            batch = []
            current_length = 0
        batch.append(uid)
        current_length += added_length
    if batch:
        yield batch



uids = read_uids("data/data.csv")
processed_uids = read_uids("data/processed_uids.txt")
failed_uids = set()

unprocessed_uids = uids - processed_uids

if verbose:
    print(f"Total UIDs: {len(uids)}, Processed UIDs: {len(processed_uids)}, Unprocessed UIDs: {len(unprocessed_uids)}")

batches = split_into_batches(unprocessed_uids, 8000)

dedicated_username = 'AR..._ALT_MAPS_INFO_DOWNL'
dedicated_password = '#zW}fiA?i{RRFq&R'

access_token = get_access_token(dedicated_username, dedicated_password)
if not access_token:
    raise Exception("Failed to obtain access token")



map_data = {}
for batch in batches:
    response_data = fetch_map_info(batch, access_token)
    if response_data is None:
        failed_uids.update(batch)
        if verbose:
            print(f"Failed to fetch data for {len(batch)} maps")
        continue
    for item in response_data:
        filename = item.get('filename', 'Unknown')
        map_data[filename] = item
    write_processed_uids("data/processed_uids.txt", batch)
    if verbose:
        print(f"Processed batch of {len(batch)} maps")
    time.sleep(0.6)

if failed_uids:
    if verbose:
        print(f"Failed to fetch data for {len(failed_uids)} maps. UID list saved to 'failed_uids.txt'")
    write_processed_uids("data/failed_uids.txt", failed_uids)

with open("data/map_data.json", 'w', encoding='utf-8') as json_file:
    json.dump(map_data, json_file, indent=4, ensure_ascii=False)
    if verbose:
        print(f"Map data saved to data/map_data.json")