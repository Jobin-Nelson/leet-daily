import itertools
import logging
import shlex
import shutil
import subprocess
import textwrap
from pathlib import Path

import requests
from requests.exceptions import Timeout
from selectolax.parser import HTMLParser

from leet_daily.config import Config, ConfigError

logger = logging.getLogger(__name__)

class Leet:
    def __init__(self):
        self.config = Config()
        self.daily_qn_link = get_daily_qn_link()
        self.leet_file = (
            self.config.leet_dir / Path(self.daily_qn_link).with_suffix(".py").name
        )
        self.armor = lambda x: shlex.split(x)

    def open_in_browser(self):
        logger.debug(f'in {self.__class__.__qualname__} method')
        browser = self.config.browser
        browser_path = shutil.which(browser)
        if browser_path is None:
            raise ConfigError(f'{browser} not found in PATH')
        cmd = self.armor(f'{browser_path} {self.daily_qn_link}')
        logger.info(f'Calling command `{cmd}`')
        subprocess.Popen(cmd, close_fds=True, start_new_session=True)
        # subprocess.Popen([self.daily_qn_link], executable=browser_path)

    def open_in_editor(self):
        # subprocess.run([self.armor(s) for s in (self.config.editor, self.leet_file)])
        logger.debug(f'in {self.__class__.__qualname__} method')
        editor = self.config.editor
        editor_path = shutil.which(editor)
        if editor_path is None:
            raise ConfigError(f'{editor} not found in PATH')
        cmd = self.armor(f'{editor_path} {self.leet_file}')
        logger.info(f'Calling command `{cmd}`')
        subprocess.run(cmd)

    def gen_leet_file(self):
        if self.leet_file.exists():
            return
        self.leet_file.parent.mkdir(parents=True, exist_ok=True)
        question = self.get_daily_question()
        leet_file_content = self.config.template_file.read_text().format(
            today=self.config.today.strftime("%Y-%m-%d"),
            question=question,
            daily_qn_link=self.daily_qn_link,
        )
        self.leet_file.write_text(leet_file_content)

    def get_daily_question(self) -> str:
        try:
            res = requests.get(self.daily_qn_link, timeout=2)
        except Timeout:
            return ""
        html = HTMLParser(res.text)
        content = html.css_first('meta[name="description"]').attributes["content"]
        if content is None:
            return ""

        # getting only the question content
        content_gen = itertools.takewhile(
            lambda x: not x.startswith("Example"), content.splitlines()
        )

        # wrapping the content to 79 characters
        content_gen = (
            textwrap.fill(
                d,
                initial_indent="    ",
                subsequent_indent="    ",
                width=79,
            )
            for d in content_gen
        )
        return "\n".join(content_gen).strip()


def get_daily_qn_link() -> str:
    base_url = "https://leetcode.com/graphql/"
    query = {
        "query": "query questionOfToday {\n\tactiveDailyCodingChallengeQuestion {\n\t\tdate\n\t\tlink\n\t}\n}\n",
        "operationName": "questionOfToday",
    }
    res = requests.post(base_url, json=query)
    relative_url = res.json()["data"]["activeDailyCodingChallengeQuestion"]["link"]
    return base_url.rstrip("/graphql/") + relative_url
