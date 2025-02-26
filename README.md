# SoundCloud Bot for Discovering Low-Like Tracks

This project automates the discovery of underappreciated tracks on SoundCloud by scanning a specified playlist, generating a "radio" (related tracks) playlist for each new track, and filtering for tracks with fewer than 100 likes. Filtered tracks are then added to a dedicated SoundCloud playlist named **sc_digger_bot_proposals**.

The script is built using Python and the SoundCloud API, and it is scheduled to run weekly via GitHub Actions. API keys are kept private by using GitHub Secrets.

## Features

- **Playlist Resolution:** Automatically resolves a SoundCloud playlist URL to retrieve its track list.
- **Radio Playlist Generation:** For each new track in the source playlist, fetches a list of related tracks using SoundCloud's "radio" feature.
- **Filtering:** Selects only the related tracks with fewer than 100 likes.
- **Playlist Update:** Adds these low-like tracks to the dedicated proposals playlist.
- **History Tracking:** Maintains a local history file (`processed_tracks.txt`) to avoid reprocessing tracks.
- **Scheduled Execution:** Runs automatically on a weekly schedule via GitHub Actions.
- **Secure API Key Storage:** API credentials are stored securely using GitHub Secrets.

## Prerequisites

- **SoundCloud API Credentials:**  
  - `SOUNDCLOUD_CLIENT_ID`
  - `SOUNDCLOUD_OAUTH_TOKEN`  
  (Obtain these by registering your app at [SoundCloud for Developers](https://developers.soundcloud.com/).)

- **SoundCloud Playlist Details:**  
  - The URL (or ID) of the playlist to process.
  - The numeric ID of the proposals playlist (`sc_digger_bot_proposals`) where filtered tracks will be added.

- **Python Environment:**  
  Ensure you have Python 3 installed along with the `requests` library. You can install dependencies via:
  ```bash
  pip install requests
  ```

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/soundcloud-bot.git
cd soundcloud-bot
```

### 2. Add the Python Script

The main bot logic is implemented in `script.py`. (See the file in the repository root for details.)

### 3. Configure GitHub Secrets

Store your sensitive API credentials and playlist settings in GitHub Secrets:
- Go to your repository on GitHub.
- Click on **Settings** → **Secrets and variables** → **Actions**.
- Click **New repository secret** and add the following:
  - `SOUNDCLOUD_CLIENT_ID`
  - `SOUNDCLOUD_OAUTH_TOKEN`
  - `SOUNDCLOUD_PLAYLIST_URL` (the URL of the playlist to process)
  - `PROPOSALS_PLAYLIST_ID` (the numeric ID of your proposals playlist)

### 4. GitHub Actions Workflow

A GitHub Actions workflow is provided in `.github/workflows/soundcloud_bot.yml` which runs the bot every Sunday at midnight UTC. This workflow installs the required dependencies and executes `script.py` using the secrets.

### 5. History File

The bot uses `processed_tracks.txt` to keep track of processed track IDs. This file is created automatically on the first run.

## Running the Bot Locally

To test the bot on your local machine, ensure the environment variables are set. You can run the script directly:

```bash
python script.py
```

You may use a tool like [python-dotenv](https://pypi.org/project/python-dotenv/) if you prefer loading environment variables from a `.env` file.

## Deployment

The bot is deployed using GitHub Actions:
- The workflow in `.github/workflows/soundcloud_bot.yml` is scheduled to run weekly.
- You can also manually trigger the workflow from the **Actions** tab in your repository.

## Troubleshooting

- **Missing API Credentials:**  
  Make sure all required secrets (`SOUNDCLOUD_CLIENT_ID`, `SOUNDCLOUD_OAUTH_TOKEN`, etc.) are correctly set in GitHub Secrets.

- **API Errors:**  
  Check the GitHub Actions logs for any error messages from the SoundCloud API. Verify that your credentials have the necessary permissions.

- **History File Issues:**  
  Ensure that the `processed_tracks.txt` file is writable. If you encounter issues, try deleting it to allow the script to recreate it.

## Contributing

Feel free to open issues or submit pull requests if you have improvements or bug fixes.

## License

This project is open-source under the [MIT License](LICENSE).

---

By automating the discovery of low-like tracks and updating your proposals playlist, this bot helps keep your SoundCloud collection fresh and full of hidden gems!

