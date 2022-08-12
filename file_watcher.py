from hashlib import sha256 as hashlib_sha256
import os
import datetime


FC = dict[str, 'File']


def sha256(path: str) -> str:
    """
    Returns sha256 hashsum (as hex-str) of a file specified by `path`
    """
    hash_sha256 = hashlib_sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()



class File:
    def __init__(self) -> None:
        self.path: str = None
        self.path_rel: str = None
        self.checksum: str = None
        self.dt_mod: datetime.datetime = None

    @staticmethod
    def from_DirEntry(entry: os.DirEntry, root_dir = None):
        s = entry.stat()

        f = File()
        f.path = entry.path
        f.path_rel = os.path.relpath(f.path, root_dir)
        f.dt_mod = datetime.datetime.fromtimestamp(s.st_mtime_ns // 10 ** 9)  # Datetime resolution - just seconds.
        f.calc_checksum()

        return f

    def calc_checksum(self) -> str:
        self.checksum = sha256(self.path)
        return self.checksum

    def basename(self) -> str:
        return os.path.basename(self.path)

    def __str__(self) -> str:
        return f'{self.path}'


# class FileCollection:
#     def __init__(self) -> None:
#         self.files: FC = {}

#     def __iter__(self):
#         return self.files.__iter__()

#     def get_file(self, )



def get_files(path: str, root_dir: str = None) -> list[File]:
    if root_dir == None:
        root_dir = path

    l: list[File] = []

    for entry in os.scandir(path):
        if entry.is_file():
            f = File.from_DirEntry(entry, root_dir)
            l.append(f)
        elif entry.is_dir():
            l.extend(get_files(entry.path, root_dir))

    return l

def get_files_collection(files: list[File]) -> FC:
    return dict(zip([f.path_rel for f in files], files))


def unite(*fcs: FC) -> FC:
    united: FC = {}
    for fc in fcs:
        for path_rel in fc:
            f: File = fc[path_rel]
            if path_rel in united:
                if united[path_rel].dt_mod < f.dt_mod:
                    united[path_rel] = f
            else:
                united[path_rel] = f
    return united


# def get_difference(target: FC, real: FC):
#     newer_in_real: FC = []
#     older_in_real: FC = []

#     united = unite(target, real)

#     for path_rel in united:
#         f: File = united[path_rel]
#         if path_rel in real:
#             real_f: File = real[path_rel]
#             if real_f.dt_mod > f.dt_mod
#         else:
#             older_in_real.append(path_rel)

def find_newer(newer_fc: FC, older_fc: FC):
    l: list[str] = []
    for path_rel in newer_fc:
        if path_rel in older_fc:
            if newer_fc[path_rel].dt_mod > older_fc[path_rel].dt_mod \
                    and newer_fc[path_rel].checksum != older_fc[path_rel].checksum:
                l.append(path_rel)
        else:
            l.append(path_rel)
    return l


def copy_file(path_from, path_to):
    d = os.path.dirname(path_to)
    if not os.path.exists(d) and not os.path.isdir(d):
        os.makedirs(d)
    code = os.system(f'copy "{path_from}" "{path_to}"')
    print(code, f'copy "{path_from}" "{path_to}"')






# os.makedirs
