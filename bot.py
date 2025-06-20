import discord
from discord.ext import commands
from discord.ui import Button, View
from datetime import datetime
import json
import os
import locale

try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except:
    pass

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

CARGO_MEMBRO_OFICIAL = "👮┃Membro Oficial"
ID_CANAL_LOGS = 1382867773239328863
ARQUIVO_PONTO = "pontos.json"
registros = {}

def estilizar_texto(texto):
    mapa = {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ',
        'f': 'ғ', 'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ',
        'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ',
        'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ',
        'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ'
    }
    return ''.join(mapa.get(c.lower(), c) for c in texto)

def abreviar_cargo(cargo_nome):
    palavras = cargo_nome.split()
    if len(palavras) == 1:
        abreviacao = cargo_nome[:3].upper()
    else:
        abreviacao = ''.join(p[0].upper() for p in palavras)
    return estilizar_texto(abreviacao.lower())

def salvar_pontos():
    with open(ARQUIVO_PONTO, 'w') as f:
        json.dump(registros, f, indent=4)

def carregar_pontos():
    global registros
    if os.path.exists(ARQUIVO_PONTO):
        with open(ARQUIVO_PONTO, 'r') as f:
            registros = json.load(f)
    else:
        registros = {}

class BatePontoView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="ABRIR PONTO", style=discord.ButtonStyle.green, custom_id="abrir_ponto")
    async def abrir_ponto(self, interaction: discord.Interaction, button: Button):
        membro = interaction.user
        canal_log = bot.get_channel(ID_CANAL_LOGS)
        vc = membro.voice

        if not vc or not vc.channel:
            await interaction.response.send_message("❌ Você precisa estar conectado a um canal de voz para abrir o ponto.", ephemeral=True)
            return

        user_id = str(membro.id)

        if user_id in registros and 'start' in registros[user_id]:
            await interaction.response.send_message("⚠️ Você já tem um ponto aberto. Use o botão FECHAR para finalizar.", ephemeral=True)
            return

        registros[user_id] = registros.get(user_id, {})
        registros[user_id]['start'] = datetime.utcnow().isoformat()
        salvar_pontos()

        data_formatada = datetime.utcnow().strftime('%A, %d de %B de %Y %H:%M').capitalize()
        embed = discord.Embed(description=(f"**{membro.name}**\n🟢 {membro.name} iniciou o ponto com sucesso!\n\nIniciado em\n🕒 {data_formatada}\n\nID: {membro.id}"), color=0x2ecc71)
        if membro.avatar:
            embed.set_thumbnail(url=membro.avatar.url)
        await canal_log.send(embed=embed)
        await interaction.response.send_message("✅ Ponto aberto com sucesso!", ephemeral=True)

    @discord.ui.button(label="FECHAR PONTO", style=discord.ButtonStyle.red, custom_id="fechar_ponto")
    async def fechar_ponto(self, interaction: discord.Interaction, button: Button):
        membro = interaction.user
        canal_log = bot.get_channel(ID_CANAL_LOGS)
        user_id = str(membro.id)

        if user_id not in registros or 'start' not in registros[user_id]:
            await interaction.response.send_message("⚠️ Você não tem um ponto aberto. Use o botão ABRIR para começar.", ephemeral=True)
            return

        start_str = registros[user_id]['start']
        start = datetime.fromisoformat(start_str)
        end = datetime.utcnow()
        duracao = (end - start).total_seconds() / 60

        registros[user_id].setdefault('total', 0)
        registros[user_id]['total'] += duracao
        registros[user_id].pop('start')
        salvar_pontos()

        data_inicio = start.strftime('%A, %d de %B de %Y %H:%M').capitalize()
        data_fim = end.strftime('%A, %d de %B de %Y %H:%M').capitalize()
        embed = discord.Embed(description=(f"**{membro.name}**\n🔴 {membro.name} fechou o ponto com sucesso!\n\nInício: 🕒 {data_inicio}\nFim: 🕒 {data_fim}\nDuração: ⏳ {duracao:.1f} minutos\n\nID: {membro.id}"), color=0xe74c3c)
        if membro.avatar:
            embed.set_thumbnail(url=membro.avatar.url)
        await canal_log.send(embed=embed)
        await interaction.response.send_message(f"⏰ Ponto fechado! Você ficou {duracao:.1f} minutos.", ephemeral=True)

    @discord.ui.button(label="HORAS", style=discord.ButtonStyle.blurple, custom_id="horas_ponto")
    async def horas_ponto(self, interaction: discord.Interaction, button: Button):
        membro = interaction.user
        user_id = str(membro.id)
        total = registros.get(user_id, {}).get('total', 0)

        horas = int(total // 60)
        minutos = int(total % 60)

        await interaction.response.send_message(f"⏳ {membro.mention}, você acumulou **{horas}h {minutos}m** em bate-pontos nesta semana.", ephemeral=True)

@bot.event
async def on_ready():
    print(f"✅ Bot online como {bot.user}")
    carregar_pontos()

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.strip()

    if "ᴠᴜʟɢᴏ:" in content and "ɪᴅ:" in content and "login" in content.lower():
        try:
            lines = content.split('\n')
            vulgo = lines[0].split(':')[1].strip()
            id_num = lines[1].split(':')[1].strip()
            vulgo_formatado = estilizar_texto(vulgo)

            membro = message.guild.get_member(message.author.id)
            if membro:
                cargos = [r for r in membro.roles if r.name != "@everyone"]
                if cargos:
                    cargo_principal = max(cargos, key=lambda r: r.position)
                    iniciais = abreviar_cargo(cargo_principal.name)
                    novo_nick = f"{iniciais} » {vulgo_formatado} ({id_num})"
                else:
                    novo_nick = f"{vulgo_formatado} ({id_num})"

                await membro.edit(nick=novo_nick)
                cargo_oficial = discord.utils.get(message.guild.roles, name=CARGO_MEMBRO_OFICIAL)
                if cargo_oficial and cargo_oficial not in membro.roles:
                    await membro.add_roles(cargo_oficial)

                await message.channel.send(f"✅ {message.author.mention}, seu nick foi atualizado para **{novo_nick}** e você recebeu o cargo oficial!")
            else:
                await message.channel.send("⚠️ Não consegui encontrar você no servidor.")
        except Exception as e:
            print(f"Erro: {e}")
            await message.channel.send("❌ Erro ao processar seu login. Fale com um administrador.")

    await bot.process_commands(message)

@bot.command()
async def ponto(ctx):
    texto = (
        "**Sistema de BATE-PONTO SEMI-AUTOMÁTICO**\n\n"
        "🟢 Nosso servidor conta com um sistema eficiente de bate-ponto semi-automático para facilitar o controle de presença.\n\n"
        "**COMO UTILIZAR:**\n\n"
        "1️⃣ Para abrir seu ponto, conecte-se a uma call e clique no botão **ABRIR**.\n"
        "2️⃣ Quando quiser encerrar o registro, clique no botão **FECHAR** para finalizar seu ponto.\n"
        "3️⃣ Para consultar o total de horas acumuladas na semana, use o botão **HORAS**.\n\n"
        "⚠️ Caso sua conexão seja interrompida ou você esqueça de fechar o ponto antes de sair da call, o sistema fechará seu ponto automaticamente.\n\n"
        "🔄 O sistema possui um mecanismo de upamento automático baseado na presença registrada.\n\n"
        "🚫 Atenção: membros que forem flagrados forjando ponto não serão upados!"
    )
    view = BatePontoView()
    await ctx.send(texto, view=view)

# Inicialização segura com variável de ambiente
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
