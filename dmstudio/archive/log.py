import logging
from pathlib import Path 

cwd = Path().absolute()
logfile = cwd/"dmstudio_log.txt"
logging.basicConfig(filename=logfile, level=logging.DEBUG, 
                    format='[%(asctime)s] %(name)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)