from os import listdir
from os.path import isdir, join
import re
from snapshot_factory import SnapshotFactory


class SnapLocation:
    __SNAP_NAME_REGEX = r'(.*)-(\d\d\d\d-\d\d-\d\d\.\d\d-\d\d-\d\d)'

    def __init__(self, path):
        self.__path = path
        self.__snap_list = self.__find_snapshots()

    def __find_snapshots(self):
        snapshots = []
        names = [snap for snap in listdir(self.__path) if (isdir(join(self.__path, snap)))]
        for name in names:
            match = re.match(self.__SNAP_NAME_REGEX, name)
            if match:
                snapshot = SnapshotFactory.get_snapshot(match.group(1), match.group(2), None)
                snapshot.add_location(self)
                snapshots.append(snapshot)
        snapshots.sort()
        return snapshots

    def print_snaps(self):
        print("Location {} contains:".format(self.__path))
        for snap in self.__snap_list:
            print("\t{}".format(snap.get_name()))

    def get_path(self):
        return self.__path

    def contains_snapshot(self, other):
        return other in self.__snap_list

    def find_shared_snapshots(self, other, subvol):
        shared = []
        for snap in self.get_snapshots_for_subvolume(subvol):
            if snap.at_location(other):
                shared.append(snap)
        return shared

    def get_subvolumes_with_snapshots(self):
        subvols = set(())
        for snap in self.__snap_list:
            subvols.add(snap.get_subvolume())
        return subvols

    def get_snapshots_for_subvolume(self, subvol):
        snapshots = []
        for snap in self.__snap_list:
            if snap.get_subvolume() == subvol:
                snapshots.append(snap)
        return snapshots
