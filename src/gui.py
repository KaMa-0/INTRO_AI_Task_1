import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys
import io
import contextlib
import main  # import your solver logic (main.py)


class RedirectedStdout(io.StringIO):
    """Helper class to redirect print() output into the GUI text box."""
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.configure(state="normal")
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.configure(state="disabled")

    def flush(self):
        pass


class PuzzleApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("8-Puzzle Solver Benchmark (A*)")
        self.geometry("750x600")
        self.resizable(False, False)
        self.benchmark_thread = None

        # --- Configuration Frame ---
        config_frame = ttk.LabelFrame(self, text="Configuration", padding=10)
        config_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(config_frame, text="Number of games to generate:").grid(row=0, column=0, sticky="w")
        self.games_var = tk.IntVar(value=100)
        ttk.Entry(config_frame, textvariable=self.games_var, width=10).grid(row=0, column=1, padx=5)

        ttk.Label(config_frame, text="Select heuristics:").grid(row=1, column=0, sticky="w", pady=(5,0))
        self.hamming_var = tk.BooleanVar(value=True)
        self.manhattan_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(config_frame, text="Hamming", variable=self.hamming_var).grid(row=1, column=1, sticky="w")
        ttk.Checkbutton(config_frame, text="Manhattan", variable=self.manhattan_var).grid(row=1, column=2, sticky="w")

        button_frame = ttk.Frame(config_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        ttk.Button(button_frame, text="Run Benchmark", command=self.start_benchmark).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Stop Benchmark", command=self.stop_benchmark).grid(row=0, column=1, padx=5)

        # --- Output Frame ---
        output_frame = ttk.LabelFrame(self, text="Output", padding=10)
        output_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.output_text = tk.Text(output_frame, wrap="word", state="disabled", bg="#111", fg="#0f0", font=("Courier", 10))
        self.output_text.pack(fill="both", expand=True)

        self.progress = ttk.Progressbar(self, mode="indeterminate")
        self.progress.pack(fill="x", padx=10, pady=(0,10))

    def start_benchmark(self):
        if self.benchmark_thread and self.benchmark_thread.is_alive():
            messagebox.showwarning("Running", "A benchmark is already running.")
            return

        games = self.games_var.get()
        heuristics = []
        if self.manhattan_var.get():
            heuristics.append("manhattan")
        if self.hamming_var.get():
            heuristics.append("hamming")

        if not heuristics:
            messagebox.showwarning("Warning", "Please select at least one heuristic!")
            return

        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", tk.END)
        self.output_text.configure(state="disabled")

        # Reset stop flag
        main.stop_requested = False

        self.progress.start()
        self.benchmark_thread = threading.Thread(target=self.run_benchmark_thread, args=(games, heuristics), daemon=True)
        self.benchmark_thread.start()

    def run_benchmark_thread(self, games, heuristics):
        redirected_output = RedirectedStdout(self.output_text)
        with contextlib.redirect_stdout(redirected_output):
            try:
                main.run_benchmark(games_to_generate=games, heuristics=heuristics)
            except Exception as e:
                print(f"Error: {e}")
        self.progress.stop()
        messagebox.showinfo("Benchmark complete", "Benchmark finished (or stopped).")

    def stop_benchmark(self):
        """Trigger stop flag in main module."""
        if not self.benchmark_thread or not self.benchmark_thread.is_alive():
            messagebox.showinfo("Info", "No benchmark is currently running.")
            return

        main.request_stop()
        print("\nStop signal sent. Waiting for current puzzle to finish...\n")


def start_gui():
    app = PuzzleApp()
    app.mainloop()


if __name__ == "__main__":
    start_gui()

