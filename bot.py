
import asyncio
import time
import aiohttp
import discord
from discord.ext import commands

from config import DISCORD_TOKEN, COMMAND_PREFIX, STATE_FILE, INACTIVITY_MINUTES, MOD_LOG_CHANNEL_ID, MISTRAL_API_KEY
from data_structures import LinkedList, Stack
from conversation import build_conversation_tree, search_topic
from persistence import save_state, load_state

# Vérification token
if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN manquant. Définis la variable d'environnement ou config.py.")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

# Structures en mémoire
user_histories = {}      # uid -> LinkedList
user_positions = {}      # uid -> node_id courant
user_undo_stacks = {}    # uid -> Stack d'ids de nœuds pour undo
last_activity = {}       # uid -> timestamp (seconds)

root, nodes = build_conversation_tree()

def now():
    return int(time.time())

async def ask_mistral(user_message):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "mistral-small-latest",
        "messages": [
            {"role": "system", "content": "Tu es un assistant Discord sympa et serviable. Réponds toujours en français, de façon courte et naturelle."},
            {"role": "user", "content": user_message}
        ]
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            data = await resp.json()
            return data["choices"][0]["message"]["content"]

def touch(uid):
    last_activity[uid] = now()

async def log_mod(message):
    if MOD_LOG_CHANNEL_ID:
        ch = bot.get_channel(MOD_LOG_CHANNEL_ID)
        if ch:
            await ch.send(message)

@bot.event
async def on_ready():
    state = load_state(STATE_FILE)
    user_histories.update(state["histories"])
    user_positions.update(state["positions"])
    user_undo_stacks.update(state["undo"])
    last_activity.update(state["last_activity"])
    await log_mod(f"Démarré comme {bot.user}. État chargé.")
    print(f"Connecté en tant que {bot.user}")

@bot.event
async def on_command(ctx):
    uid = str(ctx.author.id)
    user_histories.setdefault(uid, LinkedList()).push_front(ctx.message.content)
    touch(uid)

@bot.command(name="start")
async def cmd_help(ctx):
    uid = str(ctx.author.id)
    user_positions[uid] = root.id
    user_undo_stacks.setdefault(uid, Stack()).clear()
    await ctx.send(root.prompt)
    touch(uid)

@bot.command(name="reset")
async def cmd_reset(ctx):
    uid = str(ctx.author.id)
    user_positions[uid] = root.id
    user_undo_stacks.setdefault(uid, Stack()).clear()
    await ctx.send("Discussion réinitialisée. " + root.prompt)
    touch(uid)

@bot.command(name="history")
async def cmd_history(ctx):
    uid = str(ctx.author.id)
    ll = user_histories.get(uid, LinkedList())
    cmds = ll.to_list()
    last = cmds[0] if cmds else "Aucune"
    await ctx.send(f"Dernière commande: {last}\nToutes: {cmds}")
    touch(uid)

@bot.command(name="clearhistory")
async def cmd_clearhistory(ctx):
    uid = str(ctx.author.id)
    user_histories.setdefault(uid, LinkedList()).clear()
    await ctx.send("Historique vidé.")
    touch(uid)

@bot.command(name="speak")
async def cmd_speak(ctx, *, topic: str):
    found = search_topic(root, topic)
    await ctx.send("oui" if found else "non")
    touch(str(ctx.author.id))

@bot.command(name="stats")
async def cmd_stats(ctx):
    uid = str(ctx.author.id)
    ll = user_histories.get(uid, LinkedList())
    cmds = ll.to_list()
    count = len(cmds)
    most = most_used_command(cmds)
    await ctx.send(f"Tu as envoyé {count} commandes. Commande la plus utilisée: {most if most else 'Aucune'}")
    touch(uid)

def most_used_command(cmds):
    freq = {}
    for c in cmds:
        name = c.split()[0] if c else ""
        freq[name] = freq.get(name, 0) + 1
    if not freq:
        return None
    return max(freq.items(), key=lambda x: x[1])[0]

@bot.command(name="undo")
async def cmd_undo(ctx):
    uid = str(ctx.author.id)
    st = user_undo_stacks.setdefault(uid, Stack())
    prev = st.pop()
    if prev:
        user_positions[uid] = prev
        await ctx.send(f"Retour en arrière. {nodes[prev].prompt or 'Conclusion atteinte.'}")
    else:
        await ctx.send("Rien à annuler.")
    touch(uid)
       # Sauvegarde automatique après chaque commande
    save_state(STATE_FILE, user_histories, user_positions, user_undo_stacks, last_activity)

@bot.command(name="export")
async def cmd_export(ctx):
    uid = str(ctx.author.id)
    ll = user_histories.get(uid, LinkedList())
    import json
    payload = json.dumps({"user_id": uid, "history": ll.to_list()}, ensure_ascii=False, indent=2)
    try:
        await ctx.author.send(f"Voici ton export JSON:\n```json\n{payload}\n```")
        await ctx.send("Je t'ai envoyé ton export en message privé.")
    except discord.Forbidden:
        await ctx.send("Impossible d'envoyer un DM. Active tes messages privés.")
    touch(uid)

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)

    uid = str(message.author.id)
    save_state(STATE_FILE, user_histories, user_positions, user_undo_stacks, last_activity)

    if uid in last_activity:
        inactive_sec = now() - last_activity[uid]
        if inactive_sec > INACTIVITY_MINUTES * 60 and uid in user_positions:
            user_positions[uid] = root.id
            user_undo_stacks.setdefault(uid, Stack()).clear()
            await message.channel.send("Inactivité détectée, discussion réinitialisée. " + root.prompt)


    node_id = user_positions.get(uid)

    # Réponse IA pour les messages normaux (hors commandes et hors arbre actif)
    if not node_id and not message.content.startswith(COMMAND_PREFIX):
        try:
            response = await ask_mistral(message.content)
            await message.channel.send(response)
        except Exception as e:
            print(f"Erreur Mistral: {e}")
            await message.channel.send("Désolé, je n'ai pas pu répondre pour le moment.")
        touch(uid)
        return

    if node_id:
        current = nodes[node_id]
        if current.conclusion:
            await message.channel.send(current.conclusion)
            user_positions.pop(uid, None)
            return

        reply = message.content.strip().lower()
        
        if reply in current.options:
            next_node = current.options[reply]
            st = user_undo_stacks.setdefault(uid, Stack())
            st.push(current.id)
            user_positions[uid] = next_node.id
            if next_node.conclusion:
                await message.channel.send(next_node.conclusion)
                user_positions.pop(uid, None)
            else:
                await message.channel.send(next_node.prompt)
        else:
            opts = ", ".join(current.options.keys())
            await message.channel.send(f"Je n'ai pas compris. Options possibles: {opts}")

    touch(uid)

# Sauvegarde à l'arrêt
async def graceful_shutdown():
    save_state(STATE_FILE, user_histories, user_positions, user_undo_stacks, last_activity)
    await log_mod("État sauvegardé. Arrêt du bot.")

@bot.command(name="shutdown")
@commands.has_permissions(administrator=True)
async def cmd_shutdown(ctx):
    await ctx.send("Arrêt en cours, sauvegarde de l'état...")
    await graceful_shutdown()
    await bot.close()

def main():
    try:
        bot.run(DISCORD_TOKEN)
    finally:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.run_until_complete(graceful_shutdown())
            else:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(graceful_shutdown())
                loop.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()
