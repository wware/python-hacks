import logging
import multiprocessing
import random
import sys
import threading
import time
from functools import wraps


class TimeoutError(Exception):
    pass


class KillableThread(threading.Thread):
    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False
        self.__run_backup = self.run
        self.run = self.__run

    def __run(self):
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, event, arg):
        if event == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, event, arg):
        if self.killed:
            raise SystemExit()
        return self.localtrace

    def kill(self):
        self.killed = True


def enforce_time_limit(seconds, hard_failure=True, process=False, error_message=None):
    """
    If you use process=True, the decorated function will run in a separate process.
    It won't share variables with the caller.
    """
    if error_message is None:
        error_message = "{0} timed out after {1} seconds"

    def process_decorator(func):
        @wraps(func)
        def newfunc(*args, **kwargs):
            p = multiprocessing.Process(target=func, args=args, kwargs=kwargs)
            p.start()
            p.join(seconds)
            if p.is_alive():
                p.terminate()
                p.join()
                if hard_failure:
                    raise TimeoutError(func)
                else:
                    logging.error(error_message.format(func, seconds))
        return newfunc

    def thread_decorator(func):
        @wraps(func)
        def newfunc(*args, **kwargs):
            kill_thread_holder = []
            retval = []

            @wraps(func)
            def collect_return_value():
                retval.append(func(*args, **kwargs))
                kill_thread_holder[0].kill()

            func_thread = KillableThread(target=collect_return_value)

            def kill_func():
                for _ in xrange(100):
                    time.sleep(0.01 * seconds)
                func_thread.kill()

            kill_thread = KillableThread(target=kill_func)
            kill_thread_holder.append(kill_thread)
            func_thread.start()
            kill_thread.start()
            kill_thread.join()
            if func_thread.isAlive():
                if hard_failure:
                    raise TimeoutError(func)
                else:
                    logging.error(error_message.format(func, seconds))
                return None
            else:
                assert len(retval) == 1, retval
                return retval[0]
        return newfunc

    if process:
        return process_decorator
    else:
        return thread_decorator


def retry_on_exception(max_retries=5, delay_start_s=2.0, timeout=None,
                       hypothesis="", expected_exception=None):
    """
    Retry the wrapped function for the expected exception types
    arg: max_retries: number of times to rerun function
    arg: delay_start: seconds to sleep betwee retries (adjusted randomly by 2/3 to 3/2)
    arg: hypothesis: reason for retrying multiple times -- why is this necessary
    arg: expected_exception: (sub)instance of Exception class
    return: new function that retries the wrapped function
    """
    if expected_exception is None:
        expected_exception = Exception
    elif isinstance(expected_exception, tuple):
        assert all([issubclass(e, Exception) for e in expected_exception])
    elif not issubclass(expected_exception, Exception):
        raise TypeError(expected_exception)

    def retry_decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            if timeout is not None:
                f = enforce_time_limit(timeout)(func)
            else:
                f = func
            delay_s = delay_start_s
            attempts = max_retries + 1
            while attempts > 0:
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    s = ("{0}(*{1}, **{2}) failed{3}".format(
                        func.__name__, args, kwargs,
                        " (problem is possibly {0})".format(hypothesis) if hypothesis else ""
                    ))
                    if isinstance(e, expected_exception):
                        logging.error(s)
                        # anywhere from 2/3 to 3/2, uniformly distributed on a log scale
                        time.sleep(delay_s * (1.5 ** (2 * random.random() - 1)))
                        delay_s = delay_s * 1.5
                    else:
                        logging.exception('UNEXPECTED EXCEPTION when ' + s)
                        raise
                attempts -= 1
        return inner
    return retry_decorator
