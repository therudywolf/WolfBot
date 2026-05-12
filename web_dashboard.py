#!/usr/bin/env python3
"""
WolfBot Web Dashboard and Management API

Provides a Flask-based web interface and REST API for managing the Discord bot
without needing to use bot commands. Supports viewing statistics, managing awards,
and managing access control.

License: GNU Affero General Public License v3 (AGPLv3)
Author: therudywolf
"""

import os
import sqlite3
import json
import logging
from datetime import datetime
from functools import wraps
from typing import Dict, Any, Tuple

from flask import Flask, render_template_string, request, jsonify, abort
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', 'bot_database.db')
ADMIN_TOKEN = os.getenv('WEB_ADMIN_TOKEN', 'change-me-in-production')
WEB_PORT = int(os.getenv('WEB_PORT', 5000))


class BotDatabaseManager:
    """Manages access to the Discord bot database"""

    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._connect()

    def _connect(self):
        """Connect to the database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise

    def get_server_stats(self, server_id: int) -> Dict[str, Any]:
        """Get statistics for a server"""
        try:
            # Top users by messages
            self.cursor.execute("""
                SELECT user_id, messages_count FROM users
                WHERE server_id = ?
                ORDER BY messages_count DESC LIMIT 10
            """, (server_id,))
            top_messages = [dict(row) for row in self.cursor.fetchall()]

            # Top users by voice time
            self.cursor.execute("""
                SELECT user_id, voice_time FROM users
                WHERE server_id = ?
                ORDER BY voice_time DESC LIMIT 10
            """, (server_id,))
            top_voice = [dict(row) for row in self.cursor.fetchall()]

            # Total users
            self.cursor.execute("""
                SELECT COUNT(DISTINCT user_id) as count FROM users
                WHERE server_id = ?
            """, (server_id,))
            total_users = self.cursor.fetchone()['count']

            return {
                'server_id': server_id,
                'total_users': total_users,
                'top_by_messages': top_messages,
                'top_by_voice': top_voice,
                'timestamp': datetime.now().isoformat()
            }
        except sqlite3.Error as e:
            logger.error(f"Error fetching server stats: {e}")
            return {}

    def get_awards(self, server_id: int) -> list:
        """Get all awards for a server"""
        try:
            self.cursor.execute("""
                SELECT award_id, user_id, award_name, emoji, awarded_by, date_awarded
                FROM awards
                WHERE server_id = ?
                ORDER BY date_awarded DESC
            """, (server_id,))
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error fetching awards: {e}")
            return []

    def give_award(self, server_id: int, user_id: int, award_name: str,
                   emoji: str, awarded_by: int) -> bool:
        """Give an award to a user"""
        try:
            self.cursor.execute("""
                INSERT INTO awards (user_id, server_id, award_name, emoji, awarded_by, date_awarded)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, server_id, award_name, emoji, awarded_by, datetime.now().isoformat()))
            self.conn.commit()
            logger.info(f"Award '{award_name}' given to user {user_id} in server {server_id}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error giving award: {e}")
            return False

    def get_access_list(self, server_id: int) -> Dict[str, list]:
        """Get access control list for a server"""
        try:
            self.cursor.execute("""
                SELECT id, type, command_name FROM access
                ORDER BY command_name, type
            """)
            rows = self.cursor.fetchall()

            # Group by command
            access_dict = {}
            for row in rows:
                cmd = row['command_name']
                if cmd not in access_dict:
                    access_dict[cmd] = {'users': [], 'roles': []}

                if row['type'] == 'user':
                    access_dict[cmd]['users'].append(row['id'])
                else:
                    access_dict[cmd]['roles'].append(row['id'])

            return access_dict
        except sqlite3.Error as e:
            logger.error(f"Error fetching access list: {e}")
            return {}

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


# Initialize database manager
db_manager = BotDatabaseManager()


def require_token(f):
    """Decorator to require admin token for API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('X-Admin-Token')
        if not token or token != ADMIN_TOKEN:
            logger.warning(f"Unauthorized API access attempt from {request.remote_addr}")
            abort(401)
        return f(*args, **kwargs)
    return decorated_function


# ==================== Web Routes ====================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WolfBot Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.1em; opacity: 0.9; }
        .content {
            padding: 40px;
        }
        .section {
            margin-bottom: 40px;
        }
        .section h2 {
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: #f5f5f5;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .stat-card h3 { color: #667eea; margin-bottom: 10px; }
        .stat-card p { font-size: 2em; font-weight: bold; color: #333; }
        .api-docs {
            background: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            overflow-x: auto;
        }
        .endpoint {
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #667eea;
        }
        .method {
            display: inline-block;
            padding: 4px 8px;
            background: #667eea;
            color: white;
            border-radius: 4px;
            margin-right: 10px;
            font-weight: bold;
        }
        .method.get { background: #61affe; }
        .method.post { background: #49cc90; }
        .method.delete { background: #f93e3e; }
        footer {
            background: #f5f5f5;
            padding: 20px;
            text-align: center;
            color: #666;
            border-top: 1px solid #ddd;
        }
        .warning {
            background: #fff3cd;
            border: 1px solid #ffc107;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🐺 WolfBot Dashboard</h1>
            <p>Management Panel for Discord Bot Statistics & Control</p>
        </div>

        <div class="content">
            <div class="warning">
                <strong>⚠️ Security Notice:</strong> This dashboard requires authentication.
                Set <code>WEB_ADMIN_TOKEN</code> environment variable for secure access.
            </div>

            <div class="section">
                <h2>📊 API Documentation</h2>
                <div class="api-docs">
                    <div class="endpoint">
                        <span class="method get">GET</span>
                        <code>/api/health</code> - Health check
                    </div>
                    <div class="endpoint">
                        <span class="method get">GET</span>
                        <code>/api/stats/&lt;server_id&gt;</code> - Server statistics (requires token)
                    </div>
                    <div class="endpoint">
                        <span class="method get">GET</span>
                        <code>/api/awards/&lt;server_id&gt;</code> - List awards (requires token)
                    </div>
                    <div class="endpoint">
                        <span class="method post">POST</span>
                        <code>/api/awards/&lt;server_id&gt;</code> - Give award (requires token)
                    </div>
                    <div class="endpoint">
                        <span class="method get">GET</span>
                        <code>/api/access/&lt;server_id&gt;</code> - Access control list (requires token)
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>🔧 Usage</h2>
                <p><strong>With Authentication Token:</strong></p>
                <pre style="background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto;">
curl -H "X-Admin-Token: your_webadmin_token" http://localhost:5000/api/stats/123456789</pre>
            </div>

            <div class="section">
                <h2>📝 Features</h2>
                <ul style="margin-left: 20px; line-height: 1.8;">
                    <li>View server statistics and member rankings</li>
                    <li>Manage awards and achievements</li>
                    <li>Control command access for users and roles</li>
                    <li>REST API for integration with other tools</li>
                    <li>Full AGPL v3 compliance</li>
                </ul>
            </div>
        </div>

        <footer>
            <p>WolfBot - Licensed under GNU Affero General Public License v3</p>
            <p><a href="https://github.com/therudywolf/WolfBot">GitHub Repository</a></p>
        </footer>
    </div>
</body>
</html>
"""


@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'database': 'connected' if db_manager.conn else 'disconnected'
    })


@app.route('/api/stats/<int:server_id>', methods=['GET'])
@require_token
def get_stats(server_id: int):
    """Get server statistics"""
    stats = db_manager.get_server_stats(server_id)
    if not stats:
        abort(404)
    return jsonify(stats)


@app.route('/api/awards/<int:server_id>', methods=['GET'])
@require_token
def get_awards(server_id: int):
    """Get awards for a server"""
    awards = db_manager.get_awards(server_id)
    return jsonify({'awards': awards, 'count': len(awards)})


@app.route('/api/awards/<int:server_id>', methods=['POST'])
@require_token
def post_award(server_id: int):
    """Give an award to a user"""
    data = request.get_json()

    required = ['user_id', 'award_name', 'emoji', 'awarded_by']
    if not all(k in data for k in required):
        return jsonify({'error': f'Missing required fields: {", ".join(required)}'}), 400

    success = db_manager.give_award(
        server_id=server_id,
        user_id=data['user_id'],
        award_name=data['award_name'],
        emoji=data['emoji'],
        awarded_by=data['awarded_by']
    )

    if success:
        return jsonify({'status': 'ok', 'message': 'Award given successfully'})
    else:
        return jsonify({'error': 'Failed to give award'}), 500


@app.route('/api/access/<int:server_id>', methods=['GET'])
@require_token
def get_access_list(server_id: int):
    """Get access control list"""
    access_list = db_manager.get_access_list(server_id)
    return jsonify(access_list)


@app.errorhandler(401)
def unauthorized(error):
    """Handle 401 errors"""
    return jsonify({'error': 'Unauthorized - missing or invalid X-Admin-Token header'}), 401


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    try:
        logger.info(f"Starting WolfBot Web Dashboard on port {WEB_PORT}")
        app.run(
            host='0.0.0.0',
            port=WEB_PORT,
            debug=os.getenv('DEBUG', 'false').lower() == 'true'
        )
    except KeyboardInterrupt:
        logger.info("Shutting down dashboard")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
    finally:
        db_manager.close()
