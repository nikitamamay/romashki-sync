from sys import platform as sys_platform
if sys_platform != "win32":
    raise Exception(f'Your current platform is "{sys_platform}". Only "win32" is supported for now')

from hashlib import sha256 as hashlib_sha256
import os
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
        self.files: list[IFile] = []

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
        f.relpath = d["relpath"]
        f.mod_ts = int(d["mod_ts"])
        f.checksum = d["checksum"]
        f.size = int(d["size"])
        return f

    def update(self, new_file: 'File') -> None:
        """
        Rewrites all data except for `parent`.
        """
        self.relpath = new_file.relpath
        self.mod_ts = new_file.mod_ts
        self.checksum = new_file.checksum
        self.size = new_file.size

    def path_abs(self) -> str:
        return os.path.join(self.parent.path, self.relpath)

    def calc_checksum(self) -> str:
        self.checksum = sha256(self.path_abs())
        return self.checksum

    def basename(self) -> str:
        """
        Returns an absolute path to the file's parent directory.
        """
        return os.path.basename(self.path_abs())

    def __str__(self) -> str:
        return f'"{self.path_abs()}"'

    def __repr__(self) -> str:
        return f'<File "{self.path_abs()}" at {hex(id(self))}>'


class FilesCollection(IFilesCollection):
    def __init__(self, path: str, auto_read: bool = True, ignore: list[str] = []) -> None:
        super().__init__()
        self.path: str = path
        self.ignore: list[str] = ignore  # not used for now
        if auto_read:
            self.construct_files(self.path)

    def construct_files(self, path: str) -> list[File]:
        """
        Returns list of `File` objects, which are constructed with parent `fc`.
        Recursive.
        """
        for entry in os.scandir(path):
            # if not entry.path in self.ignore:
                if entry.is_file():
                    f = File.from_DirEntry(entry, self)
                    self.files.append(f)
                elif entry.is_dir():
                    self.construct_files(entry.path)

    @staticmethod
    def empty(path: str):
        """
        Returns an empty FilesCollection with no initial auto-read of the directory `path`.
        """
        return FilesCollection(path, False)

    def update(self, files: list[File]) -> None:
        """
        Updates (clears and adds new `File` objects to) `self.files`.
        """
        self.files.clear()
        self.files.extend(files)

    def update_partially(self, updated_files: list[File]) -> None:
        """
        Updates (adds or rewrites) only files from `updated_files`.
        """
        for new_f in updated_files:
            try:
                f = self.get_by_relpath(new_f.relpath)
                f.update(new_f)
                f.parent = self
            except:
                self.files.append(new_f)
                new_f.parent = self

    def has_relpath(self, relpath: str) -> bool:
        """
        Checks whether `self.files` has a `File` object with given `relpath`.
        """
        for f in self.files:
            if f.relpath == relpath:
                return True
        return False

    def get_by_relpath(self, relpath: str) -> File:
        """
        Returns a `File` object with given `relpath`. Throws an Exception if the object was not found.
        """
        f = get_by_relpath(self.files, relpath)
        if f == None:
            raise Exception(f'No file with relative path "{relpath}" in {self}')
        return f

    def find_newer(newer_fc: 'FilesCollection', older_fc: 'FilesCollection') -> list[File]:
        """
        Returns list of `File` objects that are newer in first passed `FilesCollection` relative to second one.

        `File` object is newer if its last modification timestamp `mod_ts` is higher and its content sha256-checksum is different.
        """
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


def get_last_sync(path_files_info: str, path_current_state: str) -> FilesCollection:
    fcs = load_files_info(path_files_info)
    if len(fcs) == 1:
        return fcs[0]
    else:
        print(f'No saved files info, using current state of "{path_current_state}" as last_sync.')
        fc = FilesCollection(path_current_state, True)
        save_last_sync(path_files_info, fc)
        return fc


def save_last_sync(path_files_info: str, fc_last_sync: FilesCollection) -> None:
    save_files_info(path_files_info, [fc_last_sync])
    print("Saved fc_last_sync.")




def get_by_relpath(l: list[File], relpath: str) -> File:
    """
    Returns a `File` object with given `relpath`. Returns `None` if there is no file with such `relpath`.
    """
    for f in l:
        if f.relpath == relpath:
            return f
    return None


def get_intersections(l1: list[File], l2: list[File]) -> list[File]:
    """
    Returns list of `File` objects that are presented in both `l1` and `l2`.
    """
    l: list[File] = []
    for path_rel in map(lambda f: f.relpath, l1):
        f = get_by_relpath(l2, path_rel)
        if f != None:
            l.append(f)
    return l


def copy_file(path_from: str, path_to: str) -> int:
    """
    Copies file from one location to another using `win32`'s command `copy <> <>`.

    Returns the execution's return code.
    """
    d = os.path.dirname(path_to)
    if not os.path.exists(d) and not os.path.isdir(d):
        os.makedirs(d)

    cmd = f'copy "{path_from}" "{path_to}"'

    return_code = os.system(cmd)
    print(return_code, cmd)
    return return_code


def copy_files_array(files: list[File], folder_from: str, folder_to: str) -> list[File]:
    """
    Copies files passed as an array `files` using `copy_file()`.

    Returns list of `File` objects that are actually copied (`copy_file()`'s return code is 0).
    """
    copied_files: list[File] = []
    for f in files:
        rc = copy_file(os.path.join(folder_from, f.relpath), os.path.join(folder_to, f.relpath))
        if rc == 0:
            copied_files.append(f)
    return copied_files


# def commit(files: list[File], dw_from: DirectoryWatcher, dw_to: DirectoryWatcher) -> None:
#     copy_files_array(files, dw_from.path, dw_to.path)
#     dw_to.fc.update_partially(files)



# os.makedirs
