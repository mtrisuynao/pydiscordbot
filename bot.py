import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from discord.ext.commands.cooldowns import BucketType
from discord import Permissions
from itertools import cycle
from colorama import Fore, Style
import asyncio
import json
import os
import random
from itertools import cycle

client = commands.Bot(command_prefix = ".")
client.remove_command("help")

SPAM_CHANNEL =  ["nuke" , "What" , "nope" , "huh?","NUKE","NUKE!!","hề"]
SPAM_MESSAGE = ["@everyone sv hề vcl"]

@client.command(aliases=['c'])
@commands.is_owner()
@commands.cooldown(1,20,commands.BucketType.user)
async def cut(ctx,member : discord.Member):
    await open_account(ctx.author)
    await open_account(member)
    bal = await update_bank(member)
    if bal[0]<100:
        await ctx.send('Hết tiền rồi không còn đâu mà cướp :(')
        return

    earning = (bal[0])

    await update_bank(ctx.author,earning)
    await update_bank(member,-1*earning)
    await ctx.send(f'{ctx.author.mention} Bạn đã cho {member} cút và nhận được {earning} coins')


@client.event
async def on_ready():
	print("bot is ready")
	await client.change_presence(activity=discord.Game(name="prefix:."))

@tasks.loop(seconds=5)
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))

mainshop = [{"name":"gậy Unmute","price":100000,"description":"unmute!!!"},
            {"name":"gậy Unban","price":999999,"description":"unban hehe"},
            {"name":"role độc quyền","price":100000,"description":"role cho riêng bạn"},
            {"name":"donate cho server","price":10000,"description":"donate hoi:>"}]

@client.command()
async def say(ctx, *, text):
    message = ctx.message
    await message.delete()

    await ctx.send(f"{text}")

@client.command()
@commands.is_owner()
async def Stop(ctx):
    await ctx.bot.logout()
    print (Fore.GREEN + f"{client.user.name} has logged out successfully." + Fore.RESET)

@client.command(aliases=['bal'])
async def balance(ctx):
    await open_account(ctx.author)
    user = ctx.author

    users = await get_bank_data()

    wallet_amt = users[str(user.id)]["wallet"]
    bank_amt = users[str(user.id)]["bank"]

    em = discord.Embed(title=f'{ctx.author.name} Balance',color = discord.Color.red())
    em.add_field(name="Ví bạn còn:", value=wallet_amt)
    em.add_field(name='Ngân hàng bạn còn:',value=bank_amt)
    await ctx.send(embed = em)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        msg = '**Lệnh vẫn đang hồi**, hãy thử lại sau {:.2f}s'.format(error.retry_after)
        await ctx.send(msg)

@client.command()
@commands.cooldown(1,5,commands.BucketType.user)
async def beg(ctx):
    await open_account(ctx.author)
    user = ctx.author

    users = await get_bank_data()

    earnings = random.randrange(51)

    await ctx.send(f'{ctx.author.mention} Sau 1 ngày làm việc bạn nhận được {earnings} coins!!')

    users[str(user.id)]["wallet"] += earnings

    with open("mainbank.json",'w') as f:
        json.dump(users,f)


@client.command(aliases=['wd'])
@commands.cooldown(1,5,commands.BucketType.user)
async def withdraw(ctx,amount = None):
    await open_account(ctx.author)
    if amount == None:
        await ctx.send("Hãy điền số coins")
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)

    if amount > bal[1]:
        await ctx.send('Bạn không có đủ tiền')
        return
    if amount < 0:
        await ctx.send('Hãy điền số tiền lớn hơn')
        return

    await update_bank(ctx.author,amount)
    await update_bank(ctx.author,-1*amount,'bank')
    await ctx.send(f'{ctx.author.mention} Bạn đã rút khỏi ngân hàng {amount} coins')


@client.command(aliases=['dp'])
@commands.cooldown(1,5,commands.BucketType.user)
async def deposit(ctx,amount = None):
    await open_account(ctx.author)
    if amount == None:
        await ctx.send("Hãy điền số coins")
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)

    if amount > bal[0]:
        await ctx.send('Bạn không có đủ tiền')
        return
    if amount < 0:
        await ctx.send('Hãy điền số tiền lớn hơn')
        return

    await update_bank(ctx.author,-1*amount)
    await update_bank(ctx.author,amount,'bank')
    await ctx.send(f'{ctx.author.mention} Bạn đã chuyển vào ngân hàng {amount} coins')


@client.command(aliases=['sm'])
@commands.cooldown(1,10,commands.BucketType.user)
async def give(ctx,member : discord.Member,amount = None):
    await open_account(ctx.author)
    await open_account(member)
    if amount == None:
        await ctx.send("Hãy điền số coins")
        return

    bal = await update_bank(ctx.author)
    if amount == 'all':
        amount = bal[0]

    amount = int(amount)

    if amount > bal[0]:
        await ctx.send('Bạn không có đủ tiền')
        return
    if amount < 0:
        await ctx.send('Hãy điền số tiền lớn hơn')
        return

    await update_bank(ctx.author,-1*amount,'bank')
    await update_bank(member,amount,'bank')
    await ctx.send(f'{ctx.author.mention} Bạn đã cho {member} {amount} coins')


@client.command(aliases=['rb'])
@commands.cooldown(1,20,commands.BucketType.user)
async def rob(ctx,member : discord.Member):
    await open_account(ctx.author)
    await open_account(member)
    bal = await update_bank(member)


    if bal[0]<100:
        await ctx.send('Hết tiền rồi không còn đâu mà cướp :(')
        return

    earning = random.randrange(0,bal[0])

    await update_bank(ctx.author,earning)
    await update_bank(member,-1*earning)
    await ctx.send(f'{ctx.author.mention} Bạn đã cướp coins của {member} và nhận được {earning} coins')


@client.command()
@commands.cooldown(1,10,commands.BucketType.user)
async def slots(ctx,amount = None):
    await open_account(ctx.author)
    if amount == None:
        await ctx.send("Hãy điền số coins")
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)

    if amount > bal[0]:
        await ctx.send('Bạn không có đủ số tiền')
        return
    if amount < 0:
        await ctx.send('Hãy điền số tiền lớn hơn')
        return
    final = []
    for i in range(3):
        a = random.choice([':red_circle:',':red_square:',':heart:'])

        final.append(a)

    await ctx.send(str(final))

    if final[0] == final[1] or final[1] == final[2] or final[0] == final[2]:
        await update_bank(ctx.author,2*amount)
        await ctx.send(f'Bạn đã thắng {amount} coins rồi:) {ctx.author.mention}')
    else:
        await update_bank(ctx.author,-1*amount)
        await ctx.send(f'Bạn đã thua {amount} coins rồi:( {ctx.author.mention}')


@client.command()
@commands.cooldown(1,5,commands.BucketType.user)
async def shop(ctx):
    em = discord.Embed(title = "Shop")

    for item in mainshop:
        name = item["name"]
        price = item["price"]
        desc = item["description"]
        em.add_field(name = name, value = f"${price} | {desc}")

    await ctx.send(embed = em)



@client.command()
@commands.cooldown(1,10,commands.BucketType.user)
async def buy(ctx,item,amount = 1):
    await open_account(ctx.author)

    res = await buy_this(ctx.author,item,amount)

    if not res[0]:
        if res[1]==1:
            await ctx.send("Bạn không mua được")
            return
        if res[1]==2:
            await ctx.send(f"Bạn không có đủ tiền để mua")
            return


    await ctx.send(f"Bạn đã mua {item} với giá {amount}")


@client.command()
@commands.cooldown(1,5,commands.BucketType.user)
async def bag(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()

    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []


    em = discord.Embed(title = "Bag")
    for item in bag:
        name = item["item"]
        amount = item["amount"]

        em.add_field(name = name, value = amount)    

    await ctx.send(embed = em)


async def buy_this(user,item_name,amount):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            price = item["price"]
            break

    if name_ == None:
        return [False,1]

    cost = price*amount

    users = await get_bank_data()

    bal = await update_bank(user)

    if bal[0]<cost:
        return [False,2]


    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt + amount
                users[str(user.id)]["bag"][index]["amount"] = new_amt
                t = 1
                break
            index+=1 
        if t == None:
            obj = {"item":item_name , "amount" : amount}
            users[str(user.id)]["bag"].append(obj)
    except:
        obj = {"item":item_name , "amount" : amount}
        users[str(user.id)]["bag"] = [obj]        

    with open("mainbank.json","w") as f:
        json.dump(users,f)

    await update_bank(user,cost*-1,"wallet")

    return [True,"Worked"]
    

@client.command()
@commands.cooldown(1,10,commands.BucketType.user)
async def sell(ctx,item,amount = 1):
    await open_account(ctx.author)

    res = await sell_this(ctx.author,item,amount)

    if not res[0]:
        if res[1]==1:
            await ctx.send("That Object isn't there!")
            return
        if res[1]==2:
            await ctx.send(f"Bạn không có {amount} {item} trong túi.")
            return
        if res[1]==3:
            await ctx.send(f"Bạn không có {item} trong túi.")
            return

    await ctx.send(f"Bạn đã bán {item} với giá {amount}.")

async def sell_this(user,item_name,amount,price = None):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            if price==None:
                price = 0.7* item["price"]
            break

    if name_ == None:
        return [False,1]

    cost = price*amount

    users = await get_bank_data()

    bal = await update_bank(user)


    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt - amount
                if new_amt < 0:
                    return [False,2]
                users[str(user.id)]["bag"][index]["amount"] = new_amt
                t = 1
                break
            index+=1 
        if t == None:
            return [False,3]
    except:
        return [False,3]    

    with open("mainbank.json","w") as f:
        json.dump(users,f)

    await update_bank(user,cost,"wallet")

    return [True,"Worked"]


@client.command(aliases = ["lb"]) #error*
async def leaderboard(ctx,x = 1):
    users = await get_bank_data()
    leader_board = {}
    total = []
    for user in users:
        name = int(user)
        total_amount = users[user]["wallet"] + users[user]["bank"]
        leader_board[total_amount] = name
        total.append(total_amount)

    total = sorted(total,reverse=True)    

    em = discord.Embed(title = f"Top {x} Richest People" , description = "This is decided on the basis of raw money in the bank and wallet",color = discord.Color(0xfa43ee))
    index = 1
    for amt in total:
        id_ = leader_board[amt]
        member = client.get_user(id_)
        name = member.name
        em.add_field(name = f"{index}. {name}" , value = f"{amt}",  inline = False)
        if index == x:
            break
        else:
            index += 1

    await ctx.send(embed = em)


async def open_account(user):

    users = await get_bank_data()

    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["wallet"] = 0
        users[str(user.id)]["bank"] = 0

    with open('mainbank.json','w') as f:
        json.dump(users,f)

    return True


async def get_bank_data():
    with open('mainbank.json','r') as f:
        users = json.load(f)

    return users


async def update_bank(user,change=0,mode = 'wallet'):
    users = await get_bank_data()

    users[str(user.id)][mode] += change

    with open('mainbank.json','w') as f:
        json.dump(users,f)
    bal = users[str(user.id)]['wallet'],users[str(user.id)]['bank']
    return bal

@client.command()
@commands.cooldown(1,5,commands.BucketType.user)
async def ping(ctx):
	await ctx.send(f'ping hiện tại là: {round(client.latency * 1000)}ms')

@client.command(pass_context=True)
async def server(ctx):
    embed=discord.Embed(title="thông tin về server",color=0x9208ea)
    embed.add_field(name="tên server", value=(ctx.message.guild.name), inline=False)
    embed.add_field(name="role trong server", value=(ctx.message.guild.roles), inline=False)
    embed.add_field(name="member trong server", value=len(ctx.message.guild.members), inline=False)
    embed.add_field(name="các kênh trong server", value=(ctx.message.guild.channels), inline=False)
    embed.add_field(name="lệnh được dùng bởi", value=str(ctx.message.author.mention), inline=False)
    embed.set_footer(text="[Ss]╏ Incognito coder#8122")


@client.command()
@commands.cooldown(1,10,commands.BucketType.user)
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount = 99):
	await ctx.channel.purge(limit=amount+1)
	await ctx.send('đã xóa tin nhắn')

@client.command()
@commands.cooldown(1,60,commands.BucketType.user)
@commands.has_permissions(kick_members=True)
async def kick(ctx, member : discord.Member, *, reason=None):
	await member.kick(reason=reason)
	await ctx.send(f"{member} đã bị kick!")

@client.command()
@commands.cooldown(1,60,commands.BucketType.user)
@commands.has_permissions(ban_members=True)
async def ban(ctx, member : discord.Member, *, reason=None):
	await member.ban(reason=reason)
	await ctx.send(f"{member} đã bị ban!")

@client.command()
@commands.cooldown(1,60,commands.BucketType.user)
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member):
    bannedUsers = await ctx.guild.bans()
    name, discriminator = member.split("#")

    for ban in bannedUsers:
        user = ban.user

        if(user.name, user.discriminator) == (name, discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f"{user.mention} đã được unban.")
            return

@client.command(description="xem info của user")
@commands.cooldown(1,10,commands.BucketType.user)
async def info(ctx):
    user = ctx.author

    embed=discord.Embed(title="USER INFO", description=f"Đây là info của {user}", colour=user.colour)
    embed.set_thumbnail(url=user.avatar_url)
    embed.add_field(name="NAME", value=user.name, inline=True)
    embed.add_field(name="NICKNAME", value=user.nick, inline=True)
    embed.add_field(name="ID", value=user.id, inline=True)
    embed.add_field(name="TOP ROLE", value=user.top_role.name, inline=True)
    await ctx.send(embed=embed)

@client.command(description="Mutes người bạn muốn.")
@commands.cooldown(1,10,commands.BucketType.user)
@commands.has_permissions(manage_messages=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name="Muted")

    if not mutedRole:
        mutedRole = await guild.create_role(name="Muted")

        for channel in guild.channels:
            await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=True, read_messages=False)

    await member.add_roles(mutedRole, reason=reason)
    await ctx.send(f"Muted {member.mention} với lí do {reason}")
    await member.send(f"bạn đã bị mute {guild.name} với lí do là: {reason}")

@client.command(description="unmute cho người bạn đã mute.")
@commands.cooldown(1,10,commands.BucketType.user)
@commands.has_permissions(manage_messages=True)
async def unmute(ctx, member: discord.Member):
    mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")

    await member.remove_roles(mutedRole)
    await ctx.send(f"Unmuted {member.mention}")
    await member.send(f"bạn đã được unmute {ctx.guild.name}")

@client.command(description="lệnh help thôi mà.")
@commands.cooldown(1,5,commands.BucketType.user)
async def help(ctx, commandSent=None):
    if commandSent != None:

        for command in bot.commands:
            if commandSent.lower() == command.name.lower():

                paramString = ""

                for param in command.clean_params:
                    paramString += param + ", "

                paramString = paramString[:-2]

                if len(command.clean_params) == 0:
                    paramString = "None"
                    
                embed=discord.Embed(title=f"HELP - {command.name}", description=command.description)
                embed.add_field(name="parameters", value=paramString)
                await ctx.message.delete()
                await ctx.author.send(embed=embed)
        
    else:
        embed=discord.Embed(title="help nè:3",color=0x9208ea)
        embed.add_field(name="ping", value="xem ping của bot", inline=True)
        embed.add_field(name="info", value="xem info của chính mình nha:3", inline=True)
        embed.add_field(name="ban", value="ban những người phạm luật", inline=True)
        embed.add_field(name="kick", value="kick những người phạm luật nha", inline=True)
        embed.add_field(name="unban", value="unban cho những người bị ban", inline=True)
        embed.add_field(name="unmute", value="unmute cho những bạn bị mute", inline=True)
        embed.add_field(name="clear", value="clear tin nhắn", inline=True)
        embed.add_field(name="mute", value="mute những người phạm luật", inline=True)
        embed.add_field(name="balance", value="kiểm tra ví và ngân hàng", inline=True)
        embed.add_field(name="beg", value="làm việc để kiếm coins", inline=True)
        embed.add_field(name="withdraw", value="cho tiền vào ngân hàng", inline=True)
        embed.add_field(name="deposit", value="rút tiền khỏi ngân hàng", inline=True)
        embed.add_field(name="give", value="cho người khác tiền", inline=True)
        embed.add_field(name="rob", value="hành nghề trộm cắp:)", inline=True)
        embed.add_field(name="slots", value="cờ bạc(slots)", inline=True)
        embed.add_field(name="shop", value="xem các đồ trong shop", inline=True)
        embed.add_field(name="buy", value="mua đồ", inline=True)
        embed.add_field(name="bag", value="túi đồ", inline=True)
        embed.add_field(name="leaderboard", value="xem leaderboard", inline=True)


        await ctx.message.delete()
        await ctx.author.send(embed=embed)

client.run("ODcyMzEwNDM0NTgwMDIxMjk5.GddfDA.WIIQDoLH1MF9ZC7JItESjh8jWtutFSXnCM2RAo")