import sys
from optparse import OptionParser

def main():
    print ("hello from rsensor.webapp.main")
    parser = OptionParser(usage="usage: %prog [options] filename",
                          version="%prog 1.0")
    parser.add_option("-x", "--xhtml",
                      action="store_true",
                      dest="xhtml_flag",
                      default=False,
                      help="create a XHTML template instead of HTM")
    (options, args) = parser.parse_args()
    print(options, args)
    
if __name__ == "__main__":
    sys.exit(main())
