import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import platform, socket, getpass, psutil, subprocess, time, os
from datetime import datetime

# ===============================
# TOOLTIP
# ===============================
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 20
        y += self.widget.winfo_rooty() + 20

        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.geometry(f"+{x}+{y}")

        label = tk.Label(self.tip, text=self.text,
                         bg="#1e293b", fg="white",
                         font=("Segoe UI", 9), relief="solid", bd=1)
        label.pack()

    def hide(self, event=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None



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
    disk = psutil.disk_usage("C:\\" if os.name == "nt" else "/")
    return {
        "Total (GB)": round(disk.total / (1024**3), 2),
        "Used (GB)": round(disk.used / (1024**3), 2),
        "Free (GB)": round(disk.free / (1024**3), 2),
        "Usage %": disk.percent,
    }


def get_memory_usage():
    mem = psutil.virtual_memory()
    return {
        "Total (GB)": round(mem.total / (1024**3), 2),
        "Used (GB)": round(mem.used / (1024**3), 2),
        "Available (GB)": round(mem.available / (1024**3), 2),
        "Usage %": mem.percent,
    }


def get_top_processes(limit=5):
    procs = []
    for p in psutil.process_iter(["pid", "name", "memory_percent"]):
        try:
            procs.append(p.info)
        except:
            pass
    return sorted(procs, key=lambda x: x["memory_percent"], reverse=True)[:limit]


def get_network_status():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        internet = "OK"
    except:
        internet = "FAILED"

    return {"Internet": internet}


def save_current_report():
    content = output.get(1.0, tk.END)

    if not content.strip():
        messagebox.showwarning("Warning", "No report to save")
        return

    if not os.path.exists("reports"):
        os.makedirs("reports")

    file_path = f"reports/report_{int(time.time())}.txt"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    messagebox.showinfo("Saved", f"Report saved:\n{file_path}")


# ===============================
# DETECTION
# ===============================
def detect_issues(disk, memory, network):
    issues = []

    if disk["Usage %"] > 90:
        issues.append(("CRITICAL", "Disk usage above 90%", "Run cleanup"))

    if memory["Usage %"] > 85:
        issues.append(("WARNING", "High memory usage", "Close heavy apps"))

    if network["Internet"] == "FAILED":
        issues.append(("HIGH", "No internet", "Reset network"))

    return issues


# ===============================
# AUTO FIX
# ===============================
def auto_fix(issues):
    results = []

    for lvl, issue, action in issues:
        try:
            if "internet" in issue.lower():
                subprocess.run("ipconfig /flushdns", shell=True)
                results.append("DNS flushed")

            elif "disk" in issue.lower():
                subprocess.run("cleanmgr", shell=True)
                results.append("Disk cleanup opened")

            elif "memory" in issue.lower():
                results.append("Close apps manually (safe mode)")

        except:
            results.append(f"Failed: {issue}")

    return results


# ===============================
# PROCESS KILL
# ===============================
def kill_process():
    pid = pid_entry.get().strip()

    if not pid.isdigit():
        messagebox.showerror("Error", "Invalid PID")
        return

    try:
        p = psutil.Process(int(pid))
        name = p.name()
        p.terminate()
        messagebox.showinfo("Success", f"{name} terminated")

    except Exception as e:
        messagebox.showerror("Error", str(e))


# ===============================
# PROGRESS
# ===============================
def draw_progress(p, msg=""):
    canvas.delete("all")

    canvas.create_oval(10, 10, 190, 190, outline="#1e3a8a", width=10)

    canvas.create_arc(
        10,
        10,
        190,
        190,
        start=90,
        extent=-(p / 100) * 360,
        style="arc",
        outline="#3b82f6",
        width=10,
    )

    canvas.create_text(
        100, 90, text=f"{p}%", fill="white", font=("Segoe UI", 16, "bold")
    )

    canvas.create_text(100, 120, text=msg, fill="#93c5fd", font=("Segoe UI", 9))

    root.update_idletasks()


def msg(p):
    if p < 30:
        return "Initializing..."
    elif p < 60:
        return "Analyzing..."
    elif p < 90:
        return "Checking network..."
    else:
        return "Almost there..."


# ===============================
# SCAN THREAD
# ===============================
def run_scan():
    threading.Thread(target=scan).start()


def scan():
    output.delete(1.0, tk.END)
    start = time.time()

    for i in range(0, 101, 2):
        draw_progress(i, msg(i))
        time.sleep(0.01)

    system = get_system_info()
    disk = get_disk_usage()
    memory = get_memory_usage()
    procs = get_top_processes()
    network = get_network_status()

    issues = detect_issues(disk, memory, network)

    # DISPLAY
    output.insert(tk.END, "===== IT SUPPORT REPORT =====\n\n")

    for k, v in system.items():
        output.insert(tk.END, f"{k}: {v}\n")

    output.insert(tk.END, "\nDisk:\n")
    for k, v in disk.items():
        output.insert(tk.END, f"{k}: {v}\n")

    output.insert(tk.END, "\nMemory:\n")
    for k, v in memory.items():
        output.insert(tk.END, f"{k}: {v}\n")

    output.insert(tk.END, "\nTop Processes:\n")
    for p in procs:
        output.insert(
            tk.END, f"{p['name']} (PID {p['pid']}) -> {round(p['memory_percent'],2)}%\n"
        )

    output.insert(tk.END, "\nNetwork:\n")
    for k, v in network.items():
        output.insert(tk.END, f"{k}: {v}\n")

    output.insert(tk.END, "\nIssues:\n", "header")
    for lvl, msgg, impact in issues:
        tag = "red" if lvl == "CRITICAL" else "orange" if lvl == "HIGH" else "yellow"
        output.insert(tk.END, f"[{lvl}] {msgg} -> {impact}\n", tag)

    if not issues:
        output.insert(tk.END, "[OK] System healthy\n", "green")

    output.insert(tk.END, f"\nScan Time: {round(time.time()-start,2)}s\n")

    draw_progress(100, "Completed")


# ===============================
# FIX BUTTON
# ===============================
def run_fix():
    content = output.get(1.0, tk.END)
    if "Issues" not in content:
        messagebox.showwarning("Run scan first", "")
        return

    disk = get_disk_usage()
    memory = get_memory_usage()
    network = get_network_status()

    issues = detect_issues(disk, memory, network)
    fixes = auto_fix(issues)

    output.insert(tk.END, "\nFix Results:\n", "header")
    for f in fixes:
        output.insert(tk.END, f"- {f}\n", "green")


# ===============================
# UI
# ===============================
root = tk.Tk()
root.title("IT Support Toolkit")
root.geometry("900x700")
root.configure(bg="#0f172a")

tk.Label(
    root,
    text="IT SUPPORT TOOL",
    bg="#0f172a",
    fg="#3b82f6",
    font=("Segoe UI", 18, "bold"),
).pack(pady=10)

canvas = tk.Canvas(root, width=200, height=200, bg="#0f172a", highlightthickness=0)
canvas.pack()

# BUTTON ROW
top_frame = tk.Frame(root, bg="#0f172a")
top_frame.pack(pady=10)

btn_scan = tk.Button(top_frame, text="▶ Scan", bg="#3b82f6", fg="white", command=run_scan)
btn_scan.pack(side=tk.LEFT, padx=5)
ToolTip(btn_scan, "Run system diagnostics")

btn_fix = tk.Button(top_frame, text="🛠 Fix", bg="#22c55e", fg="black", command=auto_fix)
btn_fix.pack(side=tk.LEFT, padx=5)
ToolTip(btn_fix, "Attempt automatic fixes")

btn_save = tk.Button(top_frame, text="💾 Save", bg="#f59e0b", fg="black", command=save_current_report)
btn_save.pack(side=tk.LEFT, padx=5)
ToolTip(btn_save, "Save report to file")

# Spacer (optional for separation)
tk.Label(top_frame, text="   ", bg="#0f172a").pack(side=tk.LEFT)

# PID Entry (SECOND LAST)
pid_entry = tk.Entry(top_frame, width=10, font=("Segoe UI", 10))
pid_entry.pack(side=tk.LEFT, padx=5)

# Kill Button (LAST)
tk.Button(
    top_frame, text="❌ Kill", bg="#ef4444", fg="white", padx=10, command=kill_process
).pack(side=tk.LEFT, padx=5)

output = scrolledtext.ScrolledText(
    root, bg="#020617", fg="white", font=("Consolas", 10)
)
output.pack(expand=True, fill="both", padx=10, pady=10)

output.tag_config("red", foreground="#ef4444")
output.tag_config("orange", foreground="#f97316")
output.tag_config("yellow", foreground="#eab308")
output.tag_config("green", foreground="#22c55e")
output.tag_config("header", foreground="#3b82f6")

root.mainloop()
