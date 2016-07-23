#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2012-2013 Marcus Popp                         marcus@popp.mx
#########################################################################
#  This file is part of SmartHome.py.    http://mknx.github.io/smarthome/
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

logger = logging.getLogger('')


def return_html(smarthome, item):
    html = ''
    if 'visu' in item.conf:
        visu = item.conf['visu']
        dom = item.id().replace('.', '_')
        if visu in ['text', 'textarea', 'toggle', 'checkbox', 'radio', 'select', 'slider']:  # regular form elements
            html += '<div data-role="fieldcontain">\n'.format(dom)
            if visu == 'text':
                html += '    <label for="{0}">{1}</label>\n'.format(dom, item)
                html += '    <input id="{0}" data-sh="{1}" type="text" />\n'.format(dom, item.id())
            elif visu == 'textarea':
                html += '    <label for="{0}">{1}</label>\n'.format(dom, item)
                html += '    <textarea id="{0}" data-sh="{1}" type="checkbox"></textarea>\n'.format(dom, item.id())
            elif visu == 'toggle':
                html += '    <label for="{0}">{1}</label>\n'.format(dom, item)
                if 'visu_opt' in item.conf:
                    opt = item.conf['visu_opt']
                else:
                    opt = ['Off', 'On']
                html += '    <select id="{0}" data-sh="{1}" data-role="slider"><option value="off">{2}</option><option value="on">{3}</option></select>\n'.format(dom, item.id(), opt[0], opt[1])
            elif visu == 'checkbox':
                html += '    <label for="{0}">{1}</label>\n'.format(dom, item)
                html += '    <input id="{0}" data-sh="{1}" type="checkbox" />\n'.format(dom, item.id())
            elif visu == 'slider':
                html += '    <label for="{0}">{1}</label>\n'.format(dom, item)
                if 'visu_opt' in item.conf:
                    opt = item.conf['visu_opt']
                else:
                    opt = [0, 100, 5]
                html += '    <input id="{0}" data-sh="{1}" type="range" min="{2}" max="{3}" step="{4}" />\n'.format(dom, item.id(), opt[0], opt[1], opt[2])
            elif visu == 'select':
                html += '<fieldset data-role="controlgroup">\n'
                if 'visu_opt' in item.conf:
                    opt = item.conf['visu_opt']
                else:
                    opt = ['Please specify the "visu_opt" attribute']
                html += '    <legend>{0}</legend>\n'.format(item)
                html += '    <select id="{0}" data-sh="{1}">\n'.format(dom, item.id())
                for value in opt:
                    html += '        <option value="{0}">{0}</option>\n'.format(value)
                html += '    </select>\n'
                html += '</fieldset>\n'
            elif visu == 'radio':
                html += '<fieldset data-role="controlgroup">\n'
                i = 0
                if 'visu_opt' in item.conf:
                    opt = item.conf['visu_opt']
                else:
                    opt = ['Please specify the "visu_opt" attribute']
                html += '    <legend>{0}</legend>\n'.format(item)
                for value in opt:
                    i += 1
                    html += '    <label for="{0}{1}">{2}</label>\n'.format(dom, i, value)
                    html += '    <input id="{0}{1}" name="{0}" data-sh="{2}" value="{3}" type="radio" />\n'.format(dom, i, item.id(), value)
                html += '</fieldset>\n'
            html += '</div>\n'
        elif visu in ['div', 'span', 'img', 'list']:  # passive elements
            if 'unit' in item.conf:
                unit = ' data-unit="{0}"'.format(item.conf['unit'])
            else:
                unit = ''
            if visu == 'div':
                html += '<div>{0}: <span data-sh="{1}"{2}></span></div>\n'.format(item, item.id(), unit)
            elif visu == 'span':
                html += '<div>{0}: <span data-sh="{1}"{2}></span></div>\n'.format(item, item.id(), unit)
            elif visu == 'img':
                html += '<div>{0}: <img data-sh="{1}" src="{2}" /></div>\n'.format(item, item.id(), item())
            elif visu == 'list':
                html += '<h2>{0}</h2><ul data-sh="{1}" data-filter="true" data-role="listview" data-inset="true"></ul>\n'.format(item, item.id())
        elif visu in ['switch', 'push', 'dpt3']:  # active elements
            if visu == 'switch':
                html += '<div>{0}: <img data-sh="{1}" src="/img/t.png" class="switch" /></div>\n'.format(item, item.id())
            elif visu == 'push':
                if 'visu_opt' not in item.conf:
                    logger.warning('No viso_opt img specified for push button {0}'.format(item.id()))
                    return
                if 'knx_dpt' in item.conf:
                    if item.conf['knx_dpt'] == '3':
                        html += '<div>{0}: <img data-sh="{1}" src="{2}" class="push" data-cycle="500" data-arr="0" />\n'.format(item, item.id(), item.conf['visu_opt'][0])
                        html += '<img data-sh="{1}" src="{2}" class="push" data-cycle="500" data-arr="1" /></div>\n'.format(item, item.id(), item.conf['visu_opt'][1])
                    else:
                        html += '<div>{0}: <img data-sh="{1}" src="{2}" class="push" /></div>\n'.format(item, item.id(), item.conf['visu_opt'])
                else:
                    html += '<div>{0}: <img data-sh="{1}" src="{2}" class="push" /></div>\n'.format(item, item.id(), item.conf['visu_opt'])
        elif visu == 'rrd':
            if 'visu_opt' in item.conf:
                if isinstance(item.conf['visu_opt'], list):
                    rrd = []
                    for path in item.conf['visu_opt']:
                        vitem = smarthome.return_item(path)
                        if vitem is not None:
                            if 'rrd' in vitem.conf:
                                rrd.append("{0}='label': '{1}'".format(vitem.id(), vitem))
                    rrd = "|".join(rrd)
            else:
                rrd = "{0}='label': '{1}'".format(item.id(), item)
            html += '<div data-rrd="{0}" data-frame="1d" style="margin:20px;width:device-width;height:300px"></div>\n'.format(rrd)
    return html


def return_tree(smarthome, item):
    html = ''
    html += return_html(smarthome, item)
    for child in item:
        html += return_tree(smarthome, child)
    return html
