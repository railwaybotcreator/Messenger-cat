import os
import smtplib
from email.mime.text import MIMEText
import discord
from discord.ext import commands
from discord import app_commands

# ========= CONFIG =========
TOKEN = os.getenv("BOT_TOKEN")  # Railway env var
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")  # your gmail from env
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # gmail app password from env
# ==========================

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Email sending function
def send_email(to_email: str, subject: str, body: str):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

class EmailView(discord.ui.View):
    def __init__(self, to_email: str, subject: str, body: str):
        super().__init__(timeout=60)
        self.to_email = to_email
        self.subject = subject
        self.body = body

    @discord.ui.button(label="✅ Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            send_email(self.to_email, self.subject, self.body)
            await interaction.response.edit_message(content=f"📧 Email sent successfully to **{self.to_email}**!", view=None)
        except Exception as e:
            await interaction.response.edit_message(content=f"❌ Failed to send email: `{e}`", view=None)

    @discord.ui.button(label="❌ Decline", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="🚫 Email sending cancelled.", view=None)

@bot.tree.command(name="sendemail", description="Send an email to any address")
@app_commands.describe(to_email="Recipient email address", subject="Subject of the email", body="Email body")
async def sendemail(interaction: discord.Interaction, to_email: str, subject: str, body: str):
    view = EmailView(to_email, subject, body)
    await interaction.response.send_message(
        f"Do you want to send this email?\n\n📩 To: `{to_email}`\n📝 Subject: `{subject}`\n💬 Body: {body}",
        view=view
    )

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Logged in as {bot.user}")

bot.run(TOKEN)
