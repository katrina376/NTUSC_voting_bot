# NTUSC_voting_bot
A Telegram Bot for the members of a congress to vote during meetings.  
Originally created by [artistic709](https://github.com/artistic709/NTUSC_voting_bot).  
Powered by [telepot](https://github.com/nickoala/telepot).  

## Requirements
* Python 3 (3.6 is used in development)
* Telepot (==12.1)

## Install , Settings and Run
1. Clone the repo and install the requirements.
```
  git clone https://github.com/katrina376/NTUSC_voting_bot
  cd NTUSC_voting_bot
  pip install -r requirements.txt
  mkdir meta
  mkdir data
```
2. Create `stu_id.txt` inside `meta/`. List the student IDs of the members in this file.
3. Setup.
```
  cp config.ini.example config.ini
  export BOT_TOKEN=<YOUR_TELEGRAM_BOT_TOKEN>
  export MAIL_PASSWORD=<PASSWORD_OF_MAIL_FOR_REGISTER>
```
4. Edit `config.ini`.
5. Run `bot.py` with Python 3.
6. The result of polls will be saved in `data/`.

## Usage
First, start a chat with the bot using any message. You can send text or stickers to the bot. It will reply.  
The commands are listed below.   

### All Members
* `/login <STUDENT_ID>`: Enter the student ID. The register code will be sent to the NTU mailbox.
* `/code <REG_CODE>`: Enter the code.
* `/vote`: Get the ballot when there is a poll. This command only works if the chairperson starts a poll.

### Chairperson
* `/ask <QUESTION>`: Enter the question of a poll.
* `/add <CHOICE>`: Add choices. If nothing is added, the default choice set (for, against and abstain) will be used.
* `/go`: Start the poll.
* `/end`: End the poll, and export the result.

## License
