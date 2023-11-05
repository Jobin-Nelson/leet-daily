from __future__ import annotations

import sys
import tomllib  # noqa I201
from datetime import datetime
from pathlib import Path  # noqa I100
from typing import Any

# config file is expected at ~/.config/leet/config.toml

class Config:
    def __init__(self):
        self.today = datetime.now()
        self._config = get_config()['leet']
        self.get_path = lambda x: Path(x).expanduser().resolve()
        self.editor = self._config['editor']
        self.browser = self._config['browser']

    @property
    def leet_dir(self) -> Path:
        leet_dir = self._config['leet_dir']
        return self.get_path(leet_dir) / f'{self.today:%Y}' / f'{self.today:%B}'

    @property
    def template_file(self) -> Path:
        template_file = self._config['template']
        return self.get_path(template_file)

def get_config() -> dict[str, Any]:
    config_file = Path.home() / '.config' / 'leet' / 'config.toml'

    if not config_file.exists():
        print(f'Config file not found at {config_file}', file=sys.stderr)
        print(f'Creating {config_file} with default values', file=sys.stderr)
        set_config(config_file)
        sys.exit(1)
    return read_config(config_file)


def set_config(config_file: Path):
    config_data = """\
[leet]
leet_dir = "~/playground/projects/learn/competitive_programming"
browser = "firefox"
editor = "nvim"
template = "~/.config/leet/leet.temp"
"""
    template_data = """\
'''
Created Date: {today}
Qn: {question}
Link: {daily_qn_link}
Notes:
'''
def main():
    pass

if __name__ == '__main__':
"""
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text(config_data)

    config = tomllib.loads(config_data)
    template_file = Path(config['leet']['template']).expanduser().resolve()
    template_file.parent.mkdir(parents=True, exist_ok=True)
    template_file.write_text(template_data)


def read_config(config_file: Path) -> dict[str, Any]:
    with open(config_file, 'rb') as f:
        config = tomllib.load(f)
        if 'leet' not in config:
            print(f'No leet section found in {config_file}', file=sys.stderr)
            sys.exit(1)
        return config
