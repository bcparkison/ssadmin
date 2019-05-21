from os.path import join
import subprocess


class SnapshotReplicator:
    def __init__(self, source, destination):
        self.__source = source
        self.__destination = destination

    def replicate_snapshots(self):
        src_subvols = self.__source.get_subvolumes_with_snapshots()
        for vol in src_subvols:
            self.__replicate_snapshots_for_subvolume(vol)

    def __replicate_snapshots_for_subvolume(self, subvol):
        src_snap = self.__source.get_snapshots_for_subvolume(subvol)[-1]
        common_snaps = self.__source.find_shared_snapshots(self.__destination, subvol)
        parent_snap = None
        if common_snaps:
            parent_snap = common_snaps[-1]
        if parent_snap and src_snap == parent_snap:
            print("Skipping {} because no new snapshots were found".format(src_snap.get_name()))
        else:
            self.__replicate_snapshot(src_snap, parent_snap)

    def __replicate_snapshot(self, snapshot, parent=None):
        parent_arg = " -p {}".format(join(self.__source.get_path(), parent.get_name())) if parent else ""
        src_path = join(self.__source.get_path(), snapshot.get_name())
        command = "btrfs send{} {} | btrfs receive {}".format(parent_arg, src_path, self.__destination.get_path())
        print("Command: {}".format(command))
        # result = subprocess.call(command, shell=True)
        # print("Result: {}".format(result))
