#!/usr/bin/env python3
'''This program sets up everything for the daily leetcode problems'''
from __future__ import annotations
from typing import Sequence
from pathlib import Path
import argparse, json, datetime, webbrowser, subprocess, textwrap, itertools
import httpx
from selectolax.parser import HTMLParser

TODAY = datetime.datetime.now()
LEET_DAILY_DIR = (Path.home()
    / 'playground'
    / 'projects'
    / 'learn'
    / 'competitive_programming'
    / f'{TODAY:%Y}'
    / f'{TODAY:%B}'.lower()
)

def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog='leet',
        description='leet helps with doing leetcode daily',
        epilog='Happy leetcoding'
    )
    parser.add_argument('-b', '--browser', action='store_false', help='do not open browser')
    parser.add_argument('-f', '--file', action='store_false', help='do not create a file')
    parser.add_argument('-n', '--neovim', action='store_false', help='do not open neovim')
    args = parser.parse_args(argv)

    daily_qn_link = get_daily_qn_link()
    leet_file = LEET_DAILY_DIR / Path(daily_qn_link).with_suffix('.py').name

    # if args.browser: webbrowser.open(daily_qn_link)
    leet_file = Path(__file__).resolve().parent / 'test.py'
    if args.file: create_file(leet_file, daily_qn_link)
    if args.neovim: subprocess.run(['nvim', str(leet_file)])

    return 0


def get_daily_qn_link() -> str:
    base_url = 'https://leetcode.com/graphql/'
    query = {
      "query": "query questionOfToday {\n\tactiveDailyCodingChallengeQuestion {\n\t\tdate\n\t\tlink\n\t}\n}\n",
      "operationName": "questionOfToday"
    }
    res = httpx.post(base_url, json=query)
    relative_url = (res
        .raise_for_status()
        .json()['data']['activeDailyCodingChallengeQuestion']['link'])
    return base_url.rstrip('/graphql/') + relative_url


def create_file(leet_file: Path, daily_qn_link: str) -> None:
    if leet_file.exists(): return
    leet_file.parent.mkdir(parents=True, exist_ok=True)
    question = get_question(daily_qn_link)
    with open(leet_file, 'w') as f:
        f.write(f"""\
'''
Created Date: {TODAY:%Y-%m-%d}
Qn: {question}
Link: {daily_qn_link}
Notes:
'''
def main():
    pass

if __name__ == '__main__':
""")


def get_question(daily_qn_link: str) -> str:
    res = httpx.get(daily_qn_link)
    html = HTMLParser(res.text)
    content = html.css_first('meta[name="description"]').attrs['content']

    # getting only the question content
    content_gen = itertools.takewhile(
        lambda x: not x.startswith('Example'),
        content.splitlines()
    )

    # wrapping the content to 79 characters
    content_gen = (
        textwrap.fill(d,
                      initial_indent='    ',
                      subsequent_indent='    ',
                      width = 79,
                      )
        for d in content_gen
    )
    return '\n'.join(content_gen).strip()


if __name__ == '__main__':
    raise SystemExit(main())

