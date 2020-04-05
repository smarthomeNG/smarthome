#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2017-       Martin Sinn                         m.sinn@gmx.de
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


"""
This script creates the files for including the plugin documentation into the developer- and
user-documentation.

it creates the files:

- plugins_gateway.rst
- plugins_interface.rst
- plugins_protocol.rst
- plugins_system.rst
- plugins_unclassified.rst
- plugins_web.rst

in the directory **../doc/<user/developer>/source/plugins_doc** .

These files contain

- an include for a header file
- a toctree directive
- a table with information about the plugins and links to further information
- an include for a footer file

"""

import os

print('')
print(os.path.basename(__file__) + ' - Builds the .rst files for the documentation')
print('')
start_dir = os.getcwd()

import sys
# find lib directory and import lib/item_conversion
os.chdir(os.path.dirname(os.path.abspath(__file__)))
#sys.path.insert(0, '../lib')
#import item_conversion

# um im Test-build_doc Umfeld zu laufen:
sys.path.insert(0, '..')
sys.path.insert(0, '../lib')
import shyaml

import subprocess

#global language
#language = 'en'


type_unclassified = 'unclassified'
plugin_sections = [ ['gateway', 'Gateway', 'Gateway'],
                    ['interface', 'Interface', 'Interface'],
                    ['protocol', 'Protocol', 'Protokoll'],
                    ['system', 'System', 'System'],
                    [type_unclassified, 'Non classified', 'nicht klassifizierte'],
                    ['web', 'Web/Cloud', 'Web/Cloud']
                  ]

def bold(s):
    return "**"+s+"**" if s else ""


def get_pluginlist_fromgit():
    plglist = []
    plg_git = subprocess.check_output(['git', 'ls-files', '*/__init__.py'], stderr=subprocess.STDOUT).decode().strip('\n')
    for plg in plg_git.split('\n'):
        if plg.split('/')[1] == '__init__.py':
#            print(plg.split('/')[0], '   -   ', plg)
            plglist.append(plg.split('/')[0])
    return plglist


def get_local_pluginlist():
    plglist = os.listdir('.')

    for entry in plglist:
        if entry[0] in ['.','_'] or entry == 'deprecated_plugins':
            plglist.remove(entry)
    for entry in plglist:
        if entry[0] in ['.','_']:
            plglist.remove(entry)
    for entry in plglist:
        if entry[0] in ['.','_']:
            plglist.remove(entry)
    return plglist


def get_pluginyamllist_fromgit():
    plglist = []
    plg_git = subprocess.check_output(['git', 'ls-files', '*/plugin.yaml'], stderr=subprocess.STDOUT).decode().strip('\n')
    for plg in plg_git.split('\n'):
        if plg.split('/')[1] == 'plugin.yaml':
#            print(plg,'   -   ', plg.split('/')[0], )
            plglist.append(plg.split('/')[0])
    return plglist


def get_description(section_dict, maxlen=70, lang='en'):
    desc = ''
    if lang == 'en':
        lang2 = 'de'
    else:
        lang2 = 'en'
    try:
        desc = section_dict['description'].get(lang, '')
    except:
        pass
    if desc == '':
        try:
            desc = section_dict['description'].get(lang2, '')
        except:
            pass

    import textwrap
    lines = textwrap.wrap(desc, maxlen, break_long_words=False)
    if lines == []:
        lines.append('')
    return lines


def get_maintainer(section_dict, maxlen=20):
    maint = section_dict.get('maintainer', '')

    import textwrap
    lines = textwrap.wrap(maint, maxlen, break_long_words=False)
    if lines == []:
        lines.append('')
    return lines


def get_tester(section_dict, maxlen=20):
    maint = section_dict.get('tester', '')

    import textwrap
    try:
        lines = textwrap.wrap(str(maint), maxlen, break_long_words=False)
    except:
        print()
        print("section_dict: {}, maint: {}".format(section_dict, maint))
        print()
    if lines == []:
        lines.append('')
    return lines


def get_docurl(section_dict, maxlen=70):
    maint = section_dict.get('documentation', '')

    import textwrap
    lines = textwrap.wrap(maint, maxlen, break_long_words=True)
    if lines == []:
        lines.append('')
    return lines


def get_supurl(section_dict, maxlen=70):
    maint = section_dict.get('support', '')

    import textwrap
    lines = textwrap.wrap(maint, maxlen, break_long_words=True)
    if lines == []:
        lines.append('')
    return lines


def html_escape(str):
#    str = str.rstrip().replace('<', '&lt;').replace('>', '&gt;')
#    str = str.rstrip().replace('(', '&#40;').replace(')', '&#41;')
#    str = str.rstrip().replace("'", '&#39;').replace('"', '&quot;')
    html = str.rstrip().replace("ä", '&auml;').replace("ö", '&ouml;').replace("ü", '&uuml;') if str else ""
    return html


def build_pluginlist( plugin_type='all' ):
    """
    Return a list of dicts with a dict for each plugin of the requested type
    The dict contains the plugin name, type and description
    """
    result = []
    plugin_type = plugin_type.lower()
    for metaplugin in plugins_git:
        metafile = metaplugin + '/plugin.yaml'
        plg_dict = {}
        if metaplugin in plugins_git:    #pluginsyaml_git
            if os.path.isfile(metafile):
                plugin_yaml = shyaml.yaml_load(metafile)
            else:
                plugin_yaml = ''
            if plugin_yaml != '':
                section_dict = plugin_yaml.get('plugin')
                if section_dict != None:
                    if section_dict.get('type') != None:
                        if section_dict.get('type').lower() in plugin_types:
                            plgtype = section_dict.get('type').lower()
                            plg_dict['name'] = metaplugin.lower()
                            plg_dict['type'] = plgtype
                            plg_dict['desc'] = get_description(section_dict, 85, language)
                            plg_dict['maint'] = get_maintainer(section_dict, 15)
                            plg_dict['test'] = get_tester(section_dict, 15)
                            plg_dict['doc'] = html_escape(section_dict.get('documentation', ''))
                            plg_dict['sup'] = html_escape(section_dict.get('support', ''))
                        else:
                            plgtype = type_unclassified
                    else:
                        plgtype = type_unclassified
                        if plugin_type == type_unclassified:
                            print("not found: plugin type '{}' defined in plugin '{}'".format(section_dict.get('type'),metaplugin))
                else:
                    plgtype = type_unclassified

                if (plgtype == type_unclassified) and (plugin_yaml != ''):
                    plg_dict['name'] = metaplugin.lower()
                    plg_dict['type'] = type_unclassified
                    plg_dict['desc'] = get_description(section_dict, 85, language)
                    plg_dict['maint'] = get_maintainer(section_dict, 15)
                    plg_dict['test'] = get_tester(section_dict, 15)
                    plg_dict['doc'] = html_escape(section_dict.get('documentation', ''))
                    plg_dict['sup'] = html_escape(section_dict.get('support', ''))
                    print("")
                    print("> unclassified plugin: metafile = {}, plg_dict = {}".format(metafile, str(plg_dict)))

                plg_dict['desc'].append('')
            else:
                plgtype = type_unclassified
                plg_dict['name'] = metaplugin.lower()
                plg_dict['type'] = type_unclassified
                plg_dict['desc'] = ['No metadata (plugin.yaml) was provided for this plugin!']
                plg_dict['maint'] = ['']
                plg_dict['test'] = ['']
                plg_dict['doc'] = ''
                plg_dict['sup'] = ''


            # Adjust list lengths
            maxlen = max( len(plg_dict['desc']), len(plg_dict['maint']), len(plg_dict['test']) )
            while len(plg_dict['desc']) < maxlen:
                plg_dict['desc'].append('')
            while len(plg_dict['maint']) < maxlen:
                plg_dict['maint'].append('')
            while len(plg_dict['test']) < maxlen:
                plg_dict['test'].append('')


        if (plgtype == plugin_type) or (plugin_type == 'all'):
#            result.append(metaplugin)
            result.append(plg_dict)
    return result


def write_rstfile(plgtype='All', plgtype_print='', heading=''):
    """
    Create a .rst file for each plugin category
    """
    fh_dummy_used = False;

    if heading == '':
        title = plgtype + ' Plugins'
    else:
        title = heading

    rst_filename = 'plugins_doc/plugins_'+plgtype.lower()+'.rst'
    rst_dummyname = 'plugins_doc/dummy_'+plgtype.lower()+'.rst'
    print('Datei: '+rst_filename+ ' '*(26-len(rst_filename)) +'  -  '+title)

    plglist = build_pluginlist(plgtype)

#    print("> Opening file "+plugin_rst_dir+'/'+rst_filename)
    fh = open(plugin_rst_dir+'/'+rst_filename, "w")

#    fh.write(title+'\n')
#    fh.write('-'*len(title)+'\n')
    if plgtype != type_unclassified:
        fh.write('.. index:: Plugins; '+plgtype_print+'\n')
        fh.write('\n')
    fh.write('.. include:: /plugins_doc/plugins_'+plgtype+'_header.rst\n')
    fh.write('\n')

    if (len(plglist) == 0):
        fh.write('At the moments there are no plugins that have not been classified.\n')
    else:
        if not fh_dummy_used:
            fh_dummy = open(plugin_rst_dir + '/' + rst_dummyname, "w")
            fh_dummy_used = True;
        # write toctree to dummy file to suppress warnings for not included README.md files.
        fh_dummy.write(':orphan:\n')
        fh_dummy.write('\n')
        fh_dummy.write('.. This file is only created to suppress Sphinx warnings about README.md files not beeing included in any toctree.\n')
        fh_dummy.write('\n')
        fh_dummy.write('.. toctree::\n')
        fh_dummy.write('   :maxdepth: 2\n')
        fh_dummy.write('   :glob:\n')
        fh_dummy.write('   :titlesonly:\n')
        fh_dummy.write('   :hidden:\n')
        fh_dummy.write('\n')

        # write toctree
        fh.write('.. toctree::\n')
        fh.write('   :maxdepth: 2\n')
        fh.write('   :glob:\n')
        fh.write('   :titlesonly:\n')
        fh.write('   :hidden:\n')
        fh.write('\n')
        for plg in plglist:
            if os.path.isfile(plg['name']+'/README.md'):
                fh_dummy.write('   /plugins/'+plg['name']+'/README.md\n')
            if docu_type == 'user':
                fp = plg['name']+'/user_doc'
#                fp_ignore = plg['name']+'/developer_doc'
                if os.path.isfile(fp+'.rst') or os.path.isfile(fp+'.md'):
                    fh.write('   /plugins/'+fp+'\n')
#                if os.path.isfile(fp_ignore+'.rst') or os.path.isfile(fp_ignore+'.md'):
#                    fh_dummy.write('   /plugins/'+fp_ignore+'\n')
            elif docu_type == 'developer':
                fp = plg['name']+'/developer_doc'
#                fp_ignore = plg['name']+'/user_doc'
                if os.path.isfile(fp+'.rst') or os.path.isfile(fp+'.md'):
                    fh.write('   /plugins/'+fp+'\n')
#                if os.path.isfile(fp_ignore+'.rst') or os.path.isfile(fp_ignore+'.md'):
#                    fh_dummy.write('   /plugins/'+fp_ignore+'\n')
            else:
                fh.write('   /plugins/'+plg['name']+'/README.md\n')
        fh.write('\n')

        # write table with details
#        fh.write('.. include:: /plugins_doc/plugins_'+plgtype+'_header.rst\n')
        fh.write('\n')
        fh.write('\n')
        fh.write('.. table:: \n')
        fh.write('   :widths: grid\n')
        fh.write('\n')
        fh.write('   +-'+ '-'*65 +'-+-'+ '-'*165 +'-+-----------------+-----------------+\n')
        if language == 'de':
            fh.write('   | {p:<65.65} | {b:<165.165} | Maintainer      | Tester          |\n'.format(p='Plugin', b='Beschreibung'))
        else:
            fh.write('   | {p:<65.65} | {b:<165.165} | Maintainer      | Tester          |\n'.format(p='Plugin', b='Description'))
        fh.write('   +='+ '='*65 +'=+=' + '='*165 + '=+=================+=================+\n')
        for plg in plglist:
            plg_readme_link = ':doc:`'+plg['name']+' </plugins/'+plg['name']+'/README.md>`'
            plg_readme_link = ':doc:`'+plg['name']+' <../plugins/'+plg['name']+'/README>`'
            if os.path.isfile(plugin_rst_dir+'/'+'plugins_doc/config/'+plg['name']+'.rst'):
                # a generated <config>.rst exists
                plg_readme_link = ':doc:`'+plg['name']+' <config/'+plg['name']+'>`'
            else:
                # no generated <config>.rst exists (for english developer documentation
                # -> test if a README really exists
                if not os.path.isfile(plg['name']+'/README.md'):
                    plg_readme_link = plg['name']

#            fh.write('   | {plg:<65.65} | {desc:<165.165} | {maint:<15.15} | {test:<15.15} |\n'.format(plg=plg['name'], desc=plg['desc'][0], maint=plg['maint'][0], test=plg['test'][0]))
            fh.write('   | {plg:<65.65} | {desc:<165.165} | {maint:<15.15} | {test:<15.15} |\n'.format(plg=plg_readme_link, desc=plg['desc'][0], maint=plg['maint'][0], test=plg['test'][0]))
            for l in range(1, len(plg['desc'])):
                fh.write('   | {plg:<65.65} | {desc:<165.165} | {maint:<15.15} | {test:<15.15} |\n'.format(plg='', desc=plg['desc'][l], maint=plg['maint'][l], test=plg['test'][l]))
            if plg['doc'] != '':
                if language == 'de':
                    plg['doc'] = "`"+plg['name']+" zusätzliche Infos <"+plg['doc']+">`_"
                else:
                    plg['doc'] = "`"+plg['name']+" additional info <"+plg['doc']+">`_"
                fh.write('   | {plg:<65.65} | - {desc:<163.163} | {maint:<15.15} | {test:<15.15} |\n'.format(plg='', desc=plg['doc'], maint='', test=''))
            if plg['sup'] != '':
#                if plg['doc'] != '':
#                    fh.write('   | {plg:<65.65} |   {desc:<163.163} | {maint:<15.15} | {test:<15.15} |\n'.format(plg='', desc='', maint='', test=''))
                if language == 'de':
                    plg['sup'] = "`"+plg['name']+" Unterstützung <"+plg['sup']+">`_"
                else:
                    plg['sup'] = "`"+plg['name']+" support <"+plg['sup']+">`_"
                fh.write('   | {plg:<65.65} | - {desc:<163.163} | {maint:<15.15} | {test:<15.15} |\n'.format(plg='', desc=plg['sup'], maint='', test=''))
            fh.write('   +-'+ '-'*65 +'-+-'+ '-'*165 +'-+-----------------+-----------------+\n')
        fh.write('\n')
        fh.write('\n')

        fh.write('.. include:: /plugins_doc/plugins_footer.rst\n')

    fh.close()
    if fh_dummy_used:
        fh_dummy.close()


# ==================================================================================
#   Main Generator Routine
#

if __name__ == '__main__':

#    print ('Number of arguments:', len(sys.argv), 'arguments.')
#    print ('Argument List:', str(sys.argv))

    global language
    language = 'en'


    if 'de' in sys.argv:
        language = 'de'
    if 'en' in sys.argv:
        language = 'en'

    global docu_type
    docu_type = start_dir.split('/')[-1:][0]     # developer / user

    print('Start directory        = '+start_dir)
    print('Documentation type     = '+docu_type)
    print('Documentation language = '+language)
    print('')

    # change the working diractory to the directory from which the converter is loaded (../tools)
    os.chdir(os.path.dirname(os.path.abspath(os.path.basename(__file__))))

    plugindirectory = '../plugins'
    pluginabsdirectory = os.path.abspath(plugindirectory)

    os.chdir(pluginabsdirectory)

    plugins_git = get_pluginlist_fromgit()
    if not 'xmpp' in plugins_git:
        plugins_git.append('xmpp')

    print('--- Liste der Plugins auf github ('+str(len(plugins_git))+'):')

    pluginsyaml_git = get_pluginyamllist_fromgit()
    if not 'xmpp' in plugins_git:
        plugins_git.append('xmpp')

    print('--- Liste der Plugins mit Metadaten auf github ('+str(len(pluginsyaml_git))+'):')
    print()



    plugin_rst_dir = start_dir+'/source'
    print('zu schreiben in: '+plugin_rst_dir)

    plugin_types = []
    for pl in plugin_sections:
       plugin_types.append(pl[0])

    for pl in plugin_sections:
#        write_rstfile(pl[0], pl[1])
        write_rstfile(pl[0], pl[2])
    print()
