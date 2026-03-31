

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Port Scanner 實用工具
====================

一個功能完整的端口掃描器，使用 Python 標準函式庫實作。

功能：
  - TCP Connect 掃描（完整三次握手）
  - 多執行緒並行掃描，大幅提升速度
  - 常見服務名稱自動辨識
  - Banner 擷取（嘗試讀取服務回應）
  - 支援單一端口、範圍、或自訂列表
  - 掃描結果摘要報告

使用方式：
  python3 port_scanner.py <目標主機> [選項]

範例：
  python3 port_scanner.py 127.0.0.1
  python3 port_scanner.py 192.168.1.1 -p 22,80,443
  python3 port_scanner.py example.com -p 1-1024 -t 200 --timeout 0.5
  python3 port_scanner.py 10.0.0.1 --top-ports

注意：僅限用於授權的安全測試與教育用途。
"""

import socket
import argparse
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# ============================================================
# 常見端口與服務對照表
# 這些是網路服務最常使用的端口號碼
# ============================================================
WELL_KNOWN_PORTS = {
    20: "FTP-Data",
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    67: "DHCP-Server",
    68: "DHCP-Client",
    80: "HTTP",
    110: "POP3",
    111: "RPCbind",
    119: "NNTP",
    123: "NTP",
    135: "MS-RPC",
    137: "NetBIOS-NS",
    138: "NetBIOS-DGM",
    139: "NetBIOS-SSN",
    143: "IMAP",
    161: "SNMP",
    162: "SNMP-Trap",
    389: "LDAP",
    443: "HTTPS",
    445: "SMB",
    465: "SMTPS",
    514: "Syslog",
    587: "SMTP-Submission",
    631: "IPP/CUPS",
    636: "LDAPS",
    993: "IMAPS",
    995: "POP3S",
    1080: "SOCKS",
    1433: "MSSQL",
    1434: "MSSQL-Browser",
    1521: "Oracle-DB",
    1883: "MQTT",
    2049: "NFS",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    5672: "AMQP",
    5900: "VNC",
    6379: "Redis",
    6443: "Kubernetes-API",
    8080: "HTTP-Proxy",
    8443: "HTTPS-Alt",
    8883: "MQTT-TLS",
    9090: "Prometheus",
    9200: "Elasticsearch",
    11211: "Memcached",
    27017: "MongoDB",
}

# 最常被掃描的端口（用於 --top-ports 模式）
TOP_PORTS = [
    21, 22, 23, 25, 53, 80, 110, 111, 135, 139,
    143, 443, 445, 993, 995, 1433, 1521, 3306, 3389,
    5432, 5900, 6379, 8080, 8443, 27017,
]


def resolve_host(target: str) -> str:
    """
    解析主機名稱為 IP 位址。
    如果輸入已經是 IP，則直接返回。
    """
    try:
        ip = socket.gethostbyname(target)
        return ip
    except socket.gaierror:
        raise ValueError(f"無法解析主機名稱: {target}")


def scan_port(target: str, port: int, timeout: float) -> dict:
    """
    掃描單一端口（TCP Connect 掃描）。

    原理：嘗試與目標建立完整的 TCP 連線（三次握手）。
    - 連線成功 → 端口開啟
    - 連線被拒（ConnectionRefusedError） → 端口關閉
    - 連線逾時 → 端口被過濾（防火牆丟棄封包）

    回傳包含掃描結果的字典。
    """
    result = {
        "port": port,
        "state": "closed",  # 預設為關閉
        "service": WELL_KNOWN_PORTS.get(port, "unknown"),
        "banner": "",
    }

    # 建立 TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)

    try:
        # 嘗試連線（TCP 三次握手）
        err = sock.connect_ex((target, port))

        if err == 0:
            # 連線成功，端口開啟
            result["state"] = "open"

            # 嘗試擷取 Banner（服務回應的識別字串）
            try:
                # 某些服務會在連線後主動發送 banner（如 SSH、FTP）
                sock.settimeout(1.0)
                banner = sock.recv(1024).decode("utf-8", errors="replace").strip()
                if banner:
                    result["banner"] = banner[:80]  # 限制長度
            except (socket.timeout, OSError):
                # 不是所有服務都會主動發送 banner，這是正常的
                pass

    except socket.timeout:
        # 連線逾時：通常表示有防火牆過濾
        result["state"] = "filtered"
    except ConnectionRefusedError:
        # 連線被拒：端口確實關閉
        result["state"] = "closed"
    except OSError as e:
        # 其他網路錯誤（如：網路不可達）
        result["state"] = "error"
        result["banner"] = str(e)
    finally:
        sock.close()

    return result


def parse_ports(port_str: str) -> list[int]:
    """
    解析端口參數字串，支援多種格式：
      - 單一端口: "80"
      - 範圍: "1-1024"
      - 逗號分隔: "22,80,443"
      - 混合: "22,80,8000-8010,443"
    """
    ports = set()

    for part in port_str.split(","):
        part = part.strip()
        if "-" in part:
            # 範圍格式：起始-結束
            try:
                start, end = part.split("-", 1)
                start, end = int(start), int(end)
                if start > end:
                    raise ValueError(f"端口範圍無效: {part}（起始值大於結束值）")
                if start < 1 or end > 65535:
                    raise ValueError(f"端口必須在 1-65535 之間，收到: {part}")
                ports.update(range(start, end + 1))
            except ValueError as e:
                if "invalid literal" in str(e):
                    raise ValueError(f"無法解析端口: {part}")
                raise
        else:
            # 單一端口
            try:
                p = int(part)
                if p < 1 or p > 65535:
                    raise ValueError(f"端口必須在 1-65535 之間，收到: {p}")
                ports.add(p)
            except ValueError:
                raise ValueError(f"無法解析端口: {part}")

    return sorted(ports)


def run_scan(target: str, ports: list[int], threads: int = 100,
             timeout: float = 1.0, verbose: bool = False) -> list[dict]:
    """
    執行完整的端口掃描。

    使用 ThreadPoolExecutor 實現多執行緒並行掃描：
    - 每個端口由一個獨立的執行緒負責
    - 執行緒池限制同時運行的數量，避免資源耗盡
    - 使用 as_completed 即時回報結果

    參數：
      target: 目標 IP 位址
      ports: 要掃描的端口列表
      threads: 最大並行執行緒數
      timeout: 每個連線的逾時秒數
      verbose: 是否即時顯示所有結果
    """
    results = []
    open_count = 0
    total = len(ports)

    print(f"\n{'='*60}")
    print(f"  Port Scanner — 端口掃描工具")
    print(f"{'='*60}")
    print(f"  目標主機: {target}")
    print(f"  掃描端口: {total} 個")
    print(f"  執行緒數: {threads}")
    print(f"  逾時設定: {timeout} 秒")
    print(f"  開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    start_time = time.time()

    # 使用執行緒池進行並行掃描
    with ThreadPoolExecutor(max_workers=threads) as executor:
        # 提交所有掃描任務
        future_to_port = {
            executor.submit(scan_port, target, port, timeout): port
            for port in ports
        }

        # 即時處理完成的結果
        completed = 0
        for future in as_completed(future_to_port):
            completed += 1
            result = future.result()
            results.append(result)

            # 顯示進度與結果
            if result["state"] == "open":
                open_count += 1
                banner_info = f"  ({result['banner'][:50]})" if result["banner"] else ""
                print(f"  [開啟] {result['port']:>5}/tcp  {result['service']:<20}{banner_info}")
            elif verbose and result["state"] == "filtered":
                print(f"  [過濾] {result['port']:>5}/tcp  {result['service']}")

            # 每掃描 10% 顯示一次進度
            if total > 50 and completed % max(1, total // 10) == 0:
                pct = completed * 100 // total
                sys.stdout.write(f"\r  進度: {pct}% ({completed}/{total})  ")
                sys.stdout.flush()

    elapsed = time.time() - start_time

    # 清除進度行
    if total > 50:
        sys.stdout.write("\r" + " " * 50 + "\r")

    # 依端口號排序結果
    results.sort(key=lambda r: r["port"])

    # 輸出摘要報告
    print(f"\n{'─'*60}")
    print(f"  掃描完成！耗時 {elapsed:.2f} 秒")
    print(f"  掃描速率: {total / elapsed:.0f} 端口/秒")
    print(f"{'─'*60}")

    # 統計各狀態數量
    states = {}
    for r in results:
        states[r["state"]] = states.get(r["state"], 0) + 1

    state_labels = {
        "open": "開啟",
        "closed": "關閉",
        "filtered": "被過濾",
        "error": "錯誤",
    }
    print(f"  結果摘要:")
    for state, count in sorted(states.items()):
        label = state_labels.get(state, state)
        print(f"    {label}: {count}")

    # 列出所有開啟的端口
    open_ports = [r for r in results if r["state"] == "open"]
    if open_ports:
        print(f"\n  {'端口':<10} {'服務':<20} {'Banner'}")
        print(f"  {'─'*10} {'─'*20} {'─'*30}")
        for r in open_ports:
            banner = r["banner"][:30] if r["banner"] else "—"
            print(f"  {r['port']:<10} {r['service']:<20} {banner}")
    else:
        print("\n  未發現開啟的端口。")

    print(f"{'─'*60}\n")

    return results


def build_parser() -> argparse.ArgumentParser:
    """建立命令列參數解析器。"""
    parser = argparse.ArgumentParser(
        description="Port Scanner — TCP 端口掃描工具（僅限授權測試用途）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例：
  %(prog)s 127.0.0.1                     掃描常用端口
  %(prog)s 192.168.1.1 -p 22,80,443      掃描指定端口
  %(prog)s 10.0.0.1 -p 1-1024            掃描 1~1024 端口
  %(prog)s example.com --top-ports        掃描 Top 25 常見端口
  %(prog)s 10.0.0.1 -p 1-65535 -t 500    全端口掃描（高並行）

注意：請僅對你有授權的主機進行掃描！
        """,
    )

    parser.add_argument(
        "target",
        help="目標主機（IP 位址或主機名稱）",
    )
    parser.add_argument(
        "-p", "--ports",
        default=None,
        help="端口範圍（例: 22,80,443 或 1-1024 或 22,80,8000-8100）",
    )
    parser.add_argument(
        "--top-ports",
        action="store_true",
        help="掃描最常見的 25 個端口",
    )
    parser.add_argument(
        "-t", "--threads",
        type=int,
        default=100,
        help="最大並行執行緒數（預設: 100）",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=1.0,
        help="連線逾時秒數（預設: 1.0）",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="顯示所有端口狀態（包含被過濾的端口）",
    )

    return parser


def demo_localhost():
    """
    示範模式：掃描本機常見端口。
    在沒有提供命令列參數時自動執行。
    """
    print("╔══════════════════════════════════════════════════════╗")
    print("║   Port Scanner 示範模式                              ║")
    print("║   未提供參數，將掃描本機 (127.0.0.1) 常見端口         ║")
    print("║                                                      ║")
    print("║   完整用法: python3 port_scanner.py -h               ║")
    print("╚══════════════════════════════════════════════════════╝")

    # 示範掃描本機的常見端口
    demo_ports = [22, 53, 80, 443, 631, 3000, 3306, 5432, 6379, 8080, 8443, 9090]
    results = run_scan("127.0.0.1", demo_ports, threads=20, timeout=0.5)

    # 說明如何使用
    print("提示：你可以這樣使用此工具：")
    print("  python3 port_scanner.py 192.168.1.1 -p 1-1024")
    print("  python3 port_scanner.py example.com --top-ports")
    print("  python3 port_scanner.py 10.0.0.1 -p 22,80,443 --timeout 2")

    return results


if __name__ == "__main__":
    # 如果沒有提供任何參數，執行示範模式
    if len(sys.argv) == 1:
        demo_localhost()
        sys.exit(0)

    parser = build_parser()
    args = parser.parse_args()

    # 解析目標主機
    try:
        target_ip = resolve_host(args.target)
        if target_ip != args.target:
            print(f"  主機 {args.target} 解析為 {target_ip}")
    except ValueError as e:
        print(f"錯誤: {e}", file=sys.stderr)
        sys.exit(1)

    # 決定要掃描的端口
    try:
        if args.top_ports:
            # 使用預定義的常見端口列表
            ports = TOP_PORTS
        elif args.ports:
            # 解析使用者指定的端口
            ports = parse_ports(args.ports)
        else:
            # 預設掃描常見端口
            ports = TOP_PORTS
    except ValueError as e:
        print(f"錯誤: {e}", file=sys.stderr)
        sys.exit(1)

    # 安全提醒
    if target_ip not in ("127.0.0.1", "::1", "localhost"):
        print(f"\n  ⚠ 即將掃描外部主機 {target_ip}")
        print(f"  請確認你有權限對此主機進行掃描。")

    # 執行掃描
    try:
        results = run_scan(
            target=target_ip,
            ports=ports,
            threads=args.threads,
            timeout=args.timeout,
            verbose=args.verbose,
        )
    except KeyboardInterrupt:
        print("\n\n  掃描已被使用者中斷 (Ctrl+C)")
        sys.exit(130)
    except PermissionError:
        print("錯誤: 權限不足。某些端口掃描可能需要較高權限。", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"掃描發生錯誤: {e}", file=sys.stderr)
        sys.exit(1)
