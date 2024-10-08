import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from collections import defaultdict
import os
import urllib.parse
import re

# Function to load an M3U playlist and extract file paths
def load_m3u_playlist(file_path):
    playlist_dir = os.path.dirname(file_path)  # Get the directory of the loaded playlist
    playlist = []
    print(f"Loading playlist from: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = [line.strip().replace('%20', ' ') for line in f]

    i = 0
    while i < len(lines):
        line = lines[i]
        
        if line.startswith("#EXTINF:"):
            # Extract filename from the next line (if it exists)
            if i + 1 < len(lines):
                file_path = lines[i + 1]
                # Check if the file path already starts with a drive letter or SMB path
                if re.match(r"^[a-zA-Z]:\\|^smb://", file_path):
                    full_path = file_path  # Keep as-is
                else:
                    full_path = os.path.abspath(os.path.join(playlist_dir, file_path))
                
                filename = os.path.basename(full_path)
                filename_without_ext = os.path.splitext(filename)[0]

                # If the #EXTINF line has a blank or placeholder title, replace it
                if re.match(r"#EXTINF:\d*,\s*-?\s*-?$", line):
                    line = f"#EXTINF:0,{filename_without_ext}"

            playlist.append(line)
        elif not line.startswith("#EXTM3U"):
            # Check if the line is a file path
            if re.match(r"^[a-zA-Z]:\\|^smb://", line) or not line.startswith("#"):
                # Only add the path if it does not already have a drive letter or SMB path
                if not re.match(r"^[a-zA-Z]:\\|^smb://", line):
                    line = os.path.abspath(os.path.join(playlist_dir, line))
                
                # Ensure the previous line is an #EXTINF line; if not, add one
                if len(playlist) == 0 or not playlist[-1].startswith("#EXTINF"):
                    filename = os.path.basename(line)
                    filename_without_ext = os.path.splitext(filename)[0]
                    extinf_line = f"#EXTINF:0,{filename_without_ext}"
                    playlist.append(extinf_line)
                
                playlist.append(line)
            else:
                # For the #EXTM3U header or any other line, just append it as-is
                playlist.append(line)

        i += 1

    print("\nLoaded playlist:")
    for idx, item in enumerate(playlist):
        print(f"{idx + 1}: {item}")

    return playlist

# Function to save the updated playlist
def save_m3u_playlist(playlist, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        for item in playlist:
            f.write(f"{item}\n")

# Function to create a playlist from folder
def create_m3u_from_folder(folder_path, output_path):
    playlist = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(('mp3', 'mp4', 'avi', 'mkv')):  # Add other extensions as needed
                sanitized_file = sanitize_filename(file)
                playlist.append(os.path.join(root, sanitized_file))
    save_m3u_playlist(playlist, output_path)

# Function to sanitize filenames by removing bad characters
def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

# Modify the PlaylistEditor class to handle title and path separately
class PlaylistEditor:
    def __init__(self, root, playlist):
        self.root = root
        self.playlist = playlist
        self.duplicates = self.check_duplicates()

        # Replace Listbox with ScrolledText
        self.playlist_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=120, height=30)
        self.playlist_display.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.load_playlist()

        # Button frame to hold buttons
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        # Buttons arranged symmetrically in a 2x2 grid
        self.load_button = tk.Button(button_frame, text="Load Playlist", command=self.load_playlist_button)
        self.load_button.grid(row=0, column=0, padx=10, pady=5)

        self.remove_duplicates_button = tk.Button(button_frame, text="Remove Duplicates", command=self.remove_duplicates)
        self.remove_duplicates_button.grid(row=0, column=1, padx=10, pady=5)

        self.merge_button = tk.Button(button_frame, text="Merge Playlist", command=self.merge_playlist)
        self.merge_button.grid(row=1, column=0, padx=10, pady=5)

        self.save_button = tk.Button(button_frame, text="Save Playlist", command=self.save_playlist)
        self.save_button.grid(row=1, column=1, padx=10, pady=5)

    def load_playlist(self):
        self.playlist_display.config(state=tk.NORMAL)
        self.playlist_display.delete('1.0', tk.END)  # Clear existing content

        line_number = 1
        if self.playlist and self.playlist[0].startswith('#EXTM3U'):
            self.playlist_display.insert(tk.END, f"{line_number:4d} | {self.playlist[0]}\n")
            line_number += 1
            self.playlist_display.insert(tk.END, "\n")
            start = 1
        else:
            start = 0

        for i in range(start, len(self.playlist), 2):
            if i + 1 < len(self.playlist):
                self.playlist_display.insert(tk.END, f"{line_number:4d} | {self.playlist[i]}\n")
                line_number += 1
                self.playlist_display.insert(tk.END, f"{line_number:4d} | {self.playlist[i + 1]}\n")
                line_number += 1
                self.playlist_display.insert(tk.END, "\n")

        self.playlist_display.config(state=tk.DISABLED)  # Make it read-only

    def load_playlist_button(self):
        file_path = filedialog.askopenfilename(filetypes=[("M3U files", "*.m3u")])
        if file_path:
            self.playlist = load_m3u_playlist(file_path)
            self.duplicates = self.check_duplicates()
            self.load_playlist()  # Refresh the display with the newly loaded playlist

    def check_duplicates(self):
        file_dict = defaultdict(list)
        start = 1 if self.playlist and self.playlist[0].startswith('#EXTM3U') else 0
        for i in range(start + 1, len(self.playlist), 2):  # Start from file paths
            file_path = os.path.abspath(self.playlist[i].replace('%20', ' '))  # Replace "%20" with space and ensure absolute path
            filename = os.path.basename(urllib.parse.unquote(file_path))
            file_dict[filename].append(i)

        return {filename: indices for filename, indices in file_dict.items() if len(indices) > 1}

    def remove_duplicates(self):
        if not self.duplicates:
            messagebox.showinfo("No Duplicates", "No duplicate entries found in the playlist.")
            return

        to_remove = []
        summary = []

        for filename, indices in self.duplicates.items():
            # Keep the first occurrence, remove the rest
            for index in indices[1:]:
                to_remove.extend([index - 1, index])
                summary.append(f"{self.playlist[index - 1]}\n{self.playlist[index]}")

        # Sort in reverse order to remove from end to start
        to_remove.sort(reverse=True)

        # Display summary of entries to be removed in a scrollable window
        summary_window = tk.Toplevel(self.root)
        summary_window.title("Duplicates to be Removed")
        summary_window.geometry("600x400")  # Set the size of the window

        label = tk.Label(summary_window, text="The following duplicate entries will be removed:")
        label.pack(pady=10)

        text_area = scrolledtext.ScrolledText(summary_window, wrap=tk.WORD, width=70, height=20)
        text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        text_area.insert(tk.END, "\n\n".join(summary))
        text_area.config(state=tk.DISABLED)  # Make the text area read-only

        def confirm_removal():
            summary_window.destroy()
            # Remove the duplicates
            for index in to_remove:
                del self.playlist[index]

            self.duplicates = self.check_duplicates()
            self.load_playlist()  # Reload the playlist to update the display
            messagebox.showinfo("Duplicates Removed", f"{len(summary)} duplicate entries have been removed from the playlist.")

        def cancel_removal():
            summary_window.destroy()
            messagebox.showinfo("Operation Cancelled", "No duplicates were removed.")

        button_frame = tk.Frame(summary_window)
        button_frame.pack(pady=10)

        confirm_button = tk.Button(button_frame, text="Confirm Removal", command=confirm_removal)
        confirm_button.pack(side=tk.LEFT, padx=10)

        cancel_button = tk.Button(button_frame, text="Cancel", command=cancel_removal)
        cancel_button.pack(side=tk.LEFT, padx=10)

        # Make sure the window stays open
        summary_window.transient(self.root)
        summary_window.grab_set()
        summary_window.update()
        self.root.wait_window(summary_window)

    def merge_playlist(self):
        file_path = filedialog.askopenfilename(filetypes=[("M3U files", "*.m3u")])
        if file_path:
            playlist_dir = os.path.dirname(file_path)  # Get the directory of the loaded playlist
            with open(file_path, 'r', encoding='utf-8') as f:
                new_playlist = []
                lines = [line.strip().replace('%20', ' ') for line in f]

                i = 0
                while i < len(lines):
                    line = lines[i]
                    
                    if line.startswith("#EXTINF:"):
                        # Extract filename from the next line (if it exists)
                        if i + 1 < len(lines):
                            file_path = lines[i + 1]
                            # Check if the file path already starts with a drive letter or SMB path
                            if re.match(r"^[a-zA-Z]:\\|^smb://", file_path):
                                full_path = file_path  # Keep as-is
                            else:
                                full_path = os.path.abspath(os.path.join(playlist_dir, file_path))
                            
                            filename = os.path.basename(full_path)
                            filename_without_ext = os.path.splitext(filename)[0]

                            # If the #EXTINF line has a blank or placeholder title, replace it
                            if re.match(r"#EXTINF:\d*,\s*-?\s*-?$", line):
                                line = f"#EXTINF:0,{filename_without_ext}"

                        new_playlist.append(line)
                    elif not line.startswith("#EXTM3U"):
                        # Check if the line is a file path
                        if re.match(r"^[a-zA-Z]:\\|^smb://", line) or not line.startswith("#"):
                            # Only add the path if it does not already have a drive letter or SMB path
                            if not re.match(r"^[a-zA-Z]:\\|^smb://", line):
                                line = os.path.abspath(os.path.join(playlist_dir, line))
                            
                            # Ensure the previous line is an #EXTINF line; if not, add one
                            if len(new_playlist) == 0 or not new_playlist[-1].startswith("#EXTINF"):
                                filename = os.path.basename(line)
                                filename_without_ext = os.path.splitext(filename)[0]
                                extinf_line = f"#EXTINF:0,{filename_without_ext}"
                                new_playlist.append(extinf_line)
                            
                            new_playlist.append(line)
                        else:
                            # For any other line, just append it as-is
                            new_playlist.append(line)

                    i += 1

            # Merge playlists
            self.playlist.extend(new_playlist)

            # Check for duplicates
            self.duplicates = self.check_duplicates()
            if self.duplicates:
                self.remove_duplicates()

            self.load_playlist()
            messagebox.showinfo("Merge Complete", "Playlists have been merged successfully.")

    def save_playlist(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".m3u", filetypes=[("M3U files", "*.m3u")])
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                for item in self.playlist:
                    f.write(f"{item}\n")
            messagebox.showinfo("Playlist Saved", f"Playlist has been saved to {file_path}")

# Main function to run the app
def main():
    root = tk.Tk()
    root.title("M3U Playlist Editor")

    file_path = filedialog.askopenfilename(filetypes=[("M3U files", "*.m3u")])
    if file_path:
        playlist = load_m3u_playlist(file_path)
        editor = PlaylistEditor(root, playlist)
        root.mainloop()
    else:
        print("No file selected. Exiting.")

if __name__ == "__main__":
    main()
