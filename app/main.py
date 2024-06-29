"""Main module for the chat application."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncGenerator

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

from app.kafka_consumer import consume_messages_async
from app.models import Message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

connected_users = set()
websocket_connections = {}


@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str) -> None:
    """WebSocket endpoint for chat."""
    await websocket.accept()
    connected_users.add(username)
    websocket_connections[username] = websocket
    logger.info(f"User {username} connected.")

    try:
        while True:
            data = await websocket.receive_text()
            message = {"username": username, "content": data}
            logger.info(f"Received message from {username}: {data}")

            logger.info(f"Message to broadcast: {message}")
            for ws in websocket_connections.values():
                await ws.send_json(message)
    except Exception:
        logger.exception(f"WebSocket connection closed for {username}")
        connected_users.remove(username)
        del websocket_connections[username]


@app.get("/", response_class=HTMLResponse)
def homepage() -> HTMLResponse:
    """Homepage for the chat application."""
    file_path = Path("app/templates/chat.html")
    with file_path.open() as file:
        content = file.read()
    return HTMLResponse(content=content)


@app.get("/messages", response_model=list[Message])
async def get_messages() -> list[Any]:
    """Get messages from Kafka topic."""
    return [Message(**message) async for message in consume_messages_async()]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    """
    Context manager to handle the lifespan of the application.

    Args:
    ----
        app (FastAPI): FastAPI application.

    """
    logger.info("Starting up the application.")

    yield

    logger.info("Shutting down the application.")
    for websocket in websocket_connections.values():
        await websocket.close()


app.router.lifespan_context = lifespan


async def consume_messages_and_broadcast() -> None:
    """Consume messages from Kafka and broadcast to all connected users."""
    try:
        async for message in consume_messages_async():
            logger.info(f"Broadcasting message: {message}")
            for websocket in websocket_connections.values():
                await websocket.send_json(message)
    except Exception:
        logger.exception("Error in consume_messages_and_broadcast.")
