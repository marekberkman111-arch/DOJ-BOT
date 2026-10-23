"""Bezpečné publikování schválených Discord oznámení přes webhook.

Webhook URL nikdy neukládat do repozitáře. Pokud není nastavena, použít bot.send.
"""
import os
import discord

CHANNEL_WEBHOOK_ENV = {
    "státní-vyhlášky": "WEBHOOK_GOVERNMENT_DECREES",
    "státní-zákony": "WEBHOOK_GOVERNMENT_LAWS",
    "vládní-oznámení": "WEBHOOK_GOVERNMENT_ANNOUNCEMENTS",
    "soudní-jednání": "WEBHOOK_COURT_HEARINGS",
    "soudní-rozsudky": "WEBHOOK_COURT_VERDICTS",
    "soudní-případy": "WEBHOOK_COURT_CASES",
}

async def publish(channel: discord.TextChannel, embed: discord.Embed):
    """Publikace pouze do konkrétního cílového kanálu.

    Pro webhook je vyžadována URL z Railway Variables; fallback je bot.
    """
    variable = CHANNEL_WEBHOOK_ENV.get(channel.name)
    url = os.getenv(variable, "") if variable else ""
    if url:
        async with __import__("aiohttp").ClientSession() as session:
            hook = discord.Webhook.from_url(url, session=session)
            if hook.channel_id != channel.id:
                raise ValueError("Webhook nepatří do požadovaného kanálu.")
            return await hook.send(embed=embed, username="San Andreas DOJ", wait=True,
                                   allowed_mentions=discord.AllowedMentions.none())
    return await channel.send(embed=embed, allowed_mentions=discord.AllowedMentions.none())
