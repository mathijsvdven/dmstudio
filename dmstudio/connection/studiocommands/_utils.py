import inspect
import re
import os
import shutil
import copy
import logging
import numbers
from pathlib import Path, WindowsPath

logger = logging.getLogger(__name__)

# Lookup dict of Studio variables with special characters, not allowed in Python
rename_dict = {'x_or_y_or_z_f': 'X/Y/Z',
                 'x_or_y_or_zpt_f': 'X/Y/ZPT',
                 'x_or_y_or_z_p': 'X/Y/Z',
                 'da_axis1_or_2_or_3_p': 'DA_AXIS1/2/3',
                 'x_or_ygstart_p': 'X/YGSTART',
                 'modx_popen_y_or_z_pclose_min_p': 'MODX(Y/Z)MIN',
                 'modx_popen_y_or_z_pclose_max_p': 'MODX(Y/Z)MAX',
                 'x_or_y_or_zpoints_p': 'X/Y/ZPOINTS',
                 'xpt_or_ypt_or_zpt_f': 'XPT/YPT/ZPT',
                 'q1nx_or_y_or_z_p': 'Q1NX/Y/Z',
                 'q2nx_or_y_or_z_p': 'Q2NX/Y/Z',
                 'q3nx_or_y_or_z_p': 'Q3NX/Y/Z',
                 'q4nx_or_y_or_z_p': 'Q4NX/Y/Z',
                 'angle1_or_2_or_3_p': 'ANGLE1/2/3',
                 'axis1_or_2_or_3_p': 'AXIS 1/2/3',
                 '_py_3dmap_o': '3DMAP',
                 'xpt_or_ypt_or_zpt_p': 'XPT/YPT/ZPT',
                 '_py_1_p': '1',
                 '_py_2_p': '2'}

def robustEquals(a, b, precision = 0.001):
    """
    enable equals operation between floats
    """
    if type(a) == float and type(b) == float:
        return abs(a - b) / a < precision # less than 0.1% different to account for rounding issues
    else:
        return a == b

def getChangedArgs(flocals, fsignature):
    """
    compares provided arguments with function keyword arguments,
    returns kwargs that are different from the default
    
    takes:
    flocals: the local variables of the function to inspect
    fsignature: the signature object of the function to inspect
    """
    
    pos_args = [k for k, v in fsignature if v.default == inspect._empty]
    key_args = {k:v.default for k, v in fsignature if v.default != inspect._empty}

    pos_arg_provided = {k:v for k, v in flocals.items() if k in pos_args if not k == 'self'}
    key_arg_provided = {k:v for k, v in flocals.items() if k in key_args.keys()}
    key_arg_changed = {k:v for k, v in key_arg_provided.items() if not robustEquals(key_args[k], v)}
    
    return {**pos_arg_provided, **key_arg_changed}
    
def getDMArg(pyvar, argdata):
    """
    Converts python variables to DM variables and returns as string including 
    type-specific prefix ('&', '@' or '*').
    Also tries to convert list variables such as f1_to_10_p and creates 
    DM variables for each list entry based on the variable name root.
    """
    prefix_dict = {'_i':'1_&', '_o':'2_&', '_f':'3_*', '_p':'4_@', 
                   'expression':'5_', 'retrieval':'6_','arguments':'7_','test':'8_'} # numerals for sorting
    special_vars = ['expression', 'retrieval', 'arguments','test']

    # Special variables, no prefix
    if pyvar in special_vars:
        if pyvar in ['expression','test']:
            if pyvar == 'expression':
                close = 'GO'
            else:
                close = 'END'

            if isinstance(argdata, list):
                argstr = " {} {}".format(' '.join(argdata), close)
            elif isinstance(argdata, str):
                argstr = " {} {}".format(argdata, close)
                
        elif pyvar == 'retrieval':
            argstr = "'{{}}'".format(argdata)

        elif pyvar == 'arguments':
            argstr = ' '.join(["'{}'".format(x) if not isinstance(x, numbers.Number) else str(x) for x in argdata])
            # argstr = ' '.join([str(x) for x in argdata])

        dm_args = "{}{}".format(prefix_dict[pyvar], argstr)

    else:
        try: 
            sfx = pyvar[-2:]
            pfx = prefix_dict[sfx]
        except:
            raise KeyError("Argument '{}' does not have a valid suffix. Valid are '_i', '_o', '_p', and '_f', provided: {}".format(pyvar, sfx))
        
        pyvar_ = pyvar[:-2]
   
        # check if range
        try:
            dm_args = convertListArgs(pyvar_, argdata, pfx)
        
        except TypeError:
            dm_args = convertVariable(pyvar_, argdata, pfx)
    
    return dm_args
    
def convertVariable(pyvar, argdata, pfx):
    """
    Converts python variables to DM variables by using a lookup dict and
    regular expressions. Variables are compared against dict entries and converted
    dynamically if not found.
    """
    attempt = rename_dict.get(pyvar, None)
    
    # check if in dict
    if attempt is not None:
        argstr = "{}{}={}".format(pfx, attempt.upper(), argdata)
        
    # otherwise try dynamically
    else:
        # check for any special contents
        pat = re.compile('(_py_|_or_|_popen_|_pclose_)')
        mlist = re.findall(pat, pyvar)
        if len(mlist) > 0:
            replacement_dict = {'_or_':'/', '_to_':'-', '_dot_':'.', 
                            '_py_':'', '_popen_':'(', '_pclose_':')'}
            
            dmvar = copy.deepcopy(pyvar)
            for m in mlist:
                dmvar = dmvar.replace(m, replacement_dict[m])
    
            argstr = "{}{}={}".format(pfx, dmvar.upper(), argdata)
        
        else:
            # no special content, simple conversion
            argstr = "{}{}={}".format(pfx, pyvar.upper(), argdata)
            logger.debug("variable '{}' with value '{}' written to argstr: '{}'".format(pyvar, argdata, argstr))
    
    return argstr
    
def convertListArgs(pyvar, argdata, pfx):
    pat = re.compile('((?P<from>[0-9])(?P<range>_to_)(?P<to>[0-9]+))')
    m = re.search(pat, pyvar)
    if isinstance(m, re.Match):
        start = int(m.group('from'))
        stop = int(m.group('to'))
        
        if isinstance(argdata, list):
            narg = len(argdata)
            if narg > stop:
                raise IndexError("variable {}, list length {} exceeds maximum of {}".format(pyvar, narg, stop))
                                 
            else:
                dm_pfx = re.sub(pat, '', pyvar)
                dm_vars = ["{}{}".format(dm_pfx, v) for v in range(start, narg+start)]
                dm_vars_vals = zip(dm_vars, argdata)
                joinstr = ' ' + pfx
                argstr = pfx + joinstr.join(['{}={}'.format(i.upper(),j) for i, j in dm_vars_vals])
            
        elif isinstance(argdata, str):
            # Assume single value
            dm_pfx = re.sub(pat, '', pyvar)
            argstr = ' ' + pfx + "{}{}={}".format(dm_pfx, start, argdata)
            
        else:
            raise ValueError("range variable {} provided of type {}, expected a string or a list".format(pyvar, type(pyvar)))
        
        logger.debug("range variable '{}' with value '{}' written to argstr: '{}'".format(pyvar, argdata, argstr))
        return argstr

    else:
        raise TypeError("variable '{}' is not a range variable.".format(pyvar))
        
def getDMArgList(arg_value_dict):
    """
    Converts a dictionary of python argument:value pairs to a list of DM Strings
    Suffixes for DM argument type ('&', '*', '@' are added and strings are sorted to:
    input > output > fields > parameters.
    """
    
    # Get list of DM arguments as strings of format "#_&ARG=value"
    # where '#_' is a prefix used for sorting
    dm_arg_list = []
    for k, v in arg_value_dict.items():
        dmarg = getDMArg(k, v)
        if dmarg is not None:
            dm_arg_list.append(dmarg)
    
    # Sort arguments
    dm_arg_list.sort()
    logger.debug("sorted arguments: {}".format(' '.join(dm_arg_list)))
    
    # remove prefixes used for sorting
    dm_arg_list_clean = [a[2:] for a in dm_arg_list]
    
    return dm_arg_list_clean

def move_to_cwd(filepath, prefix = '_'):
    """
    Create a copy of the source file in the working directory.
    Add a suffix to easily identify temporary files.
    """

    if not isinstance(filepath, WindowsPath):
        path = Path(filepath)
    else:
        path = filepath

    parent = str(path.parent)
    file = path.name
    tempfile = prefix + file

    if parent != '.':
        cwd = Path().absolute()
        shutil.copy(path, cwd / tempfile)

    return tempfile

def clean_tempfiles(prefix:str = '_', 
                    exempt:list=['py']):
    """
    Remove temporary files, identified by a prefix (default is '_').
    Exempts files ending with suffixes in the exempt list (default is 'py')

    """
    for f in os.listdir():
        if f.startswith(prefix):
            checks = [not f.endswith(f".{sfx}") for sfx in exempt]
            if all(checks):
                os.remove(f)
            

    