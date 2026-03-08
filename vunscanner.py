import requests
import queue
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog


class HTTPSecurityScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("HTTP Security Header Scanner")
        self.root.geometry("900x650")
        self.root.resizable(True, True)

        self.log_queue = queue.Queue()
        self._setup_gui()
        self._start_log_updater()

    def _setup_gui(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=12, pady=10)

        # URL input
        ttk.Label(
            main_frame,
            text="Target URL (include http:// or https://):"
        ).grid(row=0, column=0, padx=8, pady=10, sticky="w")

        self.url_var = tk.StringVar()
        ttk.Entry(
            main_frame,
            textvariable=self.url_var,
            width=60
        ).grid(row=0, column=1, padx=8, pady=10, sticky="w")

        ttk.Button(
            main_frame,
            text="Analyze HTTP Security Headers",
            command=self.run_header_analysis
        ).grid(row=1, column=0, columnspan=2, pady=15)

        # Log area
        log_frame = ttk.LabelFrame(self.root, text=" Scan Results & Log ")
        log_frame.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        self.log_area = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            height=20,
            font=("Consolas", 10)
        )
        self.log_area.pack(fill="both", expand=True, padx=6, pady=6)
        self.log_area.config(state="disabled")

        # Bottom buttons
        bottom = ttk.Frame(self.root)
        bottom.pack(fill="x", padx=12, pady=8)

        ttk.Button(bottom, text="Clear Log", command=self.clear_log).pack(side="left", padx=6)
        ttk.Button(bottom, text="Save Log As...", command=self.save_log_file).pack(side="left", padx=6)
        ttk.Button(bottom, text="Close", command=self.root.quit).pack(side="right", padx=6)

        # Log colors
        self.log_area.tag_config("green", foreground="dark green")
        self.log_area.tag_config("blue", foreground="blue")
        self.log_area.tag_config("orange", foreground="dark orange")
        self.log_area.tag_config("red", foreground="red")
        self.log_area.tag_config("black", foreground="black")

    def log(self, message, tag="black"):
        self.log_queue.put((message + "\n", tag))

    def _start_log_updater(self):
        while not self.log_queue.empty():
            try:
                msg, tag = self.log_queue.get_nowait()
                self.log_area.config(state="normal")
                self.log_area.insert(tk.END, msg, tag)
                self.log_area.see(tk.END)
                self.log_area.config(state="disabled")
            except queue.Empty:
                break
        self.root.after(150, self._start_log_updater)

    def clear_log(self):
        self.log_area.config(state="normal")
        self.log_area.delete("1.0", tk.END)
        self.log_area.config(state="disabled")

    def save_log_file(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Scan Results"
        )
        if not filepath:
            return
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(self.log_area.get("1.0", tk.END).rstrip())
            messagebox.showinfo("Saved", f"Log saved to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    # ── HTTP Security Header Analysis ───────────────────────────────
    def run_header_analysis(self):
        url = self.url_var.get().strip()
        if not url.startswith(("http://", "https://")):
            messagebox.showwarning("Invalid URL", "Please include http:// or https://")
            return

        self.log(f"Fetching headers from: {url}", "blue")
 
        try:
            r = requests.get(url, timeout=7, allow_redirects=True)
            headers = {k.lower(): v for k, v in r.headers.items()}

            self.log(f"\nStatus Code: {r.status_code}", "blue")
            self.log("\n=== HTTP Headers ===", "black")
            for name, value in r.headers.items():
                self.log(f"{name}: {value}", "black")

            self.log("\n=== Security Header Analysis (PASS / FAIL) ===", "blue")

            security_tests = [
                ("strict-transport-security", "HSTS",
                 lambda v: v and "max-age" in v.lower(),
                 "Missing or weak HSTS"),

                ("content-security-policy", "Content Security Policy",
                 lambda v: v is not None,
                 "Missing CSP"),

                ("x-frame-options", "X-Frame-Options",
                 lambda v: v and v.upper() in ["DENY", "SAMEORIGIN"],
                 "Clickjacking risk"),

                ("x-content-type-options", "X-Content-Type-Options",
                 lambda v: v and v.lower() == "nosniff",
                 "MIME sniffing risk"),

                ("referrer-policy", "Referrer-Policy",
                 lambda v: v is not None,
                 "Referrer leakage risk"),

                ("permissions-policy", "Permissions-Policy",
                 lambda v: v is not None,
                 "Missing permissions control"),

                ("server", "Server Header Disclosure",
                 lambda v: v is None,
                 "Server information leakage"),

                ("x-powered-by", "X-Powered-By Disclosure",
                 lambda v: v is None,
                 "Technology fingerprinting"),
            ]

            passed = failed = 0

            for key, desc, condition, fail_msg in security_tests:
                value = headers.get(key)
                if condition(value):
                    self.log(f"[PASSED] {desc}", "green")
                    passed += 1
                else:
                    self.log(f"[FAILED] {desc} → {fail_msg}", "red")
                    failed += 1

            self.log(f"\nSummary: {passed} Passed | {failed} Failed", "blue")
            self.log("Header analysis completed.", "green")

        except requests.exceptions.RequestException as e:
            self.log(f"[ERROR] {str(e)}", "red")


if __name__ == "__main__":
    root = tk.Tk()
    app = HTTPSecurityScannerGUI(root)
    root.mainloop()
