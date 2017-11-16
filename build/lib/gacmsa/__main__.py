import argparse,csv,datetime,logging,os, sys,  gacmsa, loggingformatter
VERSION=0
MIN_VERSION=0
FIX_VERSION=1
PROGRAM_NAME="gacmsa.py"
PROGRAM_NAME_PRETTY="GetAllelicCountFromMultipleSequenceAlignment(GAC-MSA)"
AUTHOR="Merly Escalona <merlyescalona@uvigo.es>"
INSTITUTION="University of Vigo, Spain."
LOG_LEVEL_CHOICES=["DEBUG","INFO","WARNING","ERROR"]
LINE="--------------------------------------------------------------------------------"
################################################################################
ch = logging.StreamHandler()
loggerFormatter=loggingformatter.MELoggingFormatter(\
    fmt="%(asctime)s - %(levelname)s:\t%(message)s",\
    datefmt="%d/%m/%Y %I:%M:%S %p")
ch.setFormatter(loggerFormatter)
ch.setLevel(logging.NOTSET)
APPLOGGER=logging.getLogger("gac-msa")
APPLOGGER.addHandler(ch)

################################################################################
def createLogFile():
    formatString=""
    if platform.system()=="Darwin":
        formatString="%(asctime)s - %(levelname)s (%(module)s:%(lineno)d):\t%(message)s"
    else:
        formatString="%(asctime)s - %(levelname)s (%(module)s|%(funcName)s:%(lineno)d):\t%(message)s"
    fh=logging.FileHandler(\
        "{0}/{2}.{1:%Y}{1:%m}{1:%d}-{1:%H}:{1:%M}:{1:%S}.log".format(\
            os.getcwd(),\
            datetime.datetime.now(),\
            PROGRAM_NAME[0:-3].upper()\
            )\
        )
    fh.setLevel(logging.DEBUG)
    formatter=logging.Formatter(formatString)
    fh.setFormatter(formatter)
    APPLOGGER.addHandler(fh)
################################################################################
def handlingCmdArguments():
    parser = argparse.ArgumentParser(\
        prog="{0}".format(PROGRAM_NAME),\
        formatter_class=argparse.RawDescriptionHelpFormatter,\
        description='''
Get Allelic Count From Multiple Sequence Alignment file(GAC-MSA)
================================================================================
Assumes the input file is a Multiple Sequence Alignment file, meaning, all
sequences have the same length.
        '''
        ,\
        epilog="Version {0}.{1}.{2} (Still under development)".format(VERSION,MIN_VERSION,FIX_VERSION),\
        add_help=False
        )
    requiredGroup= parser.add_argument_group('Required arguments')
    requiredGroup.add_argument('-i','--input',metavar='<filepath>',
        type=str,required=True,\
        help='Multiple-alignment sequence file (MSA).')
    requiredGroup.add_argument('-o','--output',metavar='<filepath>',
        type=str,required=True,\
        help='Output file')
    optionalGroup= parser.add_argument_group('Optional arguments')
    optionalGroup.add_argument('-l','--log',metavar='<log_level>', type=str,\
        choices=LOG_LEVEL_CHOICES, default="INFO",\
        help='Specified level of log that will be shown through the standard output. Entire log will be stored in a separate file. Values:{0}. Default: {1}. '.format(LOG_LEVEL_CHOICES,LOG_LEVEL_CHOICES[1]))
    informationGroup=parser.add_argument_group('Information arguments')
    informationGroup.add_argument('-v', '--version',\
        action='version',\
        version='{0}: Version {1}.{2}.{3}'.format(PROGRAM_NAME_PRETTY,VERSION,MIN_VERSION,FIX_VERSION),\
        help="Show program's version number and exit")
    informationGroup.add_argument('-h', '--help',\
        action='store_true',\
        help="Show this help message and exit")
    try:
        tmpArgs = parser.parse_args()
    except:
        sys.stdout.write("\n\033[1m{}\033[0m\n".format(LINE))
        APPLOGGER.error("Something happened while parsing the arguments.")
        APPLOGGER.error("Please verify. Exiting.\n{}".format(LINE))
        parser.print_help()
        sys.exit(-1)
    return tmpArgs

def main():
    try:
        cmdArgs = handlingCmdArguments()
        APPLOGGER.setLevel(cmdArgs.log.upper())
        APPLOGGER.debug("Args. introduced: {}".format(cmdArgs))
        prog = gacmsa.GACMSA(cmdArgs)
        prog.run()
    except gacmsa.GACMSAException as ex:
        if ex.expression:
            APPLOGGER.info("GACMSA finished properly.")
            APPLOGGER.info("Elapsed time (ETA):\t{0}".format(ex.time))
            APPLOGGER.info("Ending at:\t{0}".format(datetime.datetime.now().strftime("%a, %b %d %Y. %I:%M:%S %p")))
            sys.exit()
        else:
            APPLOGGER.error(ex.message)
            APPLOGGER.error("Elapsed time (ETA):\t{0}".format(ex.time))
            APPLOGGER.error("Ending at:\t{0}".format(datetime.datetime.now().strftime("%a, %b %d %Y. %I:%M:%S %p")))
            sys.exit(-1)
    except KeyboardInterrupt:
        APPLOGGER.error("{0}{1}\nProgram has been interrupted.{2}\nPlease run again for the expected outcome.\n{3}\n".format("\033[91m","\033[1m","\033[0m",LINE))
        sys.exit(-1)

if __name__=="__main__":
    main()
