from .twitter import TwitterBot
from .linkedin import LinkedInBot
from .tiktok import TikTokBot
from .threads import ThreadsBot
from .pinterest import PinterestBot
from .bluesky import BlueskyBot
from .youtube import YouTubeBot

# Map platform names (from Excel) to Classes
PLATFORM_MAP = {
    "Twitter": TwitterBot,
    "X": TwitterBot,
    "LinkedIn": LinkedInBot,
    "TikTok": TikTokBot,
    "Threads": ThreadsBot,
    "Pinterest": PinterestBot,
    "Bluesky": BlueskyBot,
    "YouTube": YouTubeBot,
    "Google": YouTubeBot, 
}
