


class Exchange(BaseExchange):
    
    @staticmethod
    def deep_extend(*args):
        result = None
        for arg in args:
            if isinstance(arg, dict):
                if not isinstance(result, dict):
                    result = {}
                for key in arg:
                    result[key] = Exchange.deep_extend(result[key] if key in result else None, arg[key])
            else:
                result = arg
        return result
    
    @staticmethod
    def safe_value(dictionary, key, default_value=None):
        return dictionary[key] if Exchange.key_exists(dictionary, key) else default_value
    
    