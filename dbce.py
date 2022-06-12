import sys

import disnake
from disnake.ext import commands

from protectedtextapi import DB as DataBase


class Bot:
	def __init__(self, dictionary: dict={}):
		self.prefix = dictionary["prefix"] or None
		self.token = dictionary["token"] or None
		self.intents = dictionary["intents"] or False
		self.commands = []


	def connect_database(self, dictionary: dict={}, variables: dict={}):
		self.login = dictionary["login"]
		self.password = dictionary["password"]
		self.variables = variables
		print("[*] DataBase connected.")



	def command(self, dictionary: dict={}):
		self.name = dictionary["name"]
		self.code = dictionary["code"]

		self.commands.append({
			"name": self.name,
			"code": self.code
		})


	def run(self):

		if self.intents:
			self.bot = commands.Bot(
				command_prefix=self.prefix,
				intents=disnake.Intents.all()
			)
		elif not intents:
			self.bot = commands.Bot(
				command_prefix=self.prefix
			)
		

		@self.bot.event
		async def on_ready():
			self.database = DataBase(login=self.login, password=self.password)
			self.data = self.database.data
			if self.bot.is_ready() is True:
				for guild in self.bot.guilds:
					if not str(guild.id) in self.data:
						self.data[str(guild.id)] = {}
					for member in guild.members:
						if not str(member.id) in self.data[str(guild.id)]:
							self.data[str(guild.id)][str(member.id)] = self.variables
						elif str(member.id) in self.data[str(guild.id)]:
							for key, value in self.variables.items():
								if not key in self.data[str(guild.id)][str(member.id)]:
									self.data[str(guild.id)][str(member.id)][key] = value
			self.database.save(self.data)
			print(f"[*] {self.bot.user} is ready!")


		@self.bot.event
		async def on_message(message):
			for command in self.commands:
				name, code = command["name"], command["code"]
				if message.content.startswith(self.prefix+name):
					embed = disnake.Embed()

					while "$title[" in code:
						title = code.split("$title[")[1].split("]")[0]
						embed.title = title or None
						code = code.replace(f"$title[{title}]", "")


					while "$description[" in code:
						description = code.split("$description[")[1].split("]")[0]
						embed.description = description or None
						code = code.replace(f"$description[{description}]", "")

					while "$color[" in code:
						color = code.split("$color[")[1].split("]")[0]
						embed.color = eval("0x"+color)
						code = code.replace(f"$color[{color}]", "")

					try:
						await message.channel.send(content=code, embed=embed)
					except Exception:
						await message.channel.send(content=code)


		self.bot.run(self.token)
