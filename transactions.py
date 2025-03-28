import discord
from discord.ext import commands

# Set up bot with intents
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="/", intents=intents)

# Define the required roles
team_roles = ["Franchise Owner", "Team President", "General Manager", "Head Coach", "Assistant Coach"]
pickup_role = "Pickup Host"
streamer_role = "Streamer"
referee_role = "Referee"

# Channel mappings
channels = {
    "transactions": "transactions-channel",
    "alerts": "alerts-channel",
    "gametime": "gametime-channel",
    "streams": "streams-channel",
    "pickups": "pickups-channel",
    "free_agency": "free-agency-channel",
}

# Ensure user has the required role
def has_any_role(user, roles):
    return any(role.name in roles for role in user.roles)

# /setup command
@bot.command()
async def setup(ctx):
    if ctx.author.guild_permissions.administrator:
        embed = discord.Embed(title="Server Setup", description="Setting up the league server...", color=discord.Color.blue())
        await ctx.send(embed=embed)
    else:
        await ctx.send("You don't have permission to set up the server!")

# /sign <user>
@bot.command()
async def sign(ctx, user: discord.Member):
    if has_any_role(ctx.author, team_roles):
        team_name = "Your Team"  # Replace with actual team fetching logic
        await user.add_roles(discord.utils.get(ctx.guild.roles, name=team_name))
        embed = discord.Embed(title="Player Signed", description=f"{user.mention} has joined {team_name}!", color=discord.Color.green())
        await ctx.send(embed=embed)
    else:
        await ctx.send("You don't have permission to sign players!")

# /offer <user>
@bot.command()
async def offer(ctx, user: discord.Member):
    if has_any_role(ctx.author, team_roles):
        embed = discord.Embed(title="Contract Offer", description=f"{ctx.author.mention} has offered you a contract!", color=discord.Color.blue())
        view = discord.ui.View()
        accept_button = discord.ui.Button(label="Accept", style=discord.ButtonStyle.green)
        decline_button = discord.ui.Button(label="Decline", style=discord.ButtonStyle.red)

        async def accept_callback(interaction):
            if interaction.user == user:
                await user.add_roles(discord.utils.get(ctx.guild.roles, name="Your Team"))
                await interaction.response.send_message("Contract accepted!", ephemeral=True)

        async def decline_callback(interaction):
            if interaction.user == user:
                await interaction.response.send_message("Contract declined.", ephemeral=True)

        accept_button.callback = accept_callback
        decline_button.callback = decline_callback
        view.add_item(accept_button)
        view.add_item(decline_button)

        await user.send(embed=embed, view=view)
    else:
        await ctx.send("You don't have permission to offer contracts!")

# /demand
@bot.command()
async def demand(ctx):
    team_role = next((role for role in ctx.author.roles if role.name in team_roles), None)
    if team_role:
        await ctx.author.remove_roles(team_role)
        embed = discord.Embed(title="Player Left Team", description=f"{ctx.author.mention} has left their team!", color=discord.Color.orange())
        await ctx.send(embed=embed)
    else:
        await ctx.send("You're not on a team!")

# /release <user>
@bot.command()
async def release(ctx, user: discord.Member):
    if has_any_role(ctx.author, team_roles):
        team_role = next((role for role in user.roles if role.name in team_roles), None)
        if team_role:
            await user.remove_roles(team_role)
            embed = discord.Embed(title="Player Released", description=f"{user.mention} has been removed from their team.", color=discord.Color.red())
            await ctx.send(embed=embed)
        else:
            await ctx.send("This player is not on a team!")
    else:
        await ctx.send("You don't have permission to release players!")

# /team_list
@bot.command()
async def team_list(ctx):
    teams = ["Team 1", "Team 2", "Team 3"]  # Replace with actual team fetching logic
    embed = discord.Embed(title="List of Teams", description="\n".join(teams), color=discord.Color.blue())
    await ctx.send(embed=embed)

# /promote <user> <role>
@bot.command()
async def promote(ctx, user: discord.Member, role: str):
    if has_any_role(ctx.author, ["Franchise Owner", "Team President", "General Manager", "Head Coach"]):
        new_role = discord.utils.get(ctx.guild.roles, name=role)
        if new_role:
            await user.add_roles(new_role)
            embed = discord.Embed(title="Promotion", description=f"{user.mention} has been promoted to {role}.", color=discord.Color.green())
            await ctx.send(embed=embed)
        else:
            await ctx.send("Role not found!")
    else:
        await ctx.send("You don't have permission to promote players!")

# /demote <user>
@bot.command()
async def demote(ctx, user: discord.Member):
    if has_any_role(ctx.author, ["Franchise Owner", "Team President", "General Manager", "Head Coach"]):
        demotable_roles = ["Team President", "General Manager", "Head Coach", "Assistant Coach"]
        team_role = next((role for role in user.roles if role.name in demotable_roles), None)
        if team_role:
            await user.remove_roles(team_role)
            embed = discord.Embed(title="Demotion", description=f"{user.mention} has been demoted from {team_role.name}.", color=discord.Color.orange())
            await ctx.send(embed=embed)
        else:
            await ctx.send("This player has no team staff role!")
    else:
        await ctx.send("You don't have permission to demote players!")

# /gametime <team> <time> <timezone>
@bot.command()
async def gametime(ctx, team: str, time: str, timezone: str):
    if has_any_role(ctx.author, team_roles):
        embed = discord.Embed(title="Game Scheduled", description=f"Game scheduled vs {team} at {time} {timezone}.", color=discord.Color.blue())
        gametime_channel = discord.utils.get(ctx.guild.channels, name=channels["gametime"])
        if gametime_channel:
            await gametime_channel.send(embed=embed)
        else:
            await ctx.send(embed=embed)
    else:
        await ctx.send("You don't have permission to schedule games!")

# /pickups <link>
@bot.command()
async def pickups(ctx, link: str):
    if has_any_role(ctx.author, [pickup_role]):
        embed = discord.Embed(title="Pickup Game", description=f"Pickup game is happening! [Join here]({link})", color=discord.Color.blue())
        pickups_channel = discord.utils.get(ctx.guild.channels, name=channels["pickups"])
        if pickups_channel:
            await pickups_channel.send(embed=embed)
        else:
            await ctx.send(embed=embed)
    else:
        await ctx.send("You don't have permission to host pickup games!")

# Run the bot (Replace 'YOUR_BOT_TOKEN' with your actual token)
bot.run("YOUR_BOT_TOKEN")
