import logging
from pathlib import Path
import glob
import numpy as np

from dmstudio.connection.errors import COM_Error, ApplicationError
cwd = Path().absolute()

logger = logging.getLogger(__name__)

class Runner:
    """
    Base class that supports inheritance of the run_command method called by the Command and Modcommand superclasses through.
    """
    def __init__(self):
        """
        Base class to support inheritance. Do not instantiate this class.
        
        """
        self.oScript = None
        raise TypeError("This subclass contains functions accessed by the 'Connection' superclass and should not be instantiated separately.")    

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
                raise COM_Error("An issue occurred parsing this command to Studio, please inspect the log at {}\dmstudio_log.txt and validate the command".format(str(cwd)))

        # update the dmdir.py file containing list of .dm files in current directory
        self.make_dmdir()


    def make_dmdir(self):
        
        """
        make_dmdir
        -----------
        
        Internal function which creates a local '_init_.py' and python file 'dmdir.py' which contains a list of dm files in the local 
        Datamine project directory passed to variables with name of file without dm file extension and leading and trailing underscores. 
        
        The purpose of the local python file is to facilitate importing the filenames as variables which can be referenced directly in the
        scripts. 
        
        Usage:
        ------
        
        >>>import dmdir as f
        >>>print f._someDmFile_
        someDmFile
        
        The imported variables can be used as inputs in scripts:
        
        >>>import dmstudio as dm
        >>>con = dm.Connect()
        >>>con.copy(in_i=f._someDmFile_, out_o='someDmFile2')
        
        """

        dmdir_init = open('__init__.py', 'w')
        dmdir_init.write("'''\n")
        dmdir_init.write("Initialization file to enable importing of dmdir.py\n")
        dmdir_init.write("'''\n")
        dmdir_init.close()

        dmdir_f = open('dmdir.py', 'w')
        dmdir_f.write("'''\n")
        dmdir_f.write("List of datamine files in active datamine project directory\n")
        dmdir_f.write("\n")
        dmdir_f.write("This file will populate after initializing the script for the first time and will update after each command.\n")
        dmdir_f.write("\n")
        dmdir_f.write("Usage:\n")
        dmdir_f.write("------\n")
        dmdir_f.write("\n")
        dmdir_f.write(">>import dmdir as f\n")
        dmdir_f.write(">>print f._someDmFile_\n")
        dmdir_f.write("someDmFile\n")
        dmdir_f.write("\n")
        dmdir_f.write("'''\n")
        dmdir_f.write("\n")

        for infile in glob.glob("*.dm"):
            outname = np.str.split(infile, '.')[0]
            dmdir_f.write('_'+ outname + "_='" + outname + "'\n")

        dmdir_f.close()
