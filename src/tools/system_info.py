import platform
import time

import psutil

from .base import BaseTool, ToolResult


class SystemInfoTool(BaseTool):
    name = "system_info"
    description = "Get system information"

    async def execute(self, params: dict) -> ToolResult:
        try:
            cpu_percent = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            net = psutil.net_io_counters()
            boot = psutil.boot_time()
            uptime = time.time() - boot

            info = {
                "hostname": platform.node(),
                "os": f"{platform.system()} {platform.release()}",
                "arch": platform.machine(),
                "cpu": {
                    "cores": psutil.cpu_count(),
                    "percent": cpu_percent,
                },
                "memory": {
                    "total_gb": round(mem.total / (1024**3), 2),
                    "used_gb": round(mem.used / (1024**3), 2),
                    "percent": mem.percent,
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "percent": round(disk.percent, 1),
                },
                "network": {
                    "bytes_sent": net.bytes_sent,
                    "bytes_recv": net.bytes_recv,
                },
                "uptime_hours": round(uptime / 3600, 1),
            }

            lines = [
                f"Hostname: {info['hostname']}",
                f"OS: {info['os']} ({info['arch']})",
                f"CPU: {info['cpu']['cores']} cores, {info['cpu']['percent']}% used",
                f"Memory: {info['memory']['used_gb']} / {info['memory']['total_gb']} GB ({info['memory']['percent']}%)",
                f"Disk: {info['disk']['used_gb']} / {info['disk']['total_gb']} GB ({info['disk']['percent']}%)",
                f"Network: {info['network']['bytes_sent']} bytes sent, {info['network']['bytes_recv']} bytes received",
                f"Uptime: {info['uptime_hours']} hours",
            ]

            return ToolResult(success=True, output="\n".join(lines))
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))

    @staticmethod
    def get_metrics() -> dict:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        net = psutil.net_io_counters()

        return {
            "cpu": cpu_percent,
            "ram": {
                "used": mem.used,
                "total": mem.total,
                "percent": mem.percent,
            },
            "disk": {
                "used": disk.used,
                "total": disk.total,
                "percent": round(disk.percent, 1),
            },
            "network": {
                "rxBytes": net.bytes_recv,
                "txBytes": net.bytes_sent,
            },
            "processes": len(psutil.pids()),
            "uptime": time.time() - psutil.boot_time(),
        }
