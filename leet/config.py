from __future__ import annotations
import sys
from pathlib import Path
from configparser import ConfigParser

# config file is expected at ~/.config/leet/config.toml

def get_config() -> ConfigParser:
    config_file = (Path.home()
        / '.config'
        / 'leet'
        / 'config.toml'
    )

    if not config_file.exists():
        print(f'Config file not found at {config_file}', file=sys.stderr)
        print(f'Creating {config_file} with default values', file=sys.stderr)
        set_config(config_file)
        sys.exit(1)
    return read_config(config_file)


def set_config(config_file: Path):
    config_data = """\
[leet]
leet_dir = "~/playground/projects/leet"
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
    config = ConfigParser()
    config.read_string(config_data)
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text(config_data)

    template_file = Path(config['leet']['template']).expanduser().resolve()
    template_file.parent.mkdir(parents=True, exist_ok=True)
    template_file.write_text(template_data)


def read_config(config_file: Path) -> ConfigParser:
    config = ConfigParser()
    config.read(config_file)
    if not config.has_section('leet'):
        print(f'No leet section found in {config_file}', file=sys.stderr)
        sys.exit(1)
    return config
