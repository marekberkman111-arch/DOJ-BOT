import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from config import GUILD_ID
from database import initialize, connect, now, audit
from structure import install

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
            await cases.send(embed=embed)
        if str(self.termin) and hearings:
            schedule = discord.Embed(title=f"📅 Soudní jednání {number}", description=str(self.nazev))
            schedule.add_field(name="Termín", value=str(self.termin))
            schedule.add_field(name="Místo", value="Superior Court of San Andreas")
            await hearings.send(embed=schedule)
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
        await channel.send(embed=embed)
    await interaction.response.send_message(f"Návrh SD-{doc_id:05d} uložen." + ("" if channel else " Kanál návrhy-vyhlášek zatím neexistuje."), ephemeral=True)

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
