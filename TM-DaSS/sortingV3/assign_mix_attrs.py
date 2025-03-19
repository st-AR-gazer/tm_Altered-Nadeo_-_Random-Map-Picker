import json
import re
import logging
import os
import traceback
from concurrent.futures import ThreadPoolExecutor
from uids import (
    DISCOVERY_CAMPAIGNS,
    OFFICIAL_NADEO_AUTHOR_AND_SUBMITTOR_UIDS,
    special_uids,
    ALL_WEEKLY_SHORTS_MAP_NAMES,
    ALL_TOTD_MAP_NAMES,
    ALL_COMPETITION_MAP_NAMES
)

INPUT_FILE = 'map_data.json'
OUTPUT_FILE = 'parsed_map_data.json'
LOG_FILE = 'unmatched_maps.log'
if os.path.exists(LOG_FILE):
    os.remove(LOG_FILE)
    
from regex_pattern import *

OFFICIAL_NADEO_TAG = "official nadeo map"

logging.basicConfig(
    filename=LOG_FILE,
    filemode='a',
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S%z',
    level=logging.DEBUG # set to "WARNING" when done with debugging...
)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s', '%Y-%m-%dT%H:%M:%S%z')
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)

logger = logging.getLogger(__name__)

VALID_SEASONS = ["winter", "spring", "summer", "fall", "training"]
VALID_SEASONS_SHORT = ["wi", "sp", "su", "fa"]
VALID_MAPNUMBER_COLORS = ["white", "green", "blue", "red", "black"]
CHINESE_SEASON_MAP = {
    "\u590f\u5b63\u8d5b": "summer", # "夏季赛"
    "\u79cb\u5b63": "fall",         # "秋季"
    "\u8bad\u7ec3": "training",     # "训练"
    "夏季赛": "summer",
    "秋季": "fall",
    "训练": "training"   
}
MAPNUMBER_COLOR_REGEX = '|'.join(VALID_MAPNUMBER_COLORS)
SEASON_REGEX = '|'.join(VALID_SEASONS)
SEASON_SHORT_REGEX = '|'.join(VALID_SEASONS_SHORT)
SEASON_CHINESE_REGEX = '|'.join(CHINESE_SEASON_MAP.keys())

SANITIZE_PATTERN = re.compile(
    r'\$([0-9a-fA-F]{1,3}|[iIoOnNmMwWsSzZtTgG<>]|[lLhHpP](\[[^\]]+\])?)'
)

def sanitize_name(name: str) -> str:
    return SANITIZE_PATTERN.sub('', name).strip()

def validate_year(year: int) -> int:
    if year < 100:
        if 20 <= year <= 26:
            return 2000 + year
        else:
            logger.warning(f"Year {year} out of allowed range for short year (20-26).")
            return None
    else:
        if 2020 <= year <= 2026:
            return year
        else:
            logger.warning(f"Year {year} out of allowed range (2020-2026).")
            return None

def validate_mapnumber(map_nums: list) -> list:
    valid = []
    for num in map_nums:
        if 1 <= num <= 25:
            valid.append(num)
        else:
            logger.warning(f"Map number {num} out of allowed range (1-25).")
    return valid

# ------------------------------------------------------------
# REGEX PATTERNS (defined here for centralized attribute assignment)
# ------------------------------------------------------------
# see "regex_pattern.py"



ft_pattern = re.compile(
    r"(?:ft' |ft, |ft. |ft |featuring |AT by | AT  by |'AT  by |Feat )(\w+)",
    re.IGNORECASE
)

unvalidated_pattern = re.compile(
    r"(?: - unvalidated|unvalidated|not validated)",
    re.IGNORECASE)

def check_discovery_map_name(map_name: str) -> dict:
    match = discovery_full_pattern.match(map_name)
    if match:
        discovery_name = match.group()
        for campaign in DISCOVERY_CAMPAIGNS:
            for dmap_name, dmap_number in campaign['maps'].items():
                if dmap_name.lower() == discovery_name.lower():
                    year = validate_year(int(campaign.get('year', 0)))
                    mapnumber = validate_mapnumber([int(dmap_number)])
                    return {
                        'discoveryname': discovery_name,
                        'season': campaign.get('season', '').capitalize(),
                        'year': year,
                        'mapnumber': mapnumber,
                        'type': campaign.get('name', '')
                    }
    return {}

def check_totd_map_name(map_name: str) -> bool:
    return bool(totd_full_pattern.match(map_name))

def try_special_uids(map_uid: str):
    for entry in special_uids:
        if entry['uid'].lower() == map_uid.lower():
            year = int(entry['year']) if 'year' in entry and entry['year'] else None
            year = validate_year(year) if year else None

            map_nums = []
            if 'mapNumber' in entry and entry['mapNumber']:
                valid_map_nums = validate_mapnumber([int(m) for m in entry['mapNumber']])
                if valid_map_nums:
                    map_nums = valid_map_nums

            is_unvalidated = entry.get('validated', True) is False

            attributes = {
                'season': entry['season'].capitalize() if 'season' in entry and entry['season'] else None,
                'year': year,
                'mapnumber': map_nums,
                'alteration_mix': [entry['alteration']] if entry.get('alteration') else [],
                'unvalidated': is_unvalidated,
                'ft': None
            }

            attributes['pass_special'] = entry.get('pass', False)
            return attributes
    return None



def extract_and_remove_ft(map_name: str):
    match = ft_pattern.search(map_name)
    if match:
        username = match.group(1)
        start, end = match.span()
        map_name = map_name[:start] + map_name[end:]

    map_name = map_name.strip()
    if map_name.endswith('()'):
        map_name = map_name[:-2].strip()

    if map_name.startswith('(') and map_name.endswith(')'):
        map_name = map_name[1:-1].strip()

    return map_name, username if match else None

def extract_and_remove_unvalidated(map_name: str):
    match = unvalidated_pattern.search(map_name)
    is_unvalidated = False
    if match:
        is_unvalidated = True
        map_name = unvalidated_pattern.sub('', map_name).strip()

    if map_name.endswith('()'):
        map_name = map_name[:-2].strip()

    if map_name.startswith('(') and map_name.endswith(')'):
        map_name = map_name[1:-1].strip()

    return map_name, is_unvalidated


def normalize_whitespace(map_name: str):
    return re.sub(r'\s+', ' ', map_name).strip()

def match_known_patterns(map_name: str, map_uid: str = None):
    # See top of file for pattern definitions
    # CHINESE_SEASON_MAP = {
    #     "\u590f\u5b63\u8d5b": "summer", # "夏季赛"
    #     "\u79cb\u5b63": "fall",         # "秋季"
    #     "\u8bad\u7ec3": "training"      # "训练"
    # }

    for pattern in ALL_PATTERNS:
        match = pattern.match(map_name)
        if match:
            attrs = match.groupdict()
            
            # Handle discovery
            if 'discoveryname' in attrs and attrs['discoveryname']:
                discovery_name = attrs['discoveryname']
                for campaign in DISCOVERY_CAMPAIGNS:
                    for dmap_name, dmap_number in campaign['maps'].items():
                        if dmap_name.lower() == discovery_name.lower():
                            year = validate_year(int(campaign['year']))
                            mapnumber = validate_mapnumber([int(dmap_number)])
                            attrs['year'] = year
                            attrs['mapnumber'] = mapnumber
                            attrs['season'] = campaign['season'].capitalize()
                            attrs['type'] = campaign['name']
                            attrs['alteration_mix'] = [attrs['alteration_mix']]
                            break
                return attrs
            
            # Handle TOTD
            if totd_full_pattern.match(map_name):
                attrs['season'] = None
                attrs['year'] = None
                attrs['mapnumber'] = []
                attrs['type'] = 'totd'
                attrs['alteration_mix'] = [attrs['alteration_mix']]
                return attrs
            
            # Handle competitions
            if 'competitionname' in attrs and attrs['competitionname']:
                competition_name = attrs['competitionname']
                for competition in ALL_COMPETITION_MAP_NAMES:
                    if competition_name.lower() in [m.lower() for m in competition["maps"]]:
                        attrs['season'] = competition['season'] if competition['season'] != '_' else None
                        attrs['year'] = validate_year(int(competition['year']))
                        attrs['type'] = competition['competition']
                        attrs['mapnumber'] = []
                        attrs['alteration_mix'] = [attrs['alteration_mix']]
                        break
                return attrs
            
            # Handle spring2020
            if 'spring2020' in attrs and attrs['spring2020']:
                code = attrs['spring2020'].upper()
                season = 'Spring'
                year = 2020
                map_num = int(code[1:])
                if code.startswith('T'):
                    map_num += 10
                valid_mapnums = validate_mapnumber([map_num])
                if not valid_mapnums:
                    return None
                attrs['season'] = season
                attrs['year'] = year
                attrs['mapnumber'] = valid_mapnums
                attrs['alteration_mix'] = []
                attrs['type'] = None
                return attrs

            # Validate year
            if 'year' in attrs and attrs['year']:
                y = validate_year(int(attrs['year']))
                if y is None:
                    return None
                attrs['year'] = y
            else:
                attrs['year'] = None
            
            # Handle map numbers
            single_mapnumber = []
            if 'mapnumber' in attrs and attrs['mapnumber']:
                try:
                    m = validate_mapnumber([int(attrs['mapnumber'])])
                    if not m:
                        return None
                    single_mapnumber = m
                except ValueError:
                    logger.warning(f"Non-numeric single mapnumber: {attrs['mapnumber']}")
                    single_mapnumber = []

            multiple_mapnumbers = []

            # Handle color-coded sets
            if 'mapnumber_color' in attrs and attrs['mapnumber_color']:
                colour_map = {
                    'white': range(1, 6),
                    'green': range(6, 11),
                    'blue': range(11, 16),
                    'red': range(16, 21),
                    'black': range(21, 26)
                }
                c = attrs['mapnumber_color'].lower()
                if c in colour_map:
                    multiple_mapnumbers.extend(colour_map[c])
                else:
                    logger.warning(f"Unknown colour '{attrs['mapnumber_color']}' for map numbers.")

            # Handle "Sections X joined"
            if 'mapnumber_section' in attrs and attrs['mapnumber_section']:
                try:
                    sec_num = int(attrs['mapnumber_section'])
                    if not single_mapnumber and not multiple_mapnumbers:
                        single_mapnumber = validate_mapnumber([sec_num])
                    else:
                        combined = multiple_mapnumbers + single_mapnumber
                        combined.append(sec_num)
                        multiple_mapnumbers = validate_mapnumber(combined)
                        single_mapnumber = []
                except ValueError:
                    logger.warning(f"Non-numeric sections value: {attrs['mapnumber_section']}")

            # Handle mapnumber_1 [...] mapnumber_25
            for i in range(1, 26):
                key = f'mapnumber_{i}'
                if key in attrs and attrs[key]:
                    try:
                        val = int(attrs[key])
                        if single_mapnumber and not multiple_mapnumbers:
                            multiple_mapnumbers = single_mapnumber[:]
                            single_mapnumber = []
                        multiple_mapnumbers.append(val)
                    except ValueError:
                        logger.warning(f"Non-numeric map number found in {key}: {attrs[key]}")

            # Handle mapnumber_multiple
            if 'mapnumber_multiple' in attrs and attrs['mapnumber_multiple']:
                raw_multiple = attrs['mapnumber_multiple'].strip()
                raw_nums = re.split(r'[&\s]+', raw_multiple)
                found_nums = []
                for raw_num in raw_nums:
                    if raw_num.isdigit():
                        found_nums.append(int(raw_num))
                    else:
                        if raw_num:
                            logger.warning(f"Non-numeric mapnumber found: {raw_num}")
                if single_mapnumber and not multiple_mapnumbers:
                    multiple_mapnumbers = single_mapnumber[:]
                    single_mapnumber = []
                multiple_mapnumbers.extend(found_nums)

            if multiple_mapnumbers:
                multiple_mapnumbers = validate_mapnumber(multiple_mapnumbers)

            if single_mapnumber and multiple_mapnumbers:
                combined = multiple_mapnumbers + single_mapnumber
                combined = validate_mapnumber(combined)
                multiple_mapnumbers = combined
                single_mapnumber = []

            if multiple_mapnumbers:
                attrs['mapnumber'] = multiple_mapnumbers
            else:
                attrs['mapnumber'] = single_mapnumber

            # Clean up
            fields_to_remove = ['mapnumber_color', 'mapnumber_section', 'mapnumber_multiple', 'spring2020', 'discoveryname', 'competitionname']
            for i in range(1, 26):
                fields_to_remove.append(f'mapnumber_{i}')
            for field in fields_to_remove:
                if field in attrs:
                    del attrs[field]

            # Handle Chinese season names from season_chinese
            if 'season_chinese' in attrs and attrs['season_chinese']:
                season_chinese_value = attrs['season_chinese']
                if season_chinese_value in CHINESE_SEASON_MAP:
                    attrs['season'] = CHINESE_SEASON_MAP[season_chinese_value]
                else:
                    logger.warning(f"Unknown Chinese season '{season_chinese_value}'")
                del attrs['season_chinese']

            # Expand season abbreviations
            if attrs.get('season', None):
                season_abbr = attrs['season'].lower()
                if season_abbr == 'su':
                    attrs['season'] = 'summer'
                elif season_abbr == 'fa':
                    attrs['season'] = 'fall'
                elif season_abbr == 'sp':
                    attrs['season'] = 'spring'
                elif season_abbr == 'wi':
                    attrs['season'] = 'winter'

            # Updated logic: treat "training" as type, use "Spring 2020" for season.
            if attrs.get('season') and attrs.get('season').lower() in ['training', '训练']:
                attrs['type'] = 'training'
                attrs['season'] = 'Spring'
                attrs['year'] = 2020

            if attrs.get('season') and attrs.get('season').lower() == '夏季赛':
                attrs['season'] = 'summer'
            if attrs.get('season') and attrs.get('season').lower() == '秋季':
                attrs['season'] = 'fall'

            if 'season' in attrs and attrs.get('season'):
                attrs['season'] = attrs['season'].capitalize()
            else:
                attrs['season'] = None
                
            # Collect all alterations into alteration_mix
            alterations = []
            for key in list(attrs.keys()):
                if key.startswith('alteration_'):
                    alterations.append(attrs[key].strip())
                    del attrs[key]

            # Handle plain 'alteration' if present
            plain_alt = attrs.get("alteration", "").strip()
            if plain_alt:
                alterations.append(plain_alt)
                del attrs["alteration"]

            if alterations:
                attrs["alteration_mix"] = alterations
            else:
                attrs["alteration_mix"] = []

            if "alteration_additional_info" in attrs:
                attrs["alterationinfo"] = attrs["alteration_additional_info"]
                del attrs["alteration_additional_info"]

            attrs.setdefault('type', None)

            return attrs
    return None

def assign_attributes(item_data: dict) -> dict:
    raw_name = item_data['name']
    sanitized_name = sanitize_name(raw_name)
    filename = sanitize_name(item_data['filename'].replace('.Map.Gbx', ''))
    map_uid = item_data.get('mapUid', '')

    sanitized_name, ft_username = extract_and_remove_ft(sanitized_name)
    sanitized_name, is_unvalidated_name = extract_and_remove_unvalidated(sanitized_name)

    sanitized_name = normalize_whitespace(sanitized_name)
    filename = normalize_whitespace(filename)

    attributes = match_known_patterns(sanitized_name, map_uid)

    if not attributes:
        special_attrs = try_special_uids(map_uid)
        if special_attrs:
            attributes = special_attrs

    if not attributes and sanitized_name != filename:
        attributes = match_known_patterns(filename)

    if not attributes:
        attributes = {
            'season': None,
            'year': None,
            'mapnumber': [],
            'alteration_mix': [],
            'type': None,
            'ft': None,
            'unvalidated': False
        }
        logger.warning(f"Unmatched map name: {raw_name} (sanitized: {sanitized_name}), totd: {check_totd_map_name(sanitized_name)}, discovery: {check_discovery_map_name(sanitized_name)}")

    if ft_username:
        attributes['ft'] = ft_username

    if is_unvalidated_name:
        attributes['unvalidated'] = True

    special_attrs = try_special_uids(map_uid)
    if special_attrs and special_attrs.get('unvalidated', False):
        attributes['unvalidated'] = True

    if (
        item_data.get('author') in OFFICIAL_NADEO_AUTHOR_AND_SUBMITTOR_UIDS or
        item_data.get('submitter') in OFFICIAL_NADEO_AUTHOR_AND_SUBMITTOR_UIDS
    ):
        attributes['alteration_mix'] = [OFFICIAL_NADEO_TAG]

    return {**item_data, **attributes}


def process_item(item: tuple) -> tuple:
    key, data = item
    parsed_attrs = assign_attributes(data)
    combined_data = {**data, **parsed_attrs}
    return key, combined_data

def main():
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            map_data = json.load(f)
    except FileNotFoundError:
        logger.error(f"Input file {INPUT_FILE} not found.")
        return
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {INPUT_FILE}: {e}")
        return

    items = list(map_data.items())

    results = {}


    # Write totd pattern groups to files
    try:
        with open('totd_pattern_group.txt', 'w', encoding='utf-8') as f:
            f.write(totd_pattern_group)
        logger.info("totd_pattern_group written to pattern_dings.txt")
    except Exception as e:
        logger.error(f"Error writing to pattern_dings.txt: {e}")
    
    # Write discovery pattern groups to files
    try:
        discovery_map_names = []
        for campaign in DISCOVERY_CAMPAIGNS:
            discovery_map_names.extend(campaign['maps'].keys())
        discovery_pattern_group = "(?:" + "|".join([re.escape(name) for name in discovery_map_names]) + ")"
        with open('discovery_pattern_group.txt', 'w', encoding='utf-8') as f:
            f.write(discovery_pattern_group)
        logger.info("discovery_pattern_group written to discovery_pattern_group.txt")
    except Exception as e:
        logger.error(f"Error writing discovery_pattern_group.txt: {e}")
        
    # Write competition pattern groups to files
    try:
        with open('competition_pattern_group.txt', 'w', encoding='utf-8') as f:
            f.write(competition_pattern_group)
        logger.info("competition_pattern_group written to competition_pattern_group.txt")
    except Exception as e:
        logger.error(f"Error writing competition_pattern_group.txt: {e}")


    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = [executor.submit(process_item, item) for item in items]
        for future in futures:
            try:
                key, value = future.result()
                results[key] = value
            except Exception as e:
                # logger.exception("Error processing item")
                pass

    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        logger.info(f"Parsed data written to {OUTPUT_FILE}")
    except Exception as e:
        logger.error(f"Error writing to output file {OUTPUT_FILE}: {e}")

if __name__ == "__main__":
    main()