#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2013 Marcus Popp                              marcus@popp.mx
#########################################################################
#  This file is part of SmartHomeNG.    https://github.com/smarthomeNG//
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

import logging
import os
import shutil

logger = logging.getLogger('')


def parse_tpl(template, replace):
    try:
        with open(template, 'r', encoding='utf-8') as f:
            tpl = f.read()
            tpl = tpl.lstrip('\ufeff')  # remove BOM
    except Exception as e:
        logger.error("Could not read template file '{0}': {1}".format(template, e))
        return ''
    for s, r in replace:
        tpl = tpl.replace(s, r)
    return tpl


def room(smarthome, room, tpldir):
    widgets = ''
    if 'sv_img' in room.conf:
        rimg = room.conf['sv_img']
    else:
        rimg = ''
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
        heading = parse_tpl(tpldir + '/heading.html', [('{{ visu_heading_right }}', heading_right), ('{{ visu_heading_center }}', heading_center), ('{{ visu_heading_left }}', heading_left)])
    else:
        heading = ''
    if 'sv_widget' in room.conf:
        items = [room]
    else:
        items = []
    if room.conf['sv_page'] == 'room':
        items.extend(smarthome.find_children(room, 'sv_widget'))
    elif room.conf['sv_page'] == 'category':							# MSinn
        items.extend(smarthome.find_children(room, 'sv_widget'))		# MSinn
    elif room.conf['sv_page'] == 'overview':
        items.extend(smarthome.find_items('sv_item_type'))
    for item in items:
        if room.conf['sv_page'] == 'overview' and not item.conf['sv_item_type'] == room.conf['sv_overview']:
            continue
        if 'sv_img' in item.conf:
            img = item.conf['sv_img']
        else:
            img = ''
        if isinstance(item.conf['sv_widget'], list):
            for widget in item.conf['sv_widget']:
                widgets += parse_tpl(tpldir + '/widget.html', [('{{ visu_name }}', str(item)), ('{{ visu_img }}', img), ('{{ visu_widget }}', widget), ('item.name', str(item)), ("'item", "'" + item.id())])
        else:
            widget = item.conf['sv_widget']
            widgets += parse_tpl(tpldir + '/widget.html', [('{{ visu_name }}', str(item)), ('{{ visu_img }}', img), ('{{ visu_widget }}', widget), ('item.name', str(item)), ("'item", "'" + item.id())])
    return parse_tpl(tpldir + '/room.html', [('{{ visu_name }}', str(room)), ('{{ visu_widgets }}', widgets), ('{{ visu_img }}', rimg), ('{{ visu_heading }}', heading)])


def pages(smarthome, directory):
    nav_lis = ''
    outdir = directory + '/pages/smarthome'
    tpldir = directory + '/pages/base/tpl'
    tmpdir = directory + '/temp'
    # clear temp directory
    if not os.path.isdir(tmpdir):
        logger.warning("Could not find directory: {0}".format(tmpdir))
        return
    for dn in os.listdir(tmpdir):
        if len(dn) != 2:  # only delete Twig temp files
            continue
        dp = os.path.join(tmpdir, dn)
        try:
            if os.path.isdir(dp):
                shutil.rmtree(dp)
        except Exception as e:
            logger.warning("Could not delete directory {0}: {1}".format(dp, e))
    # create output directory
    try:
        os.mkdir(outdir)
    except:
        pass
    # remove old dynamic files
    if not os.path.isdir(outdir):
        logger.warning("Could not find/create directory: {0}".format(outdir))
        return
    for fn in os.listdir(outdir):
        fp = os.path.join(outdir, fn)
        try:
            if os.path.isfile(fp):
                os.unlink(fp)
        except Exception as e:
            logger.warning("Could not delete file {0}: {1}".format(fp, e))
    for item in smarthome.find_items('sv_page'):
        if item.conf['sv_page'] == 'seperator':
            nav_lis += parse_tpl(tpldir + '/navi_sep.html', [('{{ name }}', str(item))])
            continue
        if item.conf['sv_page'] == 'overview' and not 'sv_overview' in item.conf:
            logger.error("missing sv_overview for {0}".format(item.id()))
            continue
        r = room(smarthome, item, tpldir)
        if 'sv_img' in item.conf:
            img = item.conf['sv_img']
        else:
            img = ''
        if 'sv_nav_aside' in item.conf:
            if isinstance(item.conf['sv_nav_aside'], list):
                nav_aside = ', '.join(item.conf['sv_nav_aside'])
            else:
                nav_aside = item.conf['sv_nav_aside']
        else:
            nav_aside = ''
        nav_lis += parse_tpl(tpldir + '/navi.html', [('{{ visu_page }}', item.id()), ('{{ visu_name }}', str(item)), ('{{ visu_img }}', img), ('{{ visu_aside }}', nav_aside), ('item.name', str(item)), ("'item", "'" + item.id())])
        try:
            with open("{0}/{1}.html".format(outdir, item.id()), 'w') as f:
                f.write(r)
        except Exception as e:
            logger.warning("Could not write to {0}/{1}.html: {}".format(outdir, item.id(), e))
    nav = parse_tpl(tpldir + '/navigation.html', [('{{ visu_navis }}', nav_lis)])
    try:
        with open(outdir + '/navigation.html', 'w') as f:
            f.write(nav)
    except Exception as e:
        logger.warning("Could not write to {0}/navigation.html".format(outdir))
    shutil.copy(tpldir + '/rooms.html', outdir + '/')
    shutil.copy(tpldir + '/index.html', outdir + '/')
