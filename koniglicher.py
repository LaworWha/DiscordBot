import discord
from discord.ext import commands
from discord import app_commands
import os

bot = commands.Bot(command_prefix='kh!', intents=discord.Intents.all())

# Bot başladığında çalışacak kod
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'{bot.user} olarak giriş yapıldı!')
    print(f'Bot ID: {bot.user.id}')
    bot.add_view(TicketButton())
    bot.add_view(CloseTicketButton())
    await bot.change_presence(
        activity=discord.Game(name="Königlicher Holding | kh!bilgi", type=3)
    )

@bot.command(name='announce')
@commands.has_permissions(administrator=True)
async def duyuru(ctx, kanal: discord.TextChannel, mesaj: str, *, tag: str):
    """Duyuru gönderir
    Kullanım: !duyuru #kanal tag mesaj içeriği
    """
    
    # Duyuru embed'i
    embed = discord.Embed(
        title="📢 Duyuru",
        description=mesaj,
        color=0xff0000
    )
    embed.set_footer(text=f"Duyuran: Königlicher Holding Duyuru Sistemi | {tag}")
    embed.timestamp = discord.utils.utcnow()
    embed.set_author(name="Königlicher Holding", icon_url="https://umutunver.com.tr/koniglicher.png")
    
    # @everyone ve @here mention
    content = "@everyone @here"
    
    # Duyuruyu gönder
    await kanal.send(content=content, embed=embed)
    
    # Onay mesajı
    await ctx.send(f"✅ Duyuru {kanal.mention} kanalına gönderildi!", delete_after=5)
    await ctx.message.delete()


@duyuru.error
async def duyuru_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Yetkiniz yok!", delete_after=5)
    elif isinstance(error, commands.ChannelNotFound):
        await ctx.send("❌ Kanal bulunamadı!", delete_after=5)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Kullanım: `!duyuru #kanal tag mesaj`", delete_after=5)


@duyuru.error
async def duyuru_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Yetkiniz yok!", delete_after=5)
    elif isinstance(error, commands.ChannelNotFound):
        await ctx.send("❌ Kanal bulunamadı!", delete_after=5)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Kullanım: `!duyuru #kanal tag mesaj`", delete_after=5)

@duyuru.error
async def duyuru_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Bu komutu kullanmak için yönetici olmalısınız!", delete_after=5)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Kullanım: `!duyuru #kanal tag mesaj`", delete_after=5)

# Yeni üye geldiğinde mesaj gönderme
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name='genel')
    if channel:
        await channel.send(f"Königlicher'a hoşgeldin, {member.mention}")
# Bot hakkında bilgi komutu
@bot.command(name='bilgi')
async def info(ctx):
    embed = discord.Embed(
        title="Bot Bilgileri",
        description="version alpha 1 - Made for Königlicher Holding, by DreamGuyWhale",
        color=0x00ff00
    )
    embed.add_field(name="Sunucu Sayısı", value=len(bot.guilds), inline=True)
    embed.add_field(name="Kullanıcı Sayısı", value=len(bot.users), inline=True)
    await ctx.send(embed=embed)

# Ping komutu
@bot.command(name='ping')
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f'Gecikme: {latency}ms')

# Moderasyon komutu - üye kickleme
@bot.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick_member(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'{member.mention} sunucudan atıldı. Sebep: {reason}')

@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban_member(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'{member.mention} sunucudan yasaklandı. Sebep: {reason}')

class buttonView(discord.ui.View):
    @discord.ui.button(label="Test", style=discord.ButtonStyle.green)
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("buton mesaj")
    
TICKET_CATEGORY_ID = 1430297870854258782
SUPPORT_ROLES = [1427328870096441495, 1427330055750553711]

ticketEmbed = discord.Embed(title="Destek Talebi", description="Destek talebi oluşturmak için butona tıklayın.", color=0x3498db)
ticketEmbed.set_thumbnail(url="https://umutunver.com.tr/koniglicher.png")
ticketEmbed.add_field(name="",value="Yetkililerimiz en kısa sürede sizinle ilgilenecektir.")
ticketEmbed.set_footer(text="Königlicher Holding Destek Sistemi")
ticketEmbed.set_author(name="Königlicher Holding", icon_url="https://umutunver.com.tr/koniglicher.png")
# Hata yakalama
@kick_member.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Bu komutu kullanmak için yetkiniz yok!")

class TicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Destek Talebi Oluştur", style=discord.ButtonStyle.green, emoji="🎫", custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        
        # Zaten açık ticket var mı
        existing_ticket = discord.utils.get(guild.text_channels, name=f"ticket-{interaction.user.name.lower()}")
        if existing_ticket:
            await interaction.response.send_message(f"❌ Zaten açık bir talebiniz var: {existing_ticket.mention}", ephemeral=True)
            return
        
        # Kategori kontrolü
        category = guild.get_channel(TICKET_CATEGORY_ID)
        if not category:
            await interaction.response.send_message("❌ Destek kategorisi bulunamadı!", ephemeral=True)
            return
        
        # İzinleri ayarla
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }
        
        # Yetkili rollere izin ver
        for role_id in SUPPORT_ROLES:
            role = guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        
        # Ticket kanalı oluştur
        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )
        
        # Embed oluştur
        embed = discord.Embed(
            title="🎫 Destek Talebi",
            description=f"{interaction.user.mention} talebiniz oluşturuldu!\n\nYetkili ekibimiz en kısa sürede yardımcı olacaktır.",
            color=0x00ff00
        )
        embed.add_field(name="📝 Bilgi", value="Sorununuzu detaylı açıklayın.\nKapatmak için butona tıklayın.", inline=False)
        embed.set_footer(text="Königlicher Holding Destek Sistemi")
        
        # Mention yetkilileri
        role_mentions = " ".join([f"<@&{role_id}>" for role_id in SUPPORT_ROLES])
        
        await ticket_channel.send(
            content=f"{interaction.user.mention} {role_mentions}",
            embed=embed,
            view=CloseTicketButton()
        )
        
        await interaction.response.send_message(f"✅ Talebiniz oluşturuldu: {ticket_channel.mention}", ephemeral=True)
class CloseTicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Talebi Kapat", style=discord.ButtonStyle.red, emoji="🔒", custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Destek talebi kapatılıyor...", ephemeral=True)
        await interaction.channel.delete()



@bot.command(name='destek-panel')
@commands.has_permissions(administrator=True)
async def setup_ticket(ctx):
    embed = discord.Embed(
        title="Destek Talebi",
        description="Destek talebi oluşturmak için butona tıklayın..",
        color=0x3498db
    )
    embed.set_thumbnail(url="https://umutunver.com.tr/koniglicher.png")
    embed.add_field(name="", value="Yetkiliilerimiz en kısa sürede sizinle ilgilenecektir.", inline=False)
    embed.set_footer(text="Königlicher Holding Destek Sistemi")
    embed.set_author(name="Königlicher Holding", icon_url="https://umutunver.com.tr/koniglicher.png")
    
    await ctx.send(embed=embed, view=TicketButton())
    await ctx.message.delete()


bot.run('MTQyODI1ODE4Njk0NjY3NDc1OA.GZo1sv.zXUAMIyhwGhi83woCdH05vYs0iTmhgXFpNKmWU')