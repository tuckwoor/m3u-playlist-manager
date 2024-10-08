# M3U Playlist Editor

A Python-based M3U Playlist Editor with a GUI built using Tkinter. This application allows you to load, edit, merge, and save M3U playlists, providing easy-to-use features for managing your multimedia playlists. Written originally to process m3u playlists generated using VideoLAN (VLC) which leave bad formatting (particularly spaces) for filenames etc.

## Features

- Load M3U Playlist: Load an existing M3U playlist file and view its content.

- Remove Duplicates: Automatically detect and remove duplicate entries from the playlist.

- Merge Playlists: Merge an additional M3U playlist into the current playlist, with options to remove duplicate entries.

- Create Playlist from Folder: Create a new playlist from a specified folder, automatically adding supported media files.

- Sanitize Filenames: Ensure filenames are sanitized, replacing characters that are not suitable for M3U files.

- Save Playlist: Save the edited playlist to a new or existing M3U file.

## Requirements

Python 3.x

Tkinter (usually included with Python)

## Installation

Clone the repository

Navigate to the project directory

Install any required dependencies (if needed)

## Usage

Run the script with python

Load an M3U playlist or create a new one from a folder.

Use the buttons to remove duplicates, merge playlists, or save your changes.

## GUI Overview

- Load Playlist: Opens a dialog to select an M3U file to load.

- Remove Duplicates: Identifies duplicate entries in the playlist and removes them after confirmation.

- Merge Playlist: Allows merging another M3U playlist with the current one, ensuring no duplicates.

- Save Playlist: Saves the modified playlist to a new or existing M3U file.

## Example

Here's an example of using the application to load a playlist, remove duplicates, merge another playlist, and then save the resulting playlist.

Start the application.

Load an M3U playlist.

Click "Remove Duplicates" to clean up the playlist.

Click "Merge Playlist" to add content from another playlist.

Save the playlist with the "Save Playlist" button.

## Contributing

Contributions are welcome! Feel free to submit a pull request or open an issue for suggestions or bug reports.

## License

This project is licensed under the GNU General Public License (GPL).
