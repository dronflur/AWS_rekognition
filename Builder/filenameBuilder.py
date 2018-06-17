import hashlib
import time
from enum import Enum

class InOut(Enum):
    In = 0
    Out = 1

class FileNameBuilder:
    def getFileName(self, T1C=None, inout=InOut.In):
        prefix = 'in' if inout == InOut.In else 'out'
        prefix = prefix + '_'
        pre_filename = T1C + str(time.time())
        hash_obj = hashlib.sha1(pre_filename.encode())
        filename = prefix + hash_obj.hexdigest()
        return filename