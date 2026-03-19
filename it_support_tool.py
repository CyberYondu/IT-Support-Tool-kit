import tkinter as tk
from tkinter import scrolledtext, messagebox
import platform, socket, getpass, psutil, subprocess, time, os
from datetime import datetime


# ===============================
# CORE FUNCTIONS
# ===============================
def get_system_info():
    return {
        "OS": platform.system() + " " + platform.release(),
        "Hostname": socket.gethostname(),
        "IP Address": socket.gethostbyname(socket.gethostname()),
        "User": getpass.getuser(),
    }


def get_disk_usage():
    try:
        disk = psutil.disk_usage('C:\\')
    except:
        disk = psutil.disk_usage('/')

    return {"Usage %": disk.percent}


def get_memory_usage():
    return {"Usage %": psutil.virtual_memory().percent}


def get_network_status():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        internet = "OK"
    except:
        internet = "FAILED"

    return {"Internet": internet}


def detect_issues(disk, memory, network):
    issues = []

    if disk["Usage %"] > 90:
        issues.append(("CRITICAL", "Disk usage above 90%"))

    if memory["Usage %"] > 85:
        issues.append(("WARNING", "High memory usage"))

    if network["Internet"] == "FAILED":
        issues.append(("HIGH", "No internet"))

    return issues


def generate_recommendations(issues):
    rec = []

    for lvl, issue in issues:
        if "memory" in issue.lower():
            rec.append("Close unused apps")
        elif "disk" in issue.lower():
            rec.append("Free disk space")
        elif "internet" in issue.lower():
            rec.append("Check router/ISP")

    return list(set(rec)) if rec else ["System healthy"]


def save_report(text):
    if not os.path.exists("reports"):
        os.makedirs("reports")

    filename = f"reports/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

    return filename


def kill_process_by_pid():
    pid = pid_entry.get().strip()

    if not pid.isdigit():
        messagebox.showerror("Error", "Enter a valid numeric PID")
        return

    pid = int(pid)

    try:
        proc = psutil.Process(pid)
        name = proc.name()

        proc.terminate()  # graceful kill
        proc.wait(timeout=3)

        messagebox.showinfo("Success", f"Process '{name}' (PID {pid}) terminated")

    except psutil.NoSuchProcess:
        messagebox.showerror("Error", f"No process with PID {pid}")

    except psutil.AccessDenied:
        messagebox.showerror("Error", "Access denied (Run as Administrator)")

    except psutil.TimeoutExpired:
        proc.kill()
        messagebox.showwarning("Forced Kill", f"Process PID {pid} force killed")

    except Exception as e:
        messagebox.showerror("Error", str(e))


# ===============================
# PROGRESS BAR
# ===============================
def draw_progress(percent, message=""):
    canvas.delete("all")

    # Background ring
    canvas.create_oval(10, 10, 190, 190, outline="#1e293b", width=10)

    # Progress arc
    extent = (percent / 100) * 360
    canvas.create_arc(
        10, 10, 190, 190,
        start=90,
        extent=-extent,
        style="arc",
        outline="#22c55e",
        width=10
    )

    # Percentage
    canvas.create_text(
        100, 90,
        text=f"{percent}%",
        fill="white",
        font=("Segoe UI", 16, "bold")
    )

    # Message
    canvas.create_text(
        100, 120,
        text=message,
        fill="#94a3b8",
        font=("Segoe UI", 9)
    )

    root.update_idletasks()


def get_progress_message(p):
    if p < 20:
        return "Initializing..."
    elif p < 40:
        return "Collecting system info..."
    elif p < 60:
        return "Analyzing resources..."
    elif p < 80:
        return "Checking network..."
    elif p < 95:
        return "Finalizing..."
    else:
        return "Almost there..."


# ===============================
# MAIN SCAN
# ===============================
def run_scan():
    output.delete(1.0, tk.END)

    start = time.time()

    steps = [
        ("system", 15),
        ("disk", 30),
        ("memory", 45),
        ("processes", 60),
        ("network", 80),
        ("final", 100)
    ]

    results = {}

    for step, percent in steps:

        for p in range(percent - 15 if percent > 15 else 0, percent + 1, 2):
            draw_progress(p, get_progress_message(p))
            time.sleep(0.02)

        if step == "system":
            results["system"] = get_system_info()

        elif step == "disk":
            disk_full = psutil.disk_usage('C:\\' if os.name == 'nt' else '/')
            results["disk"] = {
                "Total (GB)": round(disk_full.total / (1024**3), 2),
                "Used (GB)": round(disk_full.used / (1024**3), 2),
                "Free (GB)": round(disk_full.free / (1024**3), 2),
                "Usage %": disk_full.percent
            }

        elif step == "memory":
            mem = psutil.virtual_memory()
            results["memory"] = {
                "Total (GB)": round(mem.total / (1024**3), 2),
                "Used (GB)": round(mem.used / (1024**3), 2),
                "Available (GB)": round(mem.available / (1024**3), 2),
                "Usage %": mem.percent
            }

        elif step == "processes":
            procs = []
            for proc in psutil.process_iter(['pid','name','memory_percent']):
                try:
                    procs.append(proc.info)
                except:
                    continue
            procs = sorted(procs, key=lambda x: x['memory_percent'], reverse=True)
            results["processes"] = procs[:5]

        elif step == "network":
            results["network"] = {
                "Internet": get_network_status()["Internet"],
                "DNS": "OK" if socket.gethostbyname("google.com") else "FAILED",
                "Ping": "Reachable"
            }

    # Issues with impact
    issues = []

    if results["disk"]["Usage %"] > 90:
        issues.append(("CRITICAL", "Disk usage above 90%", "System may crash"))

    if results["memory"]["Usage %"] > 85:
        issues.append(("WARNING", "High memory usage", "System slowdown"))

    if results["network"]["Internet"] == "FAILED":
        issues.append(("HIGH", "No internet", "No external access"))

    recs = generate_recommendations([(lvl, msg) for lvl, msg, _ in issues])

    # ===============================
    # FULL REPORT (RESTORED)
    # ===============================
    report = "\n==*==*==*= IT SUPPORT DIAGNOSTICS REPORT =*==*==*==\n\n"

    report += "System Info:\n"
    for k, v in results["system"].items():
        report += f"{k}: {v}\n"

    report += "\nDisk Usage:\n"
    for k, v in results["disk"].items():
        report += f"{k}: {v}\n"

    report += "\nMemory Usage:\n"
    for k, v in results["memory"].items():
        report += f"{k}: {v}\n"

    report += "\nTop Processes:\n"
    for p in results["processes"]:
        report += f"{p['name']} (PID: {p.get('pid','N/A')}) -> {round(p['memory_percent'],2)}%\n"

    report += "\nNetwork Status:\n"
    for k, v in results["network"].items():
        report += f"{k}: {v}\n"

    output.insert(tk.END, report)

    # ===============================
    # COLORED ISSUES
    # ===============================
    output.insert(tk.END, "\nIssues:\n", "header")

    for lvl, msg, impact in issues:
        tag = "red" if lvl == "CRITICAL" else "orange" if lvl == "HIGH" else "yellow"
        output.insert(tk.END, f"[{lvl}] {msg} -> {impact}\n", tag)

    if not issues:
        output.insert(tk.END, "[OK] No issues detected\n", "green")

    # ===============================
    # RECOMMENDATIONS
    # ===============================
    output.insert(tk.END, "\nRecommendations:\n", "header")
    for r in recs:
        output.insert(tk.END, f"- {r}\n", "green")

    output.insert(tk.END, f"\nScan Time: {round(time.time()-start,2)}s\n")

    draw_progress(100, "Completed")


def save_current_report():
    content = output.get(1.0, tk.END)
    if not content.strip():
        messagebox.showwarning("Warning", "Run scan first")
        return

    path = save_report(content)
    messagebox.showinfo("Saved", f"Saved to:\n{path}")


# ===============================
# UI
# ===============================
root = tk.Tk()
root.title("IT Support Toolkit")
root.geometry("850x650")
root.configure(bg="#0f172a")

# Header
header = tk.Label(root, text="IT SUPPORT DIAGNOSTICS",
                  font=("Segoe UI", 18, "bold"),
                  bg="#0f172a", fg="#38bdf8")
header.pack(pady=10)

# Progress Circle
canvas = tk.Canvas(root, width=200, height=200,
                   bg="#0f172a", highlightthickness=0)
canvas.pack(pady=5)

# Buttons
btn_frame = tk.Frame(root, bg="#0f172a")
btn_frame.pack(pady=5)

scan_btn = tk.Button(btn_frame, text="Run Scan",
                     bg="#22c55e", fg="black",
                     font=("Segoe UI", 10, "bold"),
                     padx=15, pady=5,
                     command=run_scan)
scan_btn.pack(side=tk.LEFT, padx=10)

save_btn = tk.Button(btn_frame, text="Save Report",
                     bg="#3b82f6", fg="white",
                     font=("Segoe UI", 10, "bold"),
                     padx=15, pady=5,
                     command=save_current_report)
save_btn.pack(side=tk.LEFT, padx=10)

# ===============================
# PROCESS CONTROL SECTION
# ===============================
proc_frame = tk.Frame(root, bg="#0f172a")
proc_frame.pack(pady=10)

pid_label = tk.Label(proc_frame, text="Enter PID:",
                     bg="#0f172a", fg="white",
                     font=("Segoe UI", 10))
pid_label.pack(side=tk.LEFT, padx=5)

pid_entry = tk.Entry(proc_frame, width=10, font=("Segoe UI", 10))
pid_entry.pack(side=tk.LEFT, padx=5)

kill_btn = tk.Button(proc_frame,
                     text="Kill Process",
                     bg="#ef4444",
                     fg="white",
                     font=("Segoe UI", 10, "bold"),
                     padx=10,
                     command=kill_process_by_pid)
kill_btn.pack(side=tk.LEFT, padx=10)

# Output Box
output = scrolledtext.ScrolledText(
    root,
    wrap=tk.WORD,
    font=("Consolas", 10),
    bg="#020617",
    fg="#e5e7eb",
    insertbackground="white"
)
output.pack(expand=True, fill="both", padx=15, pady=10)

# Colors
output.tag_config("red", foreground="#ef4444")
output.tag_config("orange", foreground="#f97316")
output.tag_config("yellow", foreground="#eab308")
output.tag_config("green", foreground="#22c55e")
output.tag_config("header", foreground="#38bdf8", font=("Consolas", 11, "bold"))

root.mainloop()

