from ccdxt.base.exchange import Exchange

class binance(Exchange):

    def describe(self):
        return self.deep_extend(super(binance, self).describe(), {
            'id': 'binance',
            'name': 'Binance',
            'countries': ['JP', 'MT'],  # Japan, Malta
            'rateLimit': 50,
            'certified': True,
            'pro': True,
            # new metainfo interface
            
        })
        


