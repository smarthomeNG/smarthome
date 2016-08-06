#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2016- Martin Sinn                              m.sinn@gmx.de
#  Parts Copyright 2012-2013 Marcus Popp                   marcus@popp.mx
#########################################################################
#  This file is part of SmartHome.py.  
#  Visit:  https://github.com/smarthomeNG/
#          https://knx-user-forum.de/forum/supportforen/smarthome-py
#
#  SmartHome.py is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHome.py is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHome.py. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import logging
import struct

import os
import shutil

import lib.config
from lib.model.smartplugin import SmartPlugin

import sys

# to do: copy tplNG files
# implement config parameter to copy/not to copy tplNG files (if dir exist in smartVISU)


#########################################################################

class SmartVisu(SmartPlugin):
    PLUGIN_VERSION="1.1.0"
    ALLOW_MULTIINSTANCE = False


    def my_to_bool(self, value, attr='', default=False):
        try:
            result = self.to_bool(value)
        except:
            result = default
            self.logger.error("smartVISU: Invalid value '"+str(value)+"' configured for attribute "+attr+" in plugin.conf, using '"+str(result)+"' instead")
        return result


    def __init__(self, smarthome, smartvisu_dir='', generate_pages='True', overwrite_templates='Yes', visu_style = 'std', handle_widgets='True' ):
        self.logger = logging.getLogger(__name__)
        self._sh = smarthome
        
        self.smartvisu_dir = str(smartvisu_dir)
        self._generate_pages = self.my_to_bool(generate_pages, 'generate_pages', True)
        self.overwrite_templates = self.my_to_bool(overwrite_templates, 'overwrite_templates', True)
        if visu_style.lower() in ['std','blk']:
            self.visu_style = visu_style.lower()
        else:
            self.visu_style = 'std'
            self.logger.error("smartVISU: Invalid value '"+str(visu_style)+"' configured for attribute visu_style in plugin.conf, using '"+str(self.visu_style)+"' instead")
        self._handle_widgets = self.my_to_bool(handle_widgets, "handle_widgets", False)


    def run(self):
        self.alive = True
        if self.smartvisu_dir != '':
            if not os.path.isdir(self.smartvisu_dir + '/pages'):
                self.logger.error("Could not find valid smartVISU directory: {0}".format(self.smartvisu_dir))
            else:
#                self.logger.warning("Starting smartVISU handling")
                if self._handle_widgets:
                    sv_iwdg = SmartVisuInstallWidgets(self._sh, self.smartvisu_dir)
                if self._generate_pages:
                    svgen = SmartVisuGenerator(self._sh, self.smartvisu_dir, self.overwrite_templates, self.visu_style)
#                self.logger.warning("Finished smartVISU handling")


    def stop(self):
        self.alive = False


#########################################################################
#       Visu page generator
#########################################################################


class SmartVisuGenerator:

    def __init__(self, smarthome, smartvisu_dir='', overwrite_templates='Yes', visu_style='std'):
        self.logger = logging.getLogger(__name__)
        self._sh = smarthome
        self.smartvisu_dir = smartvisu_dir
        self.overwrite_templates = overwrite_templates
        self.visu_style = visu_style.lower()
        if not self.visu_style in ['std','blk']:
            self.visu_style = 'std'
            self.logger.warning("SmartVisuGenerator: visu_style '{0}' unknown, using visu_style '{1}'".format(visu_style, self.visu_style))

        self.logger.log(logging.WARNING, "Generating pages for smartVISU")

        self.outdir = self.smartvisu_dir + '/pages/smarthome'
        self.tpldir = self.smartvisu_dir + '/pages/base/tplNG'
        self.tmpdir = self.smartvisu_dir + '/temp'

        self.thisplgdir = os.path.dirname(os.path.abspath(__file__))
        self.copy_templates()
        
        self.pages()


    def handle_heading_attributes(self, room):
        if 'sv_heading_right' in room.conf:
            heading_right = room.conf['sv_heading_right']
        else:
            heading_right = ''
        if 'sv_heading_center' in room.conf:
            heading_center = room.conf['sv_heading_center']
        else:
            heading_center = ''
        if 'sv_heading_left' in room.conf:
            heading_left = room.conf['sv_heading_left']
        else:
            heading_left = ''
        if heading_right != '' or heading_center != '' or heading_left != '':
            heading = self.parse_tpl('heading.html', [('{{ visu_heading_right }}', heading_right), ('{{ visu_heading_center }}', heading_center), ('{{ visu_heading_left }}', heading_left)])
        else:
            heading = ''
        return heading


    def get_widgetblocksize(self, item):
        """
        Returns the blocksize for the block in which the item is to be displayed. 
        :param item: Item to be displayed
        :return: The set number ('1'..'3') as defined in smartVISUs css
        """
        if 'sv_blocksize' in item.conf:
            blocksize = item.conf['sv_blocksize']
            if not blocksize in ['1','2','3']:
                blocksize = '2'
        else:
            blocksize = '2'
        return blocksize
        
        
    def get_attribute(self, attr, item):
        if attr in item.conf:
            attrvalue = item.conf[attr]
        else:
            attrvalue = ''
        return attrvalue
    
    
    def room(self, room):
        """
        Interpretation of the room-specific item-attributes. 
        This routine is called once per 'sv_page'.

        :param room: Items (with room configuration)
        :param tpldir: Directory where the template files are stored (within smartVISU)
        :return: html code to be included in the visu file for the room
        """
        block_style = 'std' # 'std' or 'noh'
        widgetblocktemplate = 'widgetblock_' + self.visu_style + '_' + block_style + '.html'
        widgetblocktemplate2 = 'widgetblock2_' + self.visu_style + '_' + block_style + '.html'
        widgets = ''

        rimg = self.get_attribute('sv_img', room)
        heading = self.handle_heading_attributes(room)

        if 'sv_widget' in room.conf:
            items = [room]
        else:
            items = []

        if (room.conf['sv_page'] == 'room') or (room.conf['sv_page'] == 'room_lite'):
            items.extend(self._sh.find_children(room, 'sv_widget'))
        elif room.conf['sv_page'] == 'category':
            items.extend(self._sh.find_children(room, 'sv_widget'))
        elif room.conf['sv_page'] == 'overview':
            items.extend(self._sh.find_items('sv_item_type'))

        r = ''
        for item in items:
            if room.conf['sv_page'] == 'overview' and not item.conf['sv_item_type'] == room.conf['sv_overview']:
                continue
            if 'sv_img' in item.conf:
                img = item.conf['sv_img']
            else:
                img = ''
            if isinstance(item.conf['sv_widget'], list):
                self.logger.warning("room: sv_widget")
                for widget in item.conf['sv_widget']:
                    widgets += self.parse_tpl(widgetblocktemplate, [('{{ visu_name }}', str(item)), ('{{ visu_img }}', img), ('{{ visu_widget }}', widget), ('item.name', str(item)), ("'item", "'" + item.id())])
            else:
                widget = self.get_attribute('sv_widget', item)
                name1 = self.get_attribute('sv_name1', item)
                if name1 == '':
                    name1 = item

                blocksize = self.get_widgetblocksize(item)

                widget2 = self.get_attribute('sv_widget2', item)
                if widget2 == '':
                    widgets += self.parse_tpl(widgetblocktemplate, [('{{ visu_name }}', str(name1)), ('{{ blocksize }}', str(blocksize)), ('{{ visu_img }}', img), ('{{ visu_widget }}', widget), ('item.name', str(item)), ("'item", "'" + item.id())])
                else:
                    name2 = self.get_attribute('sv_name2', item)
                    widgets += self.parse_tpl(widgetblocktemplate2, [('{{ visu_name }}', str(name1)), ('{{ visu_name2 }}', str(name2)), ('{{ visu_img }}', img), ('{{ visu_widget }}', widget), ('{{ visu_widget2 }}', widget2), ('item.name', str(item)), ("'item", "'" + item.id())])

            if room.conf['sv_page'] == 'room':
                r = self.parse_tpl('room.html', [('{{ visu_name }}', str(room)), ('{{ visu_widgets }}', widgets), ('{{ visu_img }}', rimg), ('{{ visu_heading }}', heading)])
            elif room.conf['sv_page'] == 'category':
                r = self.parse_tpl('category_page.html', [('{{ visu_name }}', str(room)), ('{{ visu_widgets }}', widgets), ('{{ visu_img }}', rimg), ('{{ visu_heading }}', heading)])
            elif room.conf['sv_page'] == 'room_lite':
                r = self.parse_tpl('roomlite.html', [('{{ visu_name }}', str(room)), ('{{ visu_widgets }}', widgets), ('{{ visu_img }}', rimg), ('{{ visu_heading }}', heading)])
        return r


    def pages(self):
        if not self.remove_oldpages():
            return

        nav_lis = ''
        cat_lis = ''
        lite_lis = ''
                
        for item in self._sh.find_items('sv_page'):
            if item.conf['sv_page'] == 'seperator':
                nav_lis += self.parse_tpl('navi_sep.html', [('{{ name }}', str(item))])
                continue
            elif item.conf['sv_page'] == 'cat_seperator':
                cat_lis += self.parse_tpl('navi_sep.html', [('{{ name }}', str(item))])
                continue
            elif ((item.conf['sv_page'] == 'overview') or (item.conf['sv_page'] == 'cat_overview')) and (not 'sv_overview' in item.conf):
                self.logger.error("missing sv_overview for {0}".format(item.id()))
                continue

            r = self.room(item)

            img = self.get_attribute('sv_img', item)

            if 'sv_nav_aside' in item.conf:
                if isinstance(item.conf['sv_nav_aside'], list):
                    nav_aside = ', '.join(item.conf['sv_nav_aside'])
                else:
                    nav_aside = item.conf['sv_nav_aside']
            else:
                nav_aside = ''
            if 'sv_nav_aside2' in item.conf:
                if isinstance(item.conf['sv_nav_aside2'], list):
                    nav_aside2 = ', '.join(item.conf['sv_nav_aside2'])
                else:
                    nav_aside2 = item.conf['sv_nav_aside2']
            else:
                nav_aside2 = ''
            if (item.conf['sv_page'] == 'category') or (item.conf['sv_page'] == 'cat_overview'):
                cat_lis += self.parse_tpl('navi.html', [('{{ visu_page }}', item.id()), ('{{ visu_name }}', str(item)), ('{{ visu_img }}', img), ('{{ visu_aside }}', nav_aside), ('{{ visu_aside2 }}', nav_aside2), ('item.name', str(item)), ("'item", "'" + item.id())])
            elif item.conf['sv_page'] == 'room':
                nav_lis += self.parse_tpl('navi.html', [('{{ visu_page }}', item.id()), ('{{ visu_name }}', str(item)), ('{{ visu_img }}', img), ('{{ visu_aside }}', nav_aside), ('{{ visu_aside2 }}', nav_aside2), ('item.name', str(item)), ("'item", "'" + item.id())])
            elif item.conf['sv_page'] == 'room_lite':
                lite_lis += self.parse_tpl('navi.html', [('{{ visu_page }}', item.id()), ('{{ visu_name }}', str(item)), ('{{ visu_img }}', img), ('{{ visu_aside }}', nav_aside), ('{{ visu_aside2 }}', nav_aside2), ('item.name', str(item)), ("'item", "'" + item.id())])
            self.write_parseresult(item.id()+'.html', r)


        nav = self.parse_tpl('navigation.html', [('{{ visu_navis }}', nav_lis)])
        self.write_parseresult('room_nav.html', nav)

        nav = self.parse_tpl('navigation.html', [('{{ visu_navis }}', cat_lis)])
        self.write_parseresult('category_nav.html', nav)

        nav = self.parse_tpl('navigation.html', [('{{ visu_navis }}', lite_lis)])
        self.write_parseresult('roomlite_nav.html', nav)


        self.copy_tpl('rooms.html')
        self.copy_tpl('roomslite.html')
        self.copy_tpl('category.html')
        self.copy_tpl('index.html')
        

#########################################################################

    def parse_tpl(self, template, replace):
        try:
            with open(self.tpldir + '/' + template, 'r', encoding='utf-8') as f:
                tpl = f.read()
                tpl = tpl.lstrip('\ufeff')  # remove BOM
        except Exception as e:
            self.logger.error("Could not read template file '{0}': {1}".format(template, e))
            return ''
        for s, r in replace:
            tpl = tpl.replace(s, r)
        return tpl


    def write_parseresult(self, htmlfile, parseresult):
        try:
            with open(self.outdir + '/' + htmlfile, 'w') as f:
                f.write(parseresult)
        except Exception as e:
            self.logger.warning("Could not write to {0}/{1}: {2}".format(self.outdir, htmlfile, e))


    def copy_tpl(self, tplname, destname=''):
        if destname == '':
            destname = tplname
        try:
            shutil.copy(self.tpldir + '/' + tplname, self.outdir + '/' + destname)
        except Exception as e:
            self.logger.error("Could not copy {0} from {1} to {2}".format(tplname, tpldir, destdir))


#########################################################################

    def remove_oldpages(self):
        if not os.path.isdir(self.tmpdir):
            self.logger.warning("Could not find directory: {0}".format(self.tmpdir))
            return False
        # clear temp directory
        for dn in os.listdir(self.tmpdir):
            if len(dn) != 2:  # only delete Twig temp files
                continue
            dp = os.path.join(self.tmpdir, dn)
            try:
                if os.path.isdir(dp):
                    shutil.rmtree(dp)
            except Exception as e:
                self.logger.warning("Could not delete directory {0}: {1}".format(dp, e))
        # create output directory
        try:
            os.mkdir(self.outdir)
        except:
            pass
        # remove old dynamic files
        if not os.path.isdir(self.outdir):
            self.logger.warning("Could not find/create directory: {0}".format(self.outdir))
            return False
        for fn in os.listdir(self.outdir):
            fp = os.path.join(self.outdir, fn)
            try:
                if os.path.isfile(fp):
                    os.unlink(fp)
            except Exception as e:
                self.logger.warning("Could not delete file {0}: {1}".format(fp, e))
        return True

#########################################################################

    def copy_templates(self):
        # copy widgets from the sv_widget(s) subdir of a plugin
        srcdir = self.thisplgdir + '/tplNG'
        if not os.path.isdir(srcdir):
            self.logger.warning("copy_templates: Could not find source directory {0}".format(srcdir))
            return

        # create output directory
        try:
            os.mkdir(self.tpldir)
        except:
            pass
            
#        self.logger.warning("copy_templates: Copying templates from plugin-dir '{0}' to smartVISU-dir '{1}'".format(srcdir, self.tpldir))
        
        # Open file for twig import statements (for root.html)
        for fn in os.listdir(srcdir):
            if (self.overwrite_templates) or (not os.path.isfile(self.tpldir + '/' + fn) ):
                self.logger.info("copy_templates: Copying template '{0}' from plugin to smartVISU".format(fn))
                shutil.copy2( srcdir + '/' + fn, self.tpldir )
        return


#########################################################################
#       Widget Handling
#########################################################################


class SmartVisuInstallWidgets:

    def __init__(self, smarthome, smartvisu_dir=''):
        self.logger = logging.getLogger(__name__)
        self._sh = smarthome
        self.smartvisu_dir = smartvisu_dir

        self.logger.log(logging.WARNING, "Installing widgets into smartVISU")
        
        # sv directories
        self.shwdgdir = 'sh_widgets'
        self.outdir = self.smartvisu_dir + '/widgets/' + self.shwdgdir
        self.tmpdir = self.smartvisu_dir + '/temp'
        self.pgbdir = self.smartvisu_dir + '/pages/base'          # pages/base directory

        self.logger.info("install_widgets: Installing from '{0}' to '{1}'".format(smarthome.base_dir, smartvisu_dir))

        self.install_widgets(self._sh)


    def install_widgets(self, smarthome):
        if not self.remove_oldfiles():
            return
    
        # make a backup copy of root.html if it doesn't exist (for full integeration)
        if not os.path.isfile( self.pgbdir + '/root_master.html' ):
            self.logger.warning( "install_widgets: Creating a copy of root.html" )
            shutil.copy2( self.pgbdir + '/root.html', self.pgbdir + '/root_master.html' )

        # read the unmodified root.html (from root_master.html)
        f_root = open(self.pgbdir + '/root_master.html', "r")
        root_contents = f_root.readlines()
        f_root.close()
        self.logger.debug( "root_contents: {0}".format(root_contents) )

        # find insert points in original root.html
        iln_html = self.findinsertline( root_contents, '{% import "plot.html" as plot %}' )
        iln_js = self.findinsertline( root_contents, "{% if isfile('pages/'~config_pages~'/visu.js') %}" )
        iln_css = self.findinsertline( root_contents, "{% if isfile('pages/'~config_pages~'/visu.css') %}" )
    
        # copy widgets from plugin directories of configured plugins
        # read plungin.conf
        _conf = lib.config.parse(smarthome._plugin_conf)
        mypluginlist = []
        for plugin in _conf:
    #        self.logger.warning("install_widgets: Plugin class {0}, path {1}".format(_conf[plugin]['class_name'], _conf[plugin]['class_path']))
            plgdir = _conf[plugin]['class_path']
            if plgdir not in mypluginlist:
                # process each plugin only once
                mypluginlist.append( plgdir )
                self.copy_widgets( plgdir.replace('.', '/'), root_contents, iln_html, iln_js, iln_css )
        # write root.html with additions for widgets
        self.logger.info( "Adding import statements to root.html" )
        f_root = open(self.pgbdir + '/root.html', "w")
        root_contents = "".join(root_contents)
        f_root.write(root_contents)
        f_root.close()


#########################################################################

    def findinsertline(self, root_contents, searchstring ):
        # look for insert point in root.html: find and return line that contains the searchstring
        iln = ''
        for ln in root_contents:
            if ln.find( searchstring ) != -1:
                iln = ln
        if iln == '':
            self.logger.warning("findinsertline: No insert point for pattern {0}".format(searchstring))
        return( iln )
    

    def copy_widgets(self, plgdir, root_contents, iln_html, iln_js, iln_css):
        wdgdir = 'sv_widgets'
        # copy widgets from the sv_widget(s) subdir of a plugin
        srcdir = self._sh.base_dir + '/' + plgdir + '/' + wdgdir
        if not os.path.isdir(srcdir):
            self.logger.debug("copy_widgets: Could not find source directory {0} in {1}".format(wdgdir, plgdir))
            return
        self.logger.debug("copy_widgets: Copying widgets from plugin '{0}'".format(srcdir))

        # Open file for twig import statements (for root.html)
        for fn in os.listdir(srcdir):
            if (fn[-3:] != ".md"):
                self.logger.info("copy_widgets: Copying widget-file: {0}".format(fn))
                shutil.copy2( srcdir + '/' + fn, self.outdir )
                if (fn[0:7] == "widget_") and (fn[-5:] == ".html"):
                    self.logger.info("- Installing from '{0}': {1}".format(plgdir, '\t' + fn))
                    if iln_html != '':
                        self.create_htmlinclude(fn, fn[7:-5] , root_contents, iln_html)
                if (fn[0:7] == "widget_") and (fn[-3:] == ".js"):
                    if iln_js != '':
                        self.create_jsinclude(fn, fn[7:-3] , root_contents, iln_js)
                if (fn[0:7] == "widget_") and (fn[-4:] == ".css"):
                    if iln_css != '':
                        self.create_cssinclude(fn, fn[7:-4] , root_contents, iln_css)
        return
        

    def create_htmlinclude(self, filename, classname, root_contents, iln_html):
        insertln = root_contents.index(iln_html) +1
        # Insert widget statements to root_contents
        if insertln != 0:
            self.logger.debug( "create_htmlinclude: Inserting in root.html at line {0} after '{1}'".format(insertln, iln_html) )
            twig_statement = '\t{% import "' + self.shwdgdir + '/' + filename + '" as ' + classname + ' %}'
            root_contents.insert(insertln, twig_statement+'\n')


    def create_jsinclude(self, filename, classname, root_contents, iln_js):
        insertln = root_contents.index(iln_js)
        # Insert widget statements to root_contents
        if insertln > -1:
            self.logger.debug( "create_jsinclude: Inserting in root.html at line {0} before '{1}'".format(insertln, iln_js) )
            twig_statement1 = "\t{% if isfile('widgets/sh_widgets/" + filename + "') %}"
            twig_statement2 = '\t\t<script type="text/javascript" src="widgets/sh_widgets/widget_' + classname + '.js"></script>{% endif %}'
            self.logger.debug('create_jsinclude: {0}'.format(twig_statement1))
            self.logger.debug('create_jsinclude: {0}'.format(twig_statement2))
            root_contents.insert(insertln, twig_statement2+'\n')
            root_contents.insert(insertln, twig_statement1+'\n')


    def create_cssinclude(self, filename, classname, root_contents, iln_css):
        insertln = root_contents.index(iln_css)
        # Insert widget statements to root_contents
        if insertln > -1:
            self.logger.debug( "create_jsinclude: Inserting in root.html at line {0} before '{1}'".format(insertln, iln_css) )
            twig_statement1 = "\t{% if isfile('widgets/sh_widgets/" + filename + "') %}"
            twig_statement2 = '\t\t<link rel="stylesheet" type="text/css" href="widgets/sh_widgets/widget_' + classname + '.css" />{% endif %}'
            self.logger.debug('create_cssinclude: {0}'.format(twig_statement1))
            self.logger.debug('create_cssinclude: {0}'.format(twig_statement2))
            root_contents.insert(insertln, twig_statement2+'\n')
            root_contents.insert(insertln, twig_statement1+'\n')


    def remove_oldfiles(self):
        # clear temp directory
        if not os.path.isdir(self.tmpdir):
            self.logger.warning("Could not find temp directory: {0}".format(self.tmpdir))
            return False
        for fn in os.listdir(self.tmpdir):
            if len(fn) != 2:  # only delete Twig temp files
                continue
            fp = os.path.join(self.tmpdir, fn)
            try:
                if os.path.isdir(fp):
                    shutil.rmtree(fp)
            except Exception as e:
                self.logger.warning("Could not delete directory {0}: {1}".format(fp, e))
            
        # create destination directory for widgets
        self.logger.info("install_widgets: Creating  directory for widgets")
        try:
            os.mkdir(self.outdir)
        except:
            pass

        if not os.path.isdir(self.outdir):
            self.logger.warning("Could not find or create directory for sh widgets: {0}".format(self.outdir))
            return False

        # remove old dynamic widget files
        self.logger.info("install_widgets: Removing old dynamic widget files")
        for fn in os.listdir(self.outdir):
            fp = os.path.join(self.outdir, fn)
            try:
                if os.path.isfile(fp):
                    os.unlink(fp)
            except Exception as e:
                self.logger.warning("Could not delete file {0}: {1}".format(fp, e))

        return True

