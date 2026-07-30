# Robot Control System

A complete web-based system for remotely controlling a robot, built around two core tasks:

1. **Build a control panel to move the robot**
2. **Build an interface to convert speech to text, and save the text to a database**

The project is built entirely in Python and deployed online, so anyone can access it from any device without needing to run it locally.

🔗 **Live link:** https://robot-control-s6ay.onrender.com

---

## Project Overview

The system is split into two independent pages that share the same server and database:

### 1. Robot Control Panel (`/`)
An interface featuring a D-Pad styled like a real industrial control unit:
- 4 directional buttons (forward, backward, left, right)
- A prominent circular emergency stop button
- An LCD-style status display showing the last command sent and the robot's current status

Every button press sends a request to the server, which converts the button name into a single-character code (e.g. `forward` → `f`) and stores it in the database. This allows an external device (such as an Arduino or ESP32 connected to the physical robot) to read that code and execute the corresponding movement.

### 2. Speech-to-Text (`/voice`)
An interface that uses the browser's built-in speech recognition (Web Speech API, available in Chrome):
- A microphone button to start/stop recording
- An LCD-style display showing the transcribed text live as you speak
- A save button that stores the final text in a separate database table

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python + Flask |
| Database | PostgreSQL (hosted on Supabase) |
| DB Connector | psycopg (v3) |
| Frontend | HTML / CSS / JavaScript |
| Speech-to-Text | Web Speech API (built into the browser, no external libraries) |
| Production Server | Gunicorn |
| Hosting | Render |
| Version Control | Git + GitHub |

---

## Project Structure

```
robot_control/
├── app.py                  # Main Flask server and all routes
├── requirements.txt         # Required Python packages
├── .env                     # Environment variables (DB credentials) - not committed
├── .gitignore                # Prevents .env and temp files from being pushed to GitHub
└── templates/
    ├── index.html            # Robot control panel
    └── voice.html             # Speech-to-text interface
```

---

## Database

The project uses two tables in a single PostgreSQL database (hosted on Supabase):

### `robot_state` table
Stores the last command sent to the robot (a single row, continuously updated):

| Column | Description |
|---|---|
| `id` | Fixed identifier (always 1) |
| `command` | Last command code sent (`f`, `b`, `l`, `r`, `S`) |
| `updated_at` | Timestamp of the last update |

### `voice_notes` table
Stores every transcribed voice note (a new row per recording):

| Column | Description |
|---|---|
| `id` | Auto-incrementing ID |
| `text_content` | Text transcribed from speech |
| `created_at` | Timestamp when it was saved |

---

## API Routes

| Route | Method | Purpose |
|---|---|---|
| `/` | GET | Render the robot control panel |
| `/voice` | GET | Render the speech-to-text interface |
| `/update_command` | POST | Receive a movement command from the panel and store it |
| `/get_state` | GET | Return the last stored command (intended for the physical robot to poll) |
| `/save_voice` | POST | Receive a transcribed text and store it |
| `/get_voice_notes` | GET | Return all saved voice notes |

---

## Development Journey (Summary)

1. **Built an initial PHP version** of the control panel (hosted on InfinityFree)
2. **Rebuilt the entire project in Python (Flask)** instead of PHP, for easier future development and scaling
3. **Designed a professional interface** for the control panel with an "industrial control unit" look (LCD display, D-Pad buttons, emergency stop button)
4. **Built the speech-to-text interface** using the Web Speech API, matching the same visual style
5. **Migrated from SQLite to Supabase (PostgreSQL)** to ensure data persists permanently even after server restarts — a requirement for cloud hosting
6. **Secured connection credentials** using a `.env` file and `.gitignore`, so the database password never appears in the code pushed to GitHub
7. **Pushed the project to GitHub** as the source repository
8. **Deployed the project on Render** as a Web Service connected to the GitHub repo, with the `DATABASE_URL` environment variable configured directly in Render's dashboard

---

## Running Locally (Development)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

Then open your browser at:
```
http://127.0.0.1:5000        → Robot control panel
http://127.0.0.1:5000/voice  → Speech-to-text interface
```

**Note:** Running locally requires a `.env` file in the root directory containing:
```
DATABASE_URL=postgresql://<username>:<password>@<host>:<port>/<database>
```

---

## Security Notes

- The database password never appears in the code; it's passed as an environment variable (`DATABASE_URL`), either locally via `.env` or on Render via its Environment Variables settings.
- There is currently no authentication or authorization on the `/update_command` and `/save_voice` routes — anyone with the link can send commands. This is a suggested area for future improvement (e.g. adding an API key or auth system).

---

## Suggested Future Work

- Connect the physical robot (Arduino / ESP32) to periodically poll `/get_state` and execute the actual movement
- Add a simple authentication system to protect the routes from unauthorized use
- Display a history of commands and voice notes instead of only the latest value
