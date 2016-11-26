#!/usr/bin/env python3
# -*- coding: utf8 -*-
#########################################################################
#  Copyright 2016 Bernd Meiners,
#                 Christian Strassburg            c.strassburg@gmx.de
#                 René Frieß                      rene.friess@gmail.com
#                 Martin Sinn                     m.sinn@gmx.de
#########################################################################
#  Backend plugin for SmartHomeNG
#
#  This plugin is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This plugin is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this plugin. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import logging
import json
import os

# Funktionen für Jinja2 z.Zt außerhalb der Klasse Backend, da ich Jinja2 noch nicht mit
# Methoden einer Klasse zum laufen bekam
def get_basename(p):
    """
    returns the filename of a full pathname

    This function extends the jinja2 template engine
    """
    return os.path.basename(p)


def is_userlogic(sh, logic):
    """
    returns True if userlogic and False if system logic
    
    This function extends the jinja2 template engine
    """
    return os.path.basename(os.path.dirname(sh.return_logic(logic).filename)) == 'logics'
    
    
translation_dict = {}
translation_lang = ''

def get_translation_lang():
    global translation_lang
    return translation_lang

def load_translation(language):
    global translation_dict    # Needed to modify global copy of translation_dict
    global translation_lang    # Needed to modify global copy of translation_lang
    
    logger = logging.getLogger(__name__)
    
    translation_lang = language.lower()
    if translation_lang == '':
        translation_dict = {}
    else:
        lang_filename = os.path.dirname(os.path.abspath(__file__))+'/locale/' + translation_lang + '.json'
        try:
            f=open(lang_filename,'r')
        except:
            translation_lang = ''
            return False
        try:
            translation_dict=json.load(f)
        except Exception as e:
            logger.error("Backend: load_translation language='{0}': Error '{1}'".format(translation_lang, e))
            return False
    logger.debug("Backend: translation_dict='{0}'".format(translation_dict))
    return True


def html_escape(str):
    str = str.rstrip().replace('<','&lt;').replace('>','&gt;')
    str = str.rstrip().replace('(','&#40;').replace(')','&#41;')
    html = str.rstrip().replace("'",'&#39;').replace('"','&quot;')
    return html


def translate(txt, block=''):
    """
    returns translated text
    
    This function extends the jinja2 template engine
    """
    logger = logging.getLogger(__name__)

    txt = str(txt)
    if translation_lang == '':
        tr = txt
    else:
        if block != '':
            blockdict = translation_dict.get('_'+block,{})
            tr = blockdict.get(txt,'')
            if tr == '':
                tr = translation_dict.get(txt,'')
        else:
            tr = translation_dict.get(txt,'')
        if tr == '':
            logger.warning("Backend: Language '{0}': Translation for '{1}' is missing".format(translation_lang, txt))
            tr = txt
    return html_escape(tr)

def create_hash(plaintext):
    import hashlib
    hashfunc = hashlib.sha512()
    hashfunc.update(plaintext.encode())
    return hashfunc.digest().hex()

def parse_requirements(file_path):
    fobj = open(file_path)
    req_dict = {}
    for line in fobj:
        if len(line) > 0 and '#' not in line:
            if ">" in line:
                req_dict[line[0:line.find(">")].lower().strip()] = line[line.find(">"):len(line)].lower().strip()
            elif "<" in line:
                req_dict[line[0:line.find("<")].lower().strip()] = line[line.find("<"):len(line)].lower().strip()
            elif "=" in line:
                req_dict[line[0:line.find("=")].lower().strip()] = line[line.find("="):len(line)].lower().strip()
    fobj.close()
    return req_dict