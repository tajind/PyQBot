# QBot

A python discord bot that allows friends to join a queue and create private games with additional features such as randomizing the teams.

## Commands

Prefix = "."
**_Join / J_** - join the queue
**_Leave / L_** - leave the queue
**_ConfirmTeams_** -> yes or no - confirm the teams once the games are fair
**_Shuffle_** -> yes or no - to reshuffle the teams
**_Queue / Q_** - see who is in the queue currently
**_BotChannel_** - set a specific channel for bot to reply to commands to
**_RestartQ_** - restarts the queue, limited to authorized users
**_Currentmatch / current_** - check the ongoing match

### Setup

1. Install the required modules. `pip install -r requirements.txt`
2. Add your discord bot token in the `tokenFile.py` You can obtain this by visiting [here](https://discord.com/developers/applications)
3. Run the python file by simple opening a console in the folder and typing `python main-bot.py`
4. Invite the bot to your server and set a bot channel
5. **You're ready!** .join to join a queue

#### Requirements

- discord
- asyncio

#### Thank you for checking the project

> Made with ❤️ by Tajinder.
