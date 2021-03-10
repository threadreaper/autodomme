from __future__ import annotations

from os.path import basename, dirname, join, exists
from os import makedirs
import json
from typing import Any

NOFILENAME = 'You must provide a filename.'
class UserSettings:
    """User settings object that maintain's the user's json config file."""

    def __init__(self, filename: str, path: str|None = None) -> None:
        """
        Initializes the user settings object. If the filename is provided in
        the form of a full path, it will be honored.  If only a filename is
        provided, the current working directory is assumed.

        :param filename: Full path to the file or just the filename.
        :type filename: `str`
        :param path: The (optional) path to the folder containing the user
            settings file.
        :type path: `str|None`
        """
        if filename is None:
            raise ValueError(NOFILENAME)
        (self.full_filename, self.path,
         self.filename) = self._compute_filename(filename, path)
        self.dict = self.read()

    def __repr__(self):
        """
        Converts the settings dictionary into a string for easy display.

        :return: The dictionary as a string.
        :rtype: `str`
        """
        return str(self.dict)

    def _compute_filename(self, filename: str,
                          path: str|None = None) -> tuple[str, str, str]:
        """
        Creates the full filename given the path or the filename or both.

        :param filename: Full path to the file or just the filename.
        :type filename: `str`
        :param path: The (optional) path to the folder containing the user
            settings file.
        :type path: `str|None`
        :return: Tuple with (full filename, path, filename)
        :rtype: `tuple[str, str, str]`
        """
        if path is None:
            try:
                path = dirname(filename)
            except Exception:
                path = '.'
            filename = basename(filename)

        full_filename = join(path, filename)
        return full_filename, path, filename

    def save(self) -> str:
        """
        Saves the current user settings dictionary.

        :return: The full path and filename used to save the settings
        :rtype: `str`
        """
        try:
            if not exists(self.path):
                makedirs(self.path)
            with open(self.full_filename, "w") as f:
                json.dump(self.dict, f)
        except Exception as e:
            print("Error saving settings to %s: %s" % (self.full_filename, e))
        return self.full_filename

    def read(self) -> dict[str, Any]:
        """
        Reads settings file and returns the user settings dictionary.

        :return: The user settings dictionary
        :rtype: `dict[str, Any]`
        """
        try:
            with open(self.full_filename, "w+") as f:
                self.dict = json.load(f)
        except Exception as e:
            return {}
        return self.dict

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Enables setting a user setting by using dictionary notation.
            i.e. settings[key] = value

        :param key: The key for the setting to change.
        :type key: `str`
        :param value: The value to set.
        :type value: Any
        """
        self.read()
        self.dict[key] = value
        self.save()

    def __getitem__(self, key: str) -> Any:
        """
        Enables retrieving a user setting using dictionary notation.
            i.e. foo = settings[key]

        :param key: The key for the setting to retrieve.
        :type key: `str`
        :return: The setting value or None if the entry does not exist.
        :rtype: Any
        """
        self.read()
        if key not in self.dict.keys():
            return None
        return self.dict.get(key)

    def __delitem__(self, key: str) -> None:
        """
        Enables deleting a user settings entry using dictionary notation.
            i.e. del settings[key]

        :param key: The key for the setting to be deleted.
        :type item: `str`
        """
        self.read()
        if key in self.dict:
            del self.dict[key]
            self.save()
