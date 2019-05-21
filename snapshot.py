from functools import total_ordering


@total_ordering
class Snapshot:
    def __init__(self, subvolume, timestamp):
        self.__subvolume = subvolume
        self.__timestamp = timestamp
        self.__classifier = None
        self.__locations = []

    def get_subvolume(self):
        return self.__subvolume

    def get_name(self):
        if self.__classifier:
            return "{}.{}.{}".format(self.__subvolume, self.__classifier, self.__timestamp)
        else:
            return "{}.{}".format(self.__subvolume, self.__timestamp)

    def add_location(self, location):
        self.__locations.append(location)

    def at_location(self, location):
        return location in self.__locations

    def __eq__(self, other):
        return self.get_name() == other.get_name()

    def __lt__(self, other):
        return self.get_name() < other.get_name()
