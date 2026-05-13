import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
import datetime
import os
import sqlite3
import math
import random
import psutil
from typing import Optional
from datetime import timezone
from discord.ui import View, Button

# Подключение к базе данных SQLite (потокобезопасно)
conn = sqlite3.connect('bot_database.db', check_same_thread=False)
cursor = conn.cursor()

# Создаем необходимые таблицы, если их нет
def setup_database():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER,
        server_id INTEGER,
        messages_count INTEGER DEFAULT 0,
        voice_time INTEGER DEFAULT 0,
        favorite_word TEXT,
        PRIMARY KEY (user_id, server_id)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS access (
        id INTEGER,
        type TEXT CHECK(type IN ('user', 'role')),
        command_name TEXT,
        PRIMARY KEY (id, command_name, type)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS channels (
        channel_id INTEGER PRIMARY KEY,
        last_message_id INTEGER
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS awards (
        award_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        server_id INTEGER,
        award_name TEXT,
        emoji TEXT,
        awarded_by INTEGER,
        date_awarded TEXT
    )
    """)
    # Добавляем создание таблицы word_counts
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS word_counts (
        user_id INTEGER,
        server_id INTEGER,
        word TEXT,
        count INTEGER DEFAULT 1,
        PRIMARY KEY (user_id, server_id, word)
    )
    """)
    # Добавляем создание таблицы messages
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        message_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        server_id INTEGER,
        channel_id INTEGER,
        timestamp TEXT
    )
    """)
    conn.commit()

setup_database()

# **Добавляем список стоп-слов**
STOP_WORDS = set([
    'и', 'в', 'во', 'не', 'что', 'он', 'на', 'я', 'с', 'со', 'как',
    'а', 'то', 'все', 'она', 'так', 'его', 'но', 'да', 'ты', 'к',
    'у', 'же', 'вы', 'за', 'бы', 'по', 'только', 'ее', 'мне',
    'было', 'вот', 'от', 'меня', 'еще', 'нет', 'о', 'из', 'ему',
    'теперь', 'когда', 'даже', 'ну', 'вдруг', 'ли', 'если', 'уже',
    'или', 'ни', 'быть', 'был', 'него', 'до', 'вас', 'нибудь',
    'опять', 'уж', 'вам', 'ведь', 'там', 'потом', 'себя', 'ничего',
    'ей', 'может', 'они', 'тут', 'где', 'есть', 'надо', 'ней',
    'для', 'мы', 'тебя', 'их', 'чем', 'была', 'сам', 'чтоб', 'без',
    'будто', 'чего', 'раз', 'тоже', 'себе', 'под', 'будет', 'ж',
    'тогда', 'кто', 'этот', 'того', 'потому', 'этого', 'какой',
    'совсем', 'ним', 'здесь', 'этом', 'один', 'почти', 'мой', 'тем',
    'чтобы', 'нее', 'сейчас', 'были', 'куда', 'зачем', 'всех',
    'можно', 'при', 'наконец', 'два', 'об', 'другой', 'хоть',
    'после', 'над', 'больше', 'тот', 'через', 'эти', 'нас', 'про',
    'всего', 'них', 'какая', 'много', 'разве', 'три', 'эту',
    'моя', 'впрочем', 'хорошо', 'свою', 'этой', 'перед', 'иногда',
    'лучше', 'чуть', 'том', 'нельзя', 'такой', 'им', 'более',
    'всегда', 'конечно', 'всю', 'между', 'я', 'ты', 'он', 'она',
    'оно', 'мы', 'вы', 'они', 'этот', 'эта', 'это', 'эти', 'тот',
    'та', 'те', 'все', 'всякий', 'каждый', 'кто', 'что', 'какой',
    'чей', 'мой', 'твой', 'его', 'её', 'наш', 'ваш', 'их', 'себя',
    'себе', 'собой', 'ничто', 'никто', 'ничей', 'кое-что', 'кое-кто',
    'некто', 'нечто', 'некоторый', 'сколько', 'столько', 'иной',
    'ли', 'бы', 'уж', 'ведь', 'разве', 'чуть', 'едва', 'авось',
    'пусть', 'даже', 'вот', 'только', 'как раз', 'то есть', 'словно', 'emoji', 'everyone', 'всё', 'просто', 'тебе', 'ещё'
])

def remove_stop_words_from_db():
    cursor.execute("""
    DELETE FROM word_counts WHERE word IN ({})
    """.format(','.join('?' * len(STOP_WORDS))), tuple(STOP_WORDS))
    conn.commit()

remove_stop_words_from_db()

# Идентификатор вашего пользователя (овнера)
# Load OWNER_ID from environment variable
import os
from dotenv import load_dotenv
load_dotenv()
OWNER_ID = int(os.getenv("OWNER_ID", "0"))  # Must be set in .env
if OWNER_ID == 0:
    raise ValueError("OWNER_ID must be set in .env file")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, owner_id=OWNER_ID)

# Создаем CommandTree для регистрации слэш-команд
tree = bot.tree

# Словари для временного хранения данных
voice_connections = {}
favorite_words_cache = {}
temp_voice_channels = {}  # Для отслеживания временных голосовых каналов

# Список команд, доступных всем по умолчанию
PUBLIC_COMMANDS = ['аватар', 'профиль', 'шутка', 'топ_сообщения', 'топ_голос', 'информация_о_сервере', 'помощь']

# Загрузка фурри шуток из файла
def load_jokes():
    jokes_list = []
    try:
        with open('jokes.txt', 'r', encoding='utf-8') as f:
            jokes_list = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("Файл jokes.txt не найден. Убедитесь, что он находится в одной папке с ботом.")
    return jokes_list

jokes = load_jokes()

# Событие при готовности бота
@bot.event
async def on_ready():
    print(f'Бот {bot.user.name} подключен и готов к работе!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name='АФ! - АФ! Служу Руди Волку!'))
    await sync_commands()
    await gather_history_data()
    await update_favorite_words_task()  # Инициализация любимых слов
    update_favorite_words.start()
    print('Бот полностью готов к работе!')

# Функция для синхронизации команд
async def sync_commands():
    try:
        synced = await tree.sync()
        print(f'Синхронизировано {len(synced)} команд.')
    except Exception as e:
        print(f'Ошибка при синхронизации команд: {e}')

# Сбор данных истории сообщений
async def gather_history_data():
    print("Начинаем сбор данных истории сообщений...")
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if not channel.permissions_for(guild.me).read_message_history:
                continue
            last_message_id = get_last_message_id(channel.id)
            try:
                async for message in channel.history(limit=None, after=discord.Object(id=last_message_id) if last_message_id else None, oldest_first=True):
                    if message.author.bot:
                        continue
                    # Обновление таблицы users
                    cursor.execute("""
                    INSERT OR IGNORE INTO users (user_id, server_id, messages_count)
                    VALUES (?, ?, 0)
                    """, (message.author.id, guild.id))
                    cursor.execute("""
                    UPDATE users SET messages_count = messages_count + 1
                    WHERE user_id = ? AND server_id = ?
                    """, (message.author.id, guild.id))
                    # Обновление счётчиков слов
                    words = message.content.lower().split()
                    for word in words:
                        word = ''.join(filter(str.isalpha, word))
                        if word and word not in STOP_WORDS:  # Исключаем стоп-слова
                            cursor.execute("""
                            INSERT OR IGNORE INTO word_counts (user_id, server_id, word, count)
                            VALUES (?, ?, ?, 0)
                            """, (message.author.id, guild.id, word))
                            cursor.execute("""
                            UPDATE word_counts SET count = count + 1
                            WHERE user_id = ? AND server_id = ? AND word = ?
                            """, (message.author.id, guild.id, word))
                    # Логирование сообщения в таблицу messages
                    cursor.execute("""
                    INSERT OR IGNORE INTO messages (message_id, user_id, server_id, channel_id, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                    """, (message.id, message.author.id, guild.id, channel.id, message.created_at.isoformat()))
                    conn.commit()
                    # Обновляем ID последнего обработанного сообщения
                    update_last_message_id(channel.id, message.id)
                print(f"Данные из канала {channel.name} собраны.")
                await asyncio.sleep(1)  # Задержка для избежания rate limits
            except Exception as e:
                print(f"Ошибка при сборе данных из канала {channel.name}: {e}")
    print("Сбор данных истории сообщений завершен.")

# Функции для работы с last_message_id
def get_last_message_id(channel_id):
    cursor.execute("""
    SELECT last_message_id FROM channels WHERE channel_id = ?
    """, (channel_id,))
    result = cursor.fetchone()
    return result[0] if result else None

def update_last_message_id(channel_id, message_id):
    cursor.execute("""
    INSERT OR REPLACE INTO channels (channel_id, last_message_id)
    VALUES (?, ?)
    """, (channel_id, message_id))
    conn.commit()

# Фоновая задача для обновления любимых слов пользователей
@tasks.loop(hours=1)
async def update_favorite_words():
    await update_favorite_words_task()

async def update_favorite_words_task():
    print("Начинаем обновление любимых слов пользователей...")
    cursor.execute("SELECT DISTINCT user_id, server_id FROM users")
    users = cursor.fetchall()
    for user_id, server_id in users:
        cursor.execute("""
        SELECT word, count FROM word_counts
        WHERE user_id = ? AND server_id = ?
        ORDER BY count DESC LIMIT 1
        """, (user_id, server_id))
        result = cursor.fetchone()
        if result:
            favorite_word = result[0]
            cursor.execute("""
            UPDATE users SET favorite_word = ?
            WHERE user_id = ? AND server_id = ?
            """, (favorite_word, user_id, server_id))
            favorite_words_cache[(user_id, server_id)] = favorite_word
    conn.commit()
    print("Обновление любимых слов пользователей завершено.")

# Обработка сообщений для подсчета и реакции на упоминания
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    cursor.execute("""
    INSERT OR IGNORE INTO users (user_id, server_id, messages_count)
    VALUES (?, ?, 0)
    """, (message.author.id, message.guild.id))
    cursor.execute("""
    UPDATE users SET messages_count = messages_count + 1
    WHERE user_id = ? AND server_id = ?
    """, (message.author.id, message.guild.id))

    # Обновление счётчиков слов
    words = message.content.lower().split()
    for word in words:
        word = ''.join(filter(str.isalpha, word))
        if word and word not in STOP_WORDS:  # Исключаем стоп-слова
            cursor.execute("""
            INSERT OR IGNORE INTO word_counts (user_id, server_id, word, count)
            VALUES (?, ?, ?, 0)
            """, (message.author.id, message.guild.id, word))
            cursor.execute("""
            UPDATE word_counts SET count = count + 1
            WHERE user_id = ? AND server_id = ? AND word = ?
            """, (message.author.id, message.guild.id, word))
    # Логирование сообщения в таблицу messages
    cursor.execute("""
    INSERT OR IGNORE INTO messages (message_id, user_id, server_id, channel_id, timestamp)
    VALUES (?, ?, ?, ?, ?)
    """, (message.id, message.author.id, message.guild.id, message.channel.id, message.created_at.isoformat()))
    conn.commit()

    print(f"[{datetime.datetime.now()}] Сообщение от {message.author} на сервере '{message.guild.name}' учтено.")

    # Обработка упоминаний бота только при пустом обращении
    if message.content.strip() == bot.user.mention:
        await message.channel.send("АФ!-АФ!")

    await bot.process_commands(message)

# Обработчик голосовых каналов
@bot.event
async def on_voice_state_update(member, before, after):
    server_id = member.guild.id
    # Отслеживание времени в голосовых каналах
    if before.channel is None and after.channel is not None:
        voice_connections[member.id] = datetime.datetime.now(timezone.utc)
    elif before.channel is not None and after.channel is None:
        if member.id in voice_connections:
            joined_at = voice_connections.pop(member.id)
            time_spent = int((datetime.datetime.now(timezone.utc) - joined_at).total_seconds())
            cursor.execute("""
            INSERT OR IGNORE INTO users (user_id, server_id, voice_time)
            VALUES (?, ?, 0)
            """, (member.id, server_id))
            cursor.execute("""
            UPDATE users SET voice_time = voice_time + ?
            WHERE user_id = ? AND server_id = ?
            """, (time_spent, member.id, server_id))
            conn.commit()
            print(f"[{datetime.datetime.now()}] Пользователь {member} провел в голосовом канале {time_spent} секунд.")

    # Добавленный функционал для временных голосовых каналов
    # ID канала, при присоединении к которому создаётся временный канал
    TRIGGER_VOICE_CHANNEL_ID = 13090811037720290011  # Замените на ваш целевой ID канала

    # Проверяем, присоединился ли пользователь к целевому каналу
    if after.channel and after.channel.id == TRIGGER_VOICE_CHANNEL_ID:
        if member.id in temp_voice_channels:
            # Пользователь уже имеет временный канал
            return
        # Получаем категорию целевого канала для размещения временного канала
        category = after.channel.category
        if not category:
            # Если у целевого канала нет категории, используем первую доступную
            category = member.guild.categories[0] if member.guild.categories else None
        if not category:
            await member.send("Не удалось найти категорию для создания временного голосового канала.")
            return
        # Создаём новый голосовой канал с ником пользователя
        new_channel = await member.guild.create_voice_channel(
            name=f"{member.display_name} в домике!",
            category=category,
            reason="Создание временного голосового канала"
        )
        # Перемещаем пользователя в новый канал
        await member.move_to(new_channel)
        # Сохраняем связь пользователя и канала
        temp_voice_channels[member.id] = new_channel.id
        print(f"Создан временный канал {new_channel.name} для пользователя {member}.")

    # Проверяем, покинул ли пользователь временный канал
    if before.channel and before.channel.id in temp_voice_channels.values():
        # Проверяем, остались ли в канале пользователи
        if len(before.channel.members) == 0:
            # Удаляем канал
            await before.channel.delete(reason="Удаление пустого временного голосового канала")
            # Находим пользователя, которому принадлежал этот канал
            user_id_to_remove = None
            for user_id, channel_id in temp_voice_channels.items():
                if channel_id == before.channel.id:
                    user_id_to_remove = user_id
                    break
            if user_id_to_remove:
                del temp_voice_channels[user_id_to_remove]
            print(f"Временный канал {before.channel.name} удалён, так как в нём больше нет пользователей.")

# Проверка доступа к команде
def has_access():
    async def predicate(interaction: discord.Interaction):
        if interaction.command.name in PUBLIC_COMMANDS:
            return True
        if interaction.user.id == OWNER_ID:
            return True
        cursor.execute("""
        SELECT id, type FROM access WHERE command_name = ?
        """, (interaction.command.name,))
        access_list = cursor.fetchall()
        user_roles = [role.id for role in interaction.user.roles]
        for id_, type_ in access_list:
            if type_ == 'user' and id_ == interaction.user.id:
                return True
            elif type_ == 'role' and id_ in user_roles:
                return True
        return False
    return app_commands.check(predicate)

# ================= Информационные команды =================

# Команда: Помощь
@tree.command(name='помощь', description='Показывает информацию о боте и список доступных команд')
async def помощь(interaction: discord.Interaction):
    embed = discord.Embed(title='🐺 Бот Руди Волка', description='Привет! Я бот, созданный для фурри-сервера. Автор бота: **therudywolf**.', color=discord.Color.blurple())
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.add_field(name='Доступные команды:', value='\u200b', inline=False)

    # Получаем список всех команд
    all_commands = await tree.fetch_commands()

    for cmd in all_commands:
        if cmd.name in PUBLIC_COMMANDS or interaction.user.id == OWNER_ID:
            access = 'Доступна всем' if cmd.name in PUBLIC_COMMANDS else 'Доступ ограничен'
            embed.add_field(name=f'/{cmd.name}', value=f'{cmd.description} ({access})', inline=False)
        else:
            # Проверяем, есть ли у пользователя доступ к команде
            cursor.execute("""
            SELECT id, type FROM access WHERE command_name = ?
            """, (cmd.name,))
            access_list = cursor.fetchall()
            user_roles = [role.id for role in interaction.user.roles]
            has_access_permission = False
            for id_, type_ in access_list:
                if type_ == 'user' and id_ == interaction.user.id:
                    has_access_permission = True
                    break
                elif type_ == 'role' and id_ in user_roles:
                    has_access_permission = True
                    break
            if has_access_permission:
                embed.add_field(name=f'/{cmd.name}', value=f'{cmd.description} (Доступ ограничен)', inline=False)

    await interaction.response.send_message(embed=embed)

# Команда: Информация о сервере
@tree.command(name='информация_о_сервере', description='Показывает информацию о сервере')
async def информация_о_сервере(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f'Информация о сервере {guild.name}', color=discord.Color.teal())
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name='Участники', value=str(guild.member_count), inline=True)
    roles = [role.name for role in guild.roles if role.name != '@everyone']
    roles_text = ', '.join(roles)
    if len(roles_text) > 1024:
        roles_text = roles_text[:1021] + '...'
    embed.add_field(name='Роли', value=roles_text or 'Нет ролей', inline=False)
    # Добавляем последних 5 присоединившихся пользователей
    members = sorted(guild.members, key=lambda m: m.joined_at or datetime.datetime.now(), reverse=True)[:5]
    members_text = '\n'.join([f'{member.display_name} - {member.joined_at.strftime("%Y-%m-%d %H:%M:%S")}' if member.joined_at else f'{member.display_name} - неизвестно' for member in members])
    embed.add_field(name='Недавно присоединились', value=members_text or 'Нет данных', inline=False)
    await interaction.response.send_message(embed=embed)

# Команда: Информация о хосте
@tree.command(name='информация_о_хосте', description='Показывает системную информацию о хосте')
@has_access()
async def информация_о_хосте(interaction: discord.Interaction):
    cpu_usage = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    embed = discord.Embed(title='📊 Информация о хосте', color=discord.Color.dark_blue())
    embed.add_field(name='CPU', value=f'{cpu_usage}%', inline=True)
    embed.add_field(name='RAM', value=f'{memory.percent}% использовано', inline=True)
    embed.add_field(name='Диск', value=f'{disk.percent}% использовано', inline=True)
    await interaction.response.send_message(embed=embed)

# Команда: Пинг
@tree.command(name='пинг', description='Проверяет задержку бота')
@has_access()
async def пинг(interaction: discord.Interaction):
    latency = bot.latency * 1000  # в миллисекундах
    await interaction.response.send_message(f"🏓 Задержка: {int(latency)} мс")

# ================= Развлекательные команды =================

# Команда: Фурри шутка
@tree.command(name='шутка', description='Рассказывает случайную фурри шутку')
async def шутка(interaction: discord.Interaction):
    if jokes:
        await interaction.response.send_message(random.choice(jokes))
    else:
        await interaction.response.send_message("К сожалению, у меня нет шуток. Убедитесь, что файл jokes.txt существует и содержит шутки.")

# Команда: Аватар пользователя
@tree.command(name='аватар', description='Показывает аватар пользователя в максимальном качестве')
async def аватар(interaction: discord.Interaction, пользователь: Optional[discord.Member] = None):
    member = пользователь or interaction.user
    avatar_url = member.display_avatar.replace(size=1024).url
    embed = discord.Embed(title=f'Аватар {member.display_name}', color=discord.Color.blurple())
    embed.set_image(url=avatar_url)
    await interaction.response.send_message(embed=embed)

# Команда: Профиль
@tree.command(name='профиль', description='Показывает профиль пользователя')
async def профиль(interaction: discord.Interaction, пользователь: Optional[discord.Member] = None):
    member = пользователь or interaction.user
    cursor.execute("""
    SELECT messages_count, voice_time, favorite_word FROM users
    WHERE user_id = ? AND server_id = ?
    """, (member.id, interaction.guild.id))
    result = cursor.fetchone()
    if result:
        messages_count, voice_time, favorite_word = result
    else:
        messages_count = voice_time = 0
        favorite_word = 'Нет данных'

    # Получаем награды пользователя
    cursor.execute("""
    SELECT award_name, emoji, awarded_by, date_awarded FROM awards
    WHERE user_id = ? AND server_id = ?
    """, (member.id, interaction.guild.id))
    awards = cursor.fetchall()

    # Формируем embed
    embed = discord.Embed(title=f'Профиль {member.display_name}', color=discord.Color.purple())
    embed.set_thumbnail(url=member.display_avatar.replace(size=1024).url)
    embed.add_field(name='Ник на сервере', value=member.display_name, inline=False)
    if member.joined_at:
        embed.add_field(name='Дата присоединения', value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    else:
        embed.add_field(name='Дата присоединения', value='Неизвестно', inline=True)
    roles = [role.name for role in member.roles if role.name != '@everyone']
    roles_text = ', '.join(roles) if roles else 'Нет ролей'
    embed.add_field(name='Роли', value=roles_text, inline=True)
    embed.add_field(name='Количество сообщений', value=str(messages_count), inline=True)
    hours, remainder = divmod(voice_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    time_str = f'{int(hours)}ч {int(minutes)}м {int(seconds)}с'
    embed.add_field(name='Время в голосе', value=time_str, inline=True)
    embed.add_field(name='Любимое слово', value=favorite_word or 'Нет данных', inline=False)

    if awards:
        # Форматируем награды
        awards_entries = []
        for award_name, emoji, awarded_by, date_awarded in awards:
            try:
                awarded_by_member = interaction.guild.get_member(awarded_by) or await bot.fetch_user(awarded_by)
                awarded_by_name = awarded_by_member.display_name
            except:
                awarded_by_name = f'ID {awarded_by}'
            awards_entries.append(f"{emoji} **{award_name}** - Выдано {awarded_by_name} ({date_awarded})")

        # Создаем представление для пагинации
        view = AwardsView(awards_entries, entries_per_page=10)

        # Формируем первую страницу
        start = 0
        end = view.entries_per_page
        page_entries = awards_entries[start:end]
        awards_text = '\n'.join(page_entries) if page_entries else 'Нет наград'
        if view.total_pages > 1:
            awards_text += f"\n\nСтраница 1 из {view.total_pages}"

        embed.add_field(name='Награды', value=awards_text, inline=False)
        message = await interaction.response.send_message(embed=embed, view=view)
        view.message = message  # Сохраняем ссылку на сообщение в представлении
    else:
        embed.add_field(name='Награды', value='Нет наград', inline=False)
        await interaction.response.send_message(embed=embed)

# Команда: Топ-10 пользователей по сообщениям
@tree.command(name='топ_сообщения', description='Выводит топ-10 пользователей по сообщениям на сервере')
async def топ_сообщения(interaction: discord.Interaction):
    server_id = interaction.guild.id
    now = datetime.datetime.now(timezone.utc)

    # Получаем текущих участников сервера
    current_members = interaction.guild.members
    current_member_ids = [member.id for member in current_members]

    # Периоды для топов
    periods = {
        "🏆 Общий Топ-10": None,  # Без ограничения времени
        "🏆 Топ-10 за последние 7 дней": now - datetime.timedelta(days=7),
        "🏆 Топ-10 за последние 24 часа": now - datetime.timedelta(hours=24)
    }

    # Получение топ-10 для каждого периода
    top_lists = {}
    for title, since in periods.items():
        if since:
            since_str = since.isoformat()
            # Получаем топ-10 за указанный период, учитывая только текущих участников
            query = f"""
            SELECT user_id, COUNT(*) as message_count FROM messages
            WHERE server_id = ? AND timestamp >= ? AND user_id IN ({','.join(['?']*len(current_member_ids))})
            GROUP BY user_id
            ORDER BY message_count DESC
            LIMIT 10
            """
            cursor.execute(query, (server_id, since_str, *current_member_ids))
        else:
            # Получаем общий топ-10, учитывая только текущих участников
            query = f"""
            SELECT user_id, messages_count FROM users
            WHERE server_id = ? AND user_id IN ({','.join(['?']*len(current_member_ids))})
            ORDER BY messages_count DESC
            LIMIT 10
            """
            cursor.execute(query, (server_id, *current_member_ids))
        top = cursor.fetchall()
        top_lists[title] = top

    # Создание представления для пагинации
    view = TopMessagesView(top_lists)
    embed = view.get_current_embed(interaction.guild)

    # Отправляем сообщение с embed и представлением
    message = await interaction.response.send_message(embed=embed, view=view)
    view.message = message  # Сохраняем ссылку на сообщение для отключения кнопок при тайм-ауте

# Команда: Топ-10 пользователей по голосовой активности
@tree.command(name='топ_голос', description='Выводит топ-10 пользователей по времени в голосовых каналах')
async def топ_голос(interaction: discord.Interaction):
    server_id = interaction.guild.id
    # Получаем текущих участников сервера
    current_members = interaction.guild.members
    current_member_ids = [member.id for member in current_members]

    # Получаем топ-10 по голосовой активности, учитывая только текущих участников
    placeholders = ','.join(['?']*len(current_member_ids))
    query = f"""
    SELECT user_id, voice_time FROM users
    WHERE server_id = ? AND user_id IN ({placeholders})
    ORDER BY voice_time DESC
    LIMIT 10
    """
    cursor.execute(query, (server_id, *current_member_ids))
    top_users = cursor.fetchall()

    embed = discord.Embed(title='🎙️ Топ-10 по голосовой активности', color=discord.Color.green())
    if top_users:
        for i, (user_id, voice_time) in enumerate(top_users, start=1):
            user = interaction.guild.get_member(user_id) or await bot.fetch_user(user_id)
            user_name = user.display_name if user else f'ID {user_id}'
            hours, remainder = divmod(voice_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f'{int(hours)}ч {int(minutes)}м {int(seconds)}с'
            embed.add_field(name=f'{i}. {user_name}', value=f'Время в голосе: {time_str}', inline=False)
    else:
        embed.add_field(name='Топ-10', value='Нет данных', inline=False)
    await interaction.response.send_message(embed=embed)

# ================= Управленческие команды =================

# Команда: Выдать награду пользователю
@tree.command(name='выдать_награду', description='Выдает награду пользователю')
@has_access()
async def выдать_награду(interaction: discord.Interaction, пользователь: discord.Member, награда: str, эмодзи: Optional[str] = None):
    date_awarded = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT INTO awards (user_id, server_id, award_name, emoji, awarded_by, date_awarded)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (пользователь.id, interaction.guild.id, награда, эмодзи or '', interaction.user.id, date_awarded))
    conn.commit()
    await interaction.response.send_message(f'Пользователь {пользователь.mention} получил награду: {эмодзи or ""} **{награда}**')

# Команда: Удалить награду у пользователя
@tree.command(name='удалить_награду', description='Удаляет награду у пользователя')
@has_access()
async def удалить_награду(interaction: discord.Interaction, пользователь: discord.Member, награда: str):
    cursor.execute("""
    DELETE FROM awards WHERE user_id = ? AND server_id = ? AND award_name = ?
    """, (пользователь.id, interaction.guild.id, награда))
    conn.commit()
    await interaction.response.send_message(f'У пользователя {пользователь.mention} удалена награда: **{награда}**')

# Команда: Выдать доступ к команде пользователю
@tree.command(name='выдать_доступ_пользователю', description='Выдает доступ к команде пользователю')
@has_access()
async def выдать_доступ_пользователю(interaction: discord.Interaction, пользователь: discord.Member, команда: str):
    if команда not in [cmd.name for cmd in await tree.fetch_commands()]:
        await interaction.response.send_message(f'Команда /{команда} не найдена.', ephemeral=True)
        return
    cursor.execute("INSERT OR IGNORE INTO access (id, type, command_name) VALUES (?, 'user', ?)", (пользователь.id, команда))
    conn.commit()
    await interaction.response.send_message(f'Пользователю {пользователь.mention} выдан доступ к команде **/{команда}**')

# Команда: Забрать доступ у пользователя
@tree.command(name='забрать_доступ_у_пользователя', description='Забирает доступ к команде у пользователя')
@has_access()
async def забрать_доступ_у_пользователя(interaction: discord.Interaction, пользователь: discord.Member, команда: str):
    if команда not in [cmd.name for cmd in await tree.fetch_commands()]:
        await interaction.response.send_message(f'Команда /{команда} не найдена.', ephemeral=True)
        return
    cursor.execute("DELETE FROM access WHERE id = ? AND type = 'user' AND command_name = ?", (пользователь.id, команда))
    conn.commit()
    await interaction.response.send_message(f'У пользователя {пользователь.mention} забран доступ к команде **/{команда}**')

# Команда: Выдать доступ к команде роли
@tree.command(name='выдать_доступ_роли', description='Выдает доступ к команде роли')
@has_access()
async def выдать_доступ_роли(interaction: discord.Interaction, роль: discord.Role, команда: str):
    if команда not in [cmd.name for cmd in await tree.fetch_commands()]:
        await interaction.response.send_message(f'Команда /{команда} не найдена.', ephemeral=True)
        return
    cursor.execute("INSERT OR IGNORE INTO access (id, type, command_name) VALUES (?, 'role', ?)", (роль.id, команда))
    conn.commit()
    await interaction.response.send_message(f'Роли {роль.mention} выдан доступ к команде **/{команда}**')

# Команда: Забрать доступ у роли
@tree.command(name='забрать_доступ_у_роли', description='Забирает доступ к команде у роли')
@has_access()
async def забрать_доступ_у_роли(interaction: discord.Interaction, роль: discord.Role, команда: str):
    if команда not in [cmd.name for cmd in await tree.fetch_commands()]:
        await interaction.response.send_message(f'Команда /{команда} не найдена.', ephemeral=True)
        return
    cursor.execute("DELETE FROM access WHERE id = ? AND type = 'role' AND command_name = ?", (роль.id, команда))
    conn.commit()
    await interaction.response.send_message(f'У роли {роль.mention} забран доступ к команде **/{команда}**')

# Команда: Доступы
@tree.command(name='доступы', description='Показывает доступы к командам')
@has_access()
async def доступы(interaction: discord.Interaction):
    cursor.execute("SELECT id, type, command_name FROM access")
    accesses = cursor.fetchall()
    if not accesses:
        await interaction.response.send_message("Доступы отсутствуют.")
        return
    embed = discord.Embed(title='🔑 Доступы к командам', color=discord.Color.gold())
    for id_, type_, command_name in accesses:
        if type_ == 'user':
            try:
                obj = interaction.guild.get_member(id_) or await bot.fetch_user(id_)
                obj_name = obj.display_name if obj else f'Пользователь с ID {id_}'
            except:
                obj_name = f'Пользователь с ID {id_}'
        else:
            obj = interaction.guild.get_role(id_)
            obj_name = obj.name if obj else f'Роль с ID {id_}'
        embed.add_field(name=f'{type_.capitalize()}: {obj_name}', value=f'Команда: /{command_name}', inline=False)
    await interaction.response.send_message(embed=embed)

# ================= Представления для пагинации =================

# Представление для пагинации наград
class AwardsView(View):
    def __init__(self, awards_entries, entries_per_page=10):
        super().__init__(timeout=60)  # Время ожидания взаимодействия (в секундах)
        self.awards_entries = awards_entries
        self.entries_per_page = entries_per_page
        self.total_pages = math.ceil(len(self.awards_entries) / self.entries_per_page) if self.awards_entries else 1
        self.current_page = 0
        self.message = None  # Свойство для хранения ссылки на сообщение

        # Инициализируем кнопки и устанавливаем их состояние
        self.previous_button = Button(label='Предыдущая', style=discord.ButtonStyle.primary, disabled=True)
        self.next_button = Button(label='Следующая', style=discord.ButtonStyle.primary, disabled=(self.total_pages <= 1))

        self.previous_button.callback = self.previous_page
        self.next_button.callback = self.next_page

        self.add_item(self.previous_button)
        self.add_item(self.next_button)

    async def update_embed(self, interaction):
        start = self.current_page * self.entries_per_page
        end = start + self.entries_per_page
        page_entries = self.awards_entries[start:end]
        awards_text = '\n'.join(page_entries) if page_entries else 'Нет наград'

        if self.total_pages > 1:
            awards_text += f"\n\nСтраница {self.current_page + 1} из {self.total_pages}"

        # Обновляем поле "Награды" в embed
        embed = interaction.message.embeds[0]
        # Найдем индекс поля "Награды"
        awards_field_index = next((i for i, field in enumerate(embed.fields) if field.name.startswith('Награды')), None)
        if awards_field_index is not None:
            embed.set_field_at(index=awards_field_index,
                               name='Награды',
                               value=awards_text,
                               inline=False)
        else:
            embed.add_field(name='Награды', value=awards_text, inline=False)

        # Обновляем состояние кнопок
        self.previous_button.disabled = (self.current_page == 0)
        self.next_button.disabled = (self.current_page >= self.total_pages - 1)

        await interaction.response.edit_message(embed=embed, view=self)

    async def previous_page(self, interaction: discord.Interaction):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_embed(interaction)

    async def next_page(self, interaction: discord.Interaction):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            await self.update_embed(interaction)

    async def on_timeout(self):
        # Отключаем кнопки при истечении тайм-аута
        self.previous_button.disabled = True
        self.next_button.disabled = True
        if self.message:
            await self.message.edit(view=self)

# Представление для пагинации топов сообщений
class TopMessagesView(View):
    def __init__(self, top_lists, entries_per_page=10):
        super().__init__(timeout=60)  # Время ожидания взаимодействия (в секундах)
        self.top_lists = top_lists  # Словарь с названиями топов и их данными
        self.entries_per_page = entries_per_page
        self.pages = list(self.top_lists.keys())
        self.current_page = 0
        self.message = None  # Свойство для хранения ссылки на сообщение

        # Инициализируем кнопки и устанавливаем их состояние
        self.previous_button = Button(label='Предыдущий топ', style=discord.ButtonStyle.primary, disabled=True)
        self.next_button = Button(label='Следующий топ', style=discord.ButtonStyle.primary, disabled=(len(self.pages) <= 1))

        self.previous_button.callback = self.previous_page
        self.next_button.callback = self.next_page

        self.add_item(self.previous_button)
        self.add_item(self.next_button)

    def get_current_embed(self, guild):
        title = self.pages[self.current_page]
        top = self.top_lists[title]
        embed = discord.Embed(title=title, color=discord.Color.blue())
        if top:
            for i, (user_id, count) in enumerate(top, start=1):
                user = guild.get_member(user_id) or None
                if user:
                    user_name = user.display_name
                else:
                    user_name = f'ID {user_id}'
                embed.add_field(name=f"{i}. {user_name}", value=f"Сообщений: {count}", inline=False)
        else:
            embed.add_field(name='Топ-10', value='Нет данных', inline=False)
        return embed

    async def update_embed(self, interaction, guild):
        embed = self.get_current_embed(guild)

        # Обновляем состояние кнопок
        self.previous_button.disabled = (self.current_page == 0)
        self.next_button.disabled = (self.current_page == len(self.pages) - 1)

        await interaction.response.edit_message(embed=embed, view=self)

    async def previous_page(self, interaction: discord.Interaction):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_embed(interaction, interaction.guild)

    async def next_page(self, interaction: discord.Interaction):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            await self.update_embed(interaction, interaction.guild)

    async def on_timeout(self):
        # Отключаем кнопки при истечении тайм-аута
        self.previous_button.disabled = True
        self.next_button.disabled = True
        if self.message:
            await self.message.edit(view=self)

# ================= Обработка ошибок команд =================

@bot.event
async def on_app_command_error(interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message('У вас нет прав на использование этой команды.', ephemeral=True)
    elif isinstance(error, app_commands.CommandNotFound):
        await interaction.response.send_message('Команда не найдена.', ephemeral=True)
    elif isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message('У вас нет доступа к этой команде.', ephemeral=True)
    else:
        await interaction.response.send_message(f'Произошла ошибка: {error}', ephemeral=True)

# Запуск бота
token = os.getenv('DISCORD_TOKEN')
if not token:
    raise ValueError('DISCORD_TOKEN must be set in .env file')
bot.run(token)  # Замените на токен вашего бота
