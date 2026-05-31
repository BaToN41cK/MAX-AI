import re

URL_PATTERN = re.compile(r'https?://\S+')
DOMAIN_PATTERN = re.compile(r'https?://[^/\s]+')
MAX_CONTENT_LENGTH = 50000
