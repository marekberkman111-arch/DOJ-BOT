import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from config import GUILD_ID
from database import initialize, connect, now, audit
from structure import install
from legislation import ARTICLES, get_article
from legal_registry import CODES, get_code
from webhook_publisher import publish

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = discord.Object(id=GUILD_ID)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

def find_channel(guild, name):
    return discord.utils.get(guild.text_channels, name=name)

def staff(member):
    allowed = {"Governor", "Lieutenant Governor", "Government Administration",
               "Attorney General", "Chief Justice", "Judge", "State Prosecutor"}
    return member.guild_permissions.administrator or any(r.name in allowed for r in member.roles)

def judge(member):
    return member.guild_permissions.administrator or any(r.name in {"Judge", "Chief Justice"} for r in member.roles)

class CaseModal(discord.ui.Modal, title="Nový soudní případ"):
    nazev = discord.ui.TextInput(label="Název případu", max_length=150)
    obzalovany = discord.ui.TextInput(label="Obžalovaný", max_length=120)
    zalujici = discord.ui.TextInput(label="Žalující strana", max_length=120)
    termin = discord.ui.TextInput(label="Termín jednání (nepovinný)", required=False, placeholder="YYYY-MM-DD HH:MM")
    obvineni = discord.ui.TextInput(label="Obvinění a popis", style=discord.TextStyle.paragraph, max_length=1500)

    async def on_submit(self, interaction: discord.Interaction):
        with connect() as db:
            cur = db.execute("""INSERT INTO cases
                (title,accused,claimant,judge_id,hearing_at,hearing_place,charges,created_by,created_at)
                VALUES (?,?,?,?,?,?,?,?,?)""",
                (str(self.nazev), str(self.obzalovany), str(self.zalujici), interaction.user.id,
                 str(self.termin) or None, "Superior Court of San Andreas",
                 str(self.obvineni), interaction.user.id, now()))
            case_id = cur.lastrowid
            audit(db, interaction.user.id, "CASE_CREATED", str(case_id))
        number = f"SA-{case_id:05d}"
        embed = discord.Embed(title=f"⚖️ Soudní případ {number}: {self.nazev}", description=str(self.obvineni), color=0x334e68)
        embed.add_field(name="Obžalovaný", value=str(self.obzalovany))
        embed.add_field(name="Žalující strana", value=str(self.zalujici))
        embed.add_field(name="Soudce (zakládající)", value=interaction.user.mention)
        embed.add_field(name="Stav", value="OTEVŘENÝ")
        cases = find_channel(interaction.guild, "soudní-případy")
        hearings = find_channel(interaction.guild, "soudní-jednání")
        if cases:
            await publish(cases, embed)
        if str(self.termin) and hearings:
            schedule = discord.Embed(title=f"📅 Soudní jednání {number}", description=str(self.nazev))
            schedule.add_field(name="Termín", value=str(self.termin))
            schedule.add_field(name="Místo", value="Superior Court of San Andreas")
            await publish(hearings, schedule)
        await interaction.response.send_message(f"Případ **{number}** byl založen." + ("" if cases else " Kanál soudní-případy zatím neexistuje."), ephemeral=True)

@bot.tree.command(name="instalovat_server", description="Vytvoří chybějící kategorie, kanály a role", guild=GUILD)
@app_commands.default_permissions(administrator=True)
async def install_server(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Pouze administrátor.", ephemeral=True)
    await interaction.response.defer(ephemeral=True, thinking=True)
    try:
        roles, channels = await install(interaction.guild)
        await interaction.followup.send(f"Instalace dokončena: {roles} rolí a {channels} kanálů.")
    except Exception as exc:
        await interaction.followup.send(f"Instalace se nezdařila: {type(exc).__name__}: {exc}")

@bot.tree.command(name="soudni_pripad", description="Založí případ a případné jednání zveřejní v jiném kanálu", guild=GUILD)
async def new_case(interaction: discord.Interaction):
    if not judge(interaction.user):
        return await interaction.response.send_message("Příkaz je pouze pro soudce.", ephemeral=True)
    await interaction.response.send_modal(CaseModal())

@bot.tree.command(name="spis", description="Zobrazí soudní případ podle čísla", guild=GUILD)
@app_commands.describe(cislo="Číslo spisu, například SA-00001")
async def case_lookup(interaction: discord.Interaction, cislo: str):
    try:
        case_id = int(cislo.upper().replace("SA-", ""))
    except ValueError:
        return await interaction.response.send_message("Neplatné číslo spisu.", ephemeral=True)
    if not staff(interaction.user):
        return await interaction.response.send_message("Nemáš oprávnění nahlížet do soudních spisů.", ephemeral=True)
    with connect() as db:
        row = db.execute("SELECT * FROM cases WHERE id=?", (case_id,)).fetchone()
    if row is None:
        return await interaction.response.send_message("Spis nenalezen.", ephemeral=True)
    embed = discord.Embed(title=f"Spis SA-{row['id']:05d}: {row['title']}", description=row["charges"])
    embed.add_field(name="Obžalovaný", value=row["accused"])
    embed.add_field(name="Stav", value=row["status"])
    embed.add_field(name="Termín", value=row["hearing_at"] or "Neurčen")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="vyhlaska", description="Vytvoří návrh státní vyhlášky jako Discord zprávu", guild=GUILD)
@app_commands.describe(nazev="Název", obsah="Text vyhlášky (max. 1800 znaků)")
async def decree(interaction: discord.Interaction, nazev: str, obsah: str):
    if not staff(interaction.user) or not any(r.name in {"Governor", "Lieutenant Governor", "Government Administration"} for r in interaction.user.roles) and not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Nemáš oprávnění Government.", ephemeral=True)
    if len(obsah) > 1800:
        return await interaction.response.send_message("Obsah musí mít nejvýše 1800 znaků.", ephemeral=True)
    with connect() as db:
        cur = db.execute("INSERT INTO government_documents(kind,title,body,created_by,created_at) VALUES (?,?,?,?,?)",
                         ("VYHLASKA", nazev, obsah, interaction.user.id, now()))
        doc_id = cur.lastrowid
        audit(db, interaction.user.id, "DECREE_DRAFT", str(doc_id))
    embed = discord.Embed(title=f"📜 NÁVRH SD-{doc_id:05d}: {nazev}", description=obsah, color=0xb8860b)
    embed.set_footer(text="NÁVRH – není účinnou vyhláškou")
    channel = find_channel(interaction.guild, "návrhy-vyhlášek")
    if channel:
        await publish(channel, embed)
    await interaction.response.send_message(f"Návrh SD-{doc_id:05d} uložen." + ("" if channel else " Kanál návrhy-vyhlášek zatím neexistuje."), ephemeral=True)


@bot.tree.command(name="paragraf", description="Vyhledá paragraf RP zákoníku San Andreas", guild=GUILD)
@app_commands.describe(cislo="Například 101 nebo § 201")
async def article(interaction: discord.Interaction, cislo: str):
    number = cislo.strip().removeprefix("§").strip()
    found = get_article(number)
    if not found:
        return await interaction.response.send_message("Paragraf nenalezen.", ephemeral=True)
    title, body = found
    embed = discord.Embed(title=f"§ {number} – {title}", description=body, color=0x243b53)
    embed.set_footer(text="NÁVRH RP zákoníku – schválení vedením serveru teprve proběhne")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="zakonik", description="Zobrazí přehled RP paragrafů", guild=GUILD)
async def penal_index(interaction: discord.Interaction):
    text = "\\n".join(f"**§ {key}** – {value[0]}" for key, value in ARTICLES.items())
    await interaction.response.send_message(embed=discord.Embed(title="📚 Návrh trestního a soudního řádu", description=text.replace("\\n", "\n")), ephemeral=True)

@bot.tree.command(name="zmenit_jednani", description="Změní termín jednání a zveřejní aktualizaci", guild=GUILD)
@app_commands.describe(cislo="SA-00001", termin="Nový termín, např. 2026-11-02 18:00")
async def reschedule(interaction: discord.Interaction, cislo: str, termin: str):
    if not judge(interaction.user):
        return await interaction.response.send_message("Pouze soudce.", ephemeral=True)
    try:
        case_id = int(cislo.upper().replace("SA-", ""))
    except ValueError:
        return await interaction.response.send_message("Neplatné číslo spisu.", ephemeral=True)
    with connect() as db:
        row = db.execute("SELECT title FROM cases WHERE id=?", (case_id,)).fetchone()
        if row is None:
            return await interaction.response.send_message("Případ nenalezen.", ephemeral=True)
        db.execute("UPDATE cases SET hearing_at=? WHERE id=?", (termin, case_id))
        audit(db, interaction.user.id, "HEARING_RESCHEDULED", str(case_id))
    channel = find_channel(interaction.guild, "soudní-jednání")
    if channel:
        embed = discord.Embed(title=f"📅 ZMĚNA TERMÍNU SA-{case_id:05d}", description=row["title"], color=0xd97706)
        embed.add_field(name="Nový termín", value=termin)
        await channel.send(embed=embed)
    await interaction.response.send_message("Termín byl aktualizován." + ("" if channel else " Kanál soudní-jednání nebyl nalezen."), ephemeral=True)

@bot.tree.command(name="rozsudek", description="Uzavře soudní případ a zveřejní rozsudek", guild=GUILD)
@app_commands.describe(cislo="SA-00001", rozhodnuti="Výrok soudu", oduvodneni="Stručné odůvodnění")
async def verdict(interaction: discord.Interaction, cislo: str, rozhodnuti: str, oduvodneni: str):
    if not judge(interaction.user):
        return await interaction.response.send_message("Pouze soudce.", ephemeral=True)
    try:
        case_id = int(cislo.upper().replace("SA-", ""))
    except ValueError:
        return await interaction.response.send_message("Neplatné číslo spisu.", ephemeral=True)
    with connect() as db:
        row = db.execute("SELECT title,status FROM cases WHERE id=?", (case_id,)).fetchone()
        if row is None:
            return await interaction.response.send_message("Případ nenalezen.", ephemeral=True)
        if row["status"] != "OTEVRENY":
            return await interaction.response.send_message("Případ už je uzavřen.", ephemeral=True)
        db.execute("UPDATE cases SET status='UZAVRENY' WHERE id=?", (case_id,))
        audit(db, interaction.user.id, "VERDICT_ISSUED", str(case_id))
    embed = discord.Embed(title=f"⚖️ Rozsudek SA-{case_id:05d}", description=row["title"])
    embed.add_field(name="Výrok", value=rozhodnuti[:1024], inline=False)
    embed.add_field(name="Odůvodnění", value=oduvodneni[:1024], inline=False)
    embed.set_footer(text=f"Soudce: {interaction.user.display_name} • RP dokument")
    channel = find_channel(interaction.guild, "soudní-rozsudky")
    if channel:
        await channel.send(embed=embed)
    await interaction.response.send_message("Rozsudek uložen." + ("" if channel else " Kanál soudní-rozsudky nebyl nalezen."), ephemeral=True)

@bot.tree.command(name="schvalit_vyhlasku", description="Guvernér schválí návrh vyhlášky", guild=GUILD)
@app_commands.describe(cislo="Číslo návrhu, například SD-00001")
async def approve_decree(interaction: discord.Interaction, cislo: str):
    if not interaction.user.guild_permissions.administrator and not any(r.name == "Governor" for r in interaction.user.roles):
        return await interaction.response.send_message("Schválení je vyhrazeno guvernérovi.", ephemeral=True)
    try:
        doc_id = int(cislo.upper().replace("SD-", ""))
    except ValueError:
        return await interaction.response.send_message("Neplatné číslo dokumentu.", ephemeral=True)
    with connect() as db:
        row = db.execute("SELECT * FROM government_documents WHERE id=? AND kind='VYHLASKA'", (doc_id,)).fetchone()
        if row is None or row["status"] != "NAVRH":
            return await interaction.response.send_message("Návrh neexistuje nebo už byl vyřízen.", ephemeral=True)
        db.execute("UPDATE government_documents SET status='SCHVALENO' WHERE id=?", (doc_id,))
        audit(db, interaction.user.id, "DECREE_APPROVED", str(doc_id))
    embed = discord.Embed(title=f"📜 STÁTNÍ VYHLÁŠKA SD-{doc_id:05d}: {row['title']}", description=row["body"], color=0x176b4d)
    embed.set_footer(text=f"Schválil/a: {interaction.user.display_name} • RP Government of San Andreas")
    channel = find_channel(interaction.guild, "státní-vyhlášky")
    if channel:
        await channel.send(embed=embed)
    await interaction.response.send_message("Vyhláška schválena." + ("" if channel else " Kanál státní-vyhlášky nebyl nalezen."), ephemeral=True)


@bot.tree.command(name="pravni_predpis", description="Zobrazí strukturu RP právního předpisu", guild=GUILD)
@app_commands.describe(kod="Například TZ, TR, SR, DP nebo UST")
async def legal_code(interaction: discord.Interaction, kod: str):
    item = get_code(kod)
    if item is None:
        return await interaction.response.send_message(
            "Neznámý kód. Dostupné: " + ", ".join(c.code for c in CODES), ephemeral=True)
    embed = discord.Embed(title=f"📚 {item.code} – {item.title}",
                          description="\\n".join(f"• {section}" for section in item.sections).replace("\\n", "\n"),
                          color=0x334e68)
    embed.add_field(name="Inspirace", value=item.inspiration, inline=False)
    embed.add_field(name="Publikační kanál", value=f"#{item.channel}", inline=False)
    embed.set_footer(text="NÁVRH RP legislativy • není účinným zákonem")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="publikovat_zakonik", description="Publikuje návrhový index RP předpisů", guild=GUILD)
@app_commands.default_permissions(administrator=True)
async def publish_codes(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Pouze administrátor.", ephemeral=True)
    channel = find_channel(interaction.guild, "státní-zákony")
    if channel is None:
        return await interaction.response.send_message("Nejdřív vytvoř kanál státní-zákony.", ephemeral=True)
    embed = discord.Embed(title="🏛️ NÁVRH – Registr právních předpisů San Andreas",
        description="\\n".join(f"**{item.code}** – {item.title}" for item in CODES).replace("\\n", "\n"),
        color=0xb8860b)
    embed.set_footer(text="NÁVRH • není schválená ani účinná legislativa")
    await interaction.response.defer(ephemeral=True)
    try:
        await publish(channel, embed)
    except Exception as exc:
        return await interaction.followup.send(f"Publikování selhalo: {type(exc).__name__}. Zkontroluj webhook a oprávnění.")
    await interaction.followup.send("Návrhový index byl publikován jako Discord zpráva.")

@bot.event
async def on_ready():
    if not getattr(bot, "_synced", False):
        await bot.tree.sync(guild=GUILD)
        bot._synced = True
    print(f"Přihlášen jako {bot.user}; server {GUILD_ID}")

if __name__ == "__main__":
    initialize()
    if not TOKEN:
        raise RuntimeError("Chybí DISCORD_TOKEN v prostředí Railway.")
    bot.run(TOKEN)
