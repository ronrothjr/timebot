import os, abc, shutil, datetime

class FilesInterface(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return(hasattr(subclass, 'path_exists') and callable(subclass.path_exists) and
               hasattr(subclass, 'create_path') and callable(subclass.create_path) and
               hasattr(subclass, 'remove_path') and callable(subclass.remove_path) and
               hasattr(subclass, 'write_file') and callable(subclass.write_file) and
               hasattr(subclass, 'remove_file') and callable(subclass.remove_file) and
               hasattr(subclass, 'read_file') and callable(subclass.read_file) or
               NotImplemented)

    def __init__(self):
        pass

    @abc.abstractmethod
    def path_exists(self, path: str) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def create_path(self, path: str) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def remove_path(self, path: str) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def write_file(self, file_name: str, file_data: str) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def remove_file(self, file_name: str) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def read_file(self, collection: str) -> str:
        raise NotImplementedError


class Files(FilesInterface):
    def __init__(self, local_path: str=None):
        # Used this to solve the "Finding Path" bug so I can use this on pc, mac, and linux
        # https://stackoverflow.com/questions/5137497/find-the-current-directory-and-files-directory
        self.local_path = local_path if local_path else os.path.dirname(os.path.realpath(__file__))
        self.path_separator = '\\' if '\\' in self.local_path else '/'

    def get_timestamp(self):
        return datetime.datetime.now().strftime('%Y%m%d%H%M%S.%f')

    def get_path(self, *args) -> str:
        path = self.path_separator.join(args)
        return path

    def path_exists(self, path: str) -> bool:
        return os.path.exists(f'{self.local_path}{self.path_separator}{path}')

    def create_path(self, *args) -> bool:
        path = self.get_path(*args)
        if not self.path_exists(path):
            os.makedirs(f'{self.local_path}{self.path_separator}{path}')
            return True
        return False

    def remove_path(self, path: str) -> bool:
        if self.path_exists(path):
            os.removedirs(f'{self.local_path}{self.path_separator}{path}')
            return True
        return False

    def get_paths(self, path: str) -> list:
        return [x[0] for x in os.walk(path) if path != x[0]]

    def get_files(self, path: str) -> list:
        fetched = [f for f in os.listdir(path)]
        return fetched

    def get_local_path(self, file_name: str):
        dirs = file_name.split(self.path_separator)
        if len(dirs) > 1:
            if '.' in dirs[len(dirs)-1]:
                return self.path_separator.join(dirs[:-1])
            else:
                return self.path_separator.join(dirs)
        None

    def write_file(self, file_name: str, file_data: str) -> int:
        local_path = self.get_local_path(f'{file_name}.txt')
        if local_path and not self.path_exists(local_path):
            self.create_path(local_path)
        file = open(f'{self.local_path}{self.path_separator}{file_name}.txt', 'w+')
        file_size = file.write(file_data)
        file.close()
        return file_size

    def remove_file(self, file_name: str) -> bool:
        if self.path_exists(f'{file_name}.txt'):
            os.remove(f'{self.local_path}{self.path_separator}{file_name}.txt')
            return True
        return False

    def read_file(self, collection: str) -> str:
        if not self.path_exists(f'{collection}.txt'):
            return None
        records = open(f'{self.local_path}{self.path_separator}{collection}.txt', 'r')
        file_str = records.read()
        records.close()
        return file_str

    def copy_file(self, from_path: str, to_path: str) -> bool:
        shutil.copyfile(from_path, to_path)
