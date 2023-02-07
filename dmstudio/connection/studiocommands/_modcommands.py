import dmstudio.connection.studiocommands.utils as utils
import inspect
from dmstudio.filespec import StudioFileSpec

# Modified Studio Commands

def inpfil(csv, out_o, definition=None):
    """
    Imports text file to Studio using the INPFIL command. If a Studio file definition
    is not provided as a StudioFileSpec, it is generated on the fly.
    For special fields, the file definition is amended as required.
    """

    # These fields must be 8 characters
    CHAR8_FIELDS = ['VALUE_IN', 'VALUE_OU', 'NUMSAM_F', 
                    'SVOL_F', 'VAR_F', 'MINDIS_F']

    # These fields are always implicit
    IMPLICIT_FIELDS = ['XMORIG', 'YMORIG', 'ZMORIG', 'NX', 'NY', 'NZ',
                       'X0','Y0','Z0','ANGLE1','ANGLE2','ANGLE3',
                       'ROTAXIS1','ROTAXIS2','ROTAXIS3']   

    arguments = " 'csvfile' "
    df = pd.read_csv(csv)

    if not isinstance(definition, StudioFileSpec):
        # Invalid filedefinition, creating on the fly.
        definition = StudioFileSpec.from_dataframe(df)

    for i in range(definition.shape[0]):

        if definition['Field Name'].iloc[i] in CHAR8_FIELDS:
            definition['Field Type'].iloc[i] = 'A'
            definition['Length'].iloc[i] = 8

        if definition['Field Name'].iloc[i].strip() in IMPLICIT_FIELDS:
            definition['Field Type'].iloc[i] = 'N'
            definition['Keep'].iloc[i] = 'N'
            definition['Default'].iloc[i] = df[definition['Field Name'].iloc[i]].iloc[0]

        for column in definition.columns:
            arguments += " '" + (str(definition[column].iloc[i])).strip()[:8] + "' "

    arguments += "'!' 'Y' " + csv

    dmf.inpfil(out_o=out_o, arguments=arguments)