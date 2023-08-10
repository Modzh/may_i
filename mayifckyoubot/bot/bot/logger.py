import logging


class DispatchingFormatter(logging.Formatter):
    """Dispatch formatter for logger and it's sub logger."""

    def __init__(self, formatters, default_formatter):
        self._formatters = formatters
        self._default_formatter = default_formatter

    def format(self, record):
        # Search from record's logger up to it's parents:
        logger = logging.getLogger(record.name)
        while logger:
            # Check if suitable formatter for current logger exists:
            if logger.name in self._formatters:
                formatter = self._formatters[logger.name]
                break
            else:
                logger = logger.parent
        else:
            # If no formatter found, just use default:
            formatter = self._default_formatter
        return formatter.format(record)
