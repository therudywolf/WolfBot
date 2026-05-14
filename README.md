# WolfBot 🐺

A feature-rich Discord bot written in Python with comprehensive statistics, user profiles, achievements, and more.

**License:** GNU Affero General Public License v3 (AGPLv3) - See [LICENSE](LICENSE) for details.
AGPL v3 Copyleft applies to reuse, modification, and network deployment of derived versions.

## Features

- 📊 **Activity Tracking**: Monitor message counts and voice channel time per user
- 🎯 **User Profiles**: Detailed profiles with roles, statistics, and achievements
- 🏆 **Award System**: Grant and manage user achievements with custom emojis
- 🎤 **Voice Analytics**: Track time spent in voice channels with top rankings
- 😄 **Jokes Command**: Custom joke command with phrases from `jokes.txt`
- 🔧 **Access Control**: Granular permission management for commands
- 📈 **Word Analytics**: Track popular words with configurable stop-word filtering
- 🌐 **Web Dashboard**: REST API and web interface for bot management
- 🐳 **Docker Support**: Ready-to-run containerized deployment

## Requirements

- Python 3.9+ (3.11+ recommended)
- Discord.py 2.0+
- Flask (for web dashboard)
- discord.py requires privileged intents enabled in Discord Developer Portal:
  - Message Content Intent
  - Member List Intent
  - Presence Intent

## Quick Start

### Local Installation

1. Clone the repository:
```bash
git clone https://github.com/therudywolf/WolfBot.git
cd WolfBot
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure your bot:
```bash
cp .env.example .env
# Edit .env and set:
#   - DISCORD_TOKEN: Your bot token from Discord Developer Portal
#   - OWNER_ID: Your Discord user ID
```

5. Run the bot:
```bash
python wolfbot.py
```

### Docker Installation

1. Clone and navigate to the repository:
```bash
git clone https://github.com/therudywolf/WolfBot.git
cd WolfBot
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your Discord credentials
```

3. Build and run with Docker Compose:
```bash
docker-compose up -d
```

The bot will run in a container with automatic restarts.

### Docker Build (Manual)

```bash
docker build -t wolfbot .
docker run -d --name wolfbot \
  -e DISCORD_TOKEN=your_webadmin_token \
  -e OWNER_ID=your-id \
  -v wolfbot_data:/app/data \
  wolfbot
```

## Configuration

### Environment Variables

Create a `.env` file (copy from `.env.example`):

```env
# Required
DISCORD_TOKEN=your-discord-bot-token
OWNER_ID=your-discord-user-id

# Optional
DEBUG=false
LOG_LEVEL=INFO
WEB_PORT=5000
WEB_ADMIN_TOKEN=your-secret-token
DATABASE_PATH=/app/data/bot_database.db
```

### Customization

- **jokes.txt**: Add custom jokes, one per line
- **TRIGGER_VOICE_CHANNEL_ID**: Set in code to enable temp voice channels
- **PUBLIC_COMMANDS**: Modify accessible commands list in `wolfbot.py`

## Commands

### Public Commands

- `/помощь` - List available commands
- `/информация_о_сервере` - Server information
- `/профиль` - User profile
- `/аватар` - User avatar
- `/шутка` - Random joke
- `/топ_сообщения` - Top users by message count
- `/топ_голос` - Top users by voice time

### Admin Commands (Owner Only)

- `/информация_о_хосте` - Host system information
- `/пинг` - Bot latency
- `/выдать_награду` - Grant achievement
- `/удалить_награду` - Revoke achievement
- `/выдать_доступ_пользователю` - Grant user command access
- `/забрать_доступ_у_пользователя` - Revoke user command access
- `/выдать_доступ_роли` - Grant role command access
- `/забрать_доступ_у_роли` - Revoke role command access
- `/доступы` - List command access

## Web Dashboard & API

The bot includes a web dashboard and REST API for management tasks.

### Start Web Server

```bash
python web_dashboard.py
```

Access at: `http://localhost:5000`

### API Endpoints

All endpoints (except `/health`) require `X-Admin-Token` header:

```bash
curl -H "X-Admin-Token: your_webadmin_token" http://localhost:5000/api/health
```

**Available Endpoints:**

- `GET /` - Web dashboard
- `GET /api/health` - Health check
- `GET /api/stats/<server_id>` - Server statistics
- `GET /api/awards/<server_id>` - List awards
- `POST /api/awards/<server_id>` - Grant award
- `GET /api/access/<server_id>` - Access control list

## Database

The bot uses SQLite for data persistence. The database file (`bot_database.db`) is created automatically on first run and stores:

- User messages and voice time
- Word frequency analysis
- Awards and achievements
- Command access control
- Message history (optional)

### Database Location

- **Local**: `./bot_database.db`
- **Docker**: `/app/data/bot_database.db` (persisted via volume)

## Project Structure

```
WolfBot/
├── wolfbot.py              # Main bot code
├── web_dashboard.py        # Web server and API
├── jokes.txt              # Joke phrases (one per line)
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker image definition
├── docker-compose.yml     # Docker Compose configuration
├── .env.example          # Environment variables template
├── .gitignore            # Git exclusions
├── LICENSE               # AGPLv3 License
├── FOSS.md              # FOSS compliance and dependencies
├── CONTRIBUTING.md      # Contribution guidelines
└── README.md            # This file
```

## Development

### Setup Development Environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Running Tests

```bash
# (Test suite to be added)
python -m pytest tests/
```

### Code Style

- Python 3.9+ compatibility required
- Follow PEP 8 guidelines
- Use type hints where possible

## Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## License

This project is licensed under the **GNU Affero General Public License v3 (AGPLv3)**.

Key points:
- ✅ You can use, modify, and distribute this software freely
- ✅ You must provide access to source code for network services
- ✅ Modifications must be licensed under AGPLv3
- ⚠️ This is a Copyleft license - ensure you understand your obligations

See [LICENSE](LICENSE) and [FOSS.md](FOSS.md) for complete details.

## Support & Issues

- 🐛 **Bug Reports**: Open an issue on GitHub
- 💡 **Feature Requests**: Discussions are welcome
- ❓ **Questions**: Check existing issues first

## Authors

- **therudywolf** - Original author and maintainer

## Changelog

See [GitHub Releases](https://github.com/therudywolf/WolfBot/releases) for version history.

## Acknowledgments

- Discord.py community
- Python community
- All contributors

---

**Made with ❤️ by therudywolf**

[GitHub](https://github.com/therudywolf/WolfBot) | [Issues](https://github.com/therudywolf/WolfBot/issues)
