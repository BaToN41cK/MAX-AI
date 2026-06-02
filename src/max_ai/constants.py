"""Constants for MAX-AI."""

import re

URL_PATTERN = re.compile(r"https?://[^\s'\"<>]+")
URL_VALIDATION_PATTERN = re.compile(r'^https?://[^\s/$.?#][^\s]*$')
DOMAIN_PATTERN = re.compile(r'https?://[^/\s]+')
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
