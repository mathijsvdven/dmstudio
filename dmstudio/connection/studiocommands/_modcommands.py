import inspect
import pandas as pd

import dmstudio.connection.studiocommands.utils as utils
from dmstudio.filespec import StudioFileSpec
from dmstudio.connection.studiocommands.runner import Runner

# Modified Studio Commands

class Modcommand(Runner):
    def __init__(self):
        raise TypeError("This subclass contains functions accessed by the 'Connection' superclass and should not be instantiated separately.")

    def inpfil(self, csv, out_o, filespec=None, na_values = None):
        """
        Imports text file to Studio using the INPFIL command. If a Studio file specification
        is not provided as a StudioFileSpec, it is generated on the fly.
        For special fields, the file specification is amended as required.

        Takes:
        csv: the input csv filepath (can be >8 char)
        out_o: the output .dm file (may exceed 8 char)
        filespec: the StudioFileSpec object that describes the csv, optional generated on the fly if not provided
        na_values: the na_values argument passed to pandas.read_csv if filespec is not provided.

        Returns:
        No return value, file written to working directory
        """

        # These fields must be 8 characters
        CHAR8_FIELDS = ['VALUE_IN', 'VALUE_OU', 'NUMSAM_F', 
                        'SVOL_F', 'VAR_F', 'MINDIS_F']

        # These fields are always implicit
        IMPLICIT_FIELDS = ['XMORIG', 'YMORIG', 'ZMORIG', 'NX', 'NY', 'NZ',
                        'X0','Y0','Z0','ANGLE1','ANGLE2','ANGLE3',
                        'ROTAXIS1','ROTAXIS2','ROTAXIS3']   

        arguments = "INPFIL &OUT={} '{}' ".format(out_o, out_o)
        df = pd.read_csv(csv, na_values = na_values)

        if not isinstance(filespec, StudioFileSpec):
            # No/Invalid file specification, creating on the fly.
            filespec = StudioFileSpec.from_dataframe(df)

        filespec = filespec.spec.copy() # access data

        for i in range(filespec.shape[0]):

            if filespec['Field Name'].iloc[i] in CHAR8_FIELDS:
                filespec['Field Type'].iloc[i] = 'A'
                filespec['Length'].iloc[i] = 8

            if filespec['Field Name'].iloc[i].strip() in IMPLICIT_FIELDS:
                filespec['Field Type'].iloc[i] = 'N'
                filespec['Keep'].iloc[i] = 'N'
                filespec['Default'].iloc[i] = df[filespec['Field Name'].iloc[i]].iloc[0]

        f = lambda x: "'{}' ".format(x) if str(x) != 'nan' else str(x)
        filespec = filespec[['Field Name', 'Field Type', 'Length', 'Keep', 'Default']].applymap(f)
        filespec['arg'] = filespec.sum(axis=1)

        arg = ' '.join(filespec['arg'])
            
        arguments += arg

        arguments += "'!' 'Y' " + "'{}'".format(csv)

        self.run_command(arguments)

    def xrun(self, macro_i, macro_name_p):

        """
        XRUN
        ----
        This is auto-generated documentation. For more command information visit the Datamine help file.

        """

        command = "xrun " + macro_i + " " + str(macro_name_p)

        self.run_command(command)