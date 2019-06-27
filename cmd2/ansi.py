# coding=utf-8
"""Support for ANSI escape sequences which are used for things like applying style to text"""
import functools
import re
from typing import Any, IO

import colorama
from colorama import Fore, Back, Style
from wcwidth import wcswidth

# Values for allow_ansi setting
ANSI_NEVER = 'Never'
ANSI_TERMINAL = 'Terminal'
ANSI_ALWAYS = 'Always'

# Controls when ANSI escape sequences are allowed in output
allow_ansi = ANSI_TERMINAL

# Regular expression to match ANSI escape sequences
ANSI_ESCAPE_RE = re.compile(r'\x1b[^m]*m')

# Foreground color presets
FG_COLORS = {
    'black': Fore.BLACK,
    'red': Fore.RED,
    'green': Fore.GREEN,
    'yellow': Fore.YELLOW,
    'blue': Fore.BLUE,
    'magenta': Fore.MAGENTA,
    'cyan': Fore.CYAN,
    'white': Fore.WHITE,
    'gray': Fore.LIGHTBLACK_EX,
    'lightred': Fore.LIGHTRED_EX,
    'lightblue': Fore.LIGHTBLUE_EX,
    'lightgreen': Fore.LIGHTGREEN_EX,
    'lightyellow': Fore.LIGHTYELLOW_EX,
    'lightmagenta': Fore.LIGHTMAGENTA_EX,
    'lightcyan': Fore.LIGHTCYAN_EX,
    'lightwhite': Fore.LIGHTWHITE_EX,
    'reset': Fore.RESET,
}

# Background color presets
BG_COLORS = {
    'black': Back.BLACK,
    'red': Back.RED,
    'green': Back.GREEN,
    'yellow': Back.YELLOW,
    'blue': Back.BLUE,
    'magenta': Back.MAGENTA,
    'cyan': Back.CYAN,
    'white': Back.WHITE,
    'gray': Back.LIGHTBLACK_EX,
    'lightred': Back.LIGHTRED_EX,
    'lightblue': Back.LIGHTBLUE_EX,
    'lightgreen': Back.LIGHTGREEN_EX,
    'lightyellow': Back.LIGHTYELLOW_EX,
    'lightmagenta': Back.LIGHTMAGENTA_EX,
    'lightcyan': Back.LIGHTCYAN_EX,
    'lightwhite': Back.LIGHTWHITE_EX,
    'reset': Back.RESET,
}

# ANSI escape sequences not provided by colorama
UNDERLINE_ENABLE = colorama.ansi.code_to_chars(4)
UNDERLINE_DISABLE = colorama.ansi.code_to_chars(24)


def strip_ansi(text: str) -> str:
    """
    Strip ANSI escape sequences from a string.

    :param text: string which may contain ANSI escape sequences
    :return: the same string with any ANSI escape sequences removed
    """
    return ANSI_ESCAPE_RE.sub('', text)


def ansi_safe_wcswidth(text: str) -> int:
    """
    Wrap wcswidth to make it compatible with strings that contains ANSI escape sequences

    :param text: the string being measured
    """
    # Strip ANSI escape sequences since they cause wcswidth to return -1
    return wcswidth(strip_ansi(text))


def ansi_aware_write(fileobj: IO, msg: str) -> None:
    """
    Write a string to a fileobject and strip its ANSI escape sequences if required by allow_ansi setting

    :param fileobj: the file object being written to
    :param msg: the string being written
    """
    if allow_ansi.lower() == ANSI_NEVER.lower() or \
            (allow_ansi.lower() == ANSI_TERMINAL.lower() and not fileobj.isatty()):
        msg = strip_ansi(msg)
    fileobj.write(msg)


def style(text: Any, *, fg: str = '', bg: str = '', bold: bool = False, underline: bool = False) -> str:
    """
    Applies styles to text

    :param text: Any object compatible with str.format()
    :param fg: foreground color. Expects color names in FG_COLORS (e.g. 'lightred'). Defaults to no color.
    :param bg: background color. Expects color names in BG_COLORS (e.g. 'black'). Defaults to no color.
    :param bold: apply the bold style if True. Defaults to False.
    :param underline: apply the underline style if True. Defaults to False.

    :return: the stylized string
    """
    # List of strings that add style
    additions = []

    # List of strings that remove style
    removals = []

    # Convert the text object into a string if it isn't already one
    text = "{}".format(text)

    # Process the style settings
    if fg:
        try:
            additions.append(FG_COLORS[fg.lower()])
            removals.append(FG_COLORS['reset'])
        except KeyError:
            raise ValueError('Color {} does not exist.'.format(fg))

    if bg:
        try:
            additions.append(BG_COLORS[bg.lower()])
            removals.append(BG_COLORS['reset'])
        except KeyError:
            raise ValueError('Color {} does not exist.'.format(bg))

    if bold:
        additions.append(Style.BRIGHT)
        removals.append(Style.NORMAL)

    if underline:
        additions.append(UNDERLINE_ENABLE)
        removals.append(UNDERLINE_DISABLE)

    # Combine the ANSI escape sequences with the text
    return "".join(additions) + text + "".join(removals)


# Default styles for printing strings of various types.
# These can be altered to suit an application's needs and only need to be a
# function with the following structure: func(str) -> str
style_success = functools.partial(style, fg='green', bold=True)
style_warning = functools.partial(style, fg='lightyellow')
style_error = functools.partial(style, fg='lightred')
