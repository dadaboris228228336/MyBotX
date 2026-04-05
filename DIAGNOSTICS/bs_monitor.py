#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BlueStacks Crash Monitor
Запускать отдельно от бота: python bs_monitor.py
Пишет лог в DIAGNOSTICS/bs_monitor.log
"""

import subprocess
import time
import sys
from datetime import datetime
from pathlib import Path

LOG_FILE = Path(__file__).parent / "bs_monitor.log"
CHECK_INTERVAL = 10  # секунд

BS_PROCESSES = ["HD-Player.exe", "BlueStacks.exe", "BstkSVC.exe"]


def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def is_bs_running() -> bool:
    """Проверяет запущен ли BlueStacks."""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq HD-Player.exe", "/NH"],
            capture_output=True, text=True
        )
        return "HD-Player.exe" in result.stdout
    except Exception:
        return False


def get_bs_pid() -> int | None:
    """Возвращает PID процесса HD-Player.exe."""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq HD-Player.exe", "/FO", "CSV", "/NH"],
            capture_output=True, text=True
        )
        for line in result.stdout.splitlines():
            parts = line.strip('"').split('","')
            if len(parts) >= 2 and "HD-Player" in parts[0]:
                return int(parts[1])
    except Exception:
        pass
    return None


def get_memory_info() -> dict:
    """Возвращает информацию о памяти системы."""
    try:
        import psutil
        vm = psutil.virtual_memory()
        return {
            "total_gb":     round(vm.total / 1024**3, 1),
            "available_gb": round(vm.available / 1024**3, 1),
            "used_pct":     vm.percent,
        }
    except ImportError:
        return {}


def get_bs_memory(pid: int) -> str:
    """Возвращает потребление памяти процесса BlueStacks."""
    try:
        import psutil
        proc = psutil.Process(pid)
        mem_mb = proc.memory_info().rss / 1024**2
        return f"{mem_mb:.0f} MB"
    except Exception:
        return "N/A"


def get_event_log_errors() -> list[str]:
    """
    Читает последние ошибки из Windows Event Log
    связанные с BlueStacks или нехваткой памяти.
    """
    errors = []
    try:
        # PowerShell запрос к Event Log
        ps_cmd = (
            "Get-EventLog -LogName Application -Newest 50 -EntryType Error,Warning "
            "| Where-Object { $_.Source -match 'BlueStacks|HD-Player|Application Error|Windows Error' "
            "  -or $_.Message -match 'BlueStacks|HD-Player|out of memory|memory' } "
            "| Select-Object -First 10 TimeGenerated,Source,EventID,Message "
            "| ForEach-Object { $_.TimeGenerated.ToString('HH:mm:ss') + ' | ' + $_.Source + ' | ' + $_.EventID + ' | ' + $_.Message.Substring(0, [Math]::Min(200, $_.Message.Length)) }"
        )
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True, text=True, timeout=15
        )
        if result.stdout.strip():
            errors = [line for line in result.stdout.strip().splitlines() if line.strip()]
    except Exception as e:
        errors = [f"Event Log недоступен: {e}"]
    return errors


def get_crash_dump_info() -> list[str]:
    """Ищет crash dump файлы BlueStacks."""
    info = []
    dump_dirs = [
        Path("C:/ProgramData/BlueStacks_nxt/Logs"),
        Path("C:/ProgramData/BlueStacks/Logs"),
        Path(Path.home() / "AppData/Local/Temp"),
    ]
    for d in dump_dirs:
        if d.exists():
            dumps = list(d.glob("*.dmp")) + list(d.glob("*.log"))
            for f in sorted(dumps, key=lambda x: x.stat().st_mtime, reverse=True)[:3]:
                mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%H:%M:%S")
                info.append(f"  {mtime} {f.name} ({f.stat().st_size // 1024} KB) -> {f}")
    return info


def analyze_crash():
    """Анализирует причину падения BlueStacks."""
    log("=" * 60)
    log("!!! BlueStacks ЗАКРЫЛСЯ — анализируем причину...")
    log("=" * 60)

    # 1. Память системы
    mem = get_memory_info()
    if mem:
        log(f"RAM: всего {mem['total_gb']} GB | доступно {mem['available_gb']} GB | занято {mem['used_pct']}%")
        if mem["available_gb"] < 1.0:
            log("ВЕРОЯТНАЯ ПРИЧИНА: Нехватка оперативной памяти (< 1 GB свободно)!")
        elif mem["available_gb"] < 2.0:
            log("ПРЕДУПРЕЖДЕНИЕ: Мало свободной памяти (< 2 GB)")

    # 2. Event Log
    log("--- Windows Event Log (последние ошибки) ---")
    errors = get_event_log_errors()
    if errors:
        for e in errors:
            log(f"  {e}")
    else:
        log("  Ошибок в Event Log не найдено")

    # 3. Crash dumps
    log("--- Crash dump файлы ---")
    dumps = get_crash_dump_info()
    if dumps:
        for d in dumps:
            log(d)
    else:
        log("  Crash dump файлы не найдены")

    log("=" * 60)


def main():
    # Очищаем лог при старте
    LOG_FILE.write_text(
        f"=== BlueStacks Monitor === Старт: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n\n",
        encoding="utf-8"
    )

    log("Мониторинг запущен. Проверка каждые 10 секунд.")
    log("Для остановки нажмите Ctrl+C")
    log("-" * 60)

    # ── Шаг 1: ждём пока BlueStacks запустится ──────────────
    log("Проверяем состояние BlueStacks...")
    while True:
        if is_bs_running():
            pid = get_bs_pid()
            mem_str = get_bs_memory(pid) if pid else "N/A"
            sys_mem = get_memory_info()
            log(f"BlueStacks ОТКРЫТ (PID: {pid}, RAM: {mem_str})")
            if sys_mem:
                log(f"Системная RAM: {sys_mem['total_gb']} GB всего | {sys_mem['available_gb']} GB свободно | {sys_mem['used_pct']}% занято")
            log("Начинаем отслеживание.")
            log("-" * 60)
            break
        else:
            log("BlueStacks не запущен — ожидаем запуска...")
            time.sleep(CHECK_INTERVAL)

    # ── Шаг 2: мониторим пока работает ──────────────────────
    iteration = 0
    while True:
        try:
            iteration += 1
            running = is_bs_running()

            if not running:
                # BlueStacks закрылся — анализируем
                analyze_crash()
                log("Мониторинг завершён — BlueStacks закрылся.")
                break

            # Всё ок — логируем состояние
            pid = get_bs_pid()
            mem_str = get_bs_memory(pid) if pid else "N/A"
            sys_mem = get_memory_info()
            if sys_mem:
                avail = sys_mem.get("available_gb", "?")
                used  = sys_mem.get("used_pct", 0)
                log(f"[{iteration}] Работает | BS RAM: {mem_str} | Свободно: {avail} GB ({100-used:.0f}%)")
            else:
                log(f"[{iteration}] Работает | BS RAM: {mem_str}")

        except KeyboardInterrupt:
            log("Мониторинг остановлен пользователем (Ctrl+C).")
            break
        except Exception as e:
            log(f"ОШИБКА в цикле: {e}")
            import traceback
            log(traceback.format_exc())

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        log(traceback.format_exc())
        input("Нажмите Enter для закрытия...")
