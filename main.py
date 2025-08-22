from flask import Flask
import os
from threading import Thread
import joblib
from dotenv import load_dotenv
from disnake.ext import commands
import disnake
from csv_to_dict import csv_to_dict

my_dict = csv_to_dict()

app = Flask('')
@app.route("/")
def home():
    return "Bot is running!",200

def run_flask():
    port = int(os.environ.get("PORT",8080))
    app.run(host="0.0.0.0",port=port)

if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
    Thread(target=run_flask,daemon=True).start()

load_dotenv()
token = os.getenv("token")

try:
    model = joblib.load("Testament_Classifier.pkl")
    vectorizer = joblib.load("TC_Vectorizer.pkl")
except FileNotFoundError:
    print("File not Found :)")

intents = disnake.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.InteractionBot(intents=intents,test_guilds=[1388620030358589563])

@bot.event
async def on_ready():
    print(f"Kingdom Connect is Working ")
    print(f"Bot is active on {bot.guilds[0]}")

@bot.event
async def on_message(msg):
    if "Jesus is king".lower() in msg.content.lower() or "Jesus is Lord".lower() in msg.content.lower():
        await msg.reply("Amen! 👐")
    else:
        greetings = ["hello", "hi", "hey", "yo", "howdy", "greetings"]
        if bot.user in msg.mentions:
            if any(greeting in msg.content.lower() for greeting in greetings):
                await msg.reply(f"Hello👋 {msg.author.mention}. May God bless you 🙏❤️")
    
@bot.slash_command(name="greet",description="Greet a user")
async def greetuser(inter:disnake.ApplicationCommandInteraction,user:disnake.User,msg:str=None):
    if msg:
        await inter.response.send_message(f"{inter.author.mention} says to {user.mention} : {msg}")
    else:
        await inter.response.send_message(f"{inter.author.mention} says hello to {user.mention} 👋")

@bot.slash_command(name="classify", description="Classifies the text as OT or NT")
async def classify(inter: disnake.ApplicationCommandInteraction, text: str):
    try:
        X = vectorizer.transform([text])  # FIXED
        prediction = model.predict(X)[0]  # Get the first prediction
        response = "New Testament" if prediction == 1 else "Old Testament"
        await inter.response.send_message(f'Prediction for text "{text}" is "{response}"')
    except Exception as e:
        await inter.response.send_message(f"Error during classification: {str(e)}")

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(1388639090190319728)  

    if channel:
        embed = disnake.Embed(
            title="🎉 Welcome!",
            description=f"Welcome to **{member.guild.name}**, {member.mention}!\nWe’re glad to have you here 💖",
            color=0x32CD32 
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)  
        embed.set_footer(text=f"Member #{len(member.guild.members)}")
        
        await channel.send(embed=embed)

@bot.slash_command(name="id_command",description="Identify Commandments with text")
async def id_commandment(inter:disnake.ApplicationCommandInteraction,text):
    response = []
    if text:
        msg = ""
        for ref,verse in my_dict.items():
            if text.lower() in verse.lower():
               response.append(f"{ref} -> {verse}")
        
        msg = '\n'.join(response)
        if len(msg) <= 2000:
            await inter.response.send_message(f"🔎 Matches for `{text}`:\n{msg}")
        else:
            await inter.response.send_message(f"🔎 Matches for `{text}` (split into parts):")
        
            chunks = [msg[i:i+2000] for i in range(0, len(msg), 2000)]
            for chunk in chunks:
                await inter.followup.send(chunk)
    else:
        await inter.response.send_message(f"Enter the text 😏 ")
        
@bot.event
async def on_slash_command_error(inter:disnake.ApplicationCommandInteraction,error):
   if not inter.response.is_done():
        try:
            await inter.response.send_message("❌ An error occurred...", ephemeral=True)
        except:
            pass

if token:
    bot.run(token)
else:
    print("No Token found :)")
