import inspect
import shlex
import six
import types
import pipes
import traceback
import io
import contextlib

from fire.core import _OneLineResult
from fire.core import _DictAsString

from fire.core import _Fire
from fire.core import helputils

from contextlib import contextmanager
import ctypes
import io
import os, sys
import tempfile

libc = ctypes.CDLL(None)
c_stdout = ctypes.c_void_p.in_dll(libc, 'stdout')


@contextmanager
def stdout_redirector(stream):
    # The original fd stdout points to. Usually 1 on POSIX systems.
    original_stdout_fd = sys.stdout.fileno()

    def _redirect_stdout(to_fd):
        """Redirect stdout to the given file descriptor."""
        # Flush the C-level buffer stdout
        libc.fflush(c_stdout)
        # Flush and close sys.stdout - also closes the file descriptor (fd)
        sys.stdout.close()
        # Make original_stdout_fd point to the same file as to_fd
        os.dup2(to_fd, original_stdout_fd)
        # Create a new sys.stdout that points to the redirected fd
        sys.stdout = io.TextIOWrapper(os.fdopen(original_stdout_fd, 'wb'))

    # Save a copy of the original stdout fd in saved_stdout_fd
    saved_stdout_fd = os.dup(original_stdout_fd)
    try:
        # Create a temporary file and redirect stdout to it
        tfile = tempfile.TemporaryFile(mode='w+b')
        _redirect_stdout(tfile.fileno())
        # Yield to caller, then redirect stdout back to the saved fd
        yield
        _redirect_stdout(saved_stdout_fd)
        # Copy contents of temporary file to the given stream
        tfile.flush()
        tfile.seek(0, io.SEEK_SET)
        stream.write(tfile.read())
    finally:
        tfile.close()
        os.close(saved_stdout_fd)


class Torch:
    def __init__(self, in_key, out_key):
        self.in_key = in_key
        self.out_key = out_key

    def task(self, component, message, **kwargs):
        command = message.data[self.in_key] if self.in_key in message.data else ' '

        if command is None:
            return {}

        if isinstance(command, six.string_types):
            args = shlex.split(command)
        elif isinstance(command, (list, tuple)):
            args = command
        else:
            raise ValueError('The command argument must be a string or a sequence of arguments.')

        caller = inspect.stack()[1]
        caller_frame = caller[0]
        caller_globals = caller_frame.f_globals
        caller_locals = caller_frame.f_locals
        context = {}
        context.update(caller_globals)
        context.update(caller_locals)

        temp_out = io.BytesIO()
        with stdout_redirector(temp_out):
            try:
                component_trace = _Fire(component, args, context, '.')
            except:
                return {'text': '\n'.join([i for i in traceback.format_exc().split('\n') if i])}

            if component_trace.HasError():
                for help_flag in ['-h', '--help']:
                    if help_flag in component_trace.elements[-1].args:
                        command = '{cmd} -- --help'.format(cmd=component_trace.GetCommand())
                        print(('WARNING: The proper way to show help is {cmd}.\n'
                               'Showing help anyway.\n').format(cmd=pipes.quote(command)))
                print(f'Fire trace:\n{component_trace}\n')
                result = component_trace.GetResult()
                print(helputils.HelpString(result, component_trace, component_trace.verbose))

            elif component_trace.show_trace and component_trace.show_help:
                print('Fire trace:\n{trace}\n'.format(trace=component_trace))
                result = component_trace.GetResult()
                print(helputils.HelpString(result, component_trace, component_trace.verbose))

            elif component_trace.show_trace:
                print('Fire trace:\n{trace}'.format(trace=component_trace))

            elif component_trace.show_help:
                result = component_trace.GetResult()
                print(helputils.HelpString(result, component_trace, component_trace.verbose))

            else:
                result = component_trace.GetResult()
                if isinstance(result, (list, set, types.GeneratorType)):
                    for i in result:
                        print(_OneLineResult(i))
                elif inspect.isgeneratorfunction(result):
                    raise NotImplementedError
                elif isinstance(result, dict):
                    print(_DictAsString(result, component_trace.verbose))
                elif isinstance(result, tuple):
                    print(_OneLineResult(result))
                elif isinstance(result, (bool, six.string_types, six.integer_types, float, complex)):
                    print(str(result))
                elif result is not None:
                    print(helputils.HelpString(result, component_trace, component_trace.verbose))

        s = temp_out.getvalue().decode('utf-8')
        r = {self.out_key: s}
        return r
