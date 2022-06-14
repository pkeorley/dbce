import disnake
import disnake_components
from disnake.ext import commands

from .errors import *
# from .protectedtextapi import DB as DataBase


class Helper:
    """
    Helper for Bot
    """

    def __init__(self):
        self.prefix = None
        self.commands = []
        self.data = {}
        # self.database = None
        self.login = None
        self.code = None
        self.password = None
        self.variables = None
        self.bot = None

    async def on_ready(self):
        # self.database = DataBase(login=self.login, password=self.password)
        # self.data = self.database.data
        await self.bot.wait_until_ready()
        for guild in self.bot.guilds:
            guild = await self.bot.fetch_guild(guild.id)
            try:
                self.data[str(guild.id)]
            except KeyError:
                self.data[str(guild.id)] = {}
            for member in guild.members:
                if not str(member.id) in self.data[str(guild.id)]:
                    self.data[str(guild.id)][str(member.id)] = self.variables
                elif str(member.id) in self.data[str(guild.id)]:
                    for key, value in self.variables.items():
                        if key not in self.data[str(guild.id)][str(member.id)]:
                            self.data[str(guild.id)][str(member.id)][key] = value
        # self.database.save(self.data)
        print(f"[*] {self.bot.user} is ready!")

    @staticmethod
    async def on_error(_, __):
        if isinstance(__, commands.CommandNotFound):
            return

    async def on_message(self, message):
        for command in self.commands:
            name, code = command["name"], command["code"]
            if message.content.startswith(self.prefix + name):
                embed = disnake.Embed()
                buttons = []

                while "$title[" in code:
                    title = code.split("$title[")[1].split("]")[0].split(";")
                    embed.title = title[0]
                    if len(title) == 2:
                        embed.url = title[1]
                        code = code.replace(f"$title[{title[0]};{title[1]}]", "")
                    else:
                        code = code.replace(f"$title[{title[0]}]", "")

                while "$description[" in code:
                    description = code.split("$description[")[1].split("]")[0]
                    embed.description = description
                    code = code.replace(f"$description[{description}]", "")

                while "$color[" in code:
                    color = code.split("$color[")[1].split("]")[0]
                    embed.colour = int("0x" + color, 16)
                    code = code.replace(f"$color[{color}]", "")

                while "$addField[" in code:
                    field = code.split("$addField[")[1].split("]")[0].split(";")
                    embed.add_field(name=field[0], value=field[1])
                    code = code.replace(f"$addField[{field[0]};{field[1]}]", "")

                # while "$addTimestamp[" in code:
                #     timestamp = code.split("$addTimestamp[")[1].split("]")[0].split(";")
                #     embed.timestamp = datetime.datetime(timestamp)
                #     code = code.replace(f"$addTimestamp[{timestamp}]", "")

                while "$addImage[" in code:
                    image = code.split("$addImage[")[1].split("]")[0]
                    embed.set_image(url=image)
                    code = code.replace(f"$addImage[{image}]", "")

                while "$addThumbnail[" in code:
                    thumb = code.split("$addThumbnail[")[1].split("]")[0]
                    embed.set_thumbnail(url=thumb)
                    code = code.replace(f"$addThumbnail[{thumb}]", "")

                while "$addAuthor[" in code:
                    author = code.split("$addAuthor[")[1].split("]")[0].split(";")
                    embed.set_author(name=author[0], url=author[1])
                    code = code.replace(f"$addAuthor[{author[0]};{author[1]}]", "")

                while "$addFooter[" in code:
                    footer = code.split("$addFooter[")[1].split("]")[0].split(";")
                    embed.set_footer(text=footer[0], icon_url=footer[1])
                    code = code.replace(f"$addFooter[{footer[0]};{footer[1]}]", "")

                while "$addButton[" in code:
                    btn = code.split("$addButton[")[1].split("]")[0].split(";")
                    _ = ""
                    buttons.append(disnake_components.Button(
                        label=btn[0],
                        style=btn[1] if len(btn) >= 2 else 2,
                        custom_id=btn[2] if len(btn) >= 3 else None,
                        url=btn[3] if len(btn) >= 4 else None,
                        disabled=btn[4] if len(btn) >= 5 else False,
                        emoji=btn[5] if len(btn) >= 6 else None
                    ))
                    for num, __ in enumerate(btn):
                        _ += ";"+str(btn[num]) if num != 0 else btn[num]
                    code = code.replace(f"$addButton[{_}]", "")

                # while "$buttonListen[" in code:

                try:
                    await message.channel.send(content=code, embed=embed, components=buttons)
                except (BaseException,):
                    await message.channel.send(content=f"❌ Exception in: {name}\n{code}")


class Bot(Helper):
    def __init__(self, prefix: str = None, token: str = None, intents: bool = False):
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
        self.prefix = prefix
        self.token = token
        self.intents = intents

    def connect_database(self, dictionary: dict = None, variables: dict = None):
        if variables is None:
            variables = {}
        self.login = dictionary.get("login")
        self.password = dictionary.get("password")
        if self.login == "" or self.password == "":
            raise ParamCannotBeEmpty("Login or password empty.")
        self.variables = variables
        print("[*] DataBase connected.")

    def command(self, name: str = None, code: str = None):
        if not name or not code:
            raise ParamCannotBeEmpty("Name or code empty.")
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
        disnake_components.DisnakeComponents(self.bot)

        self.bot.add_listener(super().on_ready, "on_ready")
        self.bot.add_listener(super().on_message, "on_message")
        self.bot.add_listener(super().on_error, "on_command_error")

        self.bot.run(self.token)
