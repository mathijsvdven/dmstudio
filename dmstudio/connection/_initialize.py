import win32com.client
import glob
import numpy as np
import logging
import os
from pathlib import Path
from dmstudio.errors import LicenseError

cwd = Path().absolute()
logging.basicConfig(filename=cwd/"dmstudio_log.txt", level=logging.DEBUG, 
                    format='[%(asctime)s] %(name)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# def _scriptinit(dm_object):
#     '''
#     _scriptinit
#     -----------

#     Initialize the Studio COM object. Internal function.

#     Parameters:
#     -----------

#     studio_object: str
#         Datamine studio COM object to initialize

#     Returns:
#     --------

#     ActiveX connection
#     '''

#     return win32com.client.Dispatch(dm_object);

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

    _make_dmdir()

    if version is not None:
        try:
            oScript = _scriptinit("Datamine.{}.Application".format(version))
        except:
            raise LicenseError('{} is not a valid Studio version.'.format(version))

    elif version is None:
        # no version given, will try to find a valid version
        for v in ['StudioRM', 'StudioRMPro', 'StudioEM', 'Studio3']:
            try:
                oScript = win32com.client.Dispatch("Datamine.{}.Application".format(v))
            except:
                continue

            if oScript is None:
                raise LicenseError("Could not find a valid Studio installation. Compatible versions are StudioRM, StudioRMPro, StudioEM and Studio3.")

    # Find local projects
    projects_in_cwd = [f for f in os.listdir(cwd) if f.endswith('rmproj')]

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

# def dmFile():

#     print("here")
    # assert oDmFile = _scriptinit("DmFile.DmTableADO"), "Could not initialize dmTableADO"


# def _make_dmdir():
    
#     '''
#     _make_dmdir
#     -----------
    
#     Internal function which creates a local ``_init_.py`` and python file ``dmdir.py`` which contains a list of dm files in the local 
#     Datamine project directory passed to variables with name of file without dm file extension and leading and trailing underscores. 
    
#     The purpose of the local python file is to facilitate importing the filenames as variables which can be referenced directly in the
#     scripts. 
    
#     Usage:
#     ------
    
#     >>>import dmdir as f
#     >>>print f._someDmFile_
#     someDmFile
    
#     The imported variables can be used as inputs in scripts:
    
#     >>>from dmstudio import dmcommands
#     >>> dmc = dmcommands.init()
#     >>> dmc.copy(in_i=f._someDmFile_, out_o='someDmFile2')
    
#     '''

#     dmdir_init = open('__init__.py', 'w')
#     dmdir_init.write("'''\n")
#     dmdir_init.write("Initialization file to enable importing of dmdir.py\n")
#     dmdir_init.write("'''\n")
#     dmdir_init.close()

#     dmdir_f = open('dmdir.py', 'w')
#     dmdir_f.write("'''\n")
#     dmdir_f.write("List of datamine files in active datamine project directory\n")
#     dmdir_f.write("\n")
#     dmdir_f.write("This file will populate after initializing the script for the first time and will update after each command.\n")
#     dmdir_f.write("\n")
#     dmdir_f.write("Usage:\n")
#     dmdir_f.write("------\n")
#     dmdir_f.write("\n")
#     dmdir_f.write(">>import dmdir as f\n")
#     dmdir_f.write(">>print f._someDmFile_\n")
#     dmdir_f.write("someDmFile\n")
#     dmdir_f.write("\n")
#     dmdir_f.write("'''\n")
#     dmdir_f.write("\n")

#     for infile in glob.glob("*.dm"):
#         outname = np.str.split(infile, '.')[0]
#         dmdir_f.write('_'+ outname + "_='" + outname + "'\n")

#     dmdir_f.close()



