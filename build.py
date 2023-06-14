#!/usr/bin/env python3

import os
import re
import json
import inspect
import argparse
import subprocess
import collections

from typing import Dict, List
from datetime import datetime
from pybtex.database import parse_file, Person

Config = collections.namedtuple(
    "Config", ["verbosity", "prefix", "target", "templates"]
)


def cleanup():
    for f in [
        f"{config.target}/index.html",
        f"{config.target}/news.html",
        f"{config.target}/pubs.html",
        f"{config.target}/main.css",
    ]:
        try:
            os.remove(f)
        except Exception as _:
            pass


# for printing with colours
class bcolors:
    SUCCESS = "\033[92m"
    OKCYAN = "\033[96m"
    OKBLUE = "\033[94m"
    WARNING = "\033[93m"
    ERROR = "\033[91m"
    BOLD = "\033[1m"
    ENDC = "\033[0m"


# Helper functions
def status(msg: str, priority=1):
    if priority <= config.verbosity:
        if priority == 0:
            divider = "*" * len(msg)
            msg = f"{divider}\n{msg}\n{divider}"
            print(f"{bcolors.BOLD}{bcolors.OKBLUE}{msg}{bcolors.ENDC*2}")
        elif priority == 1:
            print(f"{bcolors.BOLD}{bcolors.OKCYAN}{msg}{bcolors.ENDC*2}")
        else:
            print(f"{bcolors.OKCYAN}{msg}{bcolors.ENDC}")


def success(msg: str):
    msg = f"SUCCESS: {msg}"
    divider = "*" * len(msg)
    msg = f"{divider}\n{msg}\n{divider}"

    print(f"{bcolors.SUCCESS}{msg}{bcolors.ENDC}")


def warning(msg: str):
    msg = f"WARNING: {msg}"
    divider = "*" * len(msg)
    msg = f"{divider}\n{msg}\n{divider}"

    print(f"{bcolors.WARNING}{msg}{bcolors.ENDC}")


def error(msg: str):
    msg = f"ERROR: {msg}"
    divider = "*" * len(msg)
    msg = f"{divider}\n{msg}\n{divider}"

    print(f"{bcolors.ERROR}{msg}{bcolors.ENDC}")
    cleanup()
    exit(1)


def warn_if_not(cond: bool, msg: str):
    if not cond:
        warning(msg)


def fail_if_not(cond: bool, msg: str):
    if not cond:
        error(msg)


def fill_if_missing(json: Dict[str, str], field: str, default=""):
    if not field in json:
        json[field] = default

    return json


def is_federicos(name):
    try:
        repo_url = subprocess.getoutput(
            f"git -C {config.prefix} config --get remote.origin.url"
        ).split()[0]
    except Exception as _:
        repo_url = ""

    federicos_url = "git@github.com:FedericoAureliano/FedericoAureliano.github.io.git"
    federicos_name = "Federico Mora Rocha"

    return name == federicos_name and repo_url == federicos_url


def check_tracker(tracker):
    status("- Sanity check on tracker script")

    fail_if_not(
        "federicoaureliano" not in tracker,
        "Please use your own tracker in data/meta.json",
    )


def check_cname():
    status("- Sanity check on CNAME")

    path = os.path.join(config.target, "CNAME")
    try:
        with open(path) as f:
            cname = f.read()
    except Exception as _:
        status(f"  - Couldn't load CNAME---treating it as empty.", 1)
        cname = ""

    fail_if_not(
        "federico.morarocha.ca" != cname, f"Please use your own CNAME at {path}"
    )


def read_data(json_file_name: str, optional: bool):
    path = os.path.join(config.prefix, json_file_name)
    try:
        with open(path) as f:
            status(f"- loading {path}")
            data = json.load(f)
    except Exception as _:
        fail_if_not(
            optional,
            f"Failed to parse {path}. Check your commas, braces, and if the file exists.",
        )
        # fail_if_not will exit if needed so the code below will only run if this data is optional
        status(f"Failed to load {path}---treating it as empty.", 0)
        data = {}

    return data


def read_template(template_file_name: str, optional: bool):
    path = os.path.join(config.prefix, template_file_name)
    try:
        with open(path) as f:
            status(f"- loading {path}")
            data = f.read()
    except Exception as _:
        fail_if_not(optional, f"Failed to read {path}. Does it exist?")
        # fail_if_not will exit if needed
        status(f"Couldn't load {path}---treating it as empty.", 0)
        data = ""

    return data


def write_file(file_name: str, contents: str):
    path = os.path.join(config.prefix, file_name)
    if contents == "":
        return

    with open(path, "w") as target:
        status(f"- writing {path}")
        target.write(contents)


def replace_placeholders(text: str, map: Dict[str, str]):
    newtext = text

    for k in map:
        newtext = newtext.replace(k + "-placeholder", map[k])

    return newtext


# Define functions for website pieces


def header(has_dark):
    if has_dark:
        button = """<label class="switch-mode">
    <input type="checkbox" id="mode">
    <span class="slider round"></span>
</label>
<script src="mode.js"></script>
"""
    else:
        button = ""

    out = '<header><div id="scroller"></div>\n%s</header>\n' % button
    return out


def build_news(news: List[Dict[str, str]], count: int, standalone: bool):
    if count > len(news):
        count = len(news)

    if count <= 0:
        return ""

    status("\nAdding news:")
    news_list = ""

    for n in news[:count]:
        status("- " + n["date"])
        news_map = {
            "news-date": n["date"],
            "news-text": n["text"],
        }
        news_list += replace_placeholders(news_item_html, news_map)

    news_html = '<div class="section">\n'

    if count != len(news):
        link = '<a href="./news.html">See all posts</a>'
        news_html += (
            '<h1>Recent News <small style="font-weight: 300; float: right; padding-top: 0.23em">(%s)</small></h1>\n'
            % link
        )
    elif standalone:
        link = '<a href="./index.html">%s</a>' % meta_json["name"]
        news_html += (
            '<h1>News <small style="font-weight: 300; float: right; padding-top: 0.23em">%s</small></h1>\n'
            % link
        )
    else:
        news_html += "<h1>News</h1>\n"

    news_html += '<div class="hbar"></div>\n'
    news_html += '<div id="news">\n'
    news_html += news_list
    news_html += "</div>\n"  # close news
    news_html += "</div>\n"  # close section

    return news_html


# Helper function to decide what publication sections to include
def get_pub_titles(pubs, full: bool):
    titles = set()
    for p in pubs.entries.values():
        if p.fields["build_selected"] == "true" or full:
            titles.add(p.fields["build_keywords"])

    return sorted(list(titles))


def some_not_selected(pubs):
    for p in pubs.entries.values():
        if not p.fields["build_selected"] == "true":
            return True

    return False


def build_authors(authors):
    item = ""

    authors_split = []
    for a in authors:
        entry = "%s%s%s" % (
            " ".join(a.first_names)[0] + ". ",
            " ".join(a.middle_names)[0] + ". " if len(a.middle_names) > 0 else "",
            " ".join(a.last_names),
        )

        name = " ".join(a.first_names)
        name += "" if len(a.middle_names) == 0 else " " + " ".join(a.middle_names)
        name += " " + " ".join(a.last_names)
        if name in auto_links_json:
            entry = '<a href="%s">%s</a>' % (auto_links_json[name], entry)

        authors_split.append(entry)

    for i in range(len(authors_split)):
        entry = authors_split[i]
        if i < len(authors_split) - 2:
            entry += ",\n"
        if i == len(authors_split) - 2:
            entry += " and\n"
        authors_split[i] = entry

    authors_text = "".join(authors_split).replace('<a href="', "").replace('">', "").replace('</a>', '')
    authors_text = re.sub(r'http\S+', '', authors_text)
    if len(authors_text) > 75:
        authors_split.insert(len(authors_split) // 2, '<br class="bigscreen">')
    item += "".join(authors_split)
    return item


def build_icons(p):
    item = ""
    item += (
        '<a href="'
        + p.fields["build_link"]
        + '" alt="[PDF] "><img class="paper-icon" src="%s"/><img class="paper-icon-dark" src="%s"/></a>'
        % (style_json["paper-img"], style_json["paper-img-dark"])
        if p.fields["build_link"]
        else ""
    )
    item += (
        '<a href="'
        + p.fields["build_extra"]
        + '" alt="[Extra] "><img class="paper-icon" src="%s"/><img class="paper-icon-dark" src="%s"/></a>'
        % (style_json["extra-img"], style_json["extra-img-dark"])
        if p.fields["build_extra"]
        else ""
    )
    item += (
        '<a href="'
        + p.fields["build_slides"]
        + '" alt="[Slides] "><img class="paper-icon" src="%s"/><img class="paper-icon-dark" src="%s"/></a>'
        % (style_json["slides-img"], style_json["slides-img-dark"])
        if p.fields["build_slides"]
        else ""
    )
    item += (
        '<a href="'
        + p.fields["build_bibtex"]
        + '" alt="[Bibtex] "><img class="paper-icon" src="%s"/><img class="paper-icon-dark" src="%s"/></a>'
        % (style_json["bibtex-img"], style_json["bibtex-img-dark"])
        if p.fields["build_bibtex"]
        else ""
    )
    return item


def build_pubs_inner(pubs, title: str, full: bool):
    if title == "":
        return ""

    pubs_list = ""

    for p in pubs.entries.values():
        if title == p.fields["build_keywords"] and (p.fields["build_selected"] == "true" or full):
            status("- " + p.fields["title"])

            paper_conference = p.fields["build_short"] + " '" + p.fields["year"][-2:]
            if len(paper_conference) > 8:
                paper_conference = f'<div class="bigscreen"><small>{paper_conference}</small></div><div class="smallscreen">{paper_conference}</div>'

            title_split = p.fields["title"].split()
            if len(p.fields["title"]) > 75:
                title_split.insert(len(title_split) // 2, '<br class="bigscreen">')
            paper_title = " ".join(title_split)

            paper_map = {
                "paper-title": paper_title,
                "paper-authors": build_authors(p.persons['author']),
                "paper-conference": paper_conference,
                "paper-icons": build_icons(p),
            }
            pubs_list += replace_placeholders(paper_html, paper_map)

    pubs_html = '<h3 id="%spublications">%s</h3>' % (title, title)
    pubs_html += pubs_list

    return pubs_html


def build_pubs(pubs, full: bool):
    if len(pubs.entries) == 0:
        return ""

    status("\nAdding publications:")

    pubs_html = '<div class="section">\n'

    if some_not_selected(pubs) and not full:
        pubs_html += '<h1>Selected Publications <small style="font-weight: 300; float: right; padding-top: 0.23em">(<a href="./pubs.html">See all publications</a>)</small></h1>'
    elif full:
        link = '<a href="./index.html">%s</a>' % meta_json["name"]
        pubs_html += (
            '<h1>Publications <small style="font-weight: 300; float: right; padding-top: 0.23em">%s</small></h1>\n'
            % link
        )
    else:
        pubs_html += "<h1>Publications</h1>"

    pubs_html += '<div class="hbar"></div>\n'
    pubs_html += '<div id="publications">\n'

    titles = get_pub_titles(pubs, full)

    for i in range(len(titles)):
        title = titles[i]
        pubs_html += build_pubs_inner(pubs, title, full)

    pubs_html += "</div>\n"  # close pubs
    pubs_html += "</div>\n"  # close section

    return pubs_html


def build_profile(profile: Dict[str, str]):
    profile_html = '<div class="profile">\n'
    profile_html += (
        '<img class="headshot" src="%s" alt="Headshot"/>\n' % profile["headshot"]
    )
    profile_html += "<p>" + "</p><p>".join(profile["about"].split("\n")) + "</p>"
    if "research" in profile:
        profile_html += "<p>" + "</p><p>".join(profile["research"].split("\n")) + "</p>"
    profile_html += "\n<p>Here is my "
    profile_html += '<a href="%s">CV</a> and ' % profile["cv"]
    profile_html += '<a href="%s">Google Scholar</a>. ' % profile["scholar"]
    profile_html += "You can reach me at %s." % profile["email"]
    profile_html += "</p>\n"  # close description paragraph
    profile_html += "</div>\n"  # close profile

    return profile_html


def add_notes(html: str, notes: Dict[str, str]):
    status("\nAdding notes:", 2)

    toreplace = sorted(notes.keys(), key=len, reverse=True)

    for name in toreplace:
        pos = html.find(name)
        while pos != -1:
            prefix = html[:pos]
            suffix = html[pos:]

            open = html[:pos].count("<abbr title=")
            close = html[:pos].count("</abbr>")

            status(f"- {name} {pos} {open} {close}", 2)
            target = name + " "
            if pos >= 0 and open == close:
                target = '<abbr title="%s">%s</abbr>' % (notes[name], name)
                suffix = suffix.replace(name, target, 1)
                html = prefix + suffix

            start = (len(prefix) - len(name)) + len(
                target
            )  # we got rid of name and replaced it with target
            tmp = html[start:].find(name)
            pos = tmp + start if tmp >= 0 else tmp

    return html


def add_links(html: str, links: Dict[str, str]):
    status("\nAdding links:", 2)

    toreplace = sorted(links.keys(), key=len, reverse=True)

    for name in toreplace:
        pos = html.find(name)
        while pos != -1:
            prefix = html[:pos]
            suffix = html[pos:]

            open = html[:pos].count("<a href=")
            close = html[:pos].count("</a>")

            status(f"- {name} {pos} {open} {close}", 2)
            target = name + " "
            if pos >= 0 and open == close:
                target = '<a href="%s">%s</a>' % (links[name], name)
                suffix = suffix.replace(name, target, 1)
                html = prefix + suffix

            start = (len(prefix) - len(name)) + len(
                target
            )  # we got rid of name and replaced it with target
            tmp = html[start:].find(name)
            pos = tmp + start if tmp >= 0 else tmp

    return html


def build_index(
    profile_json: Dict[str, str],
    news_json: List[Dict[str, str]],
    pubs_bibtex,
    links: Dict[str, str],
    notes: Dict[str, str],
    has_dark: bool,
):
    body_html = "<body>\n"
    body_html += header(has_dark)
    body_html += '<div class="content">\n'
    body_html += build_profile(profile_json)
    body_html += build_news(news_json, 5, False)
    body_html += build_pubs(pubs_bibtex, False)
    body_html += "</div>\n"
    body_html += footer_html
    body_html += "</body>\n"

    index_page = "<!DOCTYPE html>\n"
    index_page += '<html lang="en">\n'
    index_page += head_html + "\n\n"
    index_page += add_notes(add_links(body_html, links), notes)
    index_page += "</html>\n"

    return inspect.cleandoc(index_page)


def build_news_page(
    news_json: List[Dict[str, str]],
    links: Dict[str, str],
    notes: Dict[str, str],
    has_dark: bool,
):
    content = build_news(news_json, len(news_json), True)

    if content == "":
        return ""

    body_html = "<body>\n"
    body_html += header(has_dark)
    body_html += '<div class="content">\n'
    body_html += content
    body_html += "</div>\n"
    body_html += footer_html
    body_html += "</body>\n"

    news_html = "<!DOCTYPE html>\n"
    news_html += '<html lang="en">\n'
    news_html += head_html + "\n\n"
    news_html += add_notes(add_links(body_html, links), notes)
    news_html += "</html>\n"

    return inspect.cleandoc(news_html)


def build_pubs_page(
    pubs_bibtex,
    links: Dict[str, str],
    notes: Dict[str, str],
    has_dark: bool,
):
    content = build_pubs(pubs_bibtex, True)

    if content == "":
        return ""

    body_html = "<body>\n"
    body_html += header(has_dark)
    body_html += '<div class="content">\n'
    body_html += content
    body_html += "</div>\n"
    body_html += footer_html
    body_html += "</body>\n"

    pubs_html = "<!DOCTYPE html>\n"
    pubs_html += '<html lang="en">\n'
    pubs_html += head_html + "\n\n"
    pubs_html += add_notes(add_links(body_html, links), notes)
    pubs_html += "</html>\n"

    return inspect.cleandoc(pubs_html)


def build_cv(
    meta_json: Dict[str, str],
    profile_json: Dict[str, str],
    education_json: Dict[str, str],
    pubs_bibtex,
):
    cv_tex = r"\documentclass{federico_cv}" + "\n"
    cv_tex += r"\frenchspacing" + "\n"
    cv_tex += r"\usepackage[backend=biber,style=numeric,refsection=section,maxbibnames=99,sorting=none,defernumbers=true]{biblatex}" + "\n"
    cv_tex += r"\bibliography{cv}" + "\n"
    cv_tex += r"\begin{document}" + "\n\n\n"

    cv_tex += f"\contact{{{meta_json['name']}}}\n"
    cv_tex += f"{{\MYhref{{{profile_json['website']}}}{{{profile_json['website']}}}}}\n"
    cv_tex += f"{{\MYhref{{mailto:{profile_json['email']}}}{{{profile_json['email']}}}}}\n\n\n"

    cv_tex += "\section{Research Interests}\n"
    cv_tex += f"{profile_json['research']}\n\n\n"

    cv_tex += r"\begin{tblSection}{Education}{0.1}{0.85}" + "\n"
    for edu in education_json:
        cv_tex += "\degree\n"
        cv_tex += f"{{{edu['year']}}}\n"
        cv_tex += f"{{{edu['degree']}}}\n"
        cv_tex += f"{{{edu['note']}}}\n"
        cv_tex += f"{{{edu['institution']}}}\n\n"
    cv_tex += r"\end{tblSection}" + "\n\n\n"

    cv_tex += r"\nocite{*}" + "\n"
    sections = []
    for pub in pubs_bibtex.entries.values():
        sections.append(pub.fields["build_keywords"])
    sections = sorted(list(set(sections)))
    for section in sections:
        cv_tex += f"\printbibliography[keyword={{{section}}},title={{{section}}},resetnumbers=true]\n"
    cv_tex += "\n\n\n"

    cv_tex += r"\end{document}"
    return cv_tex

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                prog="./build.py",
                description="Federico's Academic Website Generator: Builds a website from json files.",
                epilog="For more information, see README.md.")

    parser.add_argument('-v', '--verbosity', type=int, default=0, help=f"set the output verbosity (default: 0)")
    parser.add_argument('-o', '--output', type=str, default="docs", help=f"set the output directory (default: \"docs\")")
    parser.add_argument('-t', '--templates', type=str, default="templates", help=f"set the templates directory (default: \"templates\")")
    parser.add_argument('-c', "--curriculum-vitae", action="store_true", help="generate a curriculum vitae in LaTeX too")
    
    args = parser.parse_args()

    config = Config(
        verbosity=args.verbosity,
        prefix=os.path.dirname(__file__),
        target=args.output,
        templates=args.templates,
    )

    cleanup()

    # Load json files
    status("Loading json files:")

    meta_json = read_data("data/meta.json", optional=False)
    fail_if_not("name" in meta_json, 'Must include a "name" in data/meta.json!')
    fail_if_not(
        "description" in meta_json, 'Must include a "description" in data/meta.json!'
    )
    fail_if_not("favicon" in meta_json, 'Must include a "favicon" in data/meta.json!')
    fill_if_missing(meta_json, "tracker")

    style_json = read_data("data/style.json", optional=False)
    fail_if_not(
        "font-color" in style_json, 'Must include a "font-color" in data/style.json!'
    )
    fail_if_not(
        "background-color" in style_json,
        'Must include a "background-color" in data/style.json!',
    )
    fail_if_not(
        "header-color" in style_json,
        'Must include a "header-color" in data/style.json!',
    )
    fail_if_not(
        "accent-color" in style_json,
        'Must include a "accent-color" in data/style.json!',
    )
    fail_if_not(
        "link-hover-color" in style_json,
        'Must include a "link-hover-color" in data/style.json!',
    )
    fail_if_not(
        "divider-color" in style_json,
        'Must include a "divider-color" in data/style.json!',
    )
    fail_if_not(
        "paper-img" in style_json, 'Must include a "paper-img" in data/style.json!'
    )
    fail_if_not(
        "extra-img" in style_json, 'Must include a "extra-img" in data/style.json!'
    )
    fail_if_not(
        "slides-img" in style_json, 'Must include a "slides-img" in data/style.json!'
    )
    fail_if_not(
        "bibtex-img" in style_json, 'Must include a "bibtex-img" in data/style.json!'
    )

    fill_if_missing(style_json, "font-color-dark", style_json["font-color"])
    fill_if_missing(style_json, "background-color-dark", style_json["background-color"])
    fill_if_missing(style_json, "header-color-dark", style_json["header-color"])
    fill_if_missing(style_json, "accent-color-dark", style_json["accent-color"])
    fill_if_missing(style_json, "link-hover-color-dark", style_json["link-hover-color"])
    fill_if_missing(style_json, "divider-color-dark", style_json["divider-color"])
    fill_if_missing(style_json, "paper-img-dark", style_json["paper-img"])
    fill_if_missing(style_json, "extra-img-dark", style_json["extra-img"])
    fill_if_missing(style_json, "slides-img-dark", style_json["slides-img"])
    fill_if_missing(style_json, "bibtex-img-dark", style_json["bibtex-img"])

    profile_json = read_data("data/profile.json", optional=False)
    fail_if_not(
        "headshot" in profile_json,
        'Must include a "headshot" field in data/profile.json!',
    )
    fail_if_not(
        "about" in profile_json,
        'Must include a "about" field in data/profile.json!',
    )
    fail_if_not("cv" in profile_json, 'Must include a "cv" field in data/profile.json!')
    fail_if_not(
        "email" in profile_json, 'Must include a "email" field in data/profile.json!'
    )
    fail_if_not(
        "scholar" in profile_json,
        'Must include a "scholar" field in data/profile.json!',
    )

    # These next four can be empty
    news_json = read_data("data/news.json", optional=True)
    for news in news_json:
        fail_if_not(
            "date" in news,
            'Must include a "date" field for each news in data/news.json!',
        )
        fail_if_not(
            "text" in news,
            'Must include a "text" field for each news in data/news.json!',
        )

    dates = [datetime.strptime(n["date"], "%m/%Y") for n in news_json]
    warn_if_not(
        dates == sorted(dates, reverse=True),
        "The dates in data/news.json are not in order.",
    )

    pubs_bibtex = parse_file("data/publications.bib") if os.path.exists("data/publications.bib") else []
    for pub in pubs_bibtex.entries.values():
        fail_if_not(
            "title" in pub.fields,
            'Must include a "title" field for each pub in data/publications.json!',
        )
        fail_if_not(
            "journal" in pub.fields or "booktitle" in pub.fields,
            'Must include a "journal" or "booktitle" field for each pub in data/publications.json!',
        )
        fail_if_not(
            len(pub.persons['author']) > 0,
            'Must include an "author" field for each pub in data/publications.json!',
        )
        fail_if_not(
            "build_short" in pub.fields,
            'Must include a "build_short" subfield for each pub venue in data/publications.json!',
        )

        pub.fields["build_link"] = "" if "build_link" not in pub.fields else pub.fields["build_link"]
        pub.fields["build_extra"] = "" if "build_extra" not in pub.fields else pub.fields["build_extra"]
        pub.fields["build_slides"] = "" if "build_slides" not in pub.fields else pub.fields["build_slides"]
        pub.fields["build_bibtex"] = "" if "build_bibtex" not in pub.fields else pub.fields["build_bibtex"]

        fail_if_not(
            "build_keywords" in pub.fields,
            'Must include a "build_keywords" field for each pub in data/publications.json!',
        )
        fail_if_not(
            "build_selected" in pub.fields,
            'Must include a "build_selected" field for each pub in data/publications.json!',
        )

    education_json = read_data("data/education.json", optional=True)
    for education in education_json:
        fail_if_not(
            "year" in education,
            'Must include a "year" field for each education in data/education.json!',
        )
        fail_if_not(
            "degree" in education,
            'Must include a "degree" field for each education in data/education.json!',
        )
        fill_if_missing(education, "note")
        fail_if_not(
            "institution" in education,
            'Must include a "institution" field for each education in data/education.json!',
        )

    auto_links_json = read_data("data/auto_links.json", optional=True)
    auto_notes_json = read_data("data/auto_notes.json", optional=True)

    # Sanity checks
    if not is_federicos(meta_json["name"]):
        status("\nPerforming sanity checks:")
        check_cname()
        check_tracker(meta_json["tracker"])

    # Load templates
    status("\nLoading template files:")
    main_css = read_template(f"{config.templates}/main.css", optional=False)
    light_css = read_template(f"{config.templates}/light.css", optional=False)
    dark_css = read_template(f"{config.templates}/dark.css", optional=True)
    dark_css = light_css if dark_css == "" else dark_css
    has_dark = light_css != dark_css
    head_html = read_template(f"{config.templates}/head.html", optional=False)
    footer_html = read_template(f"{config.templates}/footer.html", optional=False)
    paper_html = read_template(f"{config.templates}/paper.html", optional=False)
    news_item_html = read_template(f"{config.templates}/news-item.html", optional=False)

    if is_federicos(meta_json["name"]):
        footer_html = """\n<footer>\n<p>Feel free to <a href="https://github.com/FedericoAureliano/FedericoAureliano.github.io">use this website template</a>.</p>\n</footer>\n"""
    else:
        footer_html = "\n" + footer_html

    # Create HTML and CSS
    head_html = replace_placeholders(head_html, meta_json)
    footer_html = replace_placeholders(footer_html, meta_json)
    main_css = replace_placeholders(main_css, style_json)
    light_css = replace_placeholders(light_css, style_json)
    dark_css = replace_placeholders(dark_css, style_json)
    news_page = build_news_page(news_json, auto_links_json, auto_notes_json, has_dark)
    pubs_page = build_pubs_page(pubs_bibtex, auto_links_json, auto_notes_json, has_dark)
    index_page = build_index(
        profile_json, news_json, pubs_bibtex, auto_links_json, auto_notes_json, has_dark
    )

    # Write to files
    status("\nWriting website:")
    write_file(f"{config.target}/index.html", index_page)
    write_file(f"{config.target}/news.html", news_page)
    write_file(f"{config.target}/pubs.html", pubs_page)
    write_file(f"{config.target}/main.css", main_css)
    write_file(f"{config.target}/light.css", light_css)
    write_file(f"{config.target}/dark.css", dark_css)

    # Got to here means everything went well
    success(f"Open {config.target}/index.html in your browser to see your website!")

    if not args.curriculum_vitae:
        exit(0)
    
    status("Generating Curriculum Vitae Latex:")
    write_file(f"{config.target}/cv/cv.tex", build_cv(meta_json, profile_json, education_json, pubs_bibtex))
    
    # remove all the entries in pubs_bibtex that start with build_
    for key in list(pubs_bibtex.entries.keys()):
        for field in list(pubs_bibtex.entries[key].fields.keys()):
            if field == "build_keywords":
                pubs_bibtex.entries[key].fields["keywords"] = pubs_bibtex.entries[key].fields["build_keywords"]
                pubs_bibtex.entries[key].fields.pop(field)
            elif field.startswith("build_"):
                pubs_bibtex.entries[key].fields.pop(field)

    # make the your name bold in cv
    for key in list(pubs_bibtex.entries.keys()):
        authors = pubs_bibtex.entries[key].persons["author"]
        for name in meta_json["name"].split():
            authors = [Person(str(author).replace(name, r"\textbf{" + name + "}")) for author in authors]
        pubs_bibtex.entries[key].persons["author"] = authors

    pubs_bibtex.to_file(f"{config.target}/cv/cv.bib")


    # Got to here means everything went well
    success(f"Navigate to {config.target}/cv and do `make view` to see your curriculum vitae!")
    exit(0)
