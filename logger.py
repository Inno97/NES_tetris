############################################################
#    logger
############################################################

# Contains the custom logger object to be used.

############################################################
#    Imports
############################################################

import logging, sys, os

############################################################
#    Functions
############################################################

def setup_custom_logger():
    """Setups the custom logger to be used globally.

    Args:
        name (string): The name of the logger.
    Returns:
        The logger to be used in the script.
    """
    filename = os.getcwd() + '\\output.log' if 'win' in sys.platform else os.getcwd() + '/output.log'
    logging.basicConfig(filename=filename,
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.INFO)
    log = logging.getLogger()
    log.setLevel(logging.INFO)

    stdout_handler = logging.StreamHandler(sys.stdout)
    log.addHandler(stdout_handler)
    return log

def get_logger():
    """Returns the logger to be used.

    Returns:
        The logger to be used in the script.
    """
    log = setup_custom_logger() if not logging.getLogger('root').hasHandlers() \
        else logging.getLogger('root')

    return log
