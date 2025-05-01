import os
import json

base_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(base_dir, 'data.csv')
json_path = os.path.join(base_dir, 'map_data.json')
out_path = os.path.join(base_dir, 'missing_uids.txt')

with open(csv_path, 'r', encoding='utf-8') as f:
    csv_uids = [line.strip() for line in f if line.strip()]

with open(json_path, 'r', encoding='utf-8') as f:
    map_data = json.load(f)

json_uids = {
    entry.get('mapUid')
    for entry in map_data.values()
    if entry.get('mapUid')
}

missing = [uid for uid in csv_uids if uid not in json_uids]

with open(out_path, 'w', encoding='utf-8') as out:
    if missing:
        out.write("Missing UIDs:\n")
        for uid in missing:
            out.write(f"{uid}\n")
    else:
        out.write("All CSV UIDs are present in map_data.json\n")
