#
# Created by ohinckel and merged May 9th, 2016
#
# maybe obsolete?
# 
import sys
import os
print(sys.path)
BASE = '/'.join(os.path.realpath(__file__).split('/')[:-2])
sys.path.insert(0, BASE)
print(sys.path)
#BASE = '/'.join(os.path.realpath(__file__).split('/')[:-3])
#sys.path.insert(0, BASE)
print(sys.path)
