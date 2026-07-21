import asyncio
import sys
import os
from typing import List, Tuple

# ===================== 服务配置 =====================
# MCP模块列表 格式：(服务名, [python, -m, 包.模块名])
MCP_SERVICE_LIST: List[Tuple[str, List[str]]] = [
    ("goods_mcp", [sys.executable, "-m", "mcp_server.goods_mcp"]),
    ("order_mcp", [sys.executable, "-m", "mcp_server.order_mcp"]),
    ("ops_mcp", [sys.executable, "-m", "mcp_server.ops_mcp"]),
    ("cart_mcp", [sys.executable, "-m", "mcp_server.cart_mcp"]),
    ("user_mcp", [sys.executable, "-m", "mcp_server.user_mcp"]),
    ("promotion_mcp", [sys.executable, "-m", "mcp_server.promoption_mcp"]),
    ("aftersale_mcp", [sys.executable, "-m", "mcp_server.aftersale_mcp"]),
    ("admin_mcp", [sys.executable, "-m", "mcp_server.admin_mcp"]),
]
# FastAPI主服务
FASTAPI_SERVICE = ("fastapi_main", [sys.executable, "-m", "main"])

# 存储所有子进程
process_map = {}

async def read_service_output(name: str, stream):
    """异步读取进程输出，带服务标识打印"""
    while True:
        line = await stream.readline()
        if not line:
            break
        text = line.decode("utf-8").strip()
        print(f"【{name}】 | {text}")

async def start_single_service(name: str, cmd: List[str]):
    """启动单个服务，注入PYTHONPATH环境变量"""
    current_root = os.getcwd()
    env = os.environ.copy()
    env["PYTHONPATH"] = current_root

    print(f"\n===== 启动 {name} 命令: {' '.join(cmd)} =====")
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env
    )
    process_map[name] = proc

    # 异步监听标准输出、错误输出
    task_stdout = asyncio.create_task(read_service_output(name, proc.stdout))
    task_stderr = asyncio.create_task(read_service_output(f"{name}-ERR", proc.stderr))

    await proc.wait()
    task_stdout.cancel()
    task_stderr.cancel()
    print(f"\n===== {name} 进程退出，退出码: {proc.returncode} =====")

async def main():
    # 1. 并行启动全部MCP
    mcp_tasks = []
    for svc_name, cmd in MCP_SERVICE_LIST:
        task = asyncio.create_task(start_single_service(svc_name, cmd))
        mcp_tasks.append(task)

    # 等待10秒，给MCP充足时间绑定端口
    wait_seconds = 3
    print(f"\n===== 等待{wait_seconds}秒，等待所有MCP服务就绪 =====")
    for sec in range(wait_seconds):
        await asyncio.sleep(1)
        print(f"已等待 {sec + 1}/{wait_seconds} s")

    # 2. 延时完成后启动FastAPI主服务
    fastapi_task = asyncio.create_task(start_single_service(*FASTAPI_SERVICE))

    # 等待所有进程运行
    all_tasks = mcp_tasks + [fastapi_task]
    await asyncio.gather(*all_tasks)

if __name__ == "__main__":
    print("========== 一键启动全部服务脚本 ==========")
    print("1. 先并行启动8个MCP微服务")
    print("2. 等待10秒确保MCP端口监听完成")
    print("3. 启动FastAPI主对话服务")
    print("关闭方式：Ctrl + C 一键关闭所有进程\n")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n检测到终止信号，正在关闭全部子进程...")
        for svc_name, proc in process_map.items():
            if proc.returncode is None:
                proc.terminate()
        print("所有服务已安全退出")