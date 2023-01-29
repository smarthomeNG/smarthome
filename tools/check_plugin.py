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

import os
import argparse

import plugin_metadata_checker as mc

BASE = os.path.dirname(os.path.dirname(os.path.abspath(os.path.basename(__file__))))

VERSION = '0.5.2'


def check_metadata(plg):
    """
    Check metadata for the selected plugin

    :param plg: plugin name
    :type plg: str
    """
    global sum_errors, sum_warnings, sum_hints
    mc.check_metadata_of_plugin(plg)
    sum_errors = mc.errors
    sum_warnings = mc.warnings
    sum_hints = mc.hints
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


def check_documentation(plg):
    """
    Check documentation for the selected plugin

    :param plg: plugin name
    :type plg: str
    """
    global sum_errors, sum_warnings, sum_hints
    mc.errors = 0
    mc.warnings = 0
    mc.hints = 0

    doc_filename = 'user_doc.rst'
    print()
    print(f"*** Checking documentation '{doc_filename}' of plugin '{plg}':")
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
                if line == '.. index:: '+plg or line.find('.. index:: '+plg+' ') == 0:

                    index2_line = lineno
            if index1_line is None or index2_line is None:
                mc.disp_warning(f"No global index entries found for the documentation", "You should at least include two lines with index statements before the title of the documentation.", f"The index statements should be '.. index:: Plugins; {plg}' and '.. index:: {plg}'")

            # - Prüfen ob ein Abschnitt für das Webinterface existiert
            if webif_found:
                if not 'Web Interface' in section_titles.keys():
                    mc.disp_warning(f"No section 'Web Interface' with the documentation for the web interface of the plugin found.", "You should document, what the web interface of the plugin does and include pictures as an example.")

    mc.print_errorcount('Documentation', mc.errors, mc.warnings, mc.hints)
    sum_errors += mc.errors
    sum_warnings += mc.warnings
    sum_hints += mc.hints
    return


# ===============================================================================================
# The following functions perform the checks on the doce of the plugin (__init__.py)
#

webif_found = False


def check_code_webinterface(lines):

    # - ist ein Webinterface definiert?
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

    # - Wird ein Webinterface initialisiert?
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

    # - ist der Code des Webinterfaces ausgegliedert in eigenen Ordner?
    if not webif_seperated:
        mc.disp_hint("The code of the webinterface is not seperated into a different file", "You should consider to seperate the code the webinterface into the subfolder 'webif'. Take a look at the sample plugin in the ../dev folder.")


def check_code(plg):
    global sum_errors, sum_warnings, sum_hints
    mc.errors = 0
    mc.warnings = 0
    mc.hints = 0

    code_filename = '__init__.py'
    print()
    print(f"*** Checking python code of plugin '{plg}' ({code_filename}):")
    print()

    if not os.path.isfile(code_filename):
        mc.disp_warning(f"No code ('{code_filename}') found for the plugin '{plg}'", "Aborting code check")
        return
    else:
        # read documentation file
        with open(code_filename) as f:
            lines = f.readlines()
        # remove newlines from the end of each line
        for lineno, line in enumerate(lines):
            lines[lineno] = lines[lineno].rstrip()

    check_code_webinterface(lines)

    mc.print_errorcount('Code', mc.errors, mc.warnings, mc.hints)
    print()
    sum_errors += mc.errors
    sum_warnings += mc.warnings
    sum_hints += mc.hints
    return


# ==================================================================================
#   Main Routine of the tool
#

if __name__ == '__main__':
    print('')
    print(os.path.basename(__file__) + ' v' + VERSION + ' - Check plugin for formal errors or improvement potential')
    print('')

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('pluginname')  # positional argument#
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-m', dest='check_metadata', help='check the metadata of a plugin')
    group.add_argument('-d', dest='check_documentation', help='check the documentation of a plugin')
    group.add_argument('-c', dest='check_code', help='check the code of a plugin')
    args = parser.parse_args()

    plg = args.pluginname

    plugindir = os.path.join(BASE, 'plugins', plg)
    try:
        os.chdir(plugindir)
    except:
        print(f"ERROR: No plugin with name '{plg}' found.")
        print()
        exit(1)

    check_metadata(plg)
    os.chdir(plugindir)
    check_code(plg)
    check_documentation(plg)

    print()
    mc.print_errorcount('TOTAL', sum_errors, sum_warnings, sum_hints)
    print()
