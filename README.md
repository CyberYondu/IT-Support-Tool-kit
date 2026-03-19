# IT Support Toolkit

A Python-based GUI application designed for **IT support diagnostics, system monitoring, and automated issue resolution**.

This tool provides a centralized interface to analyze system performance, detect common issues, and apply basic fixes.

---

## 🚀 Features

### 🔍 System Diagnostics

* OS, hostname, IP address, and user details
* Disk usage (Total, Used, Free, %)
* Memory usage (RAM analysis)

### ⚙️ Process Management

* View top processes by memory usage
* Select processes from dropdown
* Terminate processes safely

### 🌐 Network Monitoring

* Internet connectivity check
* Basic network diagnostics

### ⚠️ Issue Detection

* High disk usage detection
* High memory usage alerts
* Network connectivity issues

### 🛠️ Auto-Fix Engine

* Flush DNS cache
* Launch disk cleanup utility
* Recommend safe corrective actions

### 📊 Reporting

* Generate structured reports
* Save reports locally (`/reports` folder)

### 🎨 User Interface

* Modern **blue-themed GUI**
* Interactive buttons with icons
* Tooltips for user guidance
* Clean single-line control panel

---

## 🖥️ Technologies Used

* Python 3
* Tkinter (GUI)
* psutil (system monitoring)
* subprocess (system commands)

---

## 📦 Installation

1. Clone the repository:

```bash
git clone https://github.com/CyberYondu/IT-Support-Tool-kit.git
cd IT-Support-Tool-kit
```

2. Install dependencies:

```bash
pip install psutil
```

3. Run the application:

```bash
python it_support_tool.py
```

---

## ⚠️ Requirements & Notes

* Run as **Administrator (Windows)** for:

  * Process termination
  * Network fixes
  * Disk cleanup

* Avoid terminating critical system processes:

  * `explorer.exe`
  * `svchost.exe`

---

## 📂 Project Structure

```text
IT-Support-Tool-kit/
│
├── it_support_tool.py
├── reports/
│   └── saved reports
└── README.md
```

---

## 🔐 Security Considerations

* No sensitive data is transmitted externally
* All operations are performed locally
* Process termination requires user action

---

## 🚧 Future Improvements

* Real-time system monitoring
* SIEM-style web dashboard
* Log analysis integration
* Service monitoring (Windows services)
* Export reports in JSON/CSV

---

## 👨‍💻 Author

Developed as part of a cybersecurity and IT support learning project.

---

## 📜 License

This project is open-source and available for educational purposes.
