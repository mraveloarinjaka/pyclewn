# README

[PyCLEWN](http://pyclewn.sourceforge.net/)

A Vim_ front-end to the gdb_ and pdb_ debuggers. The debugger output is
redirected to a Vim window, the console. The debugger commands are mapped to
Vim user-defined commands and completion is available on Vim command line.

```
git submodule update --init --recursive
cd pdb-clone
python setup.py install
cd ..
python setup.py sdist
pip install --find-links=dist pyclewn==2.3
python -c "import clewn; clewn.get_vimball()"
vim -S pyclewn-2.3.vmb
```

Pyclewn currently supports the following debuggers:

- gdb:      version 7.1 and above, pyclewn uses the gdb MI interface.
- pdb:      the Python debugger.

# Quickstart

to debug "foobar foobar_arg" with gdb, run the commmand:
```
    :Pyclewn gdb --args foobar foobar_arg
```

# Instalation
Install Pyclewn with pip_ and extract a vimball from the installed Python
package, then install the Vim runtime files with the vimball. See install_.

**Features**

* When Pyclewn is started from gvim with the ``:Pyclewn`` command, the
  ``:Cinferiortty`` command may be used to launch a terminal connected to a
  pseudo terminal that becomes the controlling terminal of the program being
  debugged by gdb or by pdb.

* A debugger command can be mapped in Vim to a key sequence using Vim key
  mappings. This allows, for example, to set/clear a breakpoint or print a
  variable value at the current cursor or mouse position by just hitting a
  key.

* Breakpoints and the line in the current frame are highlighted in the source
  code. Disabled breakpoints are noted with a different highlighting color.
  Pyclewn automatically finds the source file for the breakpoint if it exists,
  and tells Vim to load and display the file and highlight the line.

* Multiple consecutive Pyclewn sessions can be started from gvim with the
  ``:Pyclewn`` command.

* The value of an expression or variable is displayed in a balloon in gvim
  when the mouse pointer is hovering over the selected expression or the
  variable.

**gdb**

* Full gdb completion on Vim command line.

* An expression can be watched in a Vim window. The expression value is
  updated and highlighted whenever it has changed. When the expression is a
  structure or class instance, it can be expanded (resp. folded) to show
  (resp. hide) its members and their values.

* Three Vim buffers are updated by gdb, they list the breakpoints, the
  backtrace and the threads. One can jump with the <CR> key or the mouse to
  the corresponding source code line from the ``(clewn)_breakpoints`` window
  or switch to the corresponding frame from the ``(clewn)_backtrace`` window,
  or switch to the correponding thread with the ``(clewn)_threads`` window.

* A sequence of gdb commands can be run from a Vim script when the ``async``
  option is set. This may be useful in a key mapping.

* The ``project`` command saves the current gdb settings to a project file
  that may be sourced later by the gdb ``source`` command. These settings are
  the working directory, the debuggee program file name, the program arguments
  and the breakpoints. The sourcing and saving of the project file can be
  automated to occur on each gdb startup and termination, with the ``project``
  command line option.

**pdb**

* Pyclewn is a front-end to pdb-clone_. With breakpoints Pyclewn runs just
  below the speed of the Python interpreter (the command line Python debugger,
  pdb, runs 10 to 100 times slower than the interpreter).

* Similarly to gdb, one may attach to a running Python process with the pdb
  debugger, interrupt the process, manage a debugging session and terminate
  the debugging session by detaching from the process. A new debugging session
  may be conducted later on this same process, possibly from another Vim
  instance.

**Specifications**

* platforms

  + All unix platforms supported by Python.

  + GNU gdb from macports is required on Mac Os X.

* languages

  + Python 2.7 or Python >= 3.2.

  + C language for the ``_bdb`` extension module of pdb-clone_.

* Vim

  + gvim 7.0 and above.

  + vim 7.3 or above (vim in a terminal).

  + ``pyclewn`` is a standalone program connected to Vim with a netbeans
    socket, that may be started from Vim with the ``:Pyclewn`` command since
    Vim 7.3.

* gdb

  + gdb/mi interface.

  + Asynchronous gdb commands.

  + The watched variables, breakpoints, backtrace and threads windows.

  + The project file.

* pdb

  + Interrupt the debuggee.

  + Attach to a running Python process.

  + The ``threadstack`` command.

**Licensing**

This software is licensed under the GNU General Public License Version 2.
Pdb-clone is a derivative work of a part of Python and as such, subject to
the Python license_.

.. _Vim: http://www.vim.org/
.. _gdb: http://www.gnu.org/software/gdb/gdb.html
.. _pdb: http://docs.python.org/3/library/pdb.html
.. _pip: http://pip.pypa.io/en/latest/
.. _install: http://pyclewn.sourceforge.net/install.html
.. _license: http://docs.python.org/2.7/license.html
.. _pdb-clone: http://pypi.python.org/pypi/pdb-clone
.. vim:filetype=rst:tw=78:ts=8:et:

