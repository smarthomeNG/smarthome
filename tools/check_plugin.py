#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2023-       Martin Sinn                         m.sinn@gmx.de
#########################################################################
#  This file is part of SmartHomeNG
#  https://github.com/smarthomeNG/smarthome
#  http://knx-user-forum.de/
#
#  SmartHomeNG is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHomeNG is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHomeNG. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

#TODO

# user_doc: Prüfen, ob im Abschnitt Konfiguration ein Link auf die generierte Konfigurationsseite vorhanden ist
# user_doc: Prüfen, ob das eingebundene Icon auch existiert

import os
import argparse

import plugin_metadata_checker as mc

BASE = os.path.dirname(os.path.dirname(os.path.abspath(os.path.basename(__file__))))

VERSION = '0.6.3'

sum_errors = 0
sum_warnings = 0
sum_hints = 0
total_errors = 0
total_warnings = 0
total_hints = 0


def check_metadata(plg, quiet=False):
    """
    Check metadata for the selected plugin

    :param plg: plugin name
    :type plg: str
    """
    mc.check_metadata_of_plugin(plg, quiet=quiet)
    #mc.print_errorcount('-> Metadata', mc.errors, mc.warnings, mc.hints)

    global sum_errors, sum_warnings, sum_hints
    sum_errors = mc.errors
    sum_warnings = mc.warnings
    sum_hints = mc.hints
    global total_errors, total_warnings, total_hints
    total_errors += mc.errors
    total_warnings += mc.warnings
    total_hints += mc.hints
    return


# ===============================================================================================
# The following functions perform the checks on the documentation of the plugin(user_doc.rst)
#

title_line = None
section_titles = {}


def check_documentation_title(plg, lines):
    # - Prüfen der Hauptüberschrift: Form === / <plg> / ===
    for lineno, line in enumerate(lines):
        if line.strip().lower() == plg:
            break
    else:
        mc.disp_error(f"The main title of the documentation is wrong",
                      f"The title of the main section of the documentation should only contain the name of the plugin in lowercase letters (in this case '{plg}').",
                      "!!! No further checks of the documentation have been made !!!")
        return
    if line.strip() != plg:
        mc.disp_warning(f"The main title of the documentation is wrong",
                      f"The title of the main section of the documentation should only contain the name of the plugin in lowercase letters (in this case '{plg}').")

    if len(lines[lineno + 1]) == 0:
        mc.disp_error(f"The main title of the documentation was not found",
                      "The lines above and below the name should contain an number of '=' characters",
                      "!!! No further checks of the documentation have been made !!!")
        return
    else:
        if lines[lineno+1] != '=' * len(lines[lineno]):
            mc.disp_warning(f"The line below the document title ({plg}) contains the wrong number of '='", "The line should have the same length as the document title. The lines above and below the title should only consist of a number of '=' characters.")

    if lineno > 1:
        if lines[lineno-1] != '=' * len(lines[lineno]):
            mc.disp_warning(f"The line above the document title ({plg}) contains the wrong number of '='", "The line should have the same length as the document title. The lines above and below the title should only consist of a number of '=' characters.")
    else:
        mc.disp_error(f"The main title of the documentation is wrong",
                      "The line above the name should contain a number of '=' characters", "The line should have the same length as the title.")

    global title_line
    title_line = lineno
    return


def find_documentation_sections(lines):

    global section_titles
    section_titles = {}
    for lineno, line in enumerate(lines):
        try:
            if line != '' and lineno != title_line and lines[lineno+1] == '=' * len(lines[lineno]):
                section_titles[line] = lineno
        except: pass

    if section_titles == {}:
        mc.disp_error("No sections (beside the document title) have been found.", "The line below the section title should have the same length as the section title. The line below the title should only consist of a number of '=' characters.")

    section_titles['###END OF FILE###'] = len(lines)
    return


def check_documentation_logo(lines):
    # - Prüfen ob der Logo-Block eingebunden ist (.. image:: webif/static/img/plugin_logo.png)
    found = None
    for lineno, line in enumerate(lines):
        if line.strip() == '.. image:: webif/static/img/plugin_logo.jpg':
            found = lineno
            break
        if line.strip() == '.. image:: webif/static/img/plugin_logo.png':
            found = lineno
            break
        if line.strip() == '.. image:: webif/static/img/plugin_logo.svg':
            found = lineno
            break
    else:
        mc.disp_warning(f"There has been no plugin logo included in the documentation",
                        f"The logo should be included after the title with the following line: '.. image:: webif/static/img/plugin_logo.<extension>'. For an example how to include a plugin logo, take a look at the sample_plugin in the ../dev folder.",
                        "The logo itself should be stored in the subdirectory 'webif/static/img' of the plugin, should be named 'plugin_logo' and have the extension of '.jpg', '.png' or '.svg'")

    # - Prüfen, ob das Logo an der richtigen Stelle im Dokument steht
    if found is not None:
        if found < title_line or found > next(iter(section_titles.values())):
            mc.disp_error(f"The plugin logo should be includes below the document title and above the first section title", "The plugin logo should be the first information following the document title and be included before the beginning of the global description text.")
        else:
            for lineno in range(title_line+2, found):
                if lines[lineno] != '' and not lines[lineno].startswith('..'):
                    break
            if lineno != found-1:
                mc.disp_error(
                    f"The plugin logo should be includes below the document title and above the first section title",
                    "The plugin logo should be the first information following the document title and be included before the beginning of the global description text.")

    # - Prüfen ob ein Logo (im webif directory) abgelegt ist
    if (not os.path.isfile('webif/static/img/plugin_logo.jpg')) and \
            (not os.path.isfile('webif/static/img/plugin_logo.png')) and \
            (not os.path.isfile('webif/static/img/plugin_logo.svg')):
        mc.disp_warning(f"No plugin logo has been found in the directory 'webif/static/img'")


def check_documentation(plg, quiet=False):
    """
    Check documentation for the selected plugin

    :param plg: plugin name
    :type plg: str
    """
    mc.errors = 0
    mc.warnings = 0
    mc.hints = 0

    doc_filename = 'user_doc.rst'
    if not quiet:
        print()
        print(f"*** Checking documentation of plugin '{plg}' ({doc_filename}):")
        print()

    if not os.path.isfile(doc_filename):
        mc.disp_warning(f"No documentation file '{doc_filename}'",
                        "You should create a documentation file for the plugin")
    else:
        # read documentation file
        with open(doc_filename) as f:
            lines = f.readlines()
        # remove newlines from the end of each line
        for lineno, line in enumerate(lines):
            lines[lineno] = lines[lineno].rstrip()

        check_documentation_title(plg, lines)
        if title_line is not None:
            find_documentation_sections(lines)
            check_documentation_logo(lines)

            # - Prüfen ob die grundsätzlichen Stichworte am Dateianfang definiert sind (.. index:: Plugins; <plg> , .. index:: <plg>
            index1_line = None
            index2_line = None
            for lineno, line in enumerate(lines):
                if lineno >= title_line:
                    break
                if line.find('.. index:: Plugins; '+plg) == 0:
                    index1_line = lineno
                if line == '.. index:: '+plg or line.find('.. index:: '+plg+' ') == 0 or line.find('.. index:: '+plg+';') == 0:
                    index2_line = lineno
            if index1_line is None or index2_line is None:
                mc.disp_warning(f"No global index entries found for the documentation", "You should at least include two lines with index statements before the title of the documentation.", f"The index statements should be '.. index:: Plugins; {plg}' and '.. index:: {plg}'")

            # - Prüfen ob ein Abschnitt für das Webinterface existiert
            if webif_found:
                if not 'Web Interface' in section_titles.keys():
                    mc.disp_warning(f"No section 'Web Interface' with the documentation for the web interface of the plugin found.", "You should document, what the web interface of the plugin does and include pictures as an example.")

    if not quiet:
        mc.print_errorcount('Documentation', mc.errors, mc.warnings, mc.hints)

    global sum_errors, sum_warnings, sum_hints
    sum_errors += mc.errors
    sum_warnings += mc.warnings
    sum_hints += mc.hints
    global total_errors, total_warnings, total_hints
    total_errors += mc.errors
    total_warnings += mc.warnings
    total_hints += mc.hints

    return


# ===============================================================================================
# The following functions perform the checks on the doce of the plugin (__init__.py)
#

webif_found = False


def check_code_webinterface(lines, webif_lines):

    # - is a webinterface defined?
    webif_seperated = False
    for line in lines:
        if line.find('from .webif import WebInterface') > -1:
            webif_seperated = True
            break
    for line in lines:
        if line.find('def init_webinterface(self') > -1:
            break
    else:
        if not webif_seperated:
            mc.disp_hint("No webinterface is implemented", "You should consider to to implement a webinterface.")
            return

    # - is the webinterface being initialized?
    for line in lines:
        if line.find('self.init_webinterface') > -1:
            if line.find('#') == -1:
                break
            if not line.find('#') < line.find('self.init_webinterface'):
                break
    else:
        mc.disp_warning("Webinterface is not beeing initialized")
    global webif_found
    webif_found = True

    # - is the code of the webinterface seperated into the webif subfolder?
    if not webif_seperated:
        mc.disp_hint("The code of the webinterface is not seperated into a different file", "You should consider to seperate the code the webinterface into the subfolder 'webif'. Take a look at the sample plugin in the ../dev folder.")
    else:
        # - was "Sample plugin" from the templaate file changed?
        for line in webif_lines:
            if line.lower().find('sample plugin') > -1 and line.startswith('#'):
                mc.disp_hint("The description of the sample plugin in the comments of the web interface code was not replaced", "Replace the description in webif/__init__.py with a meaningful text")
                break


def check_code(plg, quiet=False):
    mc.errors = 0
    mc.warnings = 0
    mc.hints = 0

    code_filename = '__init__.py'
    webif_code_filename = os.path.join('webif', '__init__.py')
    if not quiet:
        print()
        print(f"*** Checking python code of plugin '{plg}' (__init__.py, webif{os.sep}__init__.py):")
        print()

    if not os.path.isfile(code_filename):
        mc.disp_error(f"No code ('{code_filename}') found for the plugin '{plg}'", "Aborting code check")
    else:
        # read code file of the plugin
        with open(code_filename) as f:
            lines = f.readlines()
        # remove newlines from the end of each line
        for lineno, line in enumerate(lines):
            lines[lineno] = lines[lineno].rstrip()

        # read code file of the web interface
        with open(code_filename) as f:
            webif_lines = f.readlines()
        # remove newlines from the end of each line
        for lineno, line in enumerate(webif_lines):
            webif_lines[lineno] = webif_lines[lineno].rstrip()

        # TODO
        # - check if get_parameter() is used in __init__ -> Warning
        # - check if add_item is used in parse_item -> Hint

        # - is super().__init__() being called from __init__()?
        in_init_method = False
        init_found = False
        for lineno, line in enumerate(webif_lines):
            if line.lstrip().startswith('def'):
                if line.lstrip().startswith('def __init__(self'):
                    in_init_method = True
                    init_found = True
                else:
                    in_init_method = False

            if in_init_method:
                if line.find('super().__init__()') > -1:
                    if line.find('#') == -1:
                        break
                    if not line.find('#') < line.find('super().__init__()'):
                        break
        else:
            if init_found:
                mc.disp_error("super().__init__() is not called from __init__()")
            else:
                mc.disp_error("__init__() method not found")

        # - is a stop() method defined?
        for lineno, line in enumerate(webif_lines):
            if line.find('def stop(') > -1:
                if line.find('#') == -1:
                    break
                if not line.find('#') < line.find('def stop('):
                    break
        else:
                mc.disp_error("no stop() method found")

        # - was "Sample plugin" from the templaate file changed?
        for line in lines:
            if line.lower().find('sample plugin') > -1 and line.startswith('#'):
                mc.disp_hint("The description of the sample plugin in the comments was not replaced", "Replace the description in __init__.py with a meaningful text")
                break

        check_code_webinterface(lines, webif_lines)

        if not quiet:
            mc.print_errorcount('Code', mc.errors, mc.warnings, mc.hints)
            print()

    global sum_errors, sum_warnings, sum_hints
    sum_errors += mc.errors
    sum_warnings += mc.warnings
    sum_hints += mc.hints
    global total_errors, total_warnings, total_hints
    total_errors += mc.errors
    total_warnings += mc.warnings
    total_hints += mc.hints
    return


def check_one_plugin(plg, chk_meta, chk_code, chk_docu):
    try:
        os.chdir(plugindir)
    except:
        print(f"ERROR: No plugin with name '{plg}' found.")
        print()
        exit(1)
    if chk_meta:
        check_metadata(plg)
    os.chdir(plugindir)
    if chk_code:
        check_code(plg)
    if chk_docu:
        check_documentation(plg)

    print()
    mc.print_errorcount('TOTAL', sum_errors, sum_warnings, sum_hints)
    print()


def check_all_plugins(chk_meta, chk_code, chk_docu, quiet=True):
    pluginsdir = os.path.join(BASE, 'plugins')

    plugins = mc.get_local_pluginlist(pluginsdir)
    print(f"{'Plugin':<16.16}      {'Errors':>10}  {'Warnings':>10}  {'Hints':>10}")
    print(f"{'-'*16:<16.16}      {'-'*8:>10}  {'-'*8:>10}  {'-'*8:>10}")

    for plg in plugins:
        mc.quiet = quiet
        if chk_meta:
            check_metadata(plg, quiet=quiet)

        os.chdir(os.path.join(pluginsdir, plg))
        if chk_code:
            check_code(plg, quiet=quiet)

        os.chdir(os.path.join(pluginsdir, plg))
        if chk_docu:
            check_documentation(plg, quiet=quiet)

        global sum_errors, sum_warnings, sum_hints
        print(f"{plg:<16.16}    {sum_errors:10}  {sum_warnings:10}  {sum_hints:10}")

        sum_errors = 0
        sum_warnings = 0
        sum_hints = 0

    print(f"{'-'*16:<16.16}      {'-'*8:<10}  {'-'*8:<10}  {'-'*8:<10}")
    print(f"{'':<16.16}    {total_errors:10}  {total_warnings:10}  {total_hints:10}")
    print()


# ==================================================================================
#   Main Routine of the tool
#

if __name__ == '__main__':
    print('')
    print(os.path.basename(__file__) + ' v' + VERSION + ' - Check plugin for formal errors or improvement potential')
    print('')

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('pluginname', nargs='?', default='', help='name of the plugin to check')  # positional argument#
    parser.add_argument('-all', dest='check_all', help='check all plugins', action='store_true')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-m', dest='check_metadata_only', help='check only the metadata of a plugin', action='store_true')
    group.add_argument('-d', dest='check_documentation_only', help='check only the documentation of a plugin', action='store_true')
    group.add_argument('-c', dest='check_code_only', help='check only the code of a plugin', action='store_true')
    group.add_argument('-cd', dest='check_code_doc_only', help='check only the code and documentation of a plugin', action='store_true')
    args = parser.parse_args()

    plg = args.pluginname

    plugindir = os.path.join(BASE, 'plugins', plg)

    chk_meta = True
    chk_code = True
    chk_docu = True

    if args.check_metadata_only:
        chk_code = False
        chk_docu = False
    if args.check_code_only:
        chk_meta = False
        chk_docu = False
    if args.check_documentation_only:
        chk_meta = False
        chk_code = False
    if args.check_code_doc_only:
        chk_meta = False

    if args.check_all:
        check_all_plugins(chk_meta, chk_code, chk_docu)
    elif plg == '':
        parser.print_help()
        print()
    else:
        check_one_plugin(plg, chk_meta, chk_code, chk_docu)

