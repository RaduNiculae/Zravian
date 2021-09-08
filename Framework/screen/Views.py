from Framework.screen.Login import ACCOUNT
import re
from enum import IntEnum, Enum
from Framework.utils.Constants import Tribe, get_ACCOUNT, get_XPATH
from Framework.utils.Logger import get_projectLogger
from Framework.utils.SeleniumUtils import SWS


logger = get_projectLogger()
ACCOUNT = get_ACCOUNT()
XPATH = get_XPATH()
TRIBE = None


class LevelUpMode(IntEnum):
    OFF = 0
    ON = 1


class Screens(Enum):
    OVERVIEW = 'village1'
    VILLAGE = 'village2'
    MAP = 'map'
    STATS = 'statistics'


def getTribe(sws : SWS):
    """
    Gets the tribe.

    Parameters:
        - sws (SWS): Selenium Web Scraper
        - driver (WebDriver): Used to interact with the webpage.

    Returns:
        - Tribe if operation was successful, None otherwise.
    """
    global TRIBE
    if not TRIBE:
        if sws.isVisible(XPATH.ROMAN_TASK_MASTER):
            TRIBE = Tribe.ROMANS
        elif sws.isVisible(XPATH.TEUTON_TASK_MASTER):
            TRIBE = Tribe.TEUTONS
        elif sws.isVisible(XPATH.GAUL_TASK_MASTER):
            TRIBE = Tribe.GAULS
        else:
            logger.warning('In function getTribe: Could not identify the tribe by task manager')
    if not TRIBE:
        initialURL = sws.getCurrentUrl()
        PROFILE_URL = f'{ACCOUNT.URL}profile.php'
        if sws.get(PROFILE_URL):
            text = sws.getElementAttribute(XPATH.PROFILE_TRIBE, 'text')
            if text:
                text = text[0].split()[-1].upper()
                for tr in Tribe:
                    if tr.name == text:
                        TRIBE = tr
                        break
                else:
                    logger.error('In function getTribe: Tribe could not be determined')
                if not sws.get(initialURL):
                    TRIBE = None
                    logger.error('In function getTribe: Could not get back to initial page')
            else:
                logger.error('In function getTribe: Could not find text element')
        else:
            logger.error('In function getTribe: Could not get profile page')
    return TRIBE


def get_current_screen(sws : SWS):
    """
    Tells which of the following screens is active:
      - Overview
      - Village
      - Map
      - Statistics
      - None, if you are inside a menu i.e. Constructing a new building.

    Parameters:
        - sws (SWS): Selenium Web Scraper

    Returns:
        - Current screen if operation was successful, None otherwise.
    """
    for view in Screens:
        if view.value in sws.getCurrentUrl():
            return view
    return None


def get_level_up_mode(sws : SWS):
    """
    Checks level up mode status.

    Parameters:
        - sws (SWS): Selenium Web Scraper

    Returns:
        - LevelUpMode if operation was successful, None otherwise.
    """
    status = None
    currentView = get_current_screen(sws)
    if currentView == Screens.OVERVIEW or currentView == Screens.VILLAGE:
        coneTitle = sws.getElementAttribute(XPATH.LEVEL_UP_CONE, 'title')
        if coneTitle:
            coneTitle = coneTitle[0]
            if "enable" in coneTitle:
                status = LevelUpMode.OFF
            elif 'disable' in coneTitle:
                status = LevelUpMode.ON
            else:
                logger.error('In function get_level_up_mode: Unknown cone status')
        else:
            logger.error('In function get_level_up_mode: Level up cone not found')
    else:
        logger.error('In function get_level_up_mode: Level up mode is available just \
            in overview and village')
    return status


def set_level_up_mode(sws : SWS, levelUpMode):
    """
    Sets level up mode.

    Parameters:
        - sws (SWS): Selenium Web Scraper
        - levelUpMode (LevelUpMode): Will set level up mode to this.

    Returns:
        - True if the operation was successful, False otherwise.
    """
    status = False
    if isinstance(levelUpMode, LevelUpMode):
        currentView = get_current_screen(sws)
        if currentView == Screens.OVERVIEW or currentView == Screens.VILLAGE:
            coneTitle = sws.getElementAttribute(XPATH.LEVEL_UP_CONE, 'title')
            if coneTitle:
                coneTitle = coneTitle[0]
                if (levelUpMode == LevelUpMode.ON and "enable" in coneTitle) or \
                        (levelUpMode == LevelUpMode.OFF and "disable" in coneTitle):
                    if sws.clickElement(XPATH.LEVEL_UP_CONE, refresh=True):
                        status = True
                    else:
                        logger.error('In function set_level_up_mode: Failed to click LEVEL_UP_CONE')
                else:
                    status = True
            else:
                logger.error('In function set_level_up_mode: Cone title could not be found')
        else:
            logger.error('In function set_level_up_mode: Level up mode is available just \
                in overview and village')
    else:
        logger.error('In function set_level_up_mode: Invalid parameter levelUpMode')
    return status


def __move_to_screen(sws : SWS, screen, forced=False):
    """
    Ensures that the current view is the desired screen.

    Parameters:
        - sws (SWS): Selenium Web Scraper
        - screen (Screen): Desired screen.
        - forced (Boolean): If True will refresh the screen even tho
            is the desired one, False by default

    Returns:
        - True if the operation was successful, False otherwise.
    """
    URLS = {
        Screens.OVERVIEW: f'{ACCOUNT.URL}village1.php',
        Screens.VILLAGE: f'{ACCOUNT.URL}village2.php',
        Screens.MAP: f'{ACCOUNT.URL}map.php',
        Screens.STATS: f'{ACCOUNT.URL}statistics.php'
    }
    status = False
    if isinstance(screen, Screens):
        if screen != get_current_screen(sws) or forced:
            if sws.get(URLS[screen]):
                status = True
            else:
                logger.error('In function __move_to_screen: Failed to move to screen')
        else:
            status = True
    else:
        logger.error('In function __move_to_screen: Invalid parameter screen')
    return status


def move_to_overview(sws : SWS, forced=False):
    """
    Changes current screen to overview.

    Parameters:
        - sws (SWS): Selenium Web Scraper
        - forced (Boolean): If true will refresh the page.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __move_to_screen(sws, Screens.OVERVIEW, forced)


def move_to_village(sws : SWS, forced=False):
    """
    Changes current screen to village.

    Parameters:
        - sws (SWS): Selenium Web Scraper
        - forced (Boolean): If true will refresh the page.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __move_to_screen(sws, Screens.VILLAGE, forced)


def move_to_map(sws : SWS, forced=False):
    """
    Changes current screen to map.

    Parameters:
        - sws (SWS): Selenium Web Scraper
        - forced (Boolean): If true will refresh the page.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __move_to_screen(sws, Screens.MAP, forced)


def move_to_stats(sws : SWS, forced=False):
    """
    Changes current screen to stats.

    Parameters:
        - sws (SWS): Selenium Web Scraper
        - forced (Boolean): If true will refresh the page.

    Returns:
        - True if operation is successful, False otherwise.
    """
    return __move_to_screen(sws, Screens.STATS, forced)


def get_storage(sws : SWS):
    """
    Checks for storage for each resource.

    Parameters:
        - sws (SWS): Selenium Web Scraper
    
    Returns:
        - List of 4 Ints if operation was successful, None otherwise.
    """
    storage = []
    if sws.isVisible(XPATH.PRODUCTION_LUMBER):
        lumber = sws.getElementAttribute(XPATH.PRODUCTION_LUMBER, 'text')
        if lumber:
            lumber = lumber[0].split('/')
            storage.append((int(lumber[0]), int(lumber[1])))
    if sws.isVisible(XPATH.PRODUCTION_CLAY):
        clay =  sws.getElementAttribute(XPATH.PRODUCTION_CLAY, 'text')
        if clay:
            clay = clay[0].split('/')
            storage.append((int(clay[0]), int(clay[1])))
    if sws.isVisible(XPATH.PRODUCTION_IRON):
        iron = sws.getElementAttribute(XPATH.PRODUCTION_IRON, 'text')
        if iron:
            iron = iron[0].split('/')
            storage.append((int(iron[0]), int(iron[1])))
    if sws.isVisible(XPATH.PRODUCTION_CROP):
        crop = sws.getElementAttribute(XPATH.PRODUCTION_CROP, 'text')
        if crop:
            crop = crop[0].split('/')
            storage.append((int(crop[0]), int(crop[1])))
    if len(storage) != 4:
        storage = None
        logger.error('In function get_storage: Less than 4 values found')
    return storage


def get_production(sws : SWS):
    """
    Checks for production for each resource.

    Parameters:
        - sws (SWS): Selenium Web Scraper
    
    Returns:
        - List of 4 Ints if operation was successful, None otherwise.
    """
    production = []
    lumber = sws.getElementAttribute(XPATH.PRODUCTION_LUMBER, 'title')
    if lumber:
        production.append(int(lumber[0]))
    clay = sws.getElementAttribute(XPATH.PRODUCTION_CLAY, 'title')
    if clay:
        production.append(int(clay[0]))
    iron = sws.getElementAttribute(XPATH.PRODUCTION_IRON, 'title')
    if iron:
        production.append(int(iron[0]))
    crop = sws.getElementAttribute(XPATH.PRODUCTION_CROP, 'title')
    if crop:
        production.append(int(crop[0]))
    if len(production) != 4:
        production = None
        logger.error('In function get_production: Less than 4 values found')
    return production
