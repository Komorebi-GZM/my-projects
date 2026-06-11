"""APScheduler定时任务调度器配置。

本地开发阶段使用APScheduler在Flask进程内运行定时任务。
生产环境使用CloudBase定时触发器。

Source: https://apscheduler.readthedocs.io/en/stable/userguide.html
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED

from src.db.factory import get_db_adapter
from src.tasks.timeout_checker import check_pending_timeout, check_delivering_timeout


# 任务配置
TASK_CONFIG = {
    "pending_timeout_checker": {
        "func": check_pending_timeout,
        "trigger": IntervalTrigger(minutes=30),
        "kwargs": {"timeout_days": 7, "batch_size": 50},
    },
    "delivering_timeout_checker": {
        "func": check_delivering_timeout,
        "trigger": IntervalTrigger(minutes=30),
        "kwargs": {"timeout_days": 7, "batch_size": 50},
    },
}


def _job_listener(event):
    """任务执行监听器。"""
    if event.exception:
        print(f"[Scheduler] 任务执行失败: {event.job_id}, 异常: {event.exception}")
    else:
        print(f"[Scheduler] 任务执行成功: {event.job_id}")


def init_scheduler(app):
    """初始化定时任务调度器。

    在Flask应用启动时调用，注册所有定时任务。

    Args:
        app: Flask应用实例

    Returns:
        BackgroundScheduler: 调度器实例
    """
    scheduler = BackgroundScheduler()

    # 添加任务监听器
    scheduler.add_listener(_job_listener, EVENT_JOB_ERROR | EVENT_JOB_EXECUTED)

    # 注册定时任务
    for job_id, config in TASK_CONFIG.items():
        scheduler.add_job(
            func=_wrap_task(config["func"]),
            trigger=config["trigger"],
            id=job_id,
            replace_existing=True,
            kwargs=config.get("kwargs", {}),
        )
        print(f"[Scheduler] 已注册任务: {job_id}")

    # 启动调度器
    scheduler.start()
    app.scheduler = scheduler

    print(f"[Scheduler] 调度器已启动，共{len(TASK_CONFIG)}个任务")
    return scheduler


def _wrap_task(task_func):
    """包装任务函数，注入数据库适配器。

    Args:
        task_func: 原始任务函数

    Returns:
        包装后的任务函数
    """
    def wrapper(*args, **kwargs):
        db = get_db_adapter()
        try:
            return task_func(db, *args, **kwargs)
        finally:
            db.close()

    return wrapper


def shutdown_scheduler(app):
    """关闭定时任务调度器。

    Args:
        app: Flask应用实例
    """
    if hasattr(app, "scheduler"):
        app.scheduler.shutdown()
        print("[Scheduler] 调度器已关闭")


def get_scheduler_status(app) -> dict:
    """获取调度器状态。

    Args:
        app: Flask应用实例

    Returns:
        调度器状态信息
    """
    if not hasattr(app, "scheduler"):
        return {"running": False, "jobs": []}

    scheduler = app.scheduler
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "next_run_time": str(job.next_run_time) if job.next_run_time else None,
            "trigger": str(job.trigger),
        })

    return {
        "running": scheduler.running,
        "jobs": jobs,
    }
