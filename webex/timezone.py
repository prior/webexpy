from sanetime import time

TIMEZONE_DATA = (  # webex_timezone_id, webex_timezone, python_timezone_label(s)
    (0, 'GMT-12:00, Dateline (Eniwetok)', 'Pacific/Funafuti'), # guessed at standard pytz label available
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
    (11, 'GMT-05:00, Eastern (New York)', 'America/New_York', 'US/Eastern'),
    (12, 'GMT-05:00, Eastern (Indiana)', 'America/Indiana/Indianapolis'),
    (13, 'GMT-04:00, Atlantic (Halifax)', 'America/Halifax'),
    (14, 'GMT-04:00, S. America Western (Caracas)', 'America/Caracas'),
    (15, 'GMT-03:30, Newfoundland (Newfoundland)', 'America/St_Johns'), # GMT-03:30 Newfoundland best guess
    (16, 'GMT-03:00, S. America Eastern (Brasilia)', 'America/Fortaleza'), # GMT-03:00 Brasilia best guess
    (17, 'GMT-03:00, S. America Eastern (Buenos Aires)', 'America/Buenos_Aires'),
    (18, 'GMT-02:00, Mid-Atlantic (Mid-Atlantic)', 'America/Noronha'), # GMT-02:00 Mid-Atlantic best guess
    (19, 'GMT-01:00, Azores (Azores)', 'Atlantic/Azores'),
    (20, 'GMT+00:00, Greenwich (Casablanca)', 'Africa/Casablanca'),
    (21, 'GMT+00:00, GMT (London)', 'Europe/London', 'UTC'),
    (22, 'GMT+01:00, Europe (Amsterdam)', 'Europe/Amsterdam'),
    (23, 'GMT+01:00, Europe (Berlin)', 'Europe/Paris'),
    (24, None),
    (25, 'GMT+01:00, Europe (Paris)', 'Europe/Berlin'),
    (26, 'GMT+02:00, Greece (Athens)', 'Europe/Athens'),
    (27, None),
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

PYTZ_LABEL_TO_WEBEX_TIMEZONE_ID_MAP = {}
WEBEX_TIMEZONE_ID_TO_PYTZ_LABEL_MAP = {}
for tuple_ in TIMEZONE_DATA:
    list_ = list(tuple_)
    webex_timezone_id = list_.pop(0)
    webex_label = list_.pop(0)
    if list_:
        WEBEX_TIMEZONE_ID_TO_PYTZ_LABEL_MAP[webex_timezone_id] = list_[0]
    for pytz_label in list_:
        PYTZ_LABEL_TO_WEBEX_TIMEZONE_ID_MAP[pytz_label] = webex_timezone_id


# trying to find an equivalent timezone that webex actually knows about
def get_id(timezone_label):
    if timezone_label in PYTZ_LABEL_TO_WEBEX_TIMEZONE_ID_MAP:
        return PYTZ_LABEL_TO_WEBEX_TIMEZONE_ID_MAP[timezone_label]

    us = time().us
    dt = time(us).to_naive_datetime()
    st = time(dt, tz=timezone_label)
    for tuple_ in TIMEZONE_DATA:
        for pytz_label in tuple_[2:]:
            testing_st = time(dt, tz=pytz_label)
            if st == testing_st:
                PYTZ_LABEL_TO_WEBEX_TIMEZONE_ID_MAP[timezone_label] = webex_timezone_id
                break
    return PYTZ_LABEL_TO_WEBEX_TIMEZONE_ID_MAP.get(timezone_label)

