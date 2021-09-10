from pathlib import Path

"""
Base data directory
"""
DATA_DIR = Path('/data')


"""
Temp directory (upload directory)
"""
TMP_DIR = DATA_DIR / 'temp'


"""
Recorded faces
"""
FACES_DIR = DATA_DIR / 'faces'


"""
Query directory
"""
QUERIES_DIR = DATA_DIR / 'queries'


"""
Records directory
"""
RECORDS_DIR = DATA_DIR / 'records'


"""
Sockets directory
"""
SOCKET_DIR = Path('/sockets')
