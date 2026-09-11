import discord
from discord.ext import commands
from groq import Groq

# =========================================================
# 🔑 YOUR API KEYS
# =========================================================

DISCORD_TOKEN = "MTU0Nzk5ODQ1NDQ0ODM5MDE1NA.G9Ti6U.SBA9Ct965qn2UCTROM_TaJynZyFjVWOzd9zZxo"
GROQ_API_KEY = "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"

# =========================================================
# ⚙️ CONFIG
# =========================================================

MODEL = "openai/gpt-oss-20b"
PREFIX = "gt "

# =========================================================
# 👻 GHOST PERSONALITY
# =========================================================

SYSTEM_PROMPT = """
You are Ghost, a Discord AI assistant.

Personality:
- Cool, witty, smart and helpful.
- Talk naturally like a Discord user.
- If the user speaks Hinglish, reply in Hinglish.
- If the user speaks English, reply in English.
- Keep replies reasonably short and conversational.
- Don't sound robotic.
- Don't unnecessarily explain things.
- Be friendly but not cringe.
"""

# =========================================================
# 🤖 DISCORD SETUP
# =========================================================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None
)

# =========================================================
# 🧠 GROQ
# =========================================================

groq = Groq(api_key=GROQ_API_KEY)

# =========================================================
# 🧠 MEMORY
# =========================================================

conversation_memory = {}

MAX_MEMORY_MESSAGES = 10


def get_memory(user_id):
    if user_id not in conversation_memory:
        conversation_memory[user_id] = []

    return conversation_memory[user_id]


def add_memory(user_id, role, content):

    memory = get_memory(user_id)

    memory.append({
        "role": role,
        "content": content
    })

    # Only keep recent messages
    if len(memory) > MAX_MEMORY_MESSAGES:
        conversation_memory[user_id] = memory[-MAX_MEMORY_MESSAGES:]


# =========================================================
# 🧠 ASK GHOST
# =========================================================

async def ask_ghost(user_id, question):

    add_memory(
        user_id,
        "user",
        question
    )

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        *get_memory(user_id)
    ]

    try:

        response = groq.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )

        answer = response.choices[0].message.content

        if not answer:
            answer = "Bhai kuch response nahi aaya 😭"

        add_memory(
            user_id,
            "assistant",
            answer
        )

        return answer

    except Exception as e:

        print("================================")
        print("GROQ ERROR:")
        print(e)
        print("================================")

        return "Bhai AI side pe error aa gaya 😭"


# =========================================================
# 🟢 BOT ONLINE
# =========================================================

@bot.event
async def on_ready():

    print()
    print("=" * 55)
    print("👻 GHOST BOT IS ONLINE")
    print("=" * 55)
    print(f"Bot     : {bot.user}")
    print(f"Bot ID  : {bot.user.id}")
    print(f"Model   : {MODEL}")
    print(f"Prefix  : {PREFIX}")
    print("=" * 55)
    print()

    await bot.change_presence(
        activity=discord.Game(
            name="gt help"
        )
    )


# =========================================================
# ❓ HELP
# =========================================================

@bot.command(name="help")
async def ghost_help(ctx):

    embed = discord.Embed(
        title="👻 Ghost Bot",
        description="Available commands:",
        color=discord.Color.purple()
    )

    embed.add_field(
        name="`gt help`",
        value="Show this help menu.",
        inline=False
    )

    embed.add_field(
        name="`gt hello`",
        value="Say hello to Ghost.",
        inline=False
    )

    embed.add_field(
        name="`gt ai <message>`",
        value="Talk to Ghost AI.",
        inline=False
    )

    embed.add_field(
        name="`gt clear`",
        value="Clear your conversation memory.",
        inline=False
    )

    embed.add_field(
        name="`gt ping`",
        value="Check Ghost's latency.",
        inline=False
    )

    embed.set_footer(
        text="Ghost AI"
    )

    await ctx.send(embed=embed)


# =========================================================
# 👋 HELLO
# =========================================================

@bot.command()
async def hello(ctx):

    await ctx.send(
        "Hey! Main Ghost hoon 👻"
    )


# =========================================================
# 🏓 PING
# =========================================================

@bot.command()
async def ping(ctx):

    latency = round(
        bot.latency * 1000
    )

    await ctx.send(
        f"🏓 Pong! `{latency}ms`"
    )


# =========================================================
# 🤖 AI COMMAND
# =========================================================

@bot.command()
async def ai(ctx, *, question=None):

    if not question:

        await ctx.send(
            "Bhai kuch pooch bhi le 😭\n"
            "`gt ai <message>`"
        )

        return

    user_id = str(ctx.author.id)

    async with ctx.typing():

        answer = await ask_ghost(
            user_id,
            question
        )

    await send_long_message(
        ctx.channel,
        answer
    )


# =========================================================
# 🧹 CLEAR MEMORY
# =========================================================

@bot.command()
async def clear(ctx):

    user_id = str(ctx.author.id)

    if user_id in conversation_memory:

        del conversation_memory[user_id]

        await ctx.send(
            "🧠 Memory cleared.\n"
            "Ghost ab fresh start karega."
        )

    else:

        await ctx.send(
            "Memory already empty hai."
        )


# =========================================================
# 📩 LONG MESSAGE HANDLER
# =========================================================

async def send_long_message(channel, text):

    # Discord message limit is 2000 characters
    chunk_size = 1900

    if len(text) <= chunk_size:

        await channel.send(
            f"**Ghost:**\n{text}"
        )

        return

    for i in range(
        0,
        len(text),
        chunk_size
    ):

        chunk = text[i:i + chunk_size]

        await channel.send(
            f"**Ghost:**\n{chunk}"
        )


# =========================================================
# 🗣️ MENTION @GHOST
# =========================================================

@bot.event
async def on_message(message):

    # Ignore every bot
    if message.author.bot:
        return

    # If Ghost is mentioned
    if bot.user and bot.user.mentioned_in(message):

        content = message.content

        # Remove Ghost mention
        content = content.replace(
            bot.user.mention,
            ""
        ).strip()

        # Only @Ghost
        if not content:

            await message.channel.send(
                "Haan bhai? 👻"
            )

            return

        user_id = str(
            message.author.id
        )

        async with message.channel.typing():

            answer = await ask_ghost(
                user_id,
                content
            )

        await send_long_message(
            message.channel,
            answer
        )

        return

    # IMPORTANT:
    # Process normal commands
    await bot.process_commands(message)


# =========================================================
# 🚀 START GHOST
# =========================================================

print("Starting Ghost...")

bot.run(DISCORD_TOKEN)
