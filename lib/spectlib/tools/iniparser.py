# Copyright (c) 2001, 2002, 2003 Python Software Foundation
# Copyright (c) 2004 Paramjit Oberoi <param.cs.wisc.edu>
# All Rights Reserved.  See LICENSE-PSF & LICENSE for details.

# Copyright (c) 2001, 2002, 2003 Python Software Foundation
# Copyright (c) 2004 Paramjit Oberoi <param.cs.wisc.edu>
# All Rights Reserved.  See LICENSE-PSF & LICENSE for details.

"""Implements basic mechanisms for managing configuration information

* A NAMESPACE is a collection of values and other namepsaces
* A VALUE is a basic value, like 3.1415, or 'Hello World!'
* A NAME identifies a value or namespace within a namespace

The namespace class is an abstract class that defines the basic
interface implemented by all namespace objects.  Two concrete
implementations are include: basic_namespace and ini_namespace.

Each is described in detail elsewhere.  However, here's an
example of the capabilities available:

Create namespace and populate it:

    >>> n = basic_namespace()
    >>> n.playlist.expand_playlist = True
    >>> n.ui.display_clock = True
    >>> n.ui.display_qlength = True
    >>> n.ui.width = 150

Examine data:

    >>> print n.playlist.expand_playlist
    True
    >>> print n['ui']['width']
    150

    >>> print n
    playlist.expand_playlist = True
    ui.display_clock = True
    ui.display_qlength = True
    ui.width = 150

Delete items:

    >>> del n.playlist
    >>> print n
    ui.display_clock = True
    ui.display_qlength = True
    ui.width = 150

Convert it to ini format:

    >>> from cfgparse import iniparser
    >>> i = iniparser.ini_namespace()
    >>> i.import_namespace(n)

    >>> print i
    [ui]
    display_clock = True
    display_qlength = True
    width = 150
"""

# ---- Abstract classes

class namespace(object):

    def __getitem__(self, key):
        return NotImplementedError(key)

    def __setitem__(self, key, value):
        raise NotImplementedError(key, value)

    def __delitem__(self, key):
        raise NotImplementedError(key)

    def __iter__(self):
        return NotImplementedError()

    def new_namespace(self, name):
        raise NotImplementedError(name)

    def __getattr__(self, name):
        try:
            return self.__getitem__(name)
        except KeyError:
            return unknown(name, self)

    def __setattr__(self, name, value):
        try:
            object.__getattribute__(self, name)
            object.__setattr__(self, name, value)
            return
        except AttributeError:
            self.__setitem__(name, value)

    def __delattr__(self, name):
        try:
            object.__getattribute__(self, name)
            object.__delattr__(self, name)
        except AttributeError:
            self.__delitem__(name)

    def import_namespace(self, ns):
        for name in ns:
            value = ns[name]
            if isinstance(value, namespace):
                try:
                    myns = self[name]
                    if not isinstance(myns, namespace):
                        raise TypeError('value-namespace conflict')
                except KeyError:
                    myns = self.new_namespace(name)
                myns.import_namespace(value)
            else:
                self[name] = value


class unknown(object):

    def __init__(self, name, namespace):
        object.__setattr__(self, 'name', name)
        object.__setattr__(self, 'namespace', namespace)

    def __setattr__(self, name, value):
        obj = self.namespace.new_namespace(self.name)
        obj[name] = value


# ---- Basic implementation of namespace

class basic_namespace(namespace):
    """Represents a collection of named values

    Values are added using dotted notation:

    >>> n = basic_namespace()
    >>> n.x = 7
    >>> n.name.first = 'paramjit'
    >>> n.name.last = 'oberoi'

    ...and accessed the same way, or with [...]:

    >>> n.x
    7
    >>> n.name.first
    'paramjit'
    >>> n.name.last
    'oberoi'
    >>> n['x']
    7

    The namespace object is a 'container object'.  The default
    iterator returns the names of values (i.e. keys).

    >>> l = list(n)
    >>> l.sort()
    >>> l
    ['name', 'x']

    Values can be deleted using 'del' and printed using 'print'.

    >>> n.aaa = 42
    >>> del n.x
    >>> print n
    aaa = 42
    name.first = paramjit
    name.last = oberoi

    Nested namepsaces are also namespaces:

    >>> isinstance(n.name, namespace)
    True
    >>> print n.name
    first = paramjit
    last = oberoi

    Finally, values can be read from a file as follows:

    >>> from StringIO import StringIO
    >>> sio = StringIO('''
    ... # comment
    ... ui.height = 100
    ... ui.width = 150
    ... complexity = medium
    ... have_python
    ... data.secret.password = goodness=gracious me
    ... ''')
    >>> n = basic_namespace()
    >>> n.readfp(sio)
    >>> print n
    complexity = medium
    data.secret.password = goodness=gracious me
    have_python
    ui.height = 100
    ui.width = 150
    """

    # this makes sure that __setattr__ knows this is not a value key
    _data = None

    def __init__(self):
        self._data = {}

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __str__(self, prefix=''):
        lines = []
        keys = self._data.keys()
        keys.sort()
        for name in keys:
            value = self._data[name]
            if isinstance(value, namespace):
                lines.append(value.__str__(prefix='%s%s.' % (prefix, name)))
            else:
                if value is None:
                    lines.append('%s%s' % (prefix, name))
                else:
                    lines.append('%s%s = %s' % (prefix, name, value))
        return '\n'.join(lines)

    def new_namespace(self, name):
        obj = basic_namespace()
        self._data[name] = obj
        return obj

    def readfp(self, fp):
        for line in fp:
            line = line.strip()
            if not line:
                continue
            if line[0] == '#':
                continue
            data = line.split('=', 1)
            if len(data) == 1:
                name = line
                value = None
            else:
                name = data[0].strip()
                value = data[1].strip()
            name_components = name.split('.')
            ns = self
            for n in name_components[:-1]:
                try:
                    ns = ns[n]
                    if not isinstance(ns, namespace):
                        raise TypeError('value-namespace conflict', n)
                except KeyError:
                    ns = ns.new_namespace(n)
            ns[name_components[-1]] = value

# Copyright (c) 2001, 2002, 2003 Python Software Foundation
# Copyright (c) 2004 Paramjit Oberoi <param.cs.wisc.edu>
# All Rights Reserved.  See LICENSE-PSF & LICENSE for details.

"""Access and/or modify INI files

* Compatiable with confConfigParser
* Preserves order of sections & options
* Preserves comments/blank lines/etc
* More conveninet access to data

Example:

    >>> from StringIO import StringIO
    >>> sio = StringIO('''# configure foo-application
    ... [foo]
    ... bar1 = qualia
    ... bar2 = 1977
    ... [foo-ext]
    ... special = 1
    ... ''')

    >>> cfg = ini_namespace(sio)
    >>> print cfg.special
    1
    >>> print cfg.foo.bar1
    qualia
    >>> cfg.foo.newopt = 'hi!'

    >>> print cfg
    # configure foo-application
    [foo]
    bar1 = qualia
    bar2 = 1977
    newopt = hi!
    [foo-ext]
    special = 1

"""

# An iniparser that supports ordered sections/options
# Also supports updates, while preserving structure
# Backward-compatiable with ConfigParser

import re
from sets import Set
from ConfigParser import DEFAULTSECT, ParsingError, MissingSectionHeaderError


class line_type(object):

    line = None

    def __init__(self, line=None):
        if line is not None:
            self.line = line.strip('\n')

    def __str__(self):
        if self.line is not None:
            return self.line
        else:
            return self.to_string()

    def __setattr__(self, name, value):
        if hasattr(self, name):
            self.__dict__['line'] = None
        self.__dict__[name] = value

    def to_string(self):
        raise Exception('This method must be overridden in derived classes')


class section_line(line_type):
    regex = re.compile(r'^\['
                       r'(?P<name>[^]]+)'
                       r'\]\s*'
                       r'((?P<csep>;|#)(?P<comment>.*))?$')

    def __init__(self, name, comment=None, comment_separator=None,
                             comment_offset=-1, line=None):
        super(section_line, self).__init__(line)
        self.name = name
        self.comment = comment
        self.comment_separator = comment_separator
        self.comment_offset = comment_offset

    def to_string(self):
        out = '[' + self.name + ']'
        if self.comment is not None:
            # try to preserve indentation of comments
            out = (out+' ').ljust(self.comment_offset)
            out = out + self.comment_separator + self.comment
        return out

    def parse(cls, line):
        m = cls.regex.match(line.rstrip())
        if m is None:
            return None
        return cls(m.group('name'), m.group('comment'),
                   m.group('csep'), m.start('csep'),
                   line)
    parse = classmethod(parse)


class option_line(line_type):

    def __init__(self, name, value, separator='=', comment=None,
                 comment_separator=None, comment_offset=-1, line=None):
        super(option_line, self).__init__(line)
        self.name = name
        self.value = value
        self.separator = separator
        self.comment = comment
        self.comment_separator = comment_separator
        self.comment_offset = comment_offset

    def to_string(self):
        out = '%s %s %s' % (self.name, self.separator, self.value)
        if self.comment is not None:
            # try to preserve indentation of comments
            out = (out+' ').ljust(self.comment_offset)
            out = out + self.comment_separator + self.comment
        return out

    regex = re.compile(r'^(?P<name>[^:=\s[][^:=]*)'
                       r'\s*(?P<sep>[:=])\s*'
                       r'(?P<value>.*)$')

    def parse(cls, line):
        m = cls.regex.match(line.rstrip())
        if m is None:
            return None

        name = m.group('name').rstrip()
        value = m.group('value')
        sep = m.group('sep')

        # comments are not detected in the regex because
        # ensuring total compatibility with ConfigParser
        # requires that:
        #     option = value    ;comment   // value=='value'
        #     option = value;1  ;comment   // value=='value;1  ;comment'
        #
        # Doing this in a regex would be complicated.  I
        # think this is a bug.  The whole issue of how to
        # include ';' in the value needs to be addressed.
        # Also, '#' doesn't mark comments in options...

        coff = value.find(';')
        if coff != -1 and value[coff-1].isspace():
            comment = value[coff+1:]
            csep = value[coff]
            value = value[:coff].rstrip()
            coff = m.start('value') + coff
        else:
            comment = None
            csep = None
            coff = -1

        return cls(name, value, sep, comment, csep, coff, line)
    parse = classmethod(parse)


class comment_line(line_type):
    regex = re.compile(r'^(?P<csep>[;#]|[rR][eE][mM])'
                       r'(?P<comment>.*)$')

    def __init__(self, comment='', separator='#', line=None):
        super(comment_line, self).__init__(line)
        self.comment = comment
        self.separator = separator

    def to_string(self):
        return self.separator + self.comment

    def parse(cls, line):
        m = cls.regex.match(line.rstrip())
        if m is None:
            return None
        return cls(m.group('comment'), m.group('csep'), line)
    parse = classmethod(parse)


class empty_line(line_type):

    def to_string(self):
        return ''

    def parse(cls, line):
        if line.strip():
            return None
        return cls(line)
    parse = classmethod(parse)


class continuation_line(line_type):
    regex = re.compile(r'^\s+(?P<value>.*)$')

    def __init__(self, value, value_offset=8, line=None):
        super(continuation_line, self).__init__(line)
        self.value = value
        self.value_offset = value_offset

    def to_string(self):
        return ' '*self.value_offset + self.value

    def parse(cls, line):
        m = cls.regex.match(line.rstrip())
        if m is None:
            return None
        return cls(m.group('value'), m.start('value'), line)
    parse = classmethod(parse)


class line_container(object):

    def __init__(self, d=None):
        self.contents = []
        if d:
            if isinstance(d, list):
                self.extend(d)
            else:
                self.add(d)

    def add(self, x):
        self.contents.append(x)

    def extend(self, x):
        for i in x:
            self.add(i)

    def get_name(self):
        return self.contents[0].name

    def set_name(self, data):
        self.contents[0].name = data

    def get_value(self):
        if len(self.contents) == 1:
            return self.contents[0].value
        else:
            return '\n'.join([str(x.value) for x in self.contents])

    def set_value(self, data):
        lines = str(data).split('\n')
        linediff = len(lines) - len(self.contents)
        if linediff > 0:
            for _ in range(linediff):
                self.add(continuation_line(''))
        elif linediff < 0:
            self.contents = self.contents[:linediff]
        for i, v in enumerate(lines):
            self.contents[i].value = v

    name = property(get_name, set_name)
    value = property(get_value, set_value)

    def __str__(self):
        s = [str(x) for x in self.contents]
        return '\n'.join(s)

    def finditer(self, key):
        for x in self.contents[::-1]:
            if hasattr(x, 'name') and x.name==key:
                yield x

    def find(self, key):
        for x in self.finditer(key):
            return x
        raise KeyError(key)


class section(namespace):
    _lines = None
    _options = None
    _defaults = None
    _optionxform = None

    def __init__(self, lineobj, defaults = None, optionxform=None):
        self._lines = [lineobj]
        self._defaults = defaults
        self._optionxform = optionxform
        self._options = {}

    def __getitem__(self, key):
        if key == '__name__':
            return self._lines[-1].name
        if self._optionxform:
            key = self._optionxform(key)
        try:
            return self._options[key].value
        except KeyError:
            if self._defaults and key in self._defaults._options:
                return self._defaults._options[key].value
            else:
                raise

    def __setitem__(self, key, value):
        if self._optionxform:
            xkey = self._optionxform(key)
        else:
            xkey = key
        if xkey not in self._options:
            # create a dummy object - value may have multiple lines
            obj = line_container(option_line(key, ''))
            self._lines[-1].add(obj)
            self._options[xkey] = obj
        # the set_value() function in line_container
        # automatically handles multi-line values
        self._options[xkey].value = value

    def __delitem__(self, key):
        if self._optionxform:
            key = self._optionxform(key)
        for l in self._lines:
            remaining = []
            for o in l.contents:
                if isinstance(o, line_container):
                    n = o.name
                    if self._optionxform:
                        n = self._optionxform(n)
                    if key != n:
                        remaining.append(o)
                else:
                    remaining.append(o)
            l.contents = remaining
        del self._options[key]

    def __iter__(self):
        d = Set()
        for l in self._lines:
            for x in l.contents:
                if isinstance(x, line_container):
                    if self._optionxform:
                        ans = self._optionxform(x.name)
                    else:
                        ans = x.name
                    if ans not in d:
                        yield ans
                        d.add(ans)
        if self._defaults:
            for x in self._defaults:
                if x not in d:
                    yield x
                    d.add(x)

    def new_namespace(self, name):
        raise Exception('No sub-sections allowed', name)


def make_comment(line):
    return comment_line(line.rstrip())


class ini_namespace(namespace):
    _data = None
    _sections = None
    _defaults = None
    _sectionxform = None
    _optionxform = None
    _parse_exc = None

    def __init__(self, fp=None, defaults = None, parse_exc=True,
                 optionxform=str.lower, sectionxform=None):
        self._data = line_container()
        self._parse_exc = parse_exc
        self._optionxform = optionxform
        self._sectionxform = sectionxform
        self._sections = {}
        if defaults is None:
            defaults = {}
        self._defaults = section(line_container(), optionxform=optionxform)
        for name, value in defaults.iteritems():
            self._defaults[name] = value
        if fp is not None:
            self.readfp(fp)

    def __getitem__(self, key):
        if key == DEFAULTSECT:
            return self._defaults
        if self._sectionxform:
            key = self._sectionxform(key)
        return self._sections[key]

    def __setitem__(self, key, value):
        raise Exception('Values must be inside sections', key, value)

    def __delitem__(self, key):
        if self._sectionxform:
            key = self._sectionxform(key)
        self._data.contents.remove(self._sections[key]._lineobj)
        del self._sections[key]

    def __iter__(self):
        d = Set()
        for x in self._data.contents:
            if isinstance(x, line_container):
                if x.name not in d:
                    yield x.name
                    d.add(x.name)

    def new_namespace(self, name):
        if self._data.contents:
            self._data.add(empty_line())
        obj = line_container(section_line(name))
        self._data.add(obj)
        if self._sectionxform:
            name = self._sectionxform(name)
        if name in self._sections:
            ns = self._sections[name]
            ns._lines.append(obj)
        else:
            ns = section(obj, defaults=self._defaults,
                              optionxform=self._optionxform)
            self._sections[name] = ns
        return ns

    def __str__(self):
        return str(self._data)

    _line_types = [empty_line, comment_line,
                   section_line, option_line,
                   continuation_line]

    def _parse(self, line):
        for linetype in self._line_types:
            lineobj = linetype.parse(line)
            if lineobj:
                return lineobj
        else:
            # can't parse line
            return None

    def readfp(self, fp):
        cur_section = None
        cur_option = None
        cur_section_name = None
        cur_option_name = None
        line = None
        pending_lines = []
        try:
            fname = fp.name
        except AttributeError:
            fname = '<???>'
        linecount = 0
        exc = None
        for line in fp:
            lineobj = self._parse(line)
            linecount += 1

            if not cur_section and not isinstance(lineobj,
                                (comment_line, empty_line, section_line)):
                if self._parse_exc:
                    raise MissingSectionHeaderError(fname, linecount, line)
                else:
                    lineobj = make_comment(line)

            if lineobj is None:
                if self._parse_exc:
                    if exc is None:
                        exc = ParsingError(fname)
                    exc.append(linecount, line)
                lineobj = make_comment(line)

            if isinstance(lineobj, continuation_line):
                if cur_option:
                    cur_option.add(lineobj)
                else:
                    # illegal continuation line - convert to comment
                    if self._parse_exc:
                        if exc is None:
                            exc = ParsingError(fname)
                        exc.append(linecount, line)
                    lineobj = make_comment(line)
            else:
                cur_option = None
                cur_option_name = None

            if isinstance(lineobj, option_line):
                cur_section.extend(pending_lines)
                pending_lines = []
                cur_option = line_container(lineobj)
                cur_section.add(cur_option)
                if self._optionxform:
                    cur_option_name = self._optionxform(cur_option.name)
                else:
                    cur_option_name = cur_option.name
                if cur_section_name == DEFAULTSECT:
                    optobj = self._defaults
                else:
                    optobj = self._sections[cur_section_name]
                optobj._options[cur_option_name] = cur_option

            if isinstance(lineobj, section_line):
                self._data.extend(pending_lines)
                pending_lines = []
                cur_section = line_container(lineobj)
                self._data.add(cur_section)
                if cur_section.name == DEFAULTSECT:
                    self._defaults._lines.append(cur_section)
                    cur_section_name = DEFAULTSECT
                else:
                    if self._sectionxform:
                        cur_section_name = self._sectionxform(cur_section.name)
                    else:
                        cur_section_name = cur_section.name
                    if not cur_section_name in self._sections:
                        self._sections[cur_section_name] = \
                                section(cur_section, defaults=self._defaults,
                                        optionxform=self._optionxform)
                    else:
                        self._sections[cur_section_name]._lines. \
                            append(cur_section)

            if isinstance(lineobj, (comment_line, empty_line)):
                pending_lines.append(lineobj)

        self._data.extend(pending_lines)
        if line and line[-1] == '\n':
            self._data.add(empty_line())

        if exc:
            raise exc
