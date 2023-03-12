import logging
import os
import win32com.client
from pathlib import Path

from dmstudio.connection.errors import ApplicationError
from dmstudio.connection.studiocommands._commands import Command
from dmstudio.connection.studiocommands._modcommands import Modcommand

cwd = Path().absolute()
logger = logging.getLogger(__name__)

# constant to avoid redundant COM connections which slows down processing
OSCRIPTCON = None

class Connection(Command, Modcommand):

    """
    Superclass that instantiates the Datamine connection. This class inherits from the command and modcommand classes, which
    inherit from the Runner class that contains the COM logic.
    """

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
            self.oScript = self.Connect(self.version)

    def Connect(self, version):
        """
        Connect to Studio Application. Versions Studio3, StudioRM, StudioEM and StudioRMPro supported

        Takes:
        version: str, Datamine studio version, choose from: StudioRM, Studio3, StudioEM, StudioRMPro

        Returns:
        self.oScript: the COM application handle

        usage:

        >>> import dmstudio as dm
        >>> con = dm.Connect()
        >>> con._someDMcommand_

        """

        oScript = None
        versions = ['StudioRM', 'StudioRMPro', 'StudioEM', 'Studio3']

        self.make_dmdir()

        if version in versions:
            progid = "Datamine.{}.Application".format(version)
            try:
                oScript = win32com.client.Dispatch(progid)
            except:
                raise ConnectionError("COM Connection to {} could not be established.".format(progid))

        elif version is not None:
            raise ApplicationError('{} is not a valid Studio version.'.format(version))

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