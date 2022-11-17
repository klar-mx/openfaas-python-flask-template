import sys
from os.path import dirname
sys.path.append(dirname(__file__))
sys.path.append(dirname(__file__)/'function')

from function import handler

if __name__ == '__main__':
    handler.main()
