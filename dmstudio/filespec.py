import pandas as pd

class StudioFileSpec(object):

    '''
    StudioFileSpec
    ----------

    Class for creating a Studio file specification as a pandas dataframe. The file definition is to be
    used for an input for file-handling commands such as INPFIL.

    Object Properties:
    ------------------

    StudioFilespec.definition: pandas dataframe
        Dataframe that holds the file specifications


    '''
    # columns required for creating and importing files to Studio
    spec_columns = ['Field Name', 'Field Type', 'Length', 'Keep', 'Default']

    def __init__(self, spec=None):
        self.spec = spec # a pandas Dataframe

        if self.spec is None:
            # Create empty file_definition
            self.spec = pd.DataFrame(columns=self.spec_columns)
            
        else:
            for col in self.spec_columns:
                if col not in self.spec.columns:
                    raise IndexError("Required column {} not found in file specification. Columns 'Field Name', \
                                    'Field Type', 'Length', 'Keep', 'Default' are required".format(col))
            self.spec = self.spec[self.spec_columns].copy()


    def __repr__(self):
        return self.spec.__repr__()

    def add_field(self, field_name, field_type, length='', keep='Y', default=''):
        """
        Add a row to the StudioFileSpec by specifying field_name, type and length.
        """

        data = {'Field Name': field_name, 
                'Field Type': field_type, 
                'Length': length, 
                'Keep': keep,
                'Default': default
                }

        dmtemp = pd.DataFrame(data)
        dmtemp = dmtemp[self.columns]
        self.spec = self.spec.append(dmtemp).reset_index(drop=True)

    @classmethod
    def from_text(cls, filepath, **kwargs):
        """
        Create StudioFileSpec from comma-separated text file. 
        A pandas dataframe is created first using read_csv, kwargs are passed 
        directly to the read_csv method.
        
        Takes: filepath, the path to the comma-separated file
        
        Returns: a StudioFileSpec
        
        """
        df = pd.read_csv(filepath, **kwargs)

        return cls.from_dataframe(df)

    @classmethod
    def from_dataframe(cls, df, default = ''):
        """
        Create StudioFileSpec from pandas dataframe. Inspects each column and
        records field_name, type and length. 
        
        Takes: a pandas DataFrame
        
        Returns: a StudioFileSpec
        
        """

        # Special Fields
        CHAR8_FIELDS = ['VALUE_IN', 'VALUE_OU', 'NUMSAM_F', 'SVOL_F', 'VAR_F', 'MINDIS_F']
        IMPLICIT_FIELDS = ['XMORIG', 'YMORIG', 'ZMORIG', 'NX', 'NY', 'NZ','X0','Y0','Z0','ANGLE1',
                            'ANGLE2','ANGLE3','ROTAXIS1','ROTAXIS2','ROTAXIS3']
        
        definition = None
        
        field_names, field_type, length = [], [], []
           
        for column in df.columns:

            field_names.append(column)

            if df[column].dtype=='float64' or df[column].dtype=='int64':
                field_type.append('N')
                length.append('')
            else:
                field_type.append('A')
                if column in CHAR8_FIELDS:
                    length.append(8)
                else:
                    length.append(int((df[column].str.len().max()-1)/4+1)*4)

        spec = pd.DataFrame({'Field Name': field_names, 'Field Type': field_type, 'Length': length})
        spec['Keep'] = 'Y'
        spec['Default'] = default

        # instantiate the class using the parsed definition
        return cls(spec)

def map_csv(filepath, **kwargs):
    """
    Convenience function for pandas-like operation
    """    
    return StudioFileSpec.from_text(filepath, **kwargs)
    
    



