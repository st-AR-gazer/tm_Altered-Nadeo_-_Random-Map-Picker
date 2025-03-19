import json
import sys
import argparse

from alteration_dictionary import alterations_dict

def normalize(s):
    return s.strip().lower().replace("–", "-").replace("—", "-")

def build_synonym_map(alter_dict):
    synonym_map = {}
    for canonical_key, synonyms_list in alter_dict.items():
        normalized_key = normalize(canonical_key)
        synonym_map[normalized_key] = canonical_key

        flattened = []
        for item in synonyms_list:
            if isinstance(item, list):
                flattened.extend(item)
            else:
                flattened.append(item)
        for s in flattened:
            s_norm = normalize(s)
            if s_norm:
                synonym_map[s_norm] = canonical_key
    return synonym_map


def extract_unique_alteration_mix(input_file, output_file, check_dictionary=False, skip_dict_known=False):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON. {e}")
        sys.exit(1)
    
    unique_alterations = set()
    for map_name, details in data.items():
        alteration_mix = details.get("alteration_mix", [])
        unique_alterations.add(tuple(alteration_mix))
    
    sorted_unique_alterations = sorted(
        list(unique_alterations),
        key=lambda tup: [x.lower() for x in tup]
    )
    
    if check_dictionary:
        synonym_map = build_synonym_map(alterations_dict)
    else:
        synonym_map = {}

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            count_written = 0
            idx = 0
            for alt_tuple in sorted_unique_alterations:
                idx += 1
                joined_line = "; ".join(alt_tuple)

                if not check_dictionary:
                    f.write(joined_line + "\n")
                    count_written += 1
                    continue

                recognized_flags = []
                recognized_details = []
                unrecognized = []
                for alt_str in alt_tuple:
                    alt_str_norm = normalize(alt_str)
                    if alt_str_norm in synonym_map:
                        recognized_flags.append(True)
                        recognized_details.append(f"{alt_str} -> {synonym_map[alt_str_norm]}")
                    else:
                        recognized_flags.append(False)
                        unrecognized.append(alt_str)

                if skip_dict_known and all(recognized_flags):
                    continue
                
                count_written += 1
                f.write(f"--- Alteration Mix #{idx} ---\n")
                f.write(f"Original: {joined_line}\n")
                
                if any(recognized_flags):
                    f.write("  Recognized:\n")
                    for rdet in recognized_details:
                        f.write(f"    - {rdet}\n")
                else:
                    f.write("  Recognized: None\n")
                
                if unrecognized:
                    f.write("  Unrecognized:\n")
                    for u in unrecognized:
                        f.write(f"    - {u}\n")
                else:
                    f.write("  Unrecognized: None\n")
                
                f.write("\n")
            
            print(f"Finished processing. Wrote {count_written} alteration entries to '{output_file}'.")
    
    except IOError as e:
        print(f"Error: Failed to write to '{output_file}'. {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Extract unique alteration mixes from a JSON file.")
    parser.add_argument("--input", default="./parsed_map_data.json", help="Path to input JSON file.")
    parser.add_argument("--output", default="./unique_alteration_mix.txt", help="Path to output text file.")
    parser.add_argument("--check-dict", action="store_true",
                        help="If set, attempts to match each alteration against the alterations_dict.")
    parser.add_argument("--skip-dict-known", action="store_true",
                        help="If set (together with --check-dict), skip writing any fully recognized lines to output.")
    
    args = parser.parse_args()
    
    extract_unique_alteration_mix(
        input_file=args.input,
        output_file=args.output,
        check_dictionary=args.check_dict,
        skip_dict_known=args.skip_dict_known
    )

if __name__ == "__main__":
    main()
