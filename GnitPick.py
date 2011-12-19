import java.io.File as File

import sys
import re

from GnitPickController import GnitController

class GnitPick:
    """GnitPick application
       Invoke GnitPick(projectdir) to open a project upon starting
    """

    def __init__(self,projectdir=None):
        self.controller = GnitController()
        if projectdir != None:
            self.controller.openProject( projectdir )

   # Stand-alone Unit Execution
if __name__ == "__main__":
    # gtf = GnitPick(File(sys.argv[0]))
    gtf = GnitPick( File("./stories") )
    
    