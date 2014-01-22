#!/usr/bin/python

# monkey-patch mingw32 compiler class not to link against msvcrt90.dll
#
from distutils.cygwinccompiler import Mingw32CCompiler
import distutils.cygwinccompiler


class Mingw32CCompilerPatched(Mingw32CCompiler):
    def __init__(self, verbose=0, dry_run=0, force=0):
        Mingw32CCompiler.__init__(self, verbose, dry_run, force)

        # undo following line:
        # http://hg.python.org/cpython/file/3a1db0d2747e/Lib/distutils/cygwinccompiler.py#l343
        self.dll_libraries = []

distutils.cygwinccompiler.Mingw32CCompiler = Mingw32CCompilerPatched
#
# END monkey-patch

import sys
import os

if sys.version > '3':
    PY3 = True
else:
    PY3 = False

import subprocess

from distutils.core import setup, Extension
from distutils.sysconfig import get_python_lib, get_python_version

if os.path.isfile("MANIFEST"):
    os.unlink("MANIFEST")

# You may have to change these
LUAVERSION = "5.2"
PYTHONVERSION = get_python_version()
PYLIBS = ["python" + get_python_version(), "pthread", "util"]
PYLIBDIR = [get_python_lib(standard_lib=True) + "/config"]
LUALIBS = ["lua" + LUAVERSION]
LUALIBDIR = []


def pkgconfig(*packages):
    # map pkg-config output to kwargs for distutils.core.Extension
    flag_map = {'-I': 'include_dirs', '-L': 'library_dirs', '-l': 'libraries'}

    pcoutput = ""
    for package in packages:
        # raises exception if e.g. pkg-config is not found or returns
        # some error
        pcoutput += subprocess.check_output(
            "pkg-config --libs --cflags %s" % package
        )

    kwargs = {}
    for token in pcoutput.split():
        if token[:2] in flag_map:
            kwargs.setdefault(flag_map.get(token[:2]), []).append(token[2:])
        else:                           # throw others to extra_link_args
            kwargs.setdefault('extra_link_args', []).append(token)

    if PY3:
        items = kwargs.items()
    else:
        items = kwargs.iteritems()
    for k, v in items:     # remove duplicated
        kwargs[k] = list(set(v))

    return kwargs

# lua_pkgconfig = pkgconfig('lua', 'lua' + LUAVERSION,'python-' + PYTHONVERSION)
lua_pkgconfig = pkgconfig('lua')

setup(name="lunatic-python",
      version="1.0",
      description="Two-way bridge between Python and Lua",
      author="Gustavo Niemeyer",
      author_email="gustavo@niemeyer.net",
      url="http://labix.org/lunatic-python",
      license="LGPL",
      long_description="""\
Lunatic Python is a two-way bridge between Python and Lua, allowing these
languages to intercommunicate. Being two-way means that it allows Lua inside
Python, Python inside Lua, Lua inside Python inside Lua, Python inside Lua
inside Python, and so on.
""",
      ext_modules=[
          # no idea how to get this to compile
          # Extension("lua-python",
          #         ["src/pythoninlua.c", "src/luainpython.c"],
          #         **lua_pkgconfig),
          Extension("lua",
                    ["src/pythoninlua.c", "src/luainpython.c"],
                    **lua_pkgconfig),
      ]
)
