import snapshot


class SnapshotFactory:
    snap_map = {}

    @classmethod
    def get_snapshot(cls, subvol, ts, classifier):
        if classifier:
            key = "{}.{}.{}".format(subvol, ts, classifier)
        else:
            key = "{}.{}".format(subvol, ts)
        if key in cls.snap_map:
            snap = cls.snap_map[key]
        else:
            snap = snapshot.Snapshot(subvol, ts)
            if classifier:
                snap.__classifier = classifier
            cls.snap_map[key] = snap
        return snap
