import os
import functools
import logging
import weakref

from tornado import ioloop
from tornado.log import gen_log
from tornado import process
from tornado.util import exec_in


_watched_files = set()
_reload_hooks = []
_reload_attempted = False
_io_loops = weakref.WeakKeyDictionary()  # type: ignore


def start(io_loop=None, check_time=500):
    """Begins watching source files for changes.

    .. versionchanged:: 4.1
       The ``io_loop`` argument is deprecated.
    """
    io_loop = io_loop or ioloop.IOLoop.current()
    if io_loop in _io_loops:
        return
    _io_loops[io_loop] = True
    if len(_io_loops) > 1:
        gen_log.warning("tornado.autoreload started more than once in the same process")
    modify_times = {}
    callback = functools.partial(_reload_on_update, modify_times)
    scheduler = ioloop.PeriodicCallback(callback, check_time, io_loop=io_loop)
    scheduler.start()

def wait():
    """Wait for a watched file to change, then restart the process.

    Intended to be used at the end of scripts like unit test runners,
    to run the tests again after any source file changes (but see also
    the command-line interface in `main`)
    """
    io_loop = ioloop.IOLoop()
    start(io_loop)
    io_loop.start()


def watch(filename):
    """Add a file to the watch list.

    All imported modules are watched by default.
    """
    _watched_files.add(filename)


def watch_directory(dirpath):
    map(watch, [os.path.join(root, fn) for root, _, fns in os.walk(dirpath) for fn in fns])


def add_reload_hook(fn):
    """Add a function to be called before reloading the process.

    Note that for open file and socket handles it is generally
    preferable to set the ``FD_CLOEXEC`` flag (using `fcntl` or
    ``tornado.platform.auto.set_close_exec``) instead
    of using a reload hook to close them.
    """
    _reload_hooks.append(fn)


def _reload_on_update(modify_times):
    if _reload_attempted:
        return
    for path in _watched_files:
        _check_file(modify_times, path)


def add_reload_hook(fn):
    """Add a function to be called before reloading the process.

    Note that for open file and socket handles it is generally
    preferable to set the ``FD_CLOEXEC`` flag (using `fcntl` or
    ``tornado.platform.auto.set_close_exec``) instead
    of using a reload hook to close them.
    """
    _reload_hooks.append(fn)



def _check_file(modify_times, path):
    try:
        modified = os.stat(path).st_mtime
    except Exception:
        return
    if path not in modify_times:
        modify_times[path] = modified
        return
    if modify_times[path] != modified:
        gen_log.info("%s modified; restarting server", path)
        _reload()
        modify_times[path] = modified


def _reload():
    global _reload_attempted
    _reload_attempted = True
    for fn in _reload_hooks:
        fn()
    _reload_attempted = False
