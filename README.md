# Memorization bot

This is a telegram bot, maked with aiogram.
Bot can ask question from list and check answer is correct,
it can help memorizing something.\
Bot have admin panel to edit questions and sections.

### Getting started
1. Clone repository
2. Insert your bot token and telegram id in file `config.example.ini`
3. Run `docker-compose up`


### Environment variables:
You can set environment variables in file `.env.example`\
Variables:\
`MEMORYBOT_CONFIG_PATH` - Path to custom 
configuration file. If not setting, used default
config - `config.example.ini`.

### Configuration file:
You can edit configuration file `config.example.ini` or create new configuration file.
Only supported file format - `.ini`.
