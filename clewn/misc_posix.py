# vi:set ts=8 sts=4 sw=4 et tw=80:
#
# Copyright (C) 2007 Xavier de Gaye.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program (see the file COPYING); if not, write to the
# Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA
#
# $Id$

"""Pyclewn posix miscellaneous classes and functions."""

import os
assert os.name == 'posix'

import signal
import select
import errno
import fcntl
import pty
import termios

import misc

# set the logging methods
(critical, error, warning, info, debug) = misc.logmethods('posix')
Unused = warning
Unused = debug

def daemonize():
    """Run as a daemon."""
    CHILD = 0
    if os.name == 'posix':
        # setup a pipe between the child and the parent,
        # so that the parent knows when the child has done
        # the setsid() call and is allowed to exit
        pipe_r, pipe_w = os.pipe()

        pid = os.fork()
        if pid != CHILD:
            # the read returns when the child closes the pipe
            os.close(pipe_w)
            os.read(pipe_r, 1)
            os.close(pipe_r)
            os._exit(os.EX_OK)

        # close stdin, stdout and stderr
        try:
            devnull = os.devnull
        except AttributeError:
            devnull = '/dev/null'
        fd = os.open(devnull, os.O_RDWR)
        os.close(0)
        os.close(1)
        os.close(2)
        os.dup(fd)      # replace stdin  (file descriptor 0)
        os.dup(fd)      # replace stdout (file descriptor 1)
        os.dup(fd)      # replace stderr (file descriptor 2)
        os.close(fd)    # don't need this now that we've duplicated it

        # change our process group in the child
        try:
            os.setsid()
        except OSError:
            critical('cannot run as a daemon'); raise
        os.close(pipe_r)
        os.close(pipe_w)

def sigchld_handler(signum=signal.SIGCHLD, frame=None, process=None, l=[]):
    """The SIGCHLD handler is also used to register the ProcessChannel."""
    # takes advantage of the fact that the 'l' default value
    # is evaluated only once
    unused = frame
    if process is not None and isinstance(process, misc.ProcessChannel):
        l[0:len(l)] = [process]
        return

    if len(l) and signum == signal.SIGCHLD:
        l[0].waitpid()

class ProcessChannel(misc.ProcessChannel):
    """Run a posix process and communicate with it through asynchat.

    An attempt is made to start the program with a pseudo tty. We fall back
    to pipes when the first method fails.

    Instance attributes:
        sig_handler: function
            default SIGCHLD signal handler
        ttyname: str
            pseudo tty name

    """

    INTERRUPT_CHAR = chr(3)     # <Ctl-C>

    def __init__(self, argv):
        """Constructor."""
        misc.ProcessChannel.__init__(self, argv)
        self.sig_handler = None
        self.ttyname = None

    def forkexec(self):
        """Fork and exec the program after setting the pseudo tty attributes.

        Return the pseudo tty file descriptor.

        """
        fd, slave_fd = pty.openpty()
        self.ttyname = os.ttyname(slave_fd)

        # don't map '\n' to '\r\n' - no echo - INTR is <C-C>
        try:
            attr = termios.tcgetattr(fd)
            attr[1] = attr[1] & ~termios.ONLCR  # oflag
            attr[3] = attr[3] & ~termios.ECHO   # lflags
            attr[6][termios.VINTR] = self.INTERRUPT_CHAR
            termios.tcsetattr(fd, termios.TCSADRAIN, attr)
        except termios.error:
            critical("failed to set termios attributes to pseudo tty")

        self.pid = os.fork()
        if self.pid == 0:
            # establish a new session
            os.setsid()
            os.close(fd)

            # grab control of terminal
            # (from `The GNU C Library' (glibc-2.3.1))
            try:
                fcntl.ioctl(slave_fd, termios.TIOCSCTTY)
                info("terminal control with TIOCSCTTY ioctl call")
            except:
                # this might work (it does on Linux)
                if slave_fd != 0: os.close(0)
                if slave_fd != 1: os.close(1)
                if slave_fd != 2: os.close(2)
                newfd = os.open(self.ttyname, os.O_RDWR)
                os.close(newfd)

            # slave becomes stdin/stdout/stderr of child
            os.dup2(slave_fd, 0)
            os.dup2(slave_fd, 1)
            os.dup2(slave_fd, 2)
            if (slave_fd > 2):
                os.close(slave_fd)

            # exec program
            os.execvp(self.pgm, self.argv)
            critical('failed to execvp "%"', self.pgm); raise

        return fd

    def popen(self):
        """Spawn a process using pipes."""
        self.ttyname = None
        misc.ProcessChannel.popen(self)

    def start(self):
        """Start with a pseudo tty and fall back to pipes if that fails."""
        # register self to the sigchld_handler
        sigchld_handler(process=self)
        # register the sigchld_handler
        self.sig_handler = signal.signal(signal.SIGCHLD, sigchld_handler)

        try:
            if os.environ.has_key('CLEWN_PIPES'):
                self.popen()
            else:
                try:
                    # use a pseudo tty
                    pty = misc.FileAsynchat(self.forkexec(), self)
                    self.fileasync = (pty, pty)
                    info('starting "%s" with a pseudo tty', self.pgm)
                except (ImportError, OSError):
                    # fall back to using pipes
                    self.popen()
        except OSError:
            critical('cannot start process "%"', self.pgm); raise
        info('program argv list: %s', str(self.argv))

    def waitpid(self):
        """Wait on the process."""
        if self.pid != 0:
            pid, status = os.waitpid(self.pid, os.WNOHANG)
            if (pid, status) != (0, 0):
                self.pid = 0
                if self.sig_handler is not None:
                    signal.signal(signal.SIGCHLD, self.sig_handler)
                self.close()

                if os.WCOREDUMP(status):
                    info("process %s terminated with a core dump",
                            self.pgm)
                elif os.WIFSIGNALED(status):
                    info("process %s terminated after receiving signal %d",
                            self.pgm, os.WTERMSIG(status))
                elif os.WIFEXITED(status):
                    info("process %s terminated with exit %d",
                            self.pgm, os.WEXITSTATUS(status))
                else:
                    info("process %s terminated", self.pgm)

    def close(self):
        """Close the channel an wait on the process."""
        if self.fileasync is not None:
            misc.ProcessChannel.close(self)
            self.waitpid()

    def sendintr(self):
        """Send a SIGINT interrupt to the program."""
        if self.ttyname is not None:
            self.fileasync[1].send(self.INTERRUPT_CHAR)

class PipePeek(misc.PipePeek):
    """The pipe peek thread."""

    def __init__(self, fd, asyncobj):
        """Constructor."""
        misc.PipePeek.__init__(self, fd, asyncobj)

    def peek(self):
        """Peek the pipe."""
        try:
            iwtd, owtd, ewtd = select.select([self.fd], [], [], 0)
        except select.error, err:
            if err[0] != errno.EINTR:
                # this may occur on exit
                # closing the application is handled in ProcessChannel.waitpid
                error('ignoring failed select syscall: %', err)
            return False
        unused = owtd
        unused = ewtd
        # debug('pipe select return: %s)', iwtd)
        if iwtd and iwtd[0] == self.fd:
            self.read_event = True
            return True
        return False
