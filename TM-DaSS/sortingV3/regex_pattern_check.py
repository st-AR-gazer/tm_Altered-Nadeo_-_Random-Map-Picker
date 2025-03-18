import re
import sys
import argparse

def find_missing_patterns(file_path: str, verbose: bool=False):
    if verbose:
        print("Starting to check for missing patterns...")
        print(f"Reading file from: {file_path}")

    pattern_comment_regex = re.compile(r'^\s*#\s*Pattern', re.IGNORECASE)
    
    pattern_definition_regex = re.compile(
        r'^\s*(?P<varname>[A-Za-z_]\w*)\s*=\s*re\.compile\('
    )
    
    all_patterns_var_regex = re.compile(r'\b([A-Za-z_]\w*)\b')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    if verbose:
        print("Scanning for pattern definitions in file...")

    pattern_definitions = []
    pending_comment_line = None
    inside_comment_block = False
    
    for i, line in enumerate(lines):
        if pattern_comment_regex.search(line):
            pending_comment_line = line.strip()
            inside_comment_block = True
        else:
            match_def = pattern_definition_regex.search(line)
            if match_def and inside_comment_block:
                var_name = match_def.group('varname')
                pattern_definitions.append((i + 1, pending_comment_line, var_name))
                pending_comment_line = None
                inside_comment_block = False
    
    if verbose:
        print(f"Found {len(pattern_definitions)} pattern definitions.")

    if verbose:
        print("Scanning for ALL_PATTERNS array to identify which pattern variables are included...")

    all_patterns_vars = set()
    in_all_patterns_list = False
    bracket_stack = 0
    
    for line in lines:
        if not in_all_patterns_list:
            if 'ALL_PATTERNS' in line and '=' in line and '[' in line:
                in_all_patterns_list = True
                bracket_stack += line.count('[') - line.count(']')
                for match in all_patterns_var_regex.finditer(line):
                    var_candidate = match.group(1)
                    if '_pattern_' in var_candidate:
                        all_patterns_vars.add(var_candidate)
        else:
            bracket_stack += line.count('[')
            bracket_stack -= line.count(']')
            for match in all_patterns_var_regex.finditer(line):
                var_candidate = match.group(1)
                if '_pattern_' in var_candidate:
                    all_patterns_vars.add(var_candidate)
            if bracket_stack <= 0:
                in_all_patterns_list = False
    
    if verbose:
        print(f"Found {len(all_patterns_vars)} pattern variables in ALL_PATTERNS.")

    missing = []
    for line_num, comment_line, var_name in pattern_definitions:
        if var_name not in all_patterns_vars:
            missing.append((line_num, comment_line, var_name))
    
    if verbose:
        print("Comparison complete. Reporting results...")

    if not missing:
        print("No missing patterns found!")
    else:
        print("Missing Patterns Detected:\n")
        for (line_num, comment, var_name) in missing:
            print(f"Line {line_num}: '{var_name}' is not in ALL_PATTERNS.")
            print(f"  -> Pattern comment: {comment}")
            print()

def main():
    parser = argparse.ArgumentParser(description="Check for missing regex patterns in ALL_PATTERNS list.")
    parser.add_argument("file_path", help="Path to the file to check.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose output.")
    
    args = parser.parse_args()
    find_missing_patterns(args.file_path, args.verbose)

if __name__ == "__main__":
    main()
