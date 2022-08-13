from sys import platform as sys_platform
if sys_platform != "win32":
    raise Exception(f'Your current platform is "{sys_platform}". Only "win32" is supported for now')

from hashlib import sha256 as hashlib_sha256
import os
import datetime
import threading
from time import sleep
import json

FCs = list['FilesCollection']


def sha256(path: str) -> str:
    """
    Returns sha256 hashsum (as hex-str) of a file specified by `path`
    """
    hash_sha256 = hashlib_sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


class IFile():
    pass

class IFilesCollection():
    def __init__(self) -> None:
        self.path: str = None
        self.files: list[File] = []

    def get_by_relpath(self, relpath: str) -> IFile:
        pass


class File(IFile):
    def __init__(self, parent: IFilesCollection) -> None:
        super().__init__()
        self.parent: IFilesCollection = parent
        self.relpath: str = None  # path relative to parent path
        self.mod_ts: int = None  # modification timestamp (seconds)
        self.checksum: str = None  # hex-str sha256 checksum
        self.size: int = None  # size in bytes

    @staticmethod
    def from_DirEntry(entry: os.DirEntry, parent: IFilesCollection) -> 'File':
        stat = entry.stat()
        f = File(parent)
        f.relpath = os.path.relpath(entry.path, parent.path)
        f.mod_ts = stat.st_mtime_ns // 10 ** 9  # Datetime resolution - just seconds.
        f.calc_checksum()
        f.size = stat.st_size
        return f

    @staticmethod
    def fromJSON(d: dict, parent: IFilesCollection) -> 'File':
        f = File(parent)
        # No check ?
        vars(f).update(d)
        return f

    def path_abs(self) -> str:
        return os.path.join(self.parent.path, self.relpath)

    def calc_checksum(self) -> str:
        self.checksum = sha256(self.path_abs())
        return self.checksum

    def basename(self) -> str:
        return os.path.basename(self.path_abs())

    def __str__(self) -> str:
        return f'"{self.path_abs()}"'

    def __repr__(self) -> str:
        return f'<File "{self.path_abs()}" at {hex(id(self))}>'


class FilesCollection(IFilesCollection):
    def __init__(self, path: str, auto_read: bool = True) -> None:
        super().__init__()
        self.path: str = path
        if auto_read:
            self.construct_files(self.path)

    def construct_files(self, path: str) -> list[File]:
        """
        Returns list of `File` objects, which are constructed with parent `fc`.
        Recursive.
        """
        for entry in os.scandir(path):
            if entry.is_file():
                f = File.from_DirEntry(entry, self)
                self.files.append(f)
            elif entry.is_dir():
                self.construct_files(entry.path)

    @staticmethod
    def empty(path: str):
        return FilesCollection(path, False)

    def has_relpath(self, relpath: str) -> bool:
        for f in self.files:
            if f.relpath == relpath:
                return True
        return False

    def get_by_relpath(self, relpath: str) -> File:
        for f in self.files:
            if f.relpath == relpath:
                return f
        raise Exception(f'No file with relative path "{relpath}" in {self}')

    def find_newer(newer_fc: 'FilesCollection', older_fc: 'FilesCollection') -> list[File]:
        l: list[File] = []
        for path_rel in map(lambda f: f.relpath, newer_fc.files):
            f_new = newer_fc.get_by_relpath(path_rel)
            if older_fc.has_relpath(path_rel):
                f_old = older_fc.get_by_relpath(path_rel)
                if f_new.mod_ts > f_old.mod_ts \
                        and f_new.checksum != f_old.checksum:
                    l.append(f_new)
            else:
                l.append(f_new)
        return l


def toJSON(fcs: FCs) -> dict:
    lfc = []
    for fc in fcs:
        l = []
        for f in fc.files:
            l.append({
                "relpath": f.relpath,
                "mod_ts": f.mod_ts,
                "checksum": f.checksum,
                "size": f.size,
            })
        lfc.append({
            "path": fc.path,
            "files": l,
        })
    return lfc


def fromJSON(d: dict) -> FCs:
    l: FCs = []
    for fcrepr in d:
        fc = FilesCollection.empty(fcrepr["path"])
        l.append(fc)
        for frepr in fcrepr["files"]:
            fc.files.append(File.fromJSON(frepr, fc))
    return l


def load_files_info(path: str) -> FCs:
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        fcs = fromJSON(d)
        return fcs
    else:
        return []


def save_files_info(path: str, fcs: FCs) -> None:
    d = toJSON(fcs)
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)



class DirectoryWatcher():
    def __init__(self, path: str, fc: FilesCollection) -> None:
        self.path = path
        self.fc: FilesCollection = fc

    def find_change(self) -> list[File]:
        fc_new = self.read_directory()
        l = fc_new.find_newer(self.fc)
        return l

    def read_directory(self) -> FilesCollection:
        return FilesCollection(self.path)


def copy_file(path_from, path_to):
    d = os.path.dirname(path_to)
    if not os.path.exists(d) and not os.path.isdir(d):
        os.makedirs(d)
    code = os.system(f'copy "{path_from}" "{path_to}"')
    print(code, f'copy "{path_from}" "{path_to}"')



def watch_directory(dw: DirectoryWatcher, interval_function, interval_ms: int):
    flag = {"state": True}

    def func():
        while flag["state"]:
            l: list[File] = dw.find_change()
            interval_function(l)
            sleep(interval_ms / 1000)

    t = threading.Thread(target=func)

    def turn_off():
        flag["state"] = False
        t.join()

    t.start()
    return turn_off



# os.makedirs
