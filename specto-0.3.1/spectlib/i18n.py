# -*- coding: UTF8 -*-

# Specto , Unobtrusive event notifier
#
#       il8n.py
#
# See the AUTHORS file for copyright ownership information

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

import sys
import gettext

_translation = None
MESSAGES_DIR = "%s/share/locale" % sys.prefix


def set_language(language=None):
    global _translation
    if language is not None:
        language = [language]
    try:
        _translation = gettext.translation('specto', MESSAGES_DIR,
                                           language)
    except IOError:
        # The selected language was not installed in messages, so fall back to
        # untranslated English.
        _translation = gettext.NullTranslations()


def get_translation():
    return _translation


def set_translation(translation):
    global _translation
    _translation = translation


# Set up the global translation based on environment variables.  Mostly used
# for command line scripts.
if _translation is None:
    set_language()


def _(s):
    """
    Returns the translated version of a singular string.
    """
    if not s:
        return s
    return _translation.ugettext(s)


def N_(singular, plural, n, var_singular = None, var_plural = None):
    # FIXME: the code below is UNTESTED, because pygettext hates me
    """
    Calculates plurals and returns the appropriate translation.
    Also replaces variables such as %s after translating.

    Example usage:
        i18n._n("Message from %s",
            "Messages from %s',
            len(messages),
            "Linus",
            "Linus, Bill, Steve")
    Or maybe (untested):
        i18n._n("1 message from %s",
            len(messages) + " messages from %s',
            len(messages),
            "Linus",
            "Linus, Bill, Steve")
    """
    foo = _translation.ungettext(singular, plural, n)  # Get the translation

    # Now, if the translation has variables to replace, do it.
    if n == 1 and var_singular is not None:
        foo = foo % var_singular
    elif n > 1 and var_plural is not None:
        foo = foo % var_plural

    return foo
