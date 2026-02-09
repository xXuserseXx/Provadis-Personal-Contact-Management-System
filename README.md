# Contact Management CLI

## Quick start (Windows)

1. **Install Python 3.10+**
2. **Clone the repo** and open a terminal in the project folder.
3. **(Recommended) Create and activate a virtual environment:**
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
4. **Install the CLI:**
   ```powershell
   py -m pip install -e .
   ```
5. **Run the CLI:**
   ```powershell
   contact-manager
   ```

The CLI will load existing contacts automatically and guide you through menus for adding, listing, searching, and saving contacts.

## Where the JSON data is saved (and how to view/alter it)

The contact data is stored in a JSON file named `contacts.json` under your OS-specific user data directory. On Windows, this resolves to:

```
C:\Users\<your-username>\AppData\Local\contact-management\contacts.json
```

You can open this file in any text editor to inspect or edit the saved contacts. The CLI reads from this file on startup and writes updates when you choose **Save contacts** or exit the program.

## Logging (what gets logged and where)

The application logs function calls and errors to a file named `contacts.log` in the **current working directory** (the folder you run `contact-manager` from). Each log entry includes a timestamp and log level.

If you want the log file in a different location, run the CLI from that directory (so `contacts.log` is created there), or update the logger configuration in `CustomLogging.logger.make_logger()` to point to a specific file path.

## Running tests

1. Install development dependencies:
   ```powershell
   py -m pip install -e ".[dev]"
   ```
2. Run the test suite:
   ```powershell
   py -m pytest
   ```