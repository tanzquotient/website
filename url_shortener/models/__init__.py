from .destination import Destination

# generate_short_tag is referenced by migration 0001 as url_shortener.models
from .short_link import ShortLink, generate_short_tag
from .source import Source
from .visit import Visit
