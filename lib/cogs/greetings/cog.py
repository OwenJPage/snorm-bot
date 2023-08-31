from typing import Self
from discord import Cog, ApplicationContext, Member
from discord.ext.commands import user_command


class Greetings(Cog):
    @user_command(name="Wave")
    async def wave(self: Self, ctx: ApplicationContext, member: Member) -> None:
        await ctx.send(f"{ctx.author.mention} waves hello to {member.mention}!")

        await ctx.defer(invisible=True)
