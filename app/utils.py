import threading

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

def setInterval(interval):
    """ Periodically calls the specified function. 
    
    Args: 
        interval (float): interval in seconds between calls
        
        @setInterval(.5)
        def function():
            doSomething()
        
        stop = function()   # start timer, the first call is in .5 seconds
        stop.set()          # stop the loop
        stop = function()   # start again
    """
    def decorator(function):
        def wrapper(*args, **kwargs):
            stopped = threading.Event()

            def loop(): # executed in another thread
                while not stopped.wait(interval): # until stopped
                    function(*args, **kwargs)

            t = threading.Thread(target=loop)
            t.daemon = True # stop if the program exits
            t.start()
            return stopped
        return wrapper
    return decorator