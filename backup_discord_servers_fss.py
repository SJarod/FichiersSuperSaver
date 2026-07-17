# resources : https://discord.com/developers/docs/resources/channel
# TODO : md is not working
# TODO : sort files and attachements

import sys

import discord
from discord.ext import commands
import os
from datetime import datetime
import aiohttp
import logging
import re
import ntpath

# Function to generate a safe filename
def sanitize_filename(filename):
    # Remove invalid characters and ensure it retains the file extension
    filename_no_ext, file_ext = os.path.splitext(filename)
    filename_no_ext = re.sub(r'[<>:"/\\|?*]', '_', filename_no_ext)  # Replace invalid characters
    return (filename_no_ext[:255 - len(file_ext)] + file_ext)  # Limit name length, keep extension

# Function to generate directory path for attachments
def get_attachment_folder(guild_name, category_name):
    safe_category_name = sanitize_filename(category_name)
    attachment_folder = os.path.join(BASE_FOLDER, guild_name, safe_category_name, "attachments")
    if not os.path.exists(attachment_folder):
        os.makedirs(attachment_folder)
    return attachment_folder

# Function to generate file name based on the guild, channel category, and date
def get_file_name(guild_name, category_name, channel_name, ext):
    today = datetime.now().strftime('%Y-%m-%d')
    safe_category_name = sanitize_filename(category_name)
    safe_channel_name = sanitize_filename(channel_name)

    return os.path.join(BASE_FOLDER, guild_name, safe_category_name, f"{today}_{safe_channel_name}.{ext}")

# Function to save messages in an HTML file and Markdown file
def save_message_as_html_and_markdown(guild_name, category_name, channel_name, author_name, content, timestamp, message_id):
    html_file_path = get_file_name(guild_name, category_name, channel_name, 'html')
    md_file_path = get_file_name(guild_name, category_name, channel_name, 'md')

    # Ensure the directory for the guild and category exists
    guild_folder = os.path.dirname(html_file_path)
    if not os.path.exists(guild_folder):
        os.makedirs(guild_folder)

    # Add HTML content
    with open(html_file_path, 'a', encoding='utf-8') as f:
        f.write(f"<p id='{message_id}'><b>{author_name}</b> [{timestamp}]: {content}</p>\n")

    # Add Markdown content
    with open(md_file_path, 'a', encoding='utf-8') as f:
        f.write(f"**{author_name}** [{timestamp}]: {content}\n\n")

# https://stackoverflow.com/a/57896232
def uniquify(path):
    filename, extension = os.path.splitext(path)
    counter = 1

    while os.path.exists(path):
        path = filename + " (" + str(counter) + ")" + extension
        counter += 1

    return path

# https://stackoverflow.com/a/8384788
def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

# Function to save files or images
async def save_attachment(channel, author_name, attachment):
    attachment_folder = get_attachment_folder(channel.guild.name, channel.category.name if channel.category else "No Category")
    file_name = sanitize_filename(attachment.filename)
    file_path = os.path.join(attachment_folder, file_name)
    unique_file_path = uniquify(file_path)
    unique_file_name = path_leaf(unique_file_path)

    # Download the file
    async with aiohttp.ClientSession() as session:
        async with session.get(attachment.url) as response:
            if response.status == 200:
                with open(unique_file_path, 'wb') as f :
                    f.write(await response.read())
                logging.info(f"File downloaded: {file_name} as {unique_file_name} in {attachment_folder}")
            else:
                logging.error(f"Download error for {file_name}: {response.status}")

    # html
    html_file_path = get_file_name(channel.guild.name, channel.category.name if channel.category else "No Category", channel.name, 'html')
    with open(html_file_path, 'a', encoding='utf-8') as f:
        if attachment.url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
            f.write(f"<p><b>{author_name}</b> [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]: <img src='attachments/{unique_file_name}' alt='{unique_file_name}' style='max-width:300px;'/></p>\n")
        else:
            f.write(f"<p><b>{author_name}</b> [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]: <a href='attachments/{unique_file_name}'>{unique_file_name}</a></p>\n")

    # mark down
    md_file_path = get_file_name(channel.guild.name, channel.category.name if channel.category else "No Category", channel.name, 'md')
    with open(md_file_path, 'a', encoding='utf-8') as f:
        if attachment.url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
            f.write(f"**{author_name}** [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]: ![Preview]({{attachments/{unique_file_name}}})\n")
        else:
            f.write(f"**{author_name}** [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]: [Download Attachment](attachments/{unique_file_name})\n\n")

# Function to retrieve and save old messages from a channel
async def save_old_messages(channel):
    logging.info(f"Retrieving messages in channel: {channel.name}")
    async for message in channel.history(limit=None):  # Retrieve all messages
        timestamp = message.created_at.strftime('%Y-%m-%d %H:%M:%S')
        author_name = message.author.name
        message_id = message.id
        
        # Save the message content
        save_message_as_html_and_markdown(channel.guild.name, channel.category.name if channel.category else "No Category", channel.name, author_name, message.content, timestamp, message_id)
        logging.info(f"Message saved from {author_name}: {message.content} [{timestamp}]")

        # Save attachments
        for attachment in message.attachments:
            await save_attachment(channel, author_name, attachment)

# Function to create global HTML and Markdown files
def create_global_files(guild_name):
    global_html_path = os.path.join(BASE_FOLDER, f"{guild_name}_global.html")
    global_md_path = os.path.join(BASE_FOLDER, f"{guild_name}_global.md")

    # Create or reset global files
    with open(global_html_path, 'w', encoding='utf-8') as f:
        f.write("<html><body><h1>Global File Links</h1>\n")
        
    with open(global_md_path, 'w', encoding='utf-8') as f:
        f.write(f"# Global File Links for {guild_name}\n\n")

    return global_html_path, global_md_path

# Function to add links to global files
def add_to_global_files(global_html_path, global_md_path, guild_name, channel):
    path_to_html_file = os.path.relpath(get_file_name(guild_name, channel.category.name if channel.category else 'No Category', channel.name, 'html'), os.path.dirname(global_html_path))
    path_to_md_file = os.path.relpath(get_file_name(guild_name, channel.category.name if channel.category else 'No Category', channel.name, 'md'), os.path.dirname(global_md_path))

    with open(global_html_path, 'a', encoding='utf-8') as f:
        f.write(f"<h2>{channel.name}</h2>\n")
        f.write(f"<ul>\n")
        f.write(f"<li><a href='{path_to_html_file}'>{channel.name}.html</a></li>\n")
        f.write(f"<li><a href='{path_to_md_file}'>{channel.name}.md</a></li>\n")
        f.write(f"</ul>\n")

    with open(global_md_path, 'a', encoding='utf-8') as f:
        f.write(f"## {channel.name}\n")
        f.write(f"- [{channel.name}.html]({path_to_html_file})\n")
        f.write(f"- [{channel.name}.md]({path_to_md_file})\n\n")

# Create a bot with a prefix, here "!".
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logging.info(f'The bot is connected as {bot.user}!')
    
    # Iterate through all servers and channels to retrieve old messages
    for guild in bot.guilds:
        logging.info(f"Processing server: {guild.name}")

        global_html_path, global_md_path = create_global_files(guild.name)  # Create global files

        for channel in guild.text_channels:
            await save_old_messages(channel)
            add_to_global_files(global_html_path, global_md_path, guild.name, channel)  # Pass the channel object

    logging.info("Old message retrieval completed. The bot will now shut down.")
    await bot.close()  # Stop the bot

BASE_FOLDER = "discord_backup"
if (len(sys.argv) == 1) :
    with open('token.txt', 'r') as file:
        TOKEN = file.read().strip()
else :
    for i in range(len(sys.argv)) :
        if sys.argv[i] == "-t" :
            TOKEN = sys.argv[i + 1]
        elif sys.argv[i] == "-d" :
            BASE_FOLDER = sys.argv[i + 1]

if not os.path.exists(BASE_FOLDER):
    os.makedirs(BASE_FOLDER)

logging.basicConfig(filename=BASE_FOLDER + "/log.txt",
                    filemode='a',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

bot.run(TOKEN)
