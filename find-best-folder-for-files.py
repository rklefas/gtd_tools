#!/usr/bin/env python3
# Group loose files into subfolders: if a file stem (letters only, lowercased)
# contains a subfolder's name (same normalization), move it there. Longest
# folder name wins. Dry-run unless you pass --apply.
#
#   python auto-group-files.py ./downloads
#   python auto-group-files.py ./downloads --apply

from __future__ import print_function

import argparse
import os
import shutil
import sys


class GroupFilesError(Exception):
    """Raised when required data or environment is missing; script cannot proceed."""


def alpha_only(s):
    # Letters only, lowercased (Unicode isalpha).
    return "".join(c.lower() for c in s if c.isalpha())


def create_parser():
    parser = argparse.ArgumentParser(
        description=(
            "Move top-level files into existing subfolders when the file stem "
            "contains the folder name (letters only, case-insensitive). "
            "Dry-run unless --apply."
        )
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Working directory to scan (default: current directory)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Move files (default is dry-run: print planned moves only)",
    )
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include top-level files and folders whose names start with '.'",
    )
    return parser


def normalize_working_dir(pathx):
    working_dir = os.path.abspath(pathx)
    if not os.path.isdir(working_dir):
        raise GroupFilesError("Not a directory: %s" % working_dir)
    return working_dir

# redundant!
def discover_subfolder_match_targets(working_dir, args):
    # (folder_name, needle); longest needle first so the first match is the best.
    rows = []
    for name in os.listdir(working_dir):
        path = os.path.join(working_dir, name)
        if not os.path.isdir(path):
            continue
        if not args.include_hidden and name.startswith("."):
            continue
        needle = alpha_only(name)
        if not needle:
            continue
        rows.append((name, needle))
    rows.sort(key=lambda r: (-len(r[1]), r[0].lower()))
    if not rows:
        raise GroupFilesError(
            "No subdirectories with letters in their names under %s; nothing to match."
            % working_dir
        )
    return rows


def match_dest_folder(working_dir, name, target_folders):
    stem, _ext = os.path.splitext(name)
    countMap = {}

    print("Checking for: %s" % (name,))

    for folder_name, folder_slug in target_folders:
        countMap[folder_name] = calculate_match_score(working_dir,folder_name, stem)

    sortedCountMap = sorted(countMap.items(), key=lambda x: (-x[1], x[0].lower()))
    bestMatch = None

    if sortedCountMap[0]:

        bestMatch = sortedCountMap[0]

        if bestMatch[1] > 0:
            print("  Best Match: %s/" % (bestMatch[0]))
            print("  Score:      %d" % (bestMatch[1]))
            return bestMatch[0]

    print("  No folder name match")
    return None


def calculate_match_score(working_dir, folder_name, file_stem):

    folder_slug = alpha_only(folder_name)
    file_slug = alpha_only(file_stem)
    matchScore = 0

    if folder_slug in file_slug:
        print("  Match on folder: %s/" % (folder_name,))
        matchScore += 10

    path = os.path.join(working_dir, folder_name)
    subfiles = sorted(os.listdir(path))

    for name in subfiles:
        name_slug = alpha_only(name)
        parts = file_slug.split(' ')

        for part in parts:
            if part and part in name_slug:
                print("  Match on file: %s" % (name_slug,))
                matchScore += 1

    return matchScore



def try_file_move(working_dir, name, dest_folder, args):
    if dest_folder is None:
        return 0

    src = os.path.join(working_dir, name)
    dest_dir = os.path.join(working_dir, dest_folder)
    dest = os.path.join(dest_dir, name)

    if os.path.normpath(os.path.dirname(src)) == os.path.normpath(dest_dir):
        return 0
    if os.path.exists(dest):
        print("Skip (target exists): %s -> %s" % (name, dest_folder))
        return 0

    print("%s -> %s" % (name, dest_folder))

    if args.apply:
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
        shutil.move(src, dest)

    return 1


def group_files_in_working_dir(working_dir, args):

    script_name = os.path.basename(os.path.abspath(__file__))
    target_folders = discover_subfolder_match_targets(working_dir, args)
    move_count = 0

    print("")
    print("Working Directory: %s" % working_dir)
    print("  Items: %d" % len(os.listdir(working_dir)))
    print("  Folders: %d" % len(target_folders))
    print("")

    for name in sorted(os.listdir(working_dir)):

        if name == script_name:
            continue
        if name == 'Thumbs.db':
            continue
        path = os.path.join(working_dir, name)
        if not os.path.isfile(path):
            continue
        if not args.include_hidden and name.startswith("."):
            continue

        dest_folder = match_dest_folder(working_dir, name, target_folders)
        move_count += try_file_move(working_dir, name, dest_folder, args)

    print("")

    if not args.apply:
        print(
            "Dry run: %d file(s) would move. No files moved. Use --apply to move files."
            % move_count
        )
    else:
        print("Moved %d file(s)." % move_count)

    print("")


def main():
    parser = create_parser()
    if len(sys.argv) <= 1:
        parser.print_help()
        return 0

    try:
        args = parser.parse_args()
        working_dir = normalize_working_dir(args.directory)
        group_files_in_working_dir(working_dir, args)
        return 0
    except GroupFilesError as err:
        print(str(err), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main() or 0)
