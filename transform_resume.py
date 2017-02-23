#!/usr/bin/env python3

# Copyright (C) 2014  Jim Turner
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import copy
import jinja2
import os
import os.path
import re
import yaml


@jinja2.environmentfilter
def hard_wrap(env, raw, width, indent=0, bullet="", hanging=0):
    """Hard wrap text with optionally an indent, hanging indent, and/or bullet.

    The text is broken at whitespace and any consecutive white spaces are
    shrunk into a single space. This is intended to be used as a Jinja2 filter.

    :param env: Jinja2 Environment (needed to determine newline_sequence)
    :param raw: text to wrap
    :param width: maximum line width (including indent and bullet)
    :param indent: number of characters on a line until the first character of
        text (the optional bullet is placed within this indent)
    :param bullet: bullet character to use or "" for no bullet
    :param hanging: number of additional characters of hanging indent
    :return: formatted text
    :throw ValueError: if the indent is too narrow for the bullet or the width
        is too narrow for the indent and the first word on a line
    """
    words = raw.split()
    lines = []

    # First line has the bullet
    if bullet:
        if len(bullet + " ") > indent:
            raise ValueError("`indent` isn't wide enough for bullet to fit.")
        else:
            lines.append((bullet + " ").rjust(indent))
    else:
        lines.append(" " * indent)

    # Remaining lines have whitespace indent
    for word in words:
        if len(lines[-1] + word) > width:
            if indent + hanging + len(word) > width:
                raise ValueError("`width` isn't wide enough for indent and "
                                 "the word '{}'.".format(word))
            else:
                lines.append(" " * (indent + hanging))
        lines[-1] += word + " "

    return env.newline_sequence.join([line[:-1] for line in lines])


def left_right(left, right, width):
    """Left justify and right justify two strings on a single line.

    :param left: string to left justify
    :param right: string to right justify
    :param width: desired length of the line
    :return: formatted text
    :throw ValueError: if the two strings can't fit within `width`
    """
    combined_len = len(left + right)
    if combined_len > width:
        raise ValueError(
            "'{}' and '{}' combined are longer than {} characters.".format(
                left, right, width))
    return left + " " * (width - combined_len) + right


def merge_data(orig, new):
    """Deeply merge the data from the two dictionaries. If there is a conflict,
    select the value from `new`.

    :param orig: first dictionary
    :param new: second dictionary
    :return: new dictionary (deep copied) with merged data
    """
    if isinstance(orig, dict) and isinstance(new, dict):
        res = copy.deepcopy(orig)
        for k, v in new.items():
            if k in res:
                res[k] = merge_data(orig[k], v)
            else:
                res[k] = v
        return res
    else:
        return new


def escape(data, replacements):
    """Deeply perform regex replacements on the data.

    :param data: data to replace (can be nested dicts, lists, and strings)
    :param replacements: list of (pattern, replacement) pairs
    :return: new data object (deep copied) with replacements
    """
    if isinstance(data, dict):
        res = {}
        for k, v in data.items():
            key = escape(k, replacements)
            value = escape(v, replacements)
            res[key] = value
    elif isinstance(data, list):
        res = []
        for v in data:
            res.append(escape(v, replacements))
    elif isinstance(data, str):
        res = data
        for pattern, repl in replacements:
            res = re.sub(pattern, repl, res)
    else:
        res = copy.deepcopy(data)
    return res


def safe_open_w(path):
    """Open the file at `path` for writing, creating any parent directories as
    necessary.

    :param path: desired path of file
    :return: opened file
    """
    path = os.path.normpath(path)
    dirname = os.path.dirname(path)
    if dirname:
        os.path.makedirs(dirname)
    return open(path, 'w')


def write_output(data, template_path, out_path, jinja2_delim, replacements,
                 line_endings):
    """Apply the data to the template and write the output.

    :param data: data to use in template
    :param template_path: path to template file
    :param out_path: path to output file
    :param jinja2_delim: delimeters used by Jinja2 template
    :param replacements: (pattern, replacement) regex pairs to apply
    :param line_endings: must be '\n', '\r', or '\r\n'
    """
    env = jinja2.Environment(
        *jinja2_delim,
        newline_sequence=line_endings,
        loader=jinja2.FileSystemLoader("."),
        trim_blocks=True,
        lstrip_blocks=True,
        undefined=jinja2.StrictUndefined)
    env.filters['hard_wrap'] = hard_wrap
    env.filters['left_right'] = left_right
    template = env.get_template(template_path)
    with safe_open_w(out_path) as f:
        f.write(template.render(escape(data, replacements)))


def load_data(paths):
    """Load and merge the data from YAML file(s).

    :param paths: paths of YAML files to load
    :return: data from files (merged together)
    """
    res = {}
    for path in paths:
        with open(path) as f:
            res = merge_data(res, yaml.safe_load(f))
    return res


def load_config(path):
    """Load configuration data from YAML file.

    :param path: path to YAML file to load
    :return: configuration data
    """
    with open(path) as f:
        return yaml.safe_load(f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Render resume templates.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('type', type=str,
                        choices=['latex', 'html', 'txt', 'sphinx', 'markdown'],
                        help="Output file type.")
    parser.add_argument('template', type=str,
                        help="Path to Jinja2 template file.")
    parser.add_argument('output', type=str,
                        help="Desired output path.")
    parser.add_argument('data', type=str, nargs='+',
                        help="Paths to YAML files with data.")
    parser.add_argument('--config', type=str, default="config.yml",
                        help="Path to config YAML file.")
    args = parser.parse_args()

    data = load_data(args.data)
    config = load_config(args.config)
    write_output(data, args.template, args.output,
                 config[args.type]['jinja2_delim'],
                 config[args.type]['replacements'],
                 config[args.type]['line_endings'])
