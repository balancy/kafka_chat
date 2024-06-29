"""Main module for the chat application."""
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Generator

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

from app.kafka_consumer import consume_messages_async
from app.kafka_producer import publish_message
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
            for _, ws in websocket_connections.items():
                await ws.send_json(message)
    except Exception as e:
        logger.error(f"WebSocket connection closed for {username}: {str(e)}")
        connected_users.remove(username)
        del websocket_connections[username]


@app.get("/", response_class=HTMLResponse)
async def homepage() -> HTMLResponse:
    """Homepage for the chat application."""
    return HTMLResponse(content=open("app/templates/chat.html", "r").read())


@app.get("/messages", response_model=list[Message])
async def get_messages() -> list[Any]:
    """Get messages from Kafka topic."""
    messages = []
    async for message in consume_messages_async():
        messages.append(Message(**message))
    return messages


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    """Context manager to handle the lifespan of the application.

    Args:
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
            for _, websocket in websocket_connections.items():
                await websocket.send_json(message)
    except Exception as e:
        logger.error(f"Error in consume_messages_and_broadcast: {str(e)}")