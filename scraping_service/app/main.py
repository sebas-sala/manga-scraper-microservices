import asyncio
from app.cron import Cron
from app import logging_config

if __name__ == "__main__":
  asyncio.run(Cron.run())