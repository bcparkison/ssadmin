#!/usr/bin/python3
import argparse
from collections import defaultdict
import datetime
from os import listdir
from os.path import normpath, isdir, join
import re
import subprocess

SRC_SNAP_DIR = normpath("/mnt/fsroot/snapshots")
DST_SNAP_DIR = normpath("/mnt/backup")
SNAP_TS_FORMAT = "%Y-%m-%d.%H-%M-%S"
RETENTION_DAYS = 1
SNAP_NAME_REGEX = r'(.*)-(\d\d\d\d-\d\d-\d\d\.\d\d-\d\d-\d\d)'

srcSnaps = [snap for snap in listdir(SRC_SNAP_DIR) if (isdir(join(SRC_SNAP_DIR, snap)))]
dstSnaps = [snap for snap in listdir(DST_SNAP_DIR) if (isdir(join(DST_SNAP_DIR, snap)))]


def print_src_snaps():
    for snap in srcSnaps:
        print("Source snapshot:", snap)


def print_dst_snaps():
    for snap in dstSnaps:
        print("Destination snapshot:", snap)


def run_command(command):
    if command:
        print("Running: {}".format(command))
        result = subprocess.call(command, shell=True)
        print("Command result: {}".format(result))


# Snapshot have names like <subvol>-<year-month-day>.<hour-minute-second>
# This method takes a list of snapshots, and returns a map of subvolumes to
# sorted lists of snapshots.
def sort_snaps(snapshots):
    snap_dict = defaultdict(list)
    for snap in snapshots:
        match = re.match(SNAP_NAME_REGEX, snap)
        if match:
            snap_dict[match.group(1)].append(match.group(2))
        else:
            print("No snapshot pattern matched for: ", snap)
    for name in snap_dict:
        snap_dict[name].sort()
    return snap_dict


# For a set of snapshot timestamps on the source and destination, try to
# figure out the base (parent) and current snapshot.  Right now, it's
# simplistic - either the latest snapshot on the destination matches, or
# we decide there is no matching snapshot.  The latest source snapshot
# is always considered the current.
def match_snaps(src_timestamps, dst_timestamps):
    last_dst = None
    if dst_timestamps:
        if dst_timestamps[-1] in src_timestamps:
            last_dst = dst_timestamps[-1]
    return last_dst, src_timestamps[-1]


def make_snap_path(basepath, subvol, timestamp):
    return join(basepath, subvol + "-" + timestamp)


def backup_snapshot(subvol, parent_ts, current_ts):
    src_path = make_snap_path(SRC_SNAP_DIR, subvol, current_ts)
    command = None
    if parent_ts is None:
        # print("Doing full snapshot backup on {} because there is no shared parent snapshot".format(subvol))
        run_command("btrfs send {} | btrfs receive {}".format(src_path, DST_SNAP_DIR))
    elif current_ts <= parent_ts:
        print("Skipping {} because current snapshot ({}) is not newer than parent snapshot ({})".format(
            subvol, current_ts, parent_ts))
    else:
        # print("Doing incremental backup on {} from {} -> {}".format(subvol, parent_ts, current_ts))
        parent_path = make_snap_path(SRC_SNAP_DIR, subvol, parent_ts)
        run_command("btrfs send -p {} {} | btrfs receive {}".format(parent_path, src_path, DST_SNAP_DIR))


def backup_snapshots():
    src_sorted = sort_snaps(srcSnaps)
    dst_sorted = sort_snaps(dstSnaps)
    for subvolume in src_sorted:
        (parent, current) = match_snaps(src_sorted[subvolume], dst_sorted[subvolume])
        backup_snapshot(subvolume, parent, current)


def cleanup_snapshots():
    today = datetime.datetime.today()
    retention = today - datetime.timedelta(days=RETENTION_DAYS)
    retention_str = retention.strftime(SNAP_TS_FORMAT)
    snaps = sort_snaps(srcSnaps)
    for subvol in snaps:
        for ts in snaps[subvol]:
            # TODO: Make this smart enough to not delete parent snapshot for backups
            if ts < retention_str:
                # print("Need to delete snapshot on subvolume {} with timestamp {}".format(subvol, ts))
                del_snap_path = make_snap_path(SRC_SNAP_DIR, subvol, ts)
                run_command("btrfs subvolume delete {}".format(del_snap_path))


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", type=str, choices=["backup", "cleanup"])
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    print_src_snaps()
    print_dst_snaps()
    if args.command == "backup":
        backup_snapshots()
    if args.command == "cleanup":
        cleanup_snapshots()
