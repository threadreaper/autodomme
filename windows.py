import PySimpleGUI as sG


def main_window(client) -> sG.Window:
    """
    Construct a main program window

    :param client: The client object calling for a window layout.
    :type client: :class:`Client`
    """
    sG.theme(client.options['THEME'].split()[1])

    main_menu = [
        ['&File', ['E&xit']],
        ['&Server', ['Start Server', 'Kill Server', 'Connect to Server']],
        ['&Options', ['Options Menu']]
    ]

    keys = [[]]

    media_player_panel = [
        [sG.T('Host Folder:', size=(40, 1))],
        [sG.Input(client.options['HOST_FOLDER'], size=(22, 1),
                  pad=((5, 0), 3), enable_events=True, k='HOST_FOLDER'),
         sG.B('Browse', k='HOST_BROWSE', metadata='folders',
              pad=((0, 5), 3))],
        [sG.B('', k='BACK', image_filename='icons/back.png'),
         sG.B('', k='PAUSE', image_filename='icons/pause.png'),
         sG.B('', k='PLAY', image_filename='icons/play.png'),
         sG.B('', k='FORWARD', image_filename='icons/forward.png')],
        [sG.Sizer(0, 100)]
    ]

    srv_folder = 'Not Connected' if not client.connected else\
        client.session.srv_folder

    server_media = [
        [sG.T('Server Folder:', size=(40, 1))],
        [sG.Input(srv_folder, size=(22, 1), pad=((5, 0), 3),
                  disabled=True, k='SRV_FOLDER'),
         sG.B('Browse', k='SRV_BROWSE', pad=((0, 5), 3))],
        [sG.B('', k='SRV_BACK', image_filename='icons/back.png'),
         sG.B('', k='SRV_PAUSE', image_filename='icons/pause.png'),
         sG.B('', k='SRV_PLAY', image_filename='icons/play.png'),
         sG.B('', k='SRV_FORWARD', image_filename='icons/forward.png')],
        [sG.Sizer(0, 100)]
    ]

    tab1_layout = keys
    tab2_layout = media_player_panel
    tab3_layout = server_media

    tab_group_layout = [[sG.Tab('Hot Keys', tab1_layout),
                         sG.Tab('My Media', tab2_layout),
                         sG.Tab('Server Media', tab3_layout)]]

    sidebar = [
        [sG.T(" Online Users:")],
        [sG.Multiline(size=(40, 3), k='ONLINE_USERS', do_not_clear=True,
                      auto_refresh=True, disabled=True)],
        [sG.Multiline("", size=(40, 24), do_not_clear=True,
                      autoscroll=True, write_only=True, auto_refresh=True,
                      disabled=True, reroute_cprint=True, k='CHAT')],
        [sG.Input('', size=(24, 1), pad=((5, 0), 3), do_not_clear=False,
                  k='INPUT'),
         sG.Submit(size=(5, 1), pad=((0, 5), 3))],
        [sG.TabGroup(tab_group_layout, k='TABS')]
    ]

    layout = [
        [sG.Menu(main_menu, tearoff=False, pad=(0, 0)),
         sG.Image(None, size=(980, 780), background_color='#000000',
                  k='IMAGE', pad=(0, 0)),
         sG.Column(sidebar, vertical_alignment='top', pad=(0, 0))],
        [sG.StatusBar('', relief=sG.RELIEF_RIDGE, font='ANY 11',
                      size=(40, 2), pad=(5, (0, 5)), k='SERVER_STATUS'),
         sG.StatusBar('Not connected to any server', relief=sG.RELIEF_RIDGE,
                      font='ANY 11', size=(40, 2), pad=((2, 5), (0, 5)),
                      k='CLIENT_STATUS')]
    ]

    win = sG.Window("TeaseAI", layout, margins=(0, 0), size=(1280, 810),
                    return_keyboard_events=True)
    win.finalize()
    win['INPUT'].expand(expand_y=True)
    win['SERVER_STATUS'].expand(True)
    win['HOST_FOLDER'].expand(False, True)
    win['SRV_FOLDER'].expand(False, True)
    win['HOST_BROWSE'].expand(True, True)
    win['SRV_BROWSE'].expand(True, True)
    win.finalize()

    return win


def options_window(client) -> sG.Window:
    """
    Construct the options menu

    :param client: The client object calling the options window.
    :type server: :class:`Client`
    :return: An instance of `PySimpleGUI.Window`.
    :rtype: :class:`PySimpleGUI.Window`
    """
    sG.theme(client.options['THEME'].split()[1])

    gen_col_one = [
        [sG.T('General Options')],
        [sG.CB('Automatic Updates', enable_events=True, k='UPDATES',
               default=client.options['UPDATES'])],
        [sG.T('Username for Chat:')],
        [sG.In(client.options['CHAT_NAME'], enable_events=True, size=(20, 1),
               k='CHAT_NAME')],
        [sG.HorizontalSeparator()],
        [sG.T('Client Options')],
        [sG.T('Server Address', size=(20, 1)),
         sG.In(client.options['SERVER_ADDRESS'], size=(20, 1),
               enable_events=True, k='SERVER_ADDRESS')],
        [sG.T('Server Port', size=(20, 1)),
         sG.In(client.options['SERVER_PORT'], size=(20, 1), enable_events=True,
               k='SERVER_PORT')],
        [sG.HorizontalSeparator()],
        [sG.T('Slideshow Options')],
        [sG.CB('Randomize Order', default=client.options['RANDOMIZE'],
               k='RANDOMIZE', tooltip='When enabled, randomizes the \
               order of image slideshows', enable_events=True)],
        [sG.HorizontalSeparator()],
        [sG.T("Theme Options:")],
        [sG.T('This window will refresh to preview your chosen theme.\n'
              'Restart the program to apply your theme to all windows.')],
        [sG.Listbox(values=[str(i+1)+'. '+x for i, x in
                            enumerate(sG.theme_list())], enable_events=True,
                    select_mode=sG.LISTBOX_SELECT_MODE_BROWSE, size=(20, 12),
                    default_values=client.options['THEME'], k='THEME',)],
    ]

    gen_col_two = [
        [sG.T('Boss key:')],
        [sG.In('ESCAPE', disabled=True, k='BOSS_KEY', size=(20, 1)),
         sG.B('Bind', k='BIND_BOSS_KEY', disabled=True)],
        [sG.Sizer(0, 500)]
    ]

    general_options = [
        [sG.Col(gen_col_one),
         sG.VerticalSeparator(),
         sG.Col(gen_col_two)]
    ]

    local_media_options = [
        [sG.T('Local Media Options')],
        [sG.T(' Boobs Directory:')],
        [sG.B('', image_filename='icons/browse_folder.png', k='BROWSE_BOOBS'),
         sG.In(client.options['BOOBS_FOLDER'], k='BOOBS_FOLDER',
               disabled=True)],
        [sG.T(' Butts Directory:')],
        [sG.B('', image_filename='icons/browse_folder.png', k='BROWSE_BUTTS'),
         sG.In(client.options['BUTTS_FOLDER'], k='BUTTS_FOLDER',
               disabled=True)]
    ]

    server_options = [
        [sG.T('Host Options')],
        [sG.T('Hostname/IP', size=(15, 1)),
         sG.In(client.options['HOSTNAME'], size=(20, 1), enable_events=True,
               k='HOSTNAME')],
        [sG.T('Host Port', size=(15, 1)),
         sG.In(client.options['HOST_PORT'], size=(20, 1), enable_events=True,
               k='PORT')],
        [sG.T('Host Folder', size=(15, 1)),
         sG.In(client.options['HOST_FOLDER'], size=(20, 1), enable_events=True,
               k='SRV_folder'),
         sG.B('Browse')],
        [sG.HorizontalSeparator()],
        [sG.T('Domme Options:')],
        [sG.T("Domme's Name:", size=(15, 1)),
         sG.In(client.options['DOMME_NAME'], size=(20, 1),
               k='SRV_domme-name', enable_events=True)],
        [sG.HorizontalSeparator()],
        [sG.T('Slideshow Options')],
        [sG.CB('Randomize Order',
               default=(False, True)[client.options['RANDOMIZE'] == '1'],
               k='SRV_randomize', enable_events=True)],
        [sG.CB('Include Subfolders',
               default=(False, True)[client.options['SUBFOLDERS'] == '1'],
               k='SRV_subfolders', enable_events=True)]
    ]

    tab_group_layout = [[sG.Tab('General', general_options),
                         sG.Tab('Local Media', local_media_options),
                         sG.Tab('Server', server_options)]]

    layout = [[sG.TabGroup(tab_group_layout)]]

    def _calc_vscroll() -> float:
        """
        Calculates and returns the vertical scroll offset for the theme
        listbox.

        :return: The vertical scroll offset.
        :rtype: float
        """
        offset = client.options['THEME'].split('.')[0]
        themes = len(sG.theme_list())
        return round(int(offset) / themes, 2) - .05

    dialog = sG.Window("Options", layout, finalize=True)
    dialog['THEME'].set_vscroll_position(_calc_vscroll())

    return dialog


def login_window(client, last):
    """Constructs a login window"""
    layout = [
            [sG.T(last, size=(30, 1), visible=(False, True)[last != ''])],
            [sG.T("Username:", size=(15, 1)),
             sG.Input(default_text=client.options['USERNAME'], size=(20, 1),
                      k='USERNAME')],
            [sG.T("Password:", size=(15, 1)),
             sG.Input('', size=(20, 1), k='PASSWORD', password_char='*')],
            [sG.Checkbox('Save credentials',
                         default=client.options['SAVE_CREDENTIALS'],
                         k='CREDENTIALS')],
            [sG.Submit(), sG.Cancel()]
        ]

    return sG.Window("Server Requesting Authentication", layout)
