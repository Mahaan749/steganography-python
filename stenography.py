import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import os
import traceback

class SteganographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Steganography - Text in Image")
        self.root.geometry("720x720")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f2f5")

        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 11), padding=8)
        style.configure("TLabel", background="#f0f2f5", font=("Helvetica", 11))
        style.configure("Header.TLabel", font=("Helvetica", 16, "bold"), background="#f0f2f5")

        # Main header
        ttk.Label(root, text="LSB Steganography - Hide & Extract Text", style="Header.TLabel").pack(pady=(20, 10))

        # Hide Section
        frame_hide = ttk.LabelFrame(root, text="  Hide Text in Image  ", padding=15)
        frame_hide.pack(fill="x", padx=25, pady=10)

        ttk.Label(frame_hide, text="Cover Image:").grid(row=0, column=0, sticky="w", pady=6, padx=(0,10))
        self.cover_path_var = tk.StringVar()
        ttk.Entry(frame_hide, textvariable=self.cover_path_var, width=50, state="readonly").grid(row=0, column=1, pady=6)
        ttk.Button(frame_hide, text="Browse", command=self.browse_cover, width=10).grid(row=0, column=2, padx=10, pady=6)

        ttk.Label(frame_hide, text="Message to hide:").grid(row=1, column=0, sticky="nw", pady=6, padx=(0,10))
        self.message_text = tk.Text(frame_hide, height=5, width=50, font=("Helvetica", 10), wrap="word")
        self.message_text.grid(row=1, column=1, columnspan=2, pady=6, sticky="ew")

        ttk.Label(frame_hide, text="Output (stego) image:").grid(row=2, column=0, sticky="w", pady=6, padx=(0,10))
        self.output_path_var = tk.StringVar()
        ttk.Entry(frame_hide, textvariable=self.output_path_var, width=50, state="readonly").grid(row=2, column=1, pady=6)
        ttk.Button(frame_hide, text="Browse", command=self.browse_output, width=10).grid(row=2, column=2, padx=10, pady=6)

        ttk.Button(frame_hide, text="Hide Message", command=self.hide_message, style="Accent.TButton").grid(
            row=3, column=0, columnspan=3, pady=(15,5), ipadx=10, ipady=6)

        # Extract Section
        frame_extract = ttk.LabelFrame(root, text="  Extract Hidden Text  ", padding=15)
        frame_extract.pack(fill="x", padx=25, pady=10)

        ttk.Label(frame_extract, text="Stego Image:").grid(row=0, column=0, sticky="w", pady=6, padx=(0,10))
        self.stego_path_var = tk.StringVar()
        ttk.Entry(frame_extract, textvariable=self.stego_path_var, width=50, state="readonly").grid(row=0, column=1, pady=6)
        ttk.Button(frame_extract, text="Browse", command=self.browse_stego, width=10).grid(row=0, column=2, padx=10, pady=6)

        ttk.Button(frame_extract, text="Extract Message", command=self.extract_message, style="Accent.TButton").grid(
            row=1, column=0, columnspan=3, pady=(15,5), ipadx=10, ipady=6)

        # Extracted message box
        frame_result = ttk.LabelFrame(root, text="  Extracted Hidden Message  ", padding=15)
        frame_result.pack(fill="both", expand=True, padx=25, pady=10)

        self.extracted_text = tk.Text(frame_result, height=6, width=75, font=("Helvetica", 11, "bold"),
                                      bg="#f9fafb", fg="#111827", state="disabled", wrap="word")
        self.extracted_text.pack(fill="both", expand=True, padx=5, pady=5)

        # Status messages
        ttk.Label(root, text="Status / Messages:", font=("Helvetica", 11, "bold")).pack(anchor="w", padx=25, pady=(5,0))
        self.result_text = tk.Text(root, height=5, width=75, font=("Helvetica", 10), bg="#ffffff", state="disabled")
        self.result_text.pack(padx=25, pady=(5,20), fill="both")

        # Footer note
        ttk.Label(root, text="Use solid-color PNG images • Avoid transparency & screenshots", foreground="#666").pack(pady=5)

        # Button style - IMPORTANT: text color set to black
        style.configure("Accent.TButton", background="#4a90e2", foreground="black", font=("Helvetica", 11, "bold"))
        style.map("Accent.TButton", background=[("active", "#357abd")])

    def browse_cover(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")])
        if path:
            self.cover_path_var.set(path)

    def browse_output(self):
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png")])
        if path:
            self.output_path_var.set(path)

    def browse_stego(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")])
        if path:
            self.stego_path_var.set(path)

    def show_result(self, message, error=False):
        def _update():
            self.result_text.config(state="normal")
            self.result_text.delete("1.0", tk.END)
            color = "#dc2626" if error else "#059669"
            self.result_text.insert(tk.END, message + "\n\n")
            self.result_text.tag_add("color", "1.0", tk.END)
            self.result_text.tag_config("color", foreground=color)
            self.result_text.see(tk.END)
            self.result_text.config(state="disabled")
        self.root.after(0, _update)

    def show_extracted(self, message):
        def _update():
            self.extracted_text.config(state="normal")
            self.extracted_text.delete("1.0", tk.END)
            self.extracted_text.insert(tk.END, message)
            self.extracted_text.config(state="disabled")
            self.extracted_text.see(tk.END)
        self.root.after(0, _update)

    def hide_message(self):
        cover_path = self.cover_path_var.get()
        output_path = self.output_path_var.get()
        message = self.message_text.get("1.0", tk.END).strip()

        if not cover_path or not message or not output_path:
            self.show_result("Please fill all fields.", error=True)
            return

        try:
            self._hide_text(cover_path, message, output_path)
            self.show_result(f"Success! Message hidden.\nSaved to:\n{output_path}")
            
            messagebox.showinfo(
                title="Hide Successful",
                message=f"Message successfully hidden in the image!\n\nSaved as:\n{output_path}"
            )
            
        except Exception as e:
            self.show_result(f"Hide failed: {str(e)}", error=True)

    def _hide_text(self, image_path, message, output_path):
        img = Image.open(image_path).convert("RGB")
        width, height = img.size

        binary_msg = ''.join(format(ord(c), '08b') for c in message)
        binary_msg += '1111111100000000'  # delimiter

        if len(binary_msg) > width * height * 3:
            raise ValueError("Message too long for this image.")

        pixels = list(img.getdata())
        bit_index = 0

        for i in range(len(pixels)):
            r, g, b = pixels[i]
            if bit_index < len(binary_msg):
                r = (r & ~1) | int(binary_msg[bit_index])
                bit_index += 1
            if bit_index < len(binary_msg):
                g = (g & ~1) | int(binary_msg[bit_index])
                bit_index += 1
            if bit_index < len(binary_msg):
                b = (b & ~1) | int(binary_msg[bit_index])
                bit_index += 1
            pixels[i] = (r, g, b)
            if bit_index >= len(binary_msg):
                break

        new_img = Image.new("RGB", (width, height))
        new_img.putdata(pixels)
        new_img.save(output_path, "PNG")

    def extract_message(self):
        stego_path = self.stego_path_var.get()
        if not stego_path:
            self.show_result("Please select a stego image first.", error=True)
            return

        self.show_result(f"Extracting from:\n{stego_path}\nPlease wait...", error=False)

        try:
            message = self._extract_text(stego_path)
            self.show_extracted(message)

            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(message)
            except:
                pass

            self.show_result("Extraction complete. Message shown above.\n(Copied to clipboard)", error=False)

        except Exception as e:
            self.show_result(f"Extraction failed:\n{str(e)}", error=True)

    def _extract_text(self, image_path):
        img = Image.open(image_path).convert("RGB")
        pixels = list(img.getdata())

        binary = ""
        for r, g, b in pixels:
            binary += str(r & 1)
            binary += str(g & 1)
            binary += str(b & 1)

        delimiter = "1111111100000000"
        end_index = binary.find(delimiter)

        if end_index == -1:
            raise ValueError("No hidden message found (delimiter missing). Wrong image?")

        binary_msg = binary[:end_index]

        message = ""
        for i in range(0, len(binary_msg), 8):
            byte = binary_msg[i:i+8]
            if len(byte) == 8:
                try:
                    message += chr(int(byte, 2))
                except:
                    break

        return message


if __name__ == "__main__":
    root = tk.Tk()
    app = SteganographyApp(root)
    root.mainloop()