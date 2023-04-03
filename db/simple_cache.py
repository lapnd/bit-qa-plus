"""Simple cache decorator with cache persistence"""

def cache(cache_file_dir):
    import os
    import json
    if not os.path.exists(cache_file_dir):
        os.mkdir(cache_file_dir)
    
    def decorator(func):
        cache_dict = {}
        try:
            with open(f'{cache_file_dir}/{func.__name__}_cache.json', 'r') as f:
                cache_dict = json.load(f)
        except FileNotFoundError:
            pass
        def wrapper(*args, **kwargs):
            key = str(args)
            if kwargs:
                key += '_' + str(kwargs)
            if key in cache_dict:
                # hit!
                return cache_dict[key]
            else:
                # miss: call and save result
                result = func(*args, **kwargs)
                cache_dict[key] = result
                with open(f'{cache_file_dir}/{func.__name__}_cache.json', 'w') as f:
                    json.dump(cache_dict, f, indent=2)
                return result
        return wrapper
    
    return decorator

# test
# @cache('./cache/')
# def test_function(arg1, arg2):
#     print('computing')
#     return arg1 + arg2
