import os
import json
from http.server import BaseHTTPRequestHandler

from telegram import Update
from telegram.ext import Application, CommandHandler


TOKEN = os.environ["BOT_TOKEN"]


async def start(update: Update, context):
    await update.message.reply_text(
        "👋 سلام! خوش اومدی به ربات تستی من 🤖"
    )


application = (
    Application.builder()
    .token(TOKEN)
    .updater(None)
    .build()
)

application.add_handler(
    CommandHandler("start", start)
)


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Telegram bot is working!")

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        data = json.loads(body)

        update = Update.de_json(
            data,
            application.bot
        )

        import asyncio

        asyncio.run(
            application.process_update(update)
        )

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")
