import sys


class CLI:
    requiredargs = []
    booleanargs = []
    rawargs = []
    cliargs = dict()
    orphans = []

    # requiredargs: are those args such as -a, -s, etc that are required
    # returnorphans: are those args that are not assigned to an argument and do not have a - in front of them
    def __init__(self, requiredargs, booleanargs=None, returnorphans=True):
        self.requiredargs = ["-%s" % char for char in requiredargs]
        booleanargs = ["-%s" % char for char in booleanargs]
        self.rawargs = sys.argv[1:]
        tmp_cliargs = [(self.rawargs[i], self.rawargs[i+1]) for i, b in enumerate(self.rawargs[1:]) if i % 2 == 0]
        self.cliargs = dict(tmp_cliargs)

        for i in booleanargs:
            if i in self.cliargs:
                del self.cliargs[i]

        # build boolean args list
        for arg in booleanargs:
            if arg in self.rawargs:
                self.booleanargs.append(arg)

        # check that required args are passed; exit if not
        for arg in self.requiredargs:
            if arg not in self.cliargs:
                print("%s is required. Action and options out of order?" % arg)
                sys.exit(1)
        
        # build list of orphans
        if returnorphans:
            self._build_orphans()
            
    def _build_orphans(self):
        for i in self.rawargs:
            if i in self.booleanargs:
                continue
            elif i in self.requiredargs:
                continue
            else:
                if i not in self.cliargs.values():
                    self.orphans.append(i)
