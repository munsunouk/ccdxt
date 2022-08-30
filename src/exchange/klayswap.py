

class klayswap(Exchange):

    def describe(self):
        return self.deep_extend(super(klayswap, self).describe(), {
            
            'id': 'klayswap',
            'name': 'Klayswap',
            'countries': ['SK'],  # SouthKorea
            #  hard limit of 7 requests per 200ms => 35 requests per 1000ms => 1000ms / 35 = 28.5714 ms between requests
            # 10 withdrawal requests per 30 seconds = (1000ms / rateLimit) / (1/3) = 90.1
            # cancels do not count towards rateLimit
            # only 'order-making' requests count towards ratelimit
            'rateLimit': 28.57,
            'certified': True,
            'hostname': 'klayswap.com',
            'fees': 0.3,
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/52026496/187066162-91d1a0bb-bf79-47f6-a8fa-e6cc70d2a628.png',
                'www': 'https://klayswap.com',
                'node': {
                    'public': 'https://public-node-api.klaytnapi.com/v1/cypress', #public klaytn network
                    # 'private': 'https://{hostname}',
                },
                'doc': 'https://docs.klayswap.com/',
                'fees': 'https://medium.com/klayswap/klayswap-dao-ksp-token-economy-and-governance-8e4bc2408e2',
  
            },
            'has': {
                
                'swap': True,
                'createOrder': True,
                'fetchBalance': True,
                'fetchCurrencies': True,
                'fetchDepositAddress': True,
                'fetchDeposits': True,
                'fetchMyTrades': True,
                'fetchOrder': True,
                'fetchTransactionFees': None,
                'fetchTransfer': None,
                'fetchTransfers': None,
                'transfer': True,
                'withdraw': True,
            }
            'api': {
                'public': {
                    'get': {
                        
                        'coins': 1,
                        # markets
                        'markets': 1,
                        'markets/{market_name}': 1,
                        'markets/{market_name}/orderbook': 1,
                        'markets/{market_name}/trades': 1,
                        
                        # wallet
                        'wallet/coins': 1,
            
                    }
                },
                'private': {
                    
                    'get': {
                        
                        # account
                        'account': 1,
                        
                         # wallet
                        'wallet/balances': 1,
                        'wallet/all_balances': 1,
                        'wallet/deposit_address/{coin}': 1,  # ?method={method}
                        'wallet/deposits': 1,
                        'wallet/withdrawals': 1,
                        
                        # orders
                        'orders': 1,  # ?market={market}
                        'orders/history': 1,  # ?market={market}
                        'orders/{order_id}': 1,
                        'orders/by_client_id/{client_order_id}': 1,
                        
                    },
                    'post': {
                        
                        # wallet
                        'wallet/deposit_address/list': 1,
                        'wallet/withdrawals': 90,
                        'wallet/saved_addresses': 1,
                        
                        # orders
                        'orders': 1,
                    
                    }
                },
            }
            
            'exceptions': {
                
                'exact': {
            
                    'Slow down': RateLimitExceeded,  # {"error":"Slow down","success":false}
                    'Size too small for provide': InvalidOrder,  # {"error":"Size too small for provide","success":false}
                    'Not enough balances': InsufficientFunds,  # {"error":"Not enough balances","success":false}
                    'InvalidPrice': InvalidOrder,  # {"error":"Invalid price","success":false}
                    'Size too small': InvalidOrder,  # {"error":"Size too small","success":false}
                    'Size too large': InvalidOrder,  # {"error":"Size too large","success":false}
                    'Invalid price': InvalidOrder,  # {"success":false,"error":"Invalid price"}
                    'Missing parameter price': InvalidOrder,  # {"error":"Missing parameter price","success":false}
                    'Order not found': OrderNotFound,  # {"error":"Order not found","success":false}
            
                },
                'broad': {
                
                    # {"error":"Not logged in","success":false}
                    # {"error":"Not logged in: Invalid API key","success":false}
                    'Not logged in': AuthenticationError,
                    'Account does not have enough margin for order': InsufficientFunds,
                    'Invalid parameter': BadRequest,  # {"error":"Invalid parameter start_time","success":false}
                    'The requested URL was not found on the server': BadRequest,
                    'No such coin': BadRequest,
                    'Do not send more than': RateLimitExceeded,
                    'Cannot send more than': RateLimitExceeded,  # {"success":false,"error":"Cannot send more than 1500 requests per minute"}
                    'An unexpected error occurred': ExchangeNotAvailable,  # {"error":"An unexpected error occurred, please try again later(58BC21C795).","success":false}
                    'Please retry request': ExchangeNotAvailable,  # {"error":"Please retry request","success":false}
                    'Please try again': ExchangeNotAvailable,  # {"error":"Please try again","success":false}
                    'Try again': ExchangeNotAvailable,  # {"error":"Try again","success":false}
         
                } 
            }
        }
                                
    def 