﻿import urllib
import time
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs
import xmltodict
from datetime import datetime, timedelta, date
from traceback import format_exc
from urlparse import urlparse, parse_qs

from resources.lib.game_common import *

class myPlayer(xbmc.Player):
    def __init__(self, parent, *args, **kwargs):
        xbmc.Player.__init__(self)
        self.dawindow = parent

    def onPlayBackStarted(self):
        self.dawindow.close()

    def onPlayBackStopped(self):
        self.onPlayBackEnded()

    def onPlayBackEnded(self):
        self.dawindow.list_refill = 'true'
        self.dawindow.doModal()

class GamepassGUI(xbmcgui.WindowXMLDialog):
    #Class declarations
    season_list = ''
    season_items = []
    clicked_season = -1
    weeks_list = ''
    weeks_items = []
    clicked_week = -1
    games_list = ''
    games_items = []
    clicked_game = -1
    live_list = ''
    live_items = []
    selectedSeason = ''
    selectedWeek = ''
    main_selection = ''
    player = ''
    list_refill = 'false'
    focusId = 100
    seasons_and_weeks = get_seasons_and_weeks()


    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        self.action_previous_menu = (9, 10, 92, 216, 247, 257, 275, 61467, 61448)

    def onInit(self):
        self.window = xbmcgui.Window(xbmcgui.getCurrentWindowDialogId())
        self.season_list = self.window.getControl(210)
        self.weeks_list = self.window.getControl(220)
        self.games_list = self.window.getControl(230)
        self.live_list = self.window.getControl(240)

        if subscription == '0': # GamePass
            self.window.setProperty('gamepass', 'true')

        if self.list_refill == 'true':
            self.season_list.reset()
            self.season_list.addItems(self.season_items)
            self.weeks_list.reset()
            self.weeks_list.addItems(self.weeks_items)
            self.games_list.reset()
            self.games_list.addItems(self.games_items)
            self.live_list.reset()
            self.live_list.addItems(self.live_items)
        else:
            self.window.setProperty('NW_clicked', 'false')
            self.window.setProperty('GP_clicked', 'false')

        try:
            self.setFocus(self.window.getControl(self.focusId))
        except:
            addon_log('Focus not possible: %s' %self.focusId)

    def coloring(self, text, meaning):
        if meaning == "disabled":
            color = "FF000000"
        elif meaning == "disabled-info":
            color = "FF111111"
        colored_text = "[COLOR=%s]%s[/COLOR]" %(color, text)
        return colored_text

    def display_seasons(self):
        self.season_items = []
        for season in sorted(self.seasons_and_weeks.keys(), reverse=True):
            listitem = xbmcgui.ListItem(season)
            self.season_items.append(listitem)
        self.season_list.addItems(self.season_items)

    def display_nfl_network_archive(self):
        self.weeks_items = []
        shows = get_shows(self.selected_season)
        for show_name in shows:
            listitem = xbmcgui.ListItem(show_name)
            self.weeks_items.append(listitem)

        self.weeks_list.addItems(self.weeks_items)

    def display_weeks_games(self):
        self.games_items = []
        self.games_list.reset()
        games = get_weeks_games(self.selected_season, self.selected_week)

        date_time_format = '%Y-%m-%dT%H:%M:%S.000'
        for game in games:
            if game['homeTeam']['name'] is None: # sometimes the first item is empty
                continue

            isLive = 'false'
            isPlayable = 'true'
            home_team = game['homeTeam']
            away_team = game['awayTeam']
            game_name_shrt = '[B]%s[/B] at [B]%s[/B]' %(away_team['name'], home_team['name'])
            game_name_full = '[B]%s %s[/B] at [B]%s %s[/B]' %(away_team['city'], away_team['name'], home_team['city'], home_team['name'])
            game_version_ids = {}
            for key, value in {'Condensed': 'condensedId', 'Full': 'programId', 'Live': 'id'}.items():
                try:
                    game_version_ids[key] = game[value]
                except KeyError:
                    pass

            if game.has_key('isLive') and not game.has_key('gameEndTimeGMT'): # sometimes isLive lies
                game_info = 'Live'
                isLive = 'true'
            elif game.has_key('gameEndTimeGMT'):
                try:
                    start_time = datetime(*(time.strptime(game['gameTimeGMT'], date_time_format)[0:6]))
                    end_time = datetime(*(time.strptime(game['gameEndTimeGMT'], date_time_format)[0:6]))
                    game_info = 'Final [CR] Duration: %s' %time.strftime('%H:%M:%S', time.gmtime((end_time - start_time).seconds))
                except:
                    addon_log(format_exc())
                    if game.has_key('result'):
                        game_info = 'Final'
            else:
                try:
                    # may want to change this to game['gameTimeGMT'] or do a setting maybe
                    game_datetime = datetime(*(time.strptime(game['date'], date_time_format)[0:6]))
                    game_info = game_datetime.strftime('%A, %b %d - %I:%M %p')
                    if datetime.utcnow() < datetime(*(time.strptime(game['gameTimeGMT'], date_time_format)[0:6])):
                        isPlayable = 'false'
                        game_name_full = self.coloring(game_name_full, "disabled")
                        game_name_shrt = self.coloring(game_name_shrt, "disabled")
                        game_info = self.coloring(game_info, "disabled-info")
                except:
                    game_datetime = game['date'].split('T')
                    game_info = game_datetime[0] + '[CR]' + game_datetime[1].split('.')[0] + ' ET'

            listitem = xbmcgui.ListItem(game_name_shrt, game_name_full)
            listitem.setProperty('away_thumb', 'http://i.nflcdn.com/static/site/5.31/img/logos/teams-matte-80x53/%s.png' %away_team['id'])
            listitem.setProperty('home_thumb', 'http://i.nflcdn.com/static/site/5.31/img/logos/teams-matte-80x53/%s.png' %home_team['id'])
            listitem.setProperty('game_info', game_info)
            listitem.setProperty('is_game', 'true')
            listitem.setProperty('is_show', 'false')
            listitem.setProperty('isPlayable', isPlayable)
            listitem.setProperty('isLive', isLive)
            params = {'name': game_name_full, 'url': game_version_ids}
            url = '%s?%s' %(sys.argv[0], urllib.urlencode(params))
            listitem.setProperty('url', url)
            self.games_items.append(listitem)

            self.games_list.addItems(self.games_items)

    def display_shows_episodes(self, show_name, season):
        self.games_items = []
        items = get_shows_episodes(show_name, season)

        image_path = 'http://smb.cdn.neulion.com/u/nfl/nfl/thumbs/'
        for i in items:
            try:
                listitem = xbmcgui.ListItem('[B]%s[/B]' %show_name)
                listitem.setProperty('game_info', i['name'])
                listitem.setProperty('away_thumb', image_path + i['image'])
                listitem.setProperty('url', i['publishPoint'])
                listitem.setProperty('is_game', 'false')
                listitem.setProperty('is_show', 'true')
                listitem.setProperty('isPlayable', 'true')
                self.games_items.append(listitem)
            except:
                addon_log('Exception adding archive directory: %s' %format_exc())
                addon_log('Directory name: %s' %i['name'])
        self.games_list.addItems(self.games_items)

    def playUrl(self, url):
        player = myPlayer(parent=self)
        player.play(url)

        while player.isPlaying():
            xbmc.sleep(2000)

        del player

    def init(self, level):
        if level == 'season':
            self.weeks_items = []
            self.weeks_list.reset()
            self.games_list.reset()
            self.clicked_week = -1
            self.clicked_game = -1

            if self.clicked_season > -1: # unset previously selected season
                self.season_list.getListItem(self.clicked_season).setProperty('clicked', 'false')

            self.season_list.getSelectedItem().setProperty('clicked', 'true')
            self.clicked_season = self.season_list.getSelectedPosition()
        elif level == 'week/show':
            self.games_list.reset()
            self.clicked_game = -1

            if self.clicked_week > -1: # unset previously selected week/show
                self.weeks_list.getListItem(self.clicked_week).setProperty('clicked', 'false')

            self.weeks_list.getSelectedItem().setProperty('clicked', 'true')
            self.clicked_week = self.weeks_list.getSelectedPosition()
        elif level == 'game/episode':
            if self.clicked_game > -1: # unset previously selected game/episode
                self.games_list.getListItem(self.clicked_game).setProperty('clicked', 'false')

            self.games_list.getSelectedItem().setProperty('clicked', 'true')
            self.clicked_game = self.games_list.getSelectedPosition()

    def ask_bitrate(self, bitrates):
        options = []
        for bitrate in bitrates:
            options.append(bitrate + ' Kbps')
        dialog = xbmcgui.Dialog()
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        ret = dialog.select(language(30003), options)
        return bitrates[ret]

    def select_bitrate(self, manifest_bitrates=None):
        bitrate_setting = int(addon.getSetting('preferred_bitrate'))
        bitrate_values = ['4500', '3000', '2400', '1600', '1200', '800', '400']
        if bitrate_setting == 0:
            preferred_bitrate = 'highest'
        elif bitrate_setting < 7: # specific bitrate
            preferred_bitrate = bitrate_values[bitrate_setting -1]
        else:
            preferred_bitrate = 'ask'

        if manifest_bitrates:
            manifest_bitrates.sort(key=int, reverse=True)
            if preferred_bitrate == 'highest':
                return manifest_bitrates[0]
            elif preferred_bitrate in manifest_bitrates:
                return preferred_bitrate
            else:
                return self.ask_bitrate(manifest_bitrates)
        else:
            if preferred_bitrate == 'highest':
                return bitrate_values[0]
            elif preferred_bitrate != 'ask':
                return preferred_bitrate
            else:
                return self.ask_bitrate(bitrate_values)

    # returns a gameid, while honoring user preference when applicable
    def select_version(self, game_version_ids):
        preferred_version = int(addon.getSetting('preferred_game_version'))

        # the full version is always available, but not always the condensed
        game_id = game_version_ids['Full']
        versions = [language(30014)]

        if game_version_ids.has_key('Condensed'):
            versions.append(language(30015))
            if preferred_version == 1:
                game_id = game_version_ids['Condensed']

        # user wants to be asked to select version
        if preferred_version == 2:
            dialog = xbmcgui.Dialog()
            xbmc.executebuiltin("Dialog.Close(busydialog)")
            ret = dialog.select(language(30016), versions)
            if ret == 1:
                game_id = game_version_ids['Condensed']

        return game_id

    def onFocus(self, controlId):
        #save currently focused list
        if controlId in[210, 220, 230, 240]:
            self.focusId = controlId

    def onClick(self, controlId):
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        if controlId in[110, 120, 130]:
            self.games_list.reset()
            self.weeks_list.reset()
            self.season_list.reset()
            self.live_list.reset()
            self.clicked_game = -1
            self.clicked_week = -1
            self.clicked_season = -1

            if controlId == 110:
                self.main_selection = 'GamePass/Rewind'
                self.window.setProperty('NW_clicked', 'false')
                self.window.setProperty('GP_clicked', 'true')
            elif controlId == 130:
                self.main_selection = 'NFL Network'
                self.window.setProperty('NW_clicked', 'true')
                self.window.setProperty('GP_clicked', 'false')
                self.live_items = []
                if subscription == '0': # GamePass
                    listitem = xbmcgui.ListItem('NFL Network - Live', 'NFL Network - Live')
                    self.live_items.append(listitem)

                    # Check whether RedZone is on Air
                    url = 'http://gamepass.nfl.com/nflgp/servlets/simpleconsole'
                    simple_data = make_request(url, {'isFlex':'true'})
                    simple_dict = xmltodict.parse(simple_data)['result']
                    if simple_dict['rzPhase'] == 'in':
                        listitem = xbmcgui.ListItem('NFL RedZone - Live', 'NFL RedZone - Live')
                        self.live_items.append(listitem)

                self.live_list.addItems(self.live_items)

            self.display_seasons()
            xbmc.executebuiltin( "Dialog.Close(busydialog)" )
            return

        if self.main_selection == 'GamePass/Rewind':
            if controlId == 210: # season is clicked
                self.init('season')
                self.selected_season = self.season_list.getSelectedItem().getLabel()
                weeks = self.seasons_and_weeks[self.selected_season]

                for week_code, week in sorted(weeks.iteritems()):
                    future = 'false'
                    try:
                        week_date = week['start'] + ' 06:00'
                        week_time = int(time.mktime(time.strptime(week_date, '%Y%m%d %H:%M')))
                        time_utc = str(datetime.utcnow())[:-7]
                        time_now = int(time.mktime(time.strptime(time_utc, '%Y-%m-%d %H:%M:%S')))
                        if week_time > time_now:
                            future = 'true'
                    except KeyError: # some old seasons don't provide week dates
                        pass

                    listitem = xbmcgui.ListItem(week['@label'].title())
                    listitem.setProperty('week_code', week_code)
                    listitem.setProperty('future', future)
                    self.weeks_items.append(listitem)
                self.weeks_list.addItems(self.weeks_items)
            elif controlId == 220: # week is clicked
                self.init('week/show')
                self.selected_week = self.weeks_list.getSelectedItem().getProperty('week_code')

                self.display_weeks_games()
            elif controlId == 230: # game is clicked
                selectedGame = self.games_list.getSelectedItem()
                if selectedGame.getProperty('isPlayable') == 'true':
                    self.init('game/episode')

                    url = selectedGame.getProperty('url')
                    params = parse_qs(urlparse(url).query)
                    for i in params.keys():
                        params[i] = params[i][0]
                    game_version_ids = eval(params['url'])

                    if selectedGame.getProperty('isLive') == 'true':
                        game_live_url = get_live_url(game_version_ids['Live'], self.select_bitrate())
                        self.playUrl(game_live_url)
                    else:
                        game_id = self.select_version(game_version_ids)
                        game_manifest = get_game_manifest(game_id)
                        bitrate = self.select_bitrate(game_manifest.keys())
                        game_url = game_manifest[bitrate]['full_url']
                        self.playUrl(game_url)
        elif self.main_selection == 'NFL Network':
            if controlId == 210: # season is clicked
                self.init('season')
                self.selected_season = self.season_list.getSelectedItem().getLabel()

                self.display_nfl_network_archive()
            elif controlId == 220: # show is clicked
                self.init('week/show')
                show_name = self.weeks_list.getSelectedItem().getLabel()

                self.display_shows_episodes(show_name, self.selected_season)
            elif controlId == 230: # episode is clicked
                self.init('game/episode')
                url = self.games_list.getSelectedItem().getProperty('url')
                episode_manifest = get_episode_manifest(url)
                bitrate = self.select_bitrate(episode_manifest.keys())
                episode_url = episode_manifest[bitrate]['full_url']
                self.playUrl(episode_url)
            elif controlId == 240: # Live content (though not games)
                show_name = self.live_list.getSelectedItem().getLabel()
                if show_name == 'RedZone - Live':
                    redzone_live_url = get_live_url('rz', self.select_bitrate())
                    self.playUrl(redzone_live_url)
                elif show_name == 'NFL Network - Live':
                    nfl_network_url = get_live_url('nfl_network', self.select_bitrate())
                    self.playUrl(nfl_network_url)

        xbmc.executebuiltin("Dialog.Close(busydialog)")

if (__name__ == "__main__"):
    addon_log('script starting')

    addon_path = xbmc.translatePath(addon.getAddonInfo('path'))

    if not xbmcvfs.exists(addon_profile):
        xbmcvfs.mkdir(addon_profile)

    try:
        if subscription == '0': # Game Pass
            login_gamepass(addon.getSetting('email'), addon.getSetting('password'))
        else: # Game Rewind
            login_rewind(addon.getSetting('gr_email'), addon.getSetting('gr_password'))
    except LoginFailure as e:
        dialog = xbmcgui.Dialog()
        if e.value == 'Game Rewind Blackout':
            addon_log('Rewind is in blackout.')
            dialog.ok(language(30018),
                      'Due to broadcast restrictions',
                      'NFL Game Rewind is currently unavailable.',
                      'Please try again later.')
        else:
            addon_log('auth failure')
            dialog.ok('Login Failed',
                      'Logging into NFL Game Pass/Rewind failed.',
                      'Make sure your account information is correct.')
    except:
        addon_log(format_exc())
        dialog = xbmcgui.Dialog()
        dialog.ok('Epic Failure',
                  'Some bad jujumagumbo just went down.',
                  'Please enable debuging, and submit a bug report.')
        sys.exit(0)

    gui = GamepassGUI('script-gamepass.xml', addon_path)
    gui.doModal()
    del gui

addon_log('script finished')
