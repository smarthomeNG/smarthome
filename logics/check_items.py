#!/usr/bin/env python3
# check_items.py
"""
given following items within a yaml:


MyItem:
  MyChildItem:
    type: num
    initial_value: 12
    MyGrandchildItem:
      type: str
      initial_value: "foo"

Within a logic it is possible to set the value of MyChildItem to 42 with 
``sh.MyItem.MyChildItem(42)`` and retrieve the Items value with 
``value = sh.MyItem.MyChildItem()``

Often beginners forget the parentheses and instead write 
``sh.MyItem.MyChildItem = 42`` when they really intend to assign the value ``42``
to the item or write ``value = sh.MyItem.MyChildItem`` when they really want to 
retrieve the item's value.

But using ``sh.MyItem.MyChildItem = 42`` destroys the structure here and makes 
it impossible to retrieve the value of the child 
``MyItem.MyChildItem.MyGrandchildItem``
Alike, an instruction as ``value = sh.MyItem.MyChildItem`` will not assign the 
value of ``sh.MyItem.MyChildItem`` but assign a reference to the item object 
``sh.MyItem.MyChildItem``

It is not possible with Python to intercept an assignment to a variable or an 
objects' attribute. The only thing one can do is search all items for a 
mismatching item type.

This logic checks all items returned by SmartHomeNG, and if it encounters one
which seems to be damaged like described before, it attempts to repair the
broken assignment.

"""
from lib.item import Items


def repair_item(sh, item):
    path = item.property.path
    path_elems = path.split('.')
    ref = sh

    # traverse through object structure sh.path1.path2...
    try:
        for path_part in path_elems[:-1]:
            ref = getattr(ref, path_part)

        setattr(ref, path_elems[-1], item)
        logger.info(f'Item reference repaired for {path}')
        return True
    except NameError:
        logger.error(f'Error: item traversal for {path} failed at part {path_part}. Item list not sorted?')

    return False


def get_item_type(sh, path):
    expr = f'type(sh.{path})'
    return str(eval(expr))


def check_item(sh, path):
    global get_item_type

    return get_item_type(sh, path) == "<class 'lib.item.item.Item'>"


# to get access to the object instance:
items = Items.get_instance()

# to access a method (eg. to get the list of Items):
# allitems = items.return_items()
problems_found = 0
problems_fixed = 0

for one in items.return_items(ordered=True):
    # get the items full path
    path = one.id()
    try:
        if not check_item(sh, path):
            logger.error(f"Error: item {path} has type {get_item_type(sh, path)} but should be an Item Object")
            problems_found += 1
            if repair_item(sh, one):
                if check_item(sh, path):
                    problems_fixed += 1
    except ValueError as e:
        logger.error(f'Error {e} while processing item {path}, parent defective? Items not sorted?')
        
if problems_found:
    logger.error(f"{problems_found} problematic item assignment{'' if problems_found == 1 else 's'} found, {problems_fixed} item assignment{'' if problems_fixed == 1 else 's'} fixed")
else:
    logger.notice("no problems found")
