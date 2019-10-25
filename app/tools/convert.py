#! /usr/bin/env python
from pathlib import Path

_entrypoint_ = 'FileTools'
class FileTools:
    root_path = '.'

    def __init__(self, root_path=None, hard_fail=True):
        self.root_path = Path(root_path) if root_path else Path(self.root_path)

        if not self.root_path.is_dir():
            message = f'FileTools: Missing root path: {self.root_path} !'
            self._exit(message) if hard_fail else None

    @staticmethod
    def ask(question):
        good_responses = ['y', 'Y']
        ask = input(f'{question} [y/n] ')
        return True if ask in good_responses else False

    def load_file(self, file_path, with_root=True):
        """Calls either json.load or raumel.yaml.load depending on file extension."""
        file = self.root_path / file_path if with_root else Path(file_path)
        if not file.is_file():
            self._exit(f'{file_path} is NOT a file or doesn\'t exist')

        file_parser = self._load_func(file.suffix)
        with file.open('r') as the_file:
            f = file_parser(the_file)
            print(f'READ: {file_path}')
            return f

    def dump_file(self, data, file_path, with_root=True, overwrite=False):
        """Calls either json.load or raumel.yaml.load depending on file extension."""
        path = self.root_path / file_path if with_root else Path(file_path)
        if path.is_file():
            if not overwrite:
                if self.ask(f'file "{path}" exists, overwrite?'):
                    path.touch()
                else:
                    self._exit('file creation aborted, cannot dump')
        else:
            print(f'{file_path} is NOT a file')
            if self.ask(f'create "{path}"?'):
                path.touch()
            else:
                self._exit('file creation aborted, cannot dump')

        with path.open('w') as file:
            dump = self._dump_func(path.suffix)
            print(f'WRITE: {file_path}')
            dump(data, file)

    def _dump_func(self, suffix):
        if suffix == '.json':
            import json
            return json.dump
        elif suffix == '.yml':
            from ruamel.yaml import YAML
            yml = YAML()
            return yml.dump
        else:
            self._exit('could not find matching suffix, exiting!')

    def _load_func(self, suffix):
        if suffix == '.json':
            import json
            return json.load
        elif suffix == '.yml':
            from ruamel.yaml import YAML
            yml = YAML()
            return yml.load
        else:
            self._exit('could not find matching suffix, exiting!')

    def _exit(self, reason):
        print(reason)
        exit(1)
