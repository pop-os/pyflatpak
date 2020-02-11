#!/usr/bin/env python3

"""
 pyflatpak
 A simple python3 wrapper for managing the flatpak system

Copyright (c) 2020, Ian Santopietro
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

This is a python representation of a remote.
"""

import logging

import remotes

class RemoteError(Exception):
    def __init__(self, msg, code=1):
        self.msg = msg
        self.code = code
    
class Remote:

    def __init__(self, name, option):
        """ A Flatpak Remote

        Arguments:
            name (str): the internal flatpak name to look up.
            option (str): The remote type, either 'user' or 'remote'.
        
        Attributes:
            name (str): The internal name for this remote
            title (str): The human-readable title for this remote
            url (str): The url used for this remote.
            option (str): The remote type, 'user'(default) or 'system'.
            about (str): A readable description of this remote, either the 
                comment, the description, or the name (in that order).
            comment (str): A short comment about the remote.
            description (str): A longer description of the remote.
            icon (str): A URL to look for an icon for this remote.
            homepage (str): The URL for this remote's homepage.
            enabled (bool): Whether the remote is enabled or not.
        """
        _remotes_obj = remotes.Remotes()
        remote_data = remotes.get_remotes()

        self.log = logging.getLogger(f'pyflatpak.{name}')
        
        self._name = name
        self._option = option

    # Data attributes
    @property
    def name(self):
        """ str: the internal name of this remote."""
        return self._name
    @name.setter
    def name(self, name):
        raise RemoteError('Cannot set name: property is read-only')

    @property
    def title(self):
        """ str: the fancy representation of this remote's name."""
        return self._title
    @title.setter
    def title(self, title):
        self._title = title

    @property
    def url(self):
        """ str: The URL that this remote uses to download apps."""
        return self._url
    @url.setter
    def url(self, url):
        self._url = url

    @property
    def option(self):
        """ str: Whether this remote is a user or system remote."""
        return self._option
    @option.setter
    def option(self, option):
        raise RemoteError('Cannot set option: property is read-only')

    @property
    def about(self):
        """ str: A short info blurb about the remote.

        This will grab the comment property by default, and fall back to the
        description if not. Otherwise, it will use the remote name.
        """
        if self.comment:
            return self.comment
        elif self.description:
            return self.description
        else:
            return self.name

    @property
    def comment(self):
        """ A short-form description of the remote.

        This is a quick summary of the remote. This is typically set by the 
        remote maintainers.
        """
        try:
            return self._comment
        except AttributeError as e:
            self.log.info('No comment found: %s', e.args)
            return None
    @comment.setter
    def comment(self, comment):
        self._comment = comment

    @property
    def description(self):
        """ str: A long-form description for the remote.

        This provides a description about the remote's purpose, and should be
        suitable for display within a UI to describe the remote. This is 
        typically set by the remote maintainers.
        """
        try:
            return self._description
        except AttributeError as e:
            self.log.info('No description found: %s', e.args)
            return None
    @description.setter
    def description(self, description):
        self._description = description

    @property
    def icon(self):
        """ str: This is the URL for a logo/icon for this remote.

        This is a (usually SVG) icon that is intended for display within a UI
        for a user. This is typically set by the remote maintainers.
        """
        try:
            return self._icon
        except AttributeError as e:
            self.log.info('No icon found: %s', e.args)
            return None
    @icon.setter
    def icon(self, icon):
        self._icon = icon

    @property
    def homepage(self):
        """ str: The homepage for this remote.

        This should be a webpage for users to browse for information about the
        remote, e.g. for app directories or troubleshooting and contact 
        information. This is typically set by the remote maintainers.
        """
        try:
            return self._homepage
        except AttributeError as e:
            self.log.info('No homepage found: %s', e.args)
            return None
    @homepage.setter
    def homepage(self, homepage):
        self._homepage = homepage

    @property
    def enabled(self):
        """ bool: Whether the remote is enabled or not."""
        return self._enabled
    @enabled.setter
    def enabled(self, enabled):
        """ Allow accepting strings as input values."""
        # Assume we were passed a string
        try:
            self.enabled = enabled.lower() in ['true', 'yes', '1']
        # This appears to be a boolean value...
        except AttributeError as e:
            # ...but double-check first, to be sure...
            if 'bool' in e.args[-1]:
                self._enabled = enabled
            # ...or set True as the default fallback
            else:
                self._enabled = True