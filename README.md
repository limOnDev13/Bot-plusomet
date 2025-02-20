# XTTR test task
A test assignment from the XTTR company.

# Bot-plusomet

## Description
The project is a moderator bot capable of detecting toxic and LLM-generated chat messages. Moderation takes place using LLM (currently YandexGPT). A Telegram bot (written in Aiogram) is used as a bot. But due to the project's architecture based on the Producer/Consumer pattern and Redis-based queues, a moderator bot can be added to almost any chat with minimal additions to the codebase. The architecture of the project also allows you to run a moderator as a separate service for different chats, and add separate moderators to each chat.

## Demo

![](demo.gif)

---
## Setup and launch


Installation and launching will require several key tools:
- **YandexGPT** - tokens are required for authentication and authorization. [Instruction](https://yandex.cloud/ru/docs/foundation-models/quickstart/yandexgpt)
- **Bot token** - from BotFather for telegram bot. [BotFather](https://t.me/BotFather)
- **Chat** - the chatbot must be added to the chat and made an administrator. You must also add the CHAT_ID - id of the chat - to the environment variables. For convenience, it can be obtained from the logs. You need to launch a container with a with BOT_DEBUG=1 and write any message in the chat. A message with the chat ID will appear in the logs.
- **git** - for downloading project files.
- **Docker** - for containerization of services. 

When the necessary tools are ready, it will be a small matter. Assemble environment variables based on .env.example, assemble containers using docker-compose.yml using the command ```docker compose up --build``` from root. Done!
___

## Technologies
- YandexGPT
- Aiogram
- Redis
- Docker
- pytest

## Ways of development and improvement
- The project is not sufficiently covered with tests - more tests are planned to be added in the future.
- Perhaps the prompts can be reduced to reduce the cost of requests without losing the quality of responses.
- Using queues on Redis allows you to abstract from Telegram and make a service for moderation of several chats on different platforms.