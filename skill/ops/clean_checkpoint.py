from apscheduler.schedulers.background import BackgroundScheduler
from skill.ops.clean_expire_checkpoint import CleanExpireCheckpointSkill

# 全局单例调度器
scheduler = BackgroundScheduler(timezone="Asia/Shanghai")

# 注册会话自动清理任务
def register_clean_checkpoint_job():
    clean_skill = CleanExpireCheckpointSkill()
    # 每天凌晨2点执行，清理7天前过期会话
    scheduler.add_job(
        lambda: clean_skill.run(expire_days=7, dry_run=False),
        trigger="cron",
        hour=2,
        minute=0,
        id="auto_clean_agent_checkpoint",
        replace_existing=True,
        timezone="Asia/Shanghai"
    )

# 统一初始化所有定时任务
def init_scheduler():
    register_clean_checkpoint_job()
    scheduler.start()
    print("定时任务调度器已启动")