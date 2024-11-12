.PHONY: bot
bot.start:
	ENV=development pipenv run python -m src.main

bot.test:
	ENV=development pipenv run python -m pytest -vv -s tests

bot.build:
	docker build -t telegram_bot:latest .

