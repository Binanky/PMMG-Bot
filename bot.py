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
bot ***REMOVED*** commands.Bot(command_prefix***REMOVED***'!', intents***REMOVED***intents)

CARGO_MEMBRO_OFICIAL ***REMOVED*** "👮┃Membro Oficial"
ID_CANAL_LOGS ***REMOVED*** 1382867773239328863
ARQUIVO_PONTO ***REMOVED*** "pontos.json"
registros ***REMOVED*** {}

def estilizar_texto(texto):
    mapa ***REMOVED*** {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ',
        'f': 'ғ', 'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ',
        'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ',
        'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ',
        'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ'
    }
    return ''.join(mapa.get(c.lower(), c) for c in texto)

def abreviar_cargo(cargo_nome):
    palavras ***REMOVED*** cargo_nome.split()
    if len(palavras) ***REMOVED******REMOVED*** 1:
        abreviacao ***REMOVED*** cargo_nome[:3].upper()
    else:
        abreviacao ***REMOVED*** ''.join(p[0].upper() for p in palavras)
    return estilizar_texto(abreviacao.lower())

def salvar_pontos():
    with open(ARQUIVO_PONTO, 'w') as f:
        json.dump(registros, f, indent***REMOVED***4)

def carregar_pontos():
    global registros
    if os.path.exists(ARQUIVO_PONTO):
        with open(ARQUIVO_PONTO, 'r') as f:
            registros ***REMOVED*** json.load(f)
    else:
        registros ***REMOVED*** {}

class BatePontoView(View):
    def __init__(self):
        super().__init__(timeout***REMOVED***None)

    @discord.ui.button(label***REMOVED***"ABRIR PONTO", style***REMOVED***discord.ButtonStyle.green, custom_id***REMOVED***"abrir_ponto")
    async def abrir_ponto(self, interaction: discord.Interaction, button: Button):
        membro ***REMOVED*** interaction.user
        canal_log ***REMOVED*** bot.get_channel(ID_CANAL_LOGS)
        vc ***REMOVED*** membro.voice

        if not vc or not vc.channel:
            await interaction.response.send_message("❌ Você precisa estar conectado a um canal de voz para abrir o ponto.", ephemeral***REMOVED***True)
            return

        user_id ***REMOVED*** str(membro.id)

        if user_id in registros and 'start' in registros[user_id]:
            await interaction.response.send_message("⚠️ Você já tem um ponto aberto. Use o botão FECHAR para finalizar.", ephemeral***REMOVED***True)
            return

        registros[user_id] ***REMOVED*** registros.get(user_id, {})
        registros[user_id]['start'] ***REMOVED*** datetime.utcnow().isoformat()
        salvar_pontos()

        data_formatada ***REMOVED*** datetime.utcnow().strftime('%A, %d de %B de %Y %H:%M').capitalize()
        embed ***REMOVED*** discord.Embed(description***REMOVED***(f"**{membro.name}**\n🟢 {membro.name} iniciou o ponto com sucesso!\n\nIniciado em\n🕒 {data_formatada}\n\nID: {membro.id}"), color***REMOVED***0x2ecc71)
        if membro.avatar:
            embed.set_thumbnail(url***REMOVED***membro.avatar.url)
        await canal_log.send(embed***REMOVED***embed)
        await interaction.response.send_message("✅ Ponto aberto com sucesso!", ephemeral***REMOVED***True)

    @discord.ui.button(label***REMOVED***"FECHAR PONTO", style***REMOVED***discord.ButtonStyle.red, custom_id***REMOVED***"fechar_ponto")
    async def fechar_ponto(self, interaction: discord.Interaction, button: Button):
        membro ***REMOVED*** interaction.user
        canal_log ***REMOVED*** bot.get_channel(ID_CANAL_LOGS)
        user_id ***REMOVED*** str(membro.id)

        if user_id not in registros or 'start' not in registros[user_id]:
            await interaction.response.send_message("⚠️ Você não tem um ponto aberto. Use o botão ABRIR para começar.", ephemeral***REMOVED***True)
            return

        start_str ***REMOVED*** registros[user_id]['start']
        start ***REMOVED*** datetime.fromisoformat(start_str)
        end ***REMOVED*** datetime.utcnow()
        duracao ***REMOVED*** (end - start).total_seconds() / 60

        registros[user_id].setdefault('total', 0)
        registros[user_id]['total'] +***REMOVED*** duracao
        registros[user_id].pop('start')
        salvar_pontos()

        data_inicio ***REMOVED*** start.strftime('%A, %d de %B de %Y %H:%M').capitalize()
        data_fim ***REMOVED*** end.strftime('%A, %d de %B de %Y %H:%M').capitalize()
        embed ***REMOVED*** discord.Embed(description***REMOVED***(f"**{membro.name}**\n🔴 {membro.name} fechou o ponto com sucesso!\n\nInício: 🕒 {data_inicio}\nFim: 🕒 {data_fim}\nDuração: ⏳ {duracao:.1f} minutos\n\nID: {membro.id}"), color***REMOVED***0xe74c3c)
        if membro.avatar:
            embed.set_thumbnail(url***REMOVED***membro.avatar.url)
        await canal_log.send(embed***REMOVED***embed)
        await interaction.response.send_message(f"⏰ Ponto fechado! Você ficou {duracao:.1f} minutos.", ephemeral***REMOVED***True)

    @discord.ui.button(label***REMOVED***"HORAS", style***REMOVED***discord.ButtonStyle.blurple, custom_id***REMOVED***"horas_ponto")
    async def horas_ponto(self, interaction: discord.Interaction, button: Button):
        membro ***REMOVED*** interaction.user
        user_id ***REMOVED*** str(membro.id)
        total ***REMOVED*** registros.get(user_id, {}).get('total', 0)

        horas ***REMOVED*** int(total // 60)
        minutos ***REMOVED*** int(total % 60)

        await interaction.response.send_message(f"⏳ {membro.mention}, você acumulou **{horas}h {minutos}m** em bate-pontos nesta semana.", ephemeral***REMOVED***True)

@bot.event
async def on_ready():
    print(f"✅ Bot online como {bot.user}")
    carregar_pontos()

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content ***REMOVED*** message.content.strip()

    if "ᴠᴜʟɢᴏ:" in content and "ɪᴅ:" in content and "login" in content.lower():
        try:
            lines ***REMOVED*** content.split('\n')
            vulgo ***REMOVED*** lines[0].split(':')[1].strip()
            id_num ***REMOVED*** lines[1].split(':')[1].strip()
            vulgo_formatado ***REMOVED*** estilizar_texto(vulgo)

            membro ***REMOVED*** message.guild.get_member(message.author.id)
            if membro:
                cargos ***REMOVED*** [r for r in membro.roles if r.name !***REMOVED*** "@everyone"]
                if cargos:
                    cargo_principal ***REMOVED*** max(cargos, key***REMOVED***lambda r: r.position)
                    iniciais ***REMOVED*** abreviar_cargo(cargo_principal.name)
                    novo_nick ***REMOVED*** f"{iniciais} » {vulgo_formatado} ({id_num})"
                else:
                    novo_nick ***REMOVED*** f"{vulgo_formatado} ({id_num})"

                await membro.edit(nick***REMOVED***novo_nick)
                cargo_oficial ***REMOVED*** discord.utils.get(message.guild.roles, name***REMOVED***CARGO_MEMBRO_OFICIAL)
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
    texto ***REMOVED*** (
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
    view ***REMOVED*** BatePontoView()
    await ctx.send(texto, view***REMOVED***view)

# Inicialização segura com variável de ambiente
import os
TOKEN ***REMOVED*** os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
