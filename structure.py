import discord

# All categories and channels are created only by an explicit administrator command.
STRUCTURE = {
    "🏛️ GOVERNMENT | VEŘEJNÉ": [
        "vládní-oznámení", "státní-vyhlášky", "státní-zákony", "výkonná-nařízení", "tiskové-zprávy"
    ],
    "🔒 GOVERNMENT | INTERNÍ": [
        "vládní-chat", "návrhy-vyhlášek", "schvalování-vláda", "vládní-hlasování", "vládní-audit"
    ],
    "⚖️ DOJ | VEŘEJNÉ": [
        "úvod", "pravidla", "trestní-zákoník", "soudní-řád", "seznam-advokátů", "žádosti-a-maily"
    ],
    "🔒 DOJ | INTERNÍ": [
        "vedení-doj", "státní-zástupci", "soudci", "žádosti-o-příkazy", "schvalování-příkazů"
    ],
    "👨‍⚖️ SOUDNICTVÍ": [
        "soudní-případy", "soudní-jednání", "soudní-rozsudky", "soudní-archiv"
    ],
    "🚔 STÁTNÍ SLOŽKY": [
        "lspd", "lssd", "sahp", "lsfd-ems", "dispatch"
    ],
    "📁 SPRÁVA": ["bot-logy", "technická-podpora"],
}

ROLE_NAMES = [
    "Governor", "Lieutenant Governor", "Government Administration",
    "Attorney General", "Chief Justice", "Judge", "State Prosecutor",
    "Licensed Attorney", "LSPD", "LSSD", "SAHP", "LSFD", "EMS", "Citizen",
]

PRIVATE = {"🔒 GOVERNMENT | INTERNÍ", "🔒 DOJ | INTERNÍ", "📁 SPRÁVA"}

async def install(guild: discord.Guild):
    me = guild.me
    if not me or not me.guild_permissions.manage_channels or not me.guild_permissions.manage_roles:
        raise PermissionError("Bot potřebuje Manage Channels a Manage Roles.")
    existing_roles = {r.name for r in guild.roles}
    created_roles = 0
    for name in ROLE_NAMES:
        if name not in existing_roles:
            await guild.create_role(name=name, reason="DOJ V3 instalace")
            created_roles += 1
    created_channels = 0
    for category_name, channels in STRUCTURE.items():
        category = discord.utils.get(guild.categories, name=category_name)
        if category is None:
            overwrites = {}
            if category_name in PRIVATE:
                overwrites[guild.default_role] = discord.PermissionOverwrite(view_channel=False)
                overwrites[me] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
                for role_name in (("Governor", "Lieutenant Governor", "Government Administration") if "GOVERNMENT" in category_name else ("Attorney General", "Chief Justice", "Judge", "State Prosecutor") if "DOJ" in category_name else ("Governor", "Attorney General")):
                    role = discord.utils.get(guild.roles, name=role_name)
                    if role:
                        overwrites[role] = discord.PermissionOverwrite(view_channel=True)
            category = await guild.create_category(category_name, overwrites=overwrites, reason="DOJ V3 instalace")
        existing = {c.name for c in category.channels}
        for name in channels:
            if name not in existing:
                await guild.create_text_channel(name, category=category, reason="DOJ V3 instalace")
                created_channels += 1
    return created_roles, created_channels
