import logging

DOMAIN = "chile_earthquakes"
PLATFORMS = ["sensor", "binary_sensor"]

LOGGER = logging.getLogger(__package__)

DEFAULT_SCAN_INTERVAL = 30
DEFAULT_ALERT_THRESHOLD = 4.5
DEFAULT_ALERT_RESET_MINUTES = 10
DEFAULT_PRIMARY_SOURCE = "auto"

CONF_PRIMARY_SOURCE = "primary_source"
CONF_ALERT_THRESHOLD = "alert_threshold"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_ALERT_RESET_MINUTES = "alert_reset_minutes"

SOURCE_BOOSTR = "boostr"
SOURCE_USGS = "usgs"
SOURCE_AUTO = "auto"

EVENT_NEW_EARTHQUAKE = "chile_earthquakes_new_event"

ATTR_MAGNITUDE = "magnitude"
ATTR_DEPTH = "depth"
ATTR_PLACE = "place"
ATTR_LATITUDE = "latitude"
ATTR_LONGITUDE = "longitude"
ATTR_TIME = "time"
ATTR_SOURCE = "source"
ATTR_EVENT_ID = "event_id"
ATTR_IMAGE_URL = "image_url"
ATTR_INFO_URL = "info_url"

BOOSTR_URL = "https://api.boostr.cl/earthquake.json"
USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
SISMOLOGIA_URL = "https://www.sismologia.cl/"

CHILE_MIN_LAT = -56.0
CHILE_MAX_LAT = -17.0
CHILE_MIN_LON = -110.0
CHILE_MAX_LON = -65.0
