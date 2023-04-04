"""Simple cache decorator with cache persistence"""
import os
import pickle


def cache(cache_file_dir='./cache/'):
    # NOTE: this cache does not support multiprocess
    if not os.path.exists(cache_file_dir):
        os.mkdir(cache_file_dir)
    
    def decorator(func):
        cache_dict = {}
        cache_file_path = f'{cache_file_dir}/{func.__name__}_cache.pkl'
        try:
            with open(cache_file_path, 'rb') as f:
                cache_dict.update(pickle.load(f))
        except (FileNotFoundError, pickle.PickleError):
            pass

        def wrapper(*args, **kwargs):
            key = str(args)
            if kwargs:
                key += '_' + str(kwargs)
            if key in cache_dict:
                return cache_dict[key]
            else:
                result = func(*args, **kwargs)
                cache_dict[key] = result
                return result
        
        def get_cache():
            return dict(cache_dict)
        def update_cache(new):
            cache_dict.clear()
            cache_dict.update(new)
        def save_cache():
            with open(cache_file_path, 'wb') as f:
                pickle.dump(cache_dict, f)

        wrapper.get_cache = get_cache
        wrapper.update_cache = update_cache
        wrapper.save_cache = save_cache
        return wrapper
    
    return decorator

# test
def test_cache():
    @cache('./cache/')
    def test_function(arg1, arg2):
        print('computing')
        return arg1 + arg2

    test_function(2, 3)
    test_function(0, 1)
    inner_cache = test_function.get_cache()
    print('cache:', inner_cache)
    test_function(2, 3)
    test_function.save_cache()
