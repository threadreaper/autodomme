class UserSettings:
    # A reserved settings object for use by the setting functions. It's a way for users
    # to access the user settings without diarectly using the UserSettings class
    _default_for_function_interface = None  # type: UserSettings

    def __init__(self, filename=None, path=None, silent_on_error=False):
        """
        User Settings

        :param filename: The name of the file to use. Can be a full path and filename or just filename
        :type filename: (str or None)
        :param path: The folder that the settings file will be stored in. Do not include the filename.
        :type path: (str or None)
        """
        self.path = path
        self.filename = filename
        self.full_filename = None
        self.dict = {}
        self.default_value = None
        self.silent_on_error = silent_on_error
        if filename is not None or path is not None:
            self.load(filename=filename, path=path)

    def __repr__(self):
        """
        Converts the settings dictionary into a string for easy display

        :return: (str) the dictionary as a string
        """
        return str(self.dict)

    def set_default_value(self, default):
        """
        Set the value that will be returned if a requested setting is not found

        :param default: value to be returned if a setting is not found in the settings dictionary
        :type default: Any
        """
        self.default_value = default

    def _compute_filename(self, filename=None, path=None):
        """
        Creates the full filename given the path or the filename or both.

        :param filename: The name of the file to use. Can be a full path and filename or just filename
        :type filename: (str or None)
        :param path: The folder that the settings file will be stored in. Do not include the filename.
        :type path: (str or None)
        :return: Tuple with (full filename, path, filename)
        :rtype: Tuple[str, str, str]
        """
        if filename is not None:
            dirname_from_filename = os.path.dirname(
                filename)  # see if a path was provided as part of filename
            if dirname_from_filename:
                path = dirname_from_filename
                filename = os.path.basename(filename)
        elif self.filename is not None:
            filename = self.filename
        else:
            filename = (os.path.splitext(
                os.path.basename(sys.modules["__main__"].__file__))[0] +
                        ".json")

        if path is None:
            if self.path is not None:
                path = self.path
            elif sys.platform.startswith("win"):
                path = os.path.expanduser(
                    r"~\AppData\Local\PySimpleGUI\settings")
            elif sys.platform.startswith("linux"):
                path = os.path.expanduser(r"~/.config/PySimpleGUI/settings")
            elif sys.platform.startswith("darwin"):
                path = os.path.expanduser(
                    r"~/Library/Application Support/PySimpleGUI/settings")
            else:
                path = "."

        full_filename = os.path.join(path, filename)
        return (full_filename, path, filename)

    def set_location(self, filename=None, path=None):
        """
        Sets the location of the settings file

        :param filename: The name of the file to use. Can be a full path and filename or just filename
        :type filename: (str or None)
        :param path: The folder that the settings file will be stored in. Do not include the filename.
        :type path: (str or None)
        """
        cfull_filename, cpath, cfilename = self._compute_filename(
            filename=filename, path=path)

        self.filename = cfilename
        self.path = cpath
        self.full_filename = cfull_filename

    def get_filename(self, filename=None, path=None):
        """
        Sets the filename and path for your settings file.  Either paramter can be optional.

        If you don't choose a path, one is provided for you that is OS specific
        Windows path default = users/name/AppData/Local/PySimpleGUI/settings.

        If you don't choose a filename, your application's filename + '.json' will be used.

        Normally the filename and path are split in the user_settings calls. However for this call they
        can be combined so that the filename contains both the path and filename.

        :param filename: The name of the file to use. Can be a full path and filename or just filename
        :type filename: (str or None)
        :param path: The folder that the settings file will be stored in. Do not include the filename.
        :type path: (str or None)
        :return: The full pathname of the settings file that has both the path and filename combined.
        :rtype: (str)
        """
        if (filename is not None or path is not None
                or (filename is None and path is None)):
            self.set_location(filename=filename, path=path)
            self.read()
        return self.full_filename

    def save(self, filename=None, path=None):
        """
        Saves the current settings dictionary.  If a filename or path is specified in the call, then it will override any
        previously specitfied filename to create a new settings file.  The settings dictionary is then saved to the newly defined file.

        :param filename: The fFilename to save to. Can specify a path or just the filename. If no filename specified, then the caller's filename will be used.
        :type filename: (str or None)
        :param path: The (optional) path to use to save the file.
        :type path: (str or None)
        :return: The full path and filename used to save the settings
        :rtype: (str)
        """
        if filename is not None or path is not None:
            self.set_location(filename=filename, path=path)
        try:
            if not os.path.exists(self.path):
                os.makedirs(self.path)
            with open(self.full_filename, "w") as f:
                json.dump(self.dict, f)
        except Exception as e:
            if not self.silent_on_error:
                print("*** Error saving settings to file:***\n",
                      self.full_filename, e)
                print(_create_error_message())
        return self.full_filename

    def load(self, filename=None, path=None):
        """
        Specifies the path and filename to use for the settings and reads the contents of the file.
        The filename can be a full filename including a path, or the path can be specified separately.
        If  no filename is specified, then the caller's filename will be used with the extension ".json"

        :param filename: Filename to load settings from (and save to in the future)
        :type filename: (str or None)
        :param path: Path to the file. Defaults to a specific folder depending on the operating system
        :type path: (str or None)
        :return: The settings dictionary (i.e. all settings)
        :rtype: (dict)
        """
        if filename is not None or path is not None or self.full_filename is None:
            self.set_location(filename, path)
        self.read()
        return self.dict

    def delete_file(self, filename=None, path=None):
        """
        Deltes the filename and path for your settings file.  Either paramter can be optional.
        If you don't choose a path, one is provided for you that is OS specific
        Windows path default = users/name/AppData/Local/PySimpleGUI/settings.
        If you don't choose a filename, your application's filename + '.json' will be used
        Also sets your current dictionary to a blank one.

        :param filename: The name of the file to use. Can be a full path and filename or just filename
        :type filename: (str or None)
        :param path: The folder that the settings file will be stored in. Do not include the filename.
        :type path: (str or None)
        """
        if (filename is not None or path is not None
                or (filename is None and path is None)):
            self.set_location(filename=filename, path=path)
        try:
            os.remove(self.full_filename)
        except Exception as e:
            if not self.silent_on_error:
                print("*** User settings delete filename warning ***\n", e)
                print(_create_error_message())
        self.dict = {}

    def write_new_dictionary(self, settings_dict):
        """
        Writes a specified dictionary to the currently defined settings filename.

        :param settings_dict: The dictionary to be written to the currently defined settings file
        :type settings_dict: (dict)
        """
        if self.full_filename is None:
            self.set_location()
        self.dict = settings_dict
        self.save()

    def read(self):
        """
        Reads settings file and returns the dictionary.

        :return: settings dictionary
        :rtype: (dict)
        """
        if self.full_filename is None:
            return {}
        try:
            if os.path.exists(self.full_filename):
                with open(self.full_filename, "r") as f:
                    self.dict = json.load(f)
        except Exception as e:
            if not self.silent_on_error:
                print("*** Error reading settings from file: ***\n",
                      self.full_filename, e)
                print(_create_error_message())

        return self.dict

    def exists(self, filename=None, path=None):
        """
        Check if a particular settings file exists.  Returns True if file exists

        :param filename: The name of the file to use. Can be a full path and filename or just filename
        :type filename: (str or None)
        :param path: The folder that the settings file will be stored in. Do not include the filename.
        :type path: (str or None)
        """
        cfull_filename, cpath, cfilename = self._compute_filename(
            filename=filename, path=path)
        if os.path.exists(cfull_filename):
            return True
        return False

    def delete_entry(self, key):
        """
        Deletes an individual entry.  If no filename has been specified up to this point,
        then a default filename will be used.
        After value has been deleted, the settings file is written to disk.

        :param key:  Setting to be deleted. Can be any valid dictionary key type (i.e. must be hashable)
        :type key: (Any)
        """
        if self.full_filename is None:
            self.set_location()
        self.read()
        if key in self.dict:
            del self.dict[key]
            self.save()
        else:
            if not self.silent_on_error:
                print("*** Warning - key ", key,
                      " not found in settings ***\n")
                print(_create_error_message())

    def set(self, key, value):
        """
        Sets an individual setting to the specified value.  If no filename has been specified up to this point,
        then a default filename will be used.
        After value has been modified, the settings file is written to disk.

        :param key:  Setting to be saved. Can be any valid dictionary key type
        :type key: (Any)
        :param value: Value to save as the setting's value. Can be anything
        :type value: (Any)
        """
        if self.full_filename is None:
            self.set_location()
        self.read()
        self.dict[key] = value
        self.save()

    def get(self, key, default=None):
        """
        Returns the value of a specified setting.  If the setting is not found in the settings dictionary, then
        the user specified default value will be returned.  It no default is specified and nothing is found, then
        the "default value" is returned.  This default can be specified in this call, or previously defined
        by calling set_default. If nothing specified now or previously, then None is returned as default.

        :param key: Key used to lookup the setting in the settings dictionary
        :type key: (Any)
        :param default: Value to use should the key not be found in the dictionary
        :type default: (Any)
        :return: Value of specified settings
        :rtype: (Any)
        """
        if self.default_value is not None:
            default = self.default_value

        if self.full_filename is None:
            self.set_location()
            self.read()
        value = self.dict.get(key, default)
        # Previously was saving creating an entry and saving the dictionary if the
        # key was not found.  I don't understand why it was originally coded this way.
        # Hopefully nothing is going to break removing this code.
        # if key not in self.dict:
        #     self.set(key, value)
        #     self.save()
        return value

    def get_dict(self):
        """
        Returns the current settings dictionary.  If you've not setup the filename for the
        settings, a default one will be used and then read.

        Note that you can display the dictionary in text format by printing the object itself.

        :return: The current settings dictionary
        :rtype: Dict
        """
        if self.full_filename is None:
            self.set_location()
            self.read()
            self.save()
        return self.dict

    def __setitem__(self, item, value):
        """
        Enables setting a setting by using [ ] notation like a dictionary.
        Your code will have this kind of design pattern:
        settings = sg.UserSettings()
        settings[item] = value

        :param item: The key for the setting to change. Needs to be a hashable type. Basically anything but a list
        :type item: Any
        :param value: The value to set the setting to
        :type value: Any
        """

        self.set(item, value)

    def __getitem__(self, item):
        """
        Enables accessing a setting using [ ] notation like a dictionary.
        If the entry does not exist, then the default value will be returned.  This default
        value is None unless user sets by calling UserSettings.set_default_value(default_value)

        :param item: The key for the setting to change. Needs to be a hashable type. Basically anything but a list
        :type item: Any
        :return: The setting value
        :rtype: Any
        """
        return self.get(item, self.default_value)

    def __delitem__(self, item):
        """
        Delete an individual user setting.  This is the same as calling delete_entry.  The syntax
        for deleting the item using this manner is:
            del settings['entry']
        :param item: The key for the setting to delete
        :type item: Any
        """
        self.delete_entry(key=item)


# Create a singleton for the settings information so that the settings functions can be used
if UserSettings._default_for_function_interface is None:
    UserSettings._default_for_function_interface = UserSettings()


def user_settings_filename(filename=None, path=None):
    """
    Sets the filename and path for your settings file.  Either paramter can be optional.

    If you don't choose a path, one is provided for you that is OS specific
    Windows path default = users/name/AppData/Local/PySimpleGUI/settings.

    If you don't choose a filename, your application's filename + '.json' will be used.

    Normally the filename and path are split in the user_settings calls. However for this call they
    can be combined so that the filename contains both the path and filename.

    :param filename: The name of the file to use. Can be a full path and filename or just filename
    :type filename: (str)
    :param path: The folder that the settings file will be stored in. Do not include the filename.
    :type path: (str)
    :return: The full pathname of the settings file that has both the path and filename combined.
    :rtype: (str)
    """
    settings = UserSettings._default_for_function_interface
    return settings.get_filename(filename, path)


def user_settings_delete_filename(filename=None, path=None):
    """
    Deltes the filename and path for your settings file.  Either paramter can be optional.
    If you don't choose a path, one is provided for you that is OS specific
    Windows path default = users/name/AppData/Local/PySimpleGUI/settings.
    If you don't choose a filename, your application's filename + '.json' will be used
    Also sets your current dictionary to a blank one.

    :param filename: The name of the file to use. Can be a full path and filename or just filename
    :type filename: (str)
    :param path: The folder that the settings file will be stored in. Do not include the filename.
    :type path: (str)
    """
    settings = UserSettings._default_for_function_interface
    settings.delete_file(filename, path)


def user_settings_set_entry(key, value):
    """
    Sets an individual setting to the specified value.  If no filename has been specified up to this point,
    then a default filename will be used.
    After value has been modified, the settings file is written to disk.

    :param key: Setting to be saved. Can be any valid dictionary key type
    :type key: (Any)
    :param value: Value to save as the setting's value. Can be anything
    :type value: (Any)
    """
    settings = UserSettings._default_for_function_interface
    settings.set(key, value)


def user_settings_delete_entry(key):
    """
    Deletes an individual entry.  If no filename has been specified up to this point,
    then a default filename will be used.
    After value has been deleted, the settings file is written to disk.

    :param key: Setting to be saved. Can be any valid dictionary key type (hashable)
    :type key: (Any)
    """
    settings = UserSettings._default_for_function_interface
    settings.delete_entry(key)


def user_settings_get_entry(key, default=None):
    """
    Returns the value of a specified setting.  If the setting is not found in the settings dictionary, then
    the user specified default value will be returned.  It no default is specified and nothing is found, then
    None is returned.  If the key isn't in the dictionary, then it will be added and the settings file saved.
    If no filename has been specified up to this point, then a default filename will be assigned and used.
    The settings are SAVED prior to returning.

    :param key: Key used to lookup the setting in the settings dictionary
    :type key: (Any)
    :param default: Value to use should the key not be found in the dictionary
    :type default: (Any)
    :return: Value of specified settings
    :rtype: (Any)
    """
    settings = UserSettings._default_for_function_interface
    return settings.get(key, default)


def user_settings_save(filename=None, path=None):
    """
    Saves the current settings dictionary.  If a filename or path is specified in the call, then it will override any
    previously specitfied filename to create a new settings file.  The settings dictionary is then saved to the newly defined file.

    :param filename: The fFilename to save to. Can specify a path or just the filename. If no filename specified, then the caller's filename will be used.
    :type filename: (str)
    :param path: The (optional) path to use to save the file.
    :type path: (str)
    :return: The full path and filename used to save the settings
    :rtype: (str)
    """
    settings = UserSettings._default_for_function_interface
    return settings.save(filename, path)


def user_settings_load(filename=None, path=None):
    """
    Specifies the path and filename to use for the settings and reads the contents of the file.
    The filename can be a full filename including a path, or the path can be specified separately.
    If  no filename is specified, then the caller's filename will be used with the extension ".json"

    :param filename: Filename to load settings from (and save to in the future)
    :type filename: (str)
    :param path: Path to the file. Defaults to a specific folder depending on the operating system
    :type path: (str)
    :return: The settings dictionary (i.e. all settings)
    :rtype: (dict)
    """
    settings = UserSettings._default_for_function_interface
    return settings.load(filename, path)


def user_settings_file_exists(filename=None, path=None):
    """
    Determines if a settings file exists.  If so a boolean True is returned.
    If either a filename or a path is not included, then the appropriate default
    will be used.

    :param filename: Filename to check
    :type filename: (str)
    :param path: Path to the file. Defaults to a specific folder depending on the operating system
    :type path: (str)
    :return: True if the file exists
    :rtype: (bool)
    """
    settings = UserSettings._default_for_function_interface
    return settings.exists(filename=filename, path=path)


def user_settings_write_new_dictionary(settings_dict):
    """
    Writes a specified dictionary to the currently defined settings filename.

    :param settings_dict: The dictionary to be written to the currently defined settings file
    :type settings_dict: (dict)
    """
    settings = UserSettings._default_for_function_interface
    settings.write_new_dictionary(settings_dict)


def user_settings_silent_on_error(silent_on_error=False):
    """
    Used to control the display of error messages.  By default, error messages are displayed to stdout.

    :param silent_on_error: If True then all error messages are silenced (not displayed on the console)
    :type silent_on_error: (bool)
    """
    settings = UserSettings._default_for_function_interface
    settings.silent_on_error = silent_on_error


def user_settings():
    """
    Returns the current settings dictionary.  If you've not setup the filename for the
    settings, a default one will be used and then read.

    :return: The current settings dictionary
    :rtype: (dict)
    """
    settings = UserSettings._default_for_function_interface
    return settings.get_dict()
