import inspect
import logging
import os
import win32com.client
import glob
import numpy as np
from pathlib import Path

from dmstudio.connection.errors import COM_Error, ApplicationError

cwd = Path().absolute()
logfile = cwd/"dmstudio_log.txt"
logging.basicConfig(filename=logfile, level=logging.DEBUG, 
                    format='[%(asctime)s] %(name)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# constant to avoid redundant COM connections which slows down processing
OSCRIPTCON = None

class Connection(object):

    def __init__(self, version=None, dry_run = False):

        """
        commands.__init__
        ------------------


        Commands initialization. After the commands class is initialized  for the first time the object will
         be set to the datamine studio object. This property will avoid redundant initializaiton

        Parameters:
        -----------

        version: str
            optional datamine studio versions ('Studio3', 'StudioRM', 'StudioEM', 'StudioRMPro') If no version given, 
            the initializtion will try different versions starting with StudioRM then Studio3, StudioEM, and StudioRMPro.

        """

        self.oScript = OSCRIPTCON
        self.version = version
        self.dry_run = dry_run

        if self.oScript is None:
            self.oScript = Connect(self.version)

    def run_command(self, command):

        """
        run_command
        -----------

        Uses the studio Parsecommand method to execute a datamine script.

        Parameters:
        -----------

        command: str
            Datamine command string to be parsed
        """

        if self.dry_run == True:
            print(command)
        else:
            logger.info("Running command: {}".format(command))
            try:
                self.oScript.ParseCommand(command)
            except Exception as e:
                logger.error("An issue occurred parsing this command to Studio, please inspect the parsed arguments and validate against the help files, error message: \n{}".format(e))
                raise COM_Error("An issue occurred parsing this command to Studio, please inspect the log at {}\dmstudio_log.txt and validate the command".format(logfile))

        # update the dmdir.py file containing list of .dm files in current directory

        # dmstudio.initialize._make_dmdir()


    def parse_infields_list(self, prefix, fields, maxfields, vtype='*'):

        """
        parse_infields_list
        -------------------

        Intenal function for parsing a list of *fields to a string for use in studio commands e.g. *F1, *F2, etc..

        Parameters
        ----------

        prefix: str
            starting letter or letters for the field e.g. 'F' for *F1.
        fields: list of str
            list of input fields
        maxfields: int
            maximum number of fields permitted by datamine command
        vtype: str
            variable type, input file or field. For input file vtype="&" for field vtype="*"

        Returns:
        --------

        field_string: str
            concatenated string formated for input in datamine commands

        """

        if maxfields < len(fields):
            raise ValueError("More fields have been selected than allowed by Datamine command")

        field_string = ""
        for i, field in enumerate(fields):
            field_string += " " + vtype + prefix + str(i + 1) + "=" + field + " "

        return field_string;


    def xrun(self, macro_i="required", macro_name_p="required"):

        """
        XRUN
        ----
        This is auto-generated documentation. For more command information visit the Datamine help file.

        """

        if macro_i == "required":
            raise ValueError("macro_i is required.")

        if macro_name_p == "required":
            raise ValueError("macro_name is required.")

        command = "xrun " + macro_i + " " + str(macro_name_p)

        self.run_command(command)

    # Import Initilalize Commands
    # from .dmstudio.connection._initialize import *

    # Import Studio Commands
    from .studiocommands._commands import accmlt

    # Import Modified Studio Commands
    from .studiocommands._modcommands import inpfil

def Connect(version):
    '''
    studio
    ------

    Datamine Studio Initialization. Versions Studio3, StudioRM, StudioEM and StudioRMPro supported

    Parameters:
    -----------

    version: str    
        Datamine studio version, choose from: StudioRM, Studio3, StudioEM, StudioRMPro

    Tries to connect to studio RM first.
    Need a better way to do this.
    '''

    oScript = None
    versions = ['StudioRM', 'StudioRMPro', 'StudioEM', 'Studio3']

    # _make_dmdir()

    if version in versions:
        progid = "Datamine.{}.Application".format(version)
        try:
            oScript = _scriptinit(progid)
        except:
            raise ConnectionError("COM Connection to {} could not be established.".format(progid))

    elif version is not None:
        raise LicenseError('{} is not a valid Studio version.'.format(version))

    elif version is None:
        # no version given, will try to find a valid version
        for v in ['StudioRM', 'StudioRMPro', 'StudioEM', 'Studio3']:
            try:
                oScript = win32com.client.Dispatch("Datamine.{}.Application".format(v))
            except:
                continue

    # Find local projects
    projects_in_cwd = [f for f in os.listdir(cwd) if f.endswith('rmproj')]

    try:
        v = oScript.Visible
        print(v)
    except: 
        raise ApplicationError("Connection could not be established.")

    if not oScript.Visible:
        print('Connected to Studio. Application is closed.')
        logger.warning('Connected to Studio. Application is closed.')

    elif oScript.Visible and oScript.ActiveProject is None:
        logger.warning('Connected to Studio. No active project found. Please activate a project')
        print('Connected to Studio. No active project found. Please open a project file')

        if len(projects_in_cwd) < 1:
            print('No Studio projects found in current working directory. Please run dmstudio in your working directory.')

        else:
            print('Projects found in working directory: {}'.format(', '.join(projects_in_cwd)))

    else:
        logger.info('Connected to Datamine: {}'.format(oScript.Name))

    return oScript