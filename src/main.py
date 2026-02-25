import sys
import os
# Make sure sibling modules (roadrash, tictactoe) are always importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from tkinter import ttk
from tictactoe import TicTacToe


def main():
    root = tk.Tk()
    root.title("Game Launcher")
    root.geometry("400x360")
    root.configure(bg="#1a1a2e")
    root.resizable(False, False)

    # Header
    header = tk.Frame(root, bg="#0f3460", height=70)
    header.pack(fill=tk.X)
    header.pack_propagate(False)
    tk.Label(header, text="🎮  Game Launcher", fg="white", bg="#0f3460",
             font=("Helvetica", 22, "bold")).pack(expand=True)

    # Sub-label
    tk.Label(root, text="Choose a game to play", fg="#aaaaaa", bg="#1a1a2e",
             font=("Helvetica", 11)).pack(pady=(14, 4))

    # Helper to make nice styled game cards
    def make_card(parent, icon, title, subtitle, command):
        card = tk.Frame(parent, bg="#16213e", cursor="hand2")
        card.pack(fill=tk.X, padx=30, pady=8)

        inner = tk.Frame(card, bg="#16213e", padx=14, pady=10)
        inner.pack(fill=tk.X)

        tk.Label(inner, text=icon, font=("Helvetica", 26), bg="#16213e").pack(side=tk.LEFT, padx=(0, 12))

        text_frame = tk.Frame(inner, bg="#16213e")
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(text_frame, text=title, fg="white", bg="#16213e",
                 font=("Helvetica", 14, "bold"), anchor="w").pack(fill=tk.X)
        tk.Label(text_frame, text=subtitle, fg="#aaa", bg="#16213e",
                 font=("Helvetica", 9), anchor="w").pack(fill=tk.X)

        play_btn = tk.Button(inner, text="▶ Play", bg="#e94560", fg="white",
                             font=("Helvetica", 10, "bold"), relief="flat",
                             padx=12, pady=4, cursor="hand2", command=command)
        play_btn.pack(side=tk.RIGHT)

        # Hover effect
        def on_enter(_): card.configure(bg="#1d2d6e"); inner.configure(bg="#1d2d6e")
        def on_leave(_): card.configure(bg="#16213e"); inner.configure(bg="#16213e")
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

    def open_tictactoe():
        game = TicTacToe(root)
        game.grab_set()

    def open_roadrash():
        import subprocess
        script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "roadrash.py")
        subprocess.Popen([sys.executable, script])

    make_card(root, "✖", "Tic-Tac-Toe",
              "Classic 2-player strategy game",
              open_tictactoe)

    make_card(root, "🏍", "Road Rash",
              "Dodge cars at high speed",
              open_roadrash)

    # Footer
    tk.Label(root, text="Press ▶ Play to launch a game",
             fg="#555", bg="#1a1a2e", font=("Helvetica", 9)).pack(pady=(10, 0))

    tk.Button(root, text="Quit", bg="#333", fg="white",
              relief="flat", padx=10, pady=4,
              command=root.quit).pack(pady=10)

    root.eval("tk::PlaceWindow . center")
    root.mainloop()


if __name__ == "__main__":
    main()
