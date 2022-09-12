class Market(object):

    def __init__(self) :
        self.id = None
        self.name = None
        self.symbol = None
        self.baseCurrency = None
        self.fee = None
        self.factoryAbi = None
        self.factoryAddress = None
        self.routerAbi = None
        self.routerAddress = None
        self.info = None
        self.symbols = []
        self.pools = []