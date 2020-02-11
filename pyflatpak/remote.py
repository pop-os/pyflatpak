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
from configparser import ConfigParser
import logging
import os.path
from pathlib import Path

class RemoteError(Exception):
    def __init__(self, msg, code=1):
        self.msg = msg
        self.code = code
    
class Remote:

    fp_sys_config_filepath = '/var/lib/flatpak/'
    fp_user_config_filepath = os.path.join(
        Path.home(),
        '.local/share/flatpak'
    )
    fp_config_filename = 'repo/config'

    def __init__(self, name):
        """ A Flatpak Remote

        Arguments:
            name (str): the internal flatpak name to look up.
        
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
        self.log = logging.getLogger(f'pyflatpak.{name}')
        self._name = name
        self._get_option()
        self._get_config()
        
    
    # Methods
    def _get_option(self):
        """Determines whether the requested remote is user or not.

        We set `option` accordingly and set the correct config file path too.
        """
        self.log.debug('Checking if user or system')
        config = ConfigParser()
        fp_user_config_path = os.path.join(
            self.fp_user_config_filepath, self.fp_config_filename
        )
        with open(fp_user_config_path) as config_file:
            config.read_file(config_file)
        for section in config.sections():
            self.log.debug('user config sections: %s', config.sections())
            if self.name in section:
                self.log.debug('Found in user')
                self.config_path = fp_user_config_path
                self._option = 'user'
                return 
        
        fp_sys_config_path = os.path.join(
            self.fp_sys_config_filepath, self.fp_config_filename
        )
        with open(fp_sys_config_path) as config_file:
            config.read_file(config_file)
        for section in config.sections():
            self.log.debug('system config sections: %s', config.sections())
            if self.name in section:
                self.log.debug('Found in system')
                self.config_path = fp_sys_config_path
                self._option = 'system'
                return
        
        self.log.critical('Could not find remote!')
        raise RemoteError(f'Remote \'{self.name}\' doesn\'t exist')

    def _get_config(self):
        """Updates the config for this remote. 

        This should be done after any changes to any configuration.
        """
        self.log.debug('Getting configuration')
        self._raw_config = ConfigParser()
        with open(self.config_path) as config_file:
            self._raw_config.read_file(config_file)
        self.config = self._raw_config[f'remote "{self.name}"']

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
        try:
            return self.config['xa.title']
        except KeyError as e:
            self.log.info('No title set, using name. (%s)', e.args)
            return self.name
    @title.setter
    def title(self, title):
        self._title = title

    @property
    def url(self):
        """ str: The URL that this remote uses to download apps."""
        return self.config['url']
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
            return self.config['xa.comment']
        except KeyError as e:
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
            return self.config['xa.description']
        except KeyError as e:
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
            return self.config['xa.icon']
        except KeyError as e:
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
            return self.config['xa.homepage']
        except AttributeError as e:
            self.log.info('No homepage found: %s', e.args)
            return None
    @homepage.setter
    def homepage(self, homepage):
        self._homepage = homepage

    @property
    def enabled(self):
        """ bool: Whether the remote is enabled or not."""
        try:
            # This looks backwards and sets True if disabled. This is because
            # FlatPak tracks if remtoes are *disabled*, while we track *enabled*
            # This is more intuitive. 
            _enabled = self.config['xa.disable'].lower() in [
                'false', 'no', '0'
            ]
            return _enabled
        except KeyError as e:
            self.log.info('Disable key not found, default is enabled. (%s)', e.args)
            return True
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