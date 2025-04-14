from datetime import tzinfo

from dateutil import tz

LOGGING_FORMAT: str = "[%(asctime)s] :: %(levelname)s :: %(name)s :: %(message)s"
DATE_FORMAT: str = "%d-%m-%Y %H:%M:%S"
DEFAULT_LOCALE: tzinfo | None = tz.gettz("Europe/Rome")
