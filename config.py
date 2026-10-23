import os
from pathlib import Path

GUILD_ID = int(os.getenv("DISCORD_GUILD_ID", "1558209495841243136"))
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", "data/doj.sqlite3"))
