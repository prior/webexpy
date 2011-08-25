from lxml import etree
import urllib2
import datetime
import dateutil.parser
import pytz
import pprint


WEBEX_TIMEZONE_DATA = (  # webex_timezone_id, webex_timezone, python_timezone_label
    (0, 'GMT-12:00, Dateline (Eniwetok)', None), # has no standard pytz label available
    (1, 'GMT-11:00, Samoa (Samoa)', 'Pacific/Apia'), # GMT-11:00 Samoa best guess
    (2, 'GMT-10:00, Hawaii (Honolulu)', 'Pacific/Honolulu'),
    (3, 'GMT-09:00, Alaska (Anchorage)', 'America/Anchorage'),
    (4, 'GMT-08:00, Pacific (San Jose)', 'America/Los_Angeles'),
    (5, 'GMT-07:00, Mountain (Arizona)', 'America/Phoenix'),
    (6, 'GMT-07:00, Mountain (Denver)', 'America/Denver'),
    (7, 'GMT-06:00, Central (Chicago)', 'America/Chicago'),
    (8, 'GMT-06:00, Mexico (Mexico City, Tegucigalpa)', 'America/Mexico_City'),
    (9, 'GMT-06:00, Central (Regina)', 'America/Regina'),
    (10, 'GMT-05:00, S. America Pacific (Bogota)', 'America/Bogota'),
    (11, 'GMT-05:00, Eastern (New York)', 'America/New_York'),
    (12, 'GMT-05:00, Eastern (Indiana)', 'America/Indiana/Indianapolis'),
    (13, 'GMT-04:00, Atlantic (Halifax)', 'America/Halifax'),
    (14, 'GMT-04:00, S. America Western (Caracas)', 'America/Caracas'),
    (15, 'GMT-03:30, Newfoundland (Newfoundland)', 'America/St_Johns'), # GMT-03:30 Newfoundland best guess
    (16, 'GMT-03:00, S. America Eastern (Brasilia)', 'America/Fortaleza'), # GMT-03:00 Brasilia best guess
    (17, 'GMT-03:00, S. America Eastern (Buenos Aires)', 'America/Buenos_Aires'),
    (18, 'GMT-02:00, Mid-Atlantic (Mid-Atlantic)', 'America/Noronha'), # GMT-02:00 Mid-Atlantic best guess
    (19, 'GMT-01:00, Azores (Azores)', 'Atlantic/Azores'),
    (20, 'GMT+00:00, Greenwich (Casablanca)', 'Africa/Casablanca'),
    (21, 'GMT+00:00, GMT (London)', 'Europe/London'),
    (22, 'GMT+01:00, Europe (Amsterdam)', 'Europe/Amsterdam'),
    (23, 'GMT+01:00, Europe (Berlin)', 'Europe/Paris'),
    (24, None, None),
    (25, 'GMT+01:00, Europe (Paris)', 'Europe/Berlin'),
    (26, 'GMT+02:00, Greece (Athens)', 'Europe/Athens'),
    (27, None, None),
    (28, 'GMT+02:00, Egypt (Cairo)', 'Africa/Cairo'),
    (29, 'GMT+02:00, South Africa (Pretoria)', 'Africa/Johannesburg'), # GMT+02:00 Pretoria best guess
    (30, 'GMT+02:00, Northern Europe (Helsinki)', 'Europe/Helsinki'),
    (31, 'GMT+02:00, Israel (Tel Aviv)', 'Asia/Jerusalem'), # GMT+02:00 Tel Aviv best guess
    (32, 'GMT+03:00, Saudi Arabia (Baghdad)', 'Asia/Baghdad'),
    (33, 'GMT+03:00, Russian (Moscow)', 'Europe/Moscow'),
    (34, 'GMT+03:00, Nairobi (Nairobi)', 'Africa/Nairobi'),
    (35, 'GMT+03:30, Iran (Tehran)', 'Asia/Tehran'),
    (36, 'GMT+04:00, Arabian (Abu Dhabi, Muscat)', 'Asia/Muscat'),
    (37, 'GMT+04:00, Baku (Baku)', 'Asia/Baku'),
    (38, 'GMT+04:30, Afghanistan (Kabul)', 'Asia/Kabul'),
    (39, 'GMT+05:00, West Asia (Ekaterinburg)', 'Asia/Yekaterinburg'),
    (40, 'GMT+05:00, West Asia (Islamabad)', 'Asia/Karachi'), # GMT+5:00 Islamabad best guess
    (41, 'GMT+05:30, India (Bombay)', 'Asia/Kolkata'), # GMT+05:30 Bombay best guess
    (42, 'GMT+06:00, Columbo (Columbo)', 'Indian/Chagos'), # GMT+06:00 Columbo best guess
    (43, 'GMT+06:00, Central Asia (Almaty)', 'Asia/Almaty'),
    (44, 'GMT+07:00, Bangkok (Bangkok)', 'Asia/Bangkok'),
    (45, 'GMT+08:00, China (Beijing)', 'Asia/Shanghai'),
    (46, 'GMT+08:00, Australia Western (Perth)', 'Australia/Perth'),
    (47, 'GMT+08:00, Singapore (Singapore)', 'Asia/Singapore'),
    (48, 'GMT+08:00, Taipei (Hong Kong)', 'Asia/Taipei'),
    (49, 'GMT+09:00, Tokyo (Tokyo)', 'Asia/Tokyo'),
    (50, 'GMT+09:00, Korea (Seoul)', 'Asia/Seoul'),
    (51, 'GMT+09:00, Yakutsk (Yakutsk)', 'Asia/Yakutsk'),
    (52, 'GMT+09:30, Australia Central (Adelaide)', 'Australia/Adelaide'),
    (53, 'GMT+09:30, Australia Central (Darwin)', 'Australia/Darwin'),
    (54, 'GMT+10:00, Australia Eastern (Brisbane)', 'Australia/Brisbane'),
    (55, 'GMT+10:00, Australia Eastern (Sydney)', 'Australia/Sydney'),
    (56, 'GMT+10:00, West Pacific (Guam)', 'Pacific/Guam'),
    (57, 'GMT+10:00, Tasmania (Hobart)', 'Australia/Hobart'),
    (58, 'GMT+10:00, Vladivostok (Vladivostok)', 'Asia/Vladivostok'),
    (59, 'GMT+11:00, Central Pacific (Solomon Is)', 'Pacific/Guadalcanal'), # GMT+11:00 Solomon Is best guess
    (60, 'GMT+12:00, New Zealand (Wellington)', 'Pacific/Auckland'), # GMT+12:00 Wellington best guess
    (61, 'GMT+12:00, Fiji (Fiji)', 'Pacific/Fiji'),
)

# build id to tzinfo map
WEBEX_TIMEZONE_ID_TO_TZINFO_MAP = {}
for timezone_id, webex_label, tz_label in WEBEX_TIMEZONE_DATA:
    if tz_label is not None:
        WEBEX_TIMEZONE_ID_TO_TZINFO_MAP[timezone_id] = pytz.timezone(tz_label)

# build tzinfo to id map
TZINFO_TO_WEBEX_TIMEZONE_ID_MAP = {}
for timezone_id, webex_label, tz_label in WEBEX_TIMEZONE_DATA:
    if tz_label is not None:
        TZINFO_TO_WEBEX_TIMEZONE_ID_MAP[pytz.timezone(tz_label)] = timezone_id

class WebExTimezone(object):
    def __init__(self, id=None, tzinfo=None):
        self.id = id
        self.tzinfo = tzinfo
        if self.id is None:
            self.id = TZINFO_TO_WEBEX_TIMEZONE_ID_MAP[self.tzinfo]
        if self.tzinfo is None:
            self.tzinfo = WEBEX_TIMEZONE_ID_TO_TZINFO_MAP[self.id]

    def localize_new_naive_datetime(self, year, month, day, hour=0, minute=0, second=0, microsecond=0):
        return self.tzinfo.localize(datetime.datetime(year,month,day,hour,minute,second,microsecond))

    def localize_naive_datetime(self, naive_datetime):
        return self.tzinfo.localize(naive_datetime)

    def from_localized_datetime(cls, localized_datetime):
        return WebExTimezone(tzinfo=pytz.timezone(localized_datetime.tzinfo.zone))
    from_localized_datetime = classmethod(from_localized_datetime)
  
