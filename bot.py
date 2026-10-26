import asyncio
from datetime import datetime, time
import discord
from discord import app_commands
from discord.ext import commands, tasks

# Khởi tạo Intents
intents = discord.Intents.default()
intents.message_content = True

class THPTQGBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        # Mốc thời gian chuẩn thi THPTQG 2027: 11/06/2027, 07:00:00
        self.exam_date = datetime(2027, 6, 11, 7, 0, 0)
        # ID kênh chat được lấy từ đường dẫn bạn cung cấp
        self.target_channel_id = 1564300021157863526  

    async def setup_hook(self):
        # Đồng bộ lệnh Slash với Discord
        await self.tree.sync()
        # Chạy vòng lặp cập nhật trạng thái và thông báo hàng ngày
        self.update_status.start()
        self.daily_announcement.start()
        print(f"Logged in as {self.user} (ID: {self.user.id})")

    @tasks.loop(hours=1) # Cập nhật trạng thái bot mỗi 1 giờ
    async def update_status(self):
        now = datetime.now()
        remaining = self.exam_date - now
        days = remaining.days

        if days > 0:
            activity_text = f"Còn {days} ngày thi THPTQG 2027"
        else:
            activity_text = "Đã đến ngày thi! Chiến thôi anh em!"

        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, 
                name=activity_text
            )
        )

    # Vòng lặp tự động gửi thông báo mỗi ngày vào lúc 12:00 trưa
    @tasks.loop(time=time(hour=12, minute=0, second=0))
    async def daily_announcement(self):
        channel = self.get_channel(self.target_channel_id)
        if channel is None:
            return

        now = datetime.now()
        remaining = self.exam_date - now
        days = remaining.days

        if days <= 0:
            await channel.send("🚨 **Đã đến ngày thi THPTQG 2027!** Chúc các sĩ tử bình tĩnh, tự tin chiến thắng!")
            return

        hours, remainder = divmod(remaining.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        embed = discord.Embed(
            title="🕛 THÔNG BÁO ĐẾM NGƯỢC TRƯA HÀNG NGÀY",
            description="Nghỉ ngơi và nạp lại năng lượng nhé các sĩ tử!",
            color=discord.Color.orange()
        )
        embed.add_field(
            name="⏳ Thời gian đến kỳ thi THPTQG 2027",
            value=f"• **{days}** ngày\n• **{hours}** giờ\n• **{minutes}** phút",
            inline=False
        )
        embed.set_footer(text="Mỗi ngày trôi qua là một bước tiến gần hơn đến vạch đích!")

        await channel.send(embed=embed)

    @update_status.before_loop
    async def before_loop_handler(self):
        await self.wait_until_ready()

    @daily_announcement.before_loop
    async def before_daily_loop(self):
        await self.wait_until_ready()

bot = THPTQGBot()

@bot.event
async def on_ready():
    print("Bot đã sẵn sàng và hoạt động ổn định.")

# Lệnh Slash: /demnguoc
@bot.tree.command(name="demnguoc", description="Xem thời gian chính xác còn lại đến kỳ thi THPTQG 2027")
async def demnguoc(interaction: discord.Interaction):
    now = datetime.now()
    remaining = bot.exam_date - now

    if remaining.total_seconds() <= 0:
        await interaction.response.send_message("🚨 **Đã chính thức bước vào kỳ thi THPTQG 2027!** Giữ vững tinh thần, làm bài hết mình!")
        return

    days = remaining.days
    hours, remainder = divmod(remaining.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    embed = discord.Embed(
        title="⏳ ĐẾM NGƯỢC KỲ THI THPTQG 2027",
        description="Mục tiêu: **Đại học top đầu - Không khoan nhượng!**",
        color=discord.Color.red()
    )

    embed.add_field(
        name="📅 Thời gian còn lại",
        value=f"• **{days}** ngày\n• **{hours}** giờ\n• **{minutes}** phút\n• **{seconds}** giây",
        inline=False
    )

    embed.add_field(
        name="🎯 Mốc thời gian mục tiêu",
        value="11 tháng 6, 2027",
        inline=False
    )

    embed.set_footer(text="Mỗi phút trôi qua là một bước tiến gần hơn đến vạch đích. Cố gắng nào!")

    await interaction.response.send_message(embed=embed)

# Chạy bot với Token của bạn
bot.run("MTU2NDMwNDQyMzE1MTIxNDYzNQ.GV491g.pl6e5q32SRFjWbsCiURwMC25Qs7YUkummlKRMQ")