import functools


# Based on: https://gist.github.com/phizaz/20c36c6734878c6ec053245a477572ec
def call_sync(func):
    import asyncio

    @functools.wraps(func)
    def func_wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if asyncio.iscoroutine(result):
            return asyncio.get_event_loop().run_until_complete(result)
        return result
    return func_wrapper
