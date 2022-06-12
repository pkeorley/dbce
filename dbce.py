import disnake
from disnake.ext import commands

import errors
from protectedtextapi import DB as DataBase


class Helper:
    """
    Helper for Bot
    """

    def __init__(self):
        self.prefix = None
        self.commands = []
        self.data = None
        self.database = None
        self.login = None
        self.code = None
        self.password = None
        self.variables = None
        self.bot = None

    async def on_ready(self):
        self.database = DataBase(login=self.login, password=self.password)
        self.data = self.database.data
        await self.bot.wait_until_ready()
        for guild in self.bot.guilds:
            if not str(guild.id) in self.data:
                self.data[str(guild.id)] = {}
            for member in guild.members:
                if not str(member.id) in self.data[str(guild.id)]:
                    self.data[str(guild.id)][str(member.id)] = self.variables
                elif str(member.id) in self.data[str(guild.id)]:
                    for key, value in self.variables.items():
                        if key not in self.data[str(guild.id)][str(member.id)]:
                            self.data[str(guild.id)][str(member.id)][key] = value
        self.database.save(self.data)
        print(f"[*] {self.bot.user} is ready!")

    async def on_message(self, message):
        for command in self.commands:
            name, code = command["name"], command["code"]
            if message.content.startswith(self.prefix + name):
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
                    embed.colour = hex(int("0x" + color, 16))
                    code = code.replace(f"$color[{color}]", "")

                try:
                    await message.channel.send(content=code, embed=embed)
                except (BaseException,):
                    await message.channel.send(content=f"❌ Exception in: {name}\n{code}")


class Bot(Helper):
    def __init__(self, **kwargs):
        """
        Base bot class

        :parameter prefix: default prefix for you bot
        :type prefix: str
        :parameter token: token lmao
        :type token: str
        :parameter intents: all intents or null
        :type intents: bool
        """
        super().__init__()
        self.prefix = kwargs.get("prefix")
        self.token = kwargs.get("token")
        self.intents = kwargs.get("intents", False)

    def connect_database(self, dictionary: dict = None, variables: dict = None):
        if variables is None:
            variables = {}
        self.login = dictionary.get("login")
        self.password = dictionary.get("password")
        if not self.login or not self.password:
            raise errors.ParamCannotBeEmpty("Login or password empty.")
        self.variables = variables
        print("[*] DataBase connected.")

    def command(self, dictionary: dict = None):
        if dictionary is None:
            dictionary = {}
        name = dictionary.get("name")
        code = dictionary.get("code")
        if not name or not code:
            raise errors.ParamCannotBeEmpty("Name or code empty.")
        self.commands.append({
            "name": name,
            "code": code
        })

    def run(self):
        if self.intents:
            self.bot = commands.Bot(
                command_prefix=self.prefix,
                intents=disnake.Intents.all()
            )
        else:
            self.bot = commands.Bot(
                command_prefix=self.prefix,
                intents=disnake.Intents.default()
            )

        self.bot.add_listener(super().on_ready, "on_ready")
        self.bot.add_listener(super().on_message, "on_message")

        self.bot.run(self.token)
