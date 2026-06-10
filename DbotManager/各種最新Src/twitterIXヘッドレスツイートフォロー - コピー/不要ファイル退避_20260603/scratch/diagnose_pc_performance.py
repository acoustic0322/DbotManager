import time
import os
import sys
import sqlite3
import requests
import json
import socket
from datetime import datetime

def check_system_info():
    print("=" * 60)
    print(" [SYS] SYSTEM DIAGNOSTICS & PERFORMANCE BENCHMARK ")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"OS: {sys.platform}")
    print(f"Python Version: {sys.version}")
    print(f"Current Working Dir: {os.getcwd()}")
    print("-" * 60)

def benchmark_disk_io():
    print("[DISK] 1. Disk I/O Performance Benchmark...")
    test_file = "temp_benchmark_test.txt"
    
    # Measure write speed
    start_time = time.time()
    try:
        with open(test_file, 'w', encoding='utf-8') as f:
            for i in range(5000):
                f.write(f"This is line {i} of benchmark test data. Writing dummy text.\n")
        write_duration = (time.time() - start_time) * 1000
        print(f"  - Write test (5000 lines): {write_duration:.2f} ms")
    except Exception as e:
        print(f"  - Write test FAILED: {e}")
        write_duration = float('inf')
        
    # Measure read speed
    start_time = time.time()
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        read_duration = (time.time() - start_time) * 1000
        print(f"  - Read test (5000 lines): {read_duration:.2f} ms")
    except Exception as e:
        print(f"  - Read test FAILED: {e}")
        read_duration = float('inf')
        
    # Cleanup
    if os.path.exists(test_file):
        try: os.remove(test_file)
        except: pass
        
    return write_duration, read_duration

def benchmark_sqlite():
    print("\n[SQLITE] 2. Local Database (SQLite) Benchmark...")
    db_path = "system.db"
    
    if not os.path.exists(db_path):
        print(f"  - Note: system.db not found. Creating temporary one.")
        db_path = "temp_benchmark.db"
        
    start_time = time.time()
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS temp_bench (id INTEGER PRIMARY KEY, val TEXT)")
        conn.commit()
        db_conn_duration = (time.time() - start_time) * 1000
        print(f"  - Connection and Table creation: {db_conn_duration:.2f} ms")
        
        # Test batch inserts
        start_time = time.time()
        for i in range(100):
            cursor.execute("INSERT INTO temp_bench (val) VALUES (?)", (f"Val_{i}",))
        conn.commit()
        insert_duration = (time.time() - start_time) * 1000
        print(f"  - 100 Single-commit Writes: {insert_duration:.2f} ms (Avg: {insert_duration/100:.2f} ms per write)")
        
        # Cleanup table
        cursor.execute("DROP TABLE IF EXISTS temp_bench")
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"  - SQLite test FAILED: {e}")
        insert_duration = float('inf')
        
    if db_path == "temp_benchmark.db" and os.path.exists(db_path):
        try: os.remove(db_path)
        except: pass
        
    return insert_duration

def test_supabase_connection():
    print("\n[CLOUD] 3. Cloud DB (Supabase/Postgres) Network Benchmark...")
    config_path = "db_config.json"
    
    if not os.path.exists(config_path):
        # Check parent folder just in case
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "db_config.json")
        
    if not os.path.exists(config_path):
        print("  - db_config.json not found. Skipping cloud DB check.")
        return None
        
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
            
        postgres_cfg = cfg.get("postgres", {})
        uri = postgres_cfg.get("uri")
        
        if not uri:
            print("  - Cloud DB URI not found in config. Skipping.")
            return None
            
        try:
            host_part = uri.split("@")[1].split("/")[0]
            if ":" in host_part:
                host, port = host_part.split(":")
                port = int(port)
            else:
                host = host_part
                port = 5432
        except:
            print("  - Could not parse URI for socket ping.")
            return None
            
        print(f"  - Pinging Cloud DB Host ({host}:{port})...")
        start_time = time.time()
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5.0)
            s.connect((host, port))
            network_latency = (time.time() - start_time) * 1000
            s.close()
            print(f"  - Socket Connection Latency: {network_latency:.2f} ms")
            return network_latency
        except Exception as e:
            print(f"  - Cloud DB Connection FAILED (Timeout/Unreachable): {e}")
            return float('inf')
    except Exception as e:
        print(f"  - Error reading config: {e}")
        return None

def test_ixbrowser_api():
    print("\n[IXBROWSER] 4. IXBrowser Local API (Port 53200) Benchmark...")
    url = "http://127.0.0.1:53200/v2/profile-list"
    
    start_time = time.time()
    try:
        resp = requests.post(url, json={"limit": 1, "page": 1}, timeout=5.0)
        api_latency = (time.time() - start_time) * 1000
        if resp.status_code == 200:
            print(f"  - IXBrowser API Latency: {api_latency:.2f} ms (Status: 200 OK)")
        else:
            print(f"  - IXBrowser API returned error code {resp.status_code}: {resp.text}")
    except requests.exceptions.RequestException as e:
        print(f"  - IXBrowser API is UNREACHABLE (Is IXBrowser running?): {e}")
        api_latency = float('inf')
        
    return api_latency

def analyze_results(write_ms, db_ms, cloud_ms, api_ms):
    print("\n" + "=" * 60)
    print(" [ANALYSIS] DIAGNOSIS & BOTTLENECK ANALYSIS ")
    print("=" * 60)
    
    warnings = []
    
    # 1. Disk/Drive analysis
    if write_ms > 200:
        warnings.append((
            "[CRITICAL] HIGH DISK/DRIVE LATENCY",
            f"Disk write took {write_ms:.1f}ms (Normal local SSD is <30ms).\n"
            "  Your script is running on a Virtual Network Drive (Google Drive Stream mode).\n"
            "  Python loading and UI manipulation will be severely degraded."
        ))
    elif write_ms > 80:
        warnings.append((
            "[WARNING] MODERATE DISK LATENCY",
            f"Disk write took {write_ms:.1f}ms. Slower than typical local SSDs.\n"
            "  Google Drive synchronization or other processes are locking the directory."
        ))
    else:
        print("[-] Drive Speed: Normal (Fast Local Drive).")
        
    # 2. SQLite Database analysis
    if db_ms > 1000:
        warnings.append((
            "[CRITICAL] SEVERE DATABASE LAG (SQLite)",
            f"SQLite 100-writes took {db_ms:.1f}ms (Avg {db_ms/100:.1f}ms per write).\n"
            "  Real-time file-locking by Google Drive Desktop is freezing your DB operations."
        ))
    else:
        print("[-] Local Database: Normal SQLite speed.")
        
    # 3. Cloud Connection analysis
    if cloud_ms is not None:
        if cloud_ms == float('inf'):
            warnings.append((
                "[CRITICAL] CLOUD DATABASE BLOCKED",
                "Your PC cannot connect to the Cloud Supabase Database.\n"
                "  This forces the bot to fall back to the slow Google Drive SQLite, causing freeze/lag.\n"
                "  Check if your Main PC's firewall, proxy, or antivirus is blocking connection to port 5432 / 6543."
            ))
        elif cloud_ms > 150:
            warnings.append((
                "[WARNING] HIGH NETWORK LATENCY",
                f"Cloud DB response is slow ({cloud_ms:.1f}ms). Network routing or proxy delay detected."
            ))
        else:
            print("[-] Cloud Connection: Healthy (Fast routing to Cloud DB).")
            
    # 4. IXBrowser API analysis
    if api_ms == float('inf'):
        warnings.append((
            "[CRITICAL] IXBROWSER API DISCONNECTED",
            "IXBrowser API at port 53200 did not respond.\n"
            "  Make sure IXBrowser is fully launched and API server is enabled in its settings."
        ))
    else:
        print("[-] IXBrowser Local API: Connected and responding.")
        
    # Render Warnings/Actions
    if warnings:
        print("\n!!! DETECTED BOTTLENECK(S) !!!")
        for title, desc in warnings:
            print(f"\n{title}")
            print(f"  {desc}")
    else:
        print("\nAll systems normal. No local PC bottleneck detected.")
        
    print("\n" + "=" * 60)

if __name__ == "__main__":
    check_system_info()
    write_dur, read_dur = benchmark_disk_io()
    db_dur = benchmark_sqlite()
    cloud_dur = test_supabase_connection()
    api_dur = test_ixbrowser_api()
    analyze_results(write_dur, db_dur, cloud_dur, api_dur)
