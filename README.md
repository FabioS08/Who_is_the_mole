# Who is the mole? 🕵️‍♂️

> **The privacy-first, zero-credentials social auditor that unmasks non-followers ("the moles") on GitHub and Instagram with historical timeline tracking.**

![Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen)
![Platforms](https://img.shields.io/badge/Platforms-GitHub_|_Instagram-purple)
![Exports](https://img.shields.io/badge/Exports-Terminal_|_PDF_|_Excel-orange)
![Privacy](https://img.shields.io/badge/Privacy-100%25_Local_&_Zero--Credentials-success)
![License](https://img.shields.io/badge/License-GPL_v3.0-lightgrey)

---

### *Ever wonder who quietly hit "unfollow" while you weren't looking?*

We've all been there: your follower count drops by two, and you wonder: *who left?* 

Most "unfollower tracker" apps in mobile stores demand your raw Instagram login credentials, compromise your 2FA, trigger automated bot-detection bans or harvest your private session cookies. On GitHub, scrolling through hundreds of mutual followers across paginated web views is slow, tedious and quickly blocked by API rate limits.

**Who is the mole?** is built to solve this with a **strictly private, local-first, and credential-free** framework:

- 🛡️ **Zero Credential Sharing:** No passwords, no session tokens and zero risk of account strikes. Everything runs locally on your machine.
- 🕒 **Time-Traveling Snapshots:** It doesn't just identify who isn't following you back today, it maintains an incremental historical ledger to stamp the **exact date they unfollowed you**.
- 📊 **Executive-Grade Reports:** View results directly in an interactive, color-coded terminal table with [Rich](https://github.com/Textualize/rich), export publication-ready PDF dossiers or generate styled Excel spreadsheets.

Whether you are auditing your developer network on GitHub or reviewing your personal circle on Instagram, **the mole won't stay hidden for long.**

> 🚧 **Note for Non-Programming Users:**  
> A user-friendly **Graphical User Interface** is currently **under active development**. This upcoming frontend will allow non-technical users to analyze accounts and export PDF reports without needing to touch terminal commands. In the meantime, the quick-start guide below takes less than 2 minutes to run!


## ⛓️ Table of Contents

1. [About The Project](#-about-the-project)
2. [Repository Structure](#-repository-structure)
3. [Getting Started (Virtual Environment)](#-getting-started-virtual-environment)
4. [Usage & CLI Reference](#-usage--cli-reference)
5. [Historical Snapshot Ledger](#-historical-snapshot-ledger)
6. [How to Export Instagram Data](#-how-to-export-instagram-data)
7. [Request a New Platform](#-request-a-new-platform)
8. [Dependencies & Requirements](#-dependencies--requirements)
9. [License](#-license)


## 🗼 Repository Structure

<details>
<summary><b>Visualize Repository Structure</b></summary>
<br>

```text
Who_is_the_mole/
├── LICENSE                                     # GNU General Public License v3.0
├── README.md                                   # Comprehensive project documentation
├── requirements.txt                            # Python dependencies
├── snapshots/                                  # Follower snapshots & checkpoint caches
│   ├── .checkpoints/                           # Pagination recovery cache for GitHub API
│   ├── platform_username_history.example.json  # Reference snapshot history structure
│   └── instagram_local_export_history.json     # Saved local Instagram follower snapshot
│
└── src/                                        # Core application package
    ├── BE/                                     # Backend logic & CLI engine (fully operational)
    │   ├── __init__.py                         # Package marker
    │   ├── main.py                             # Application entrypoint & CLI argument parser
    │   └── core/                               # Core engine modules
    │       ├── __init__.py
    │       ├── snapshots_manager.py            # Historical snapshot diff engine & ledger
    │       ├── utils.py                        # Path resolution & project root utilities
    │       ├── exporters/                      # Report generation adapters
    │       │   ├── __init__.py
    │       │   ├── terminal.py                 # Rich table terminal renderer
    │       │   ├── pdf.py                      # PDF generator
    │       │   └── excel.py                    # Excel spreadsheet generator
    │       │ 
    │       └── platforms/                      # Social media checkers
    │           ├── __init__.py
    │           ├── social_media_checker.py     # SocialMediaChecker abstract base class
    │           ├── github_api_checker.py       # GitHub REST API client with checkpoint recovery
    │           └── instagram_export_checker.py # Offline Meta JSON export parser
    │ 
    └── FE/                                     # Frontend GUI (under active development for non-programmers)
        └── __init__.py                         # Version definition
```

</details>


## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/FabioS08/Who_is_the_mole.git
cd Who_is_the_mole
```

### 2. Set Up a Virtual Environment (`venv`)

A virtual environment isolates this project's dependencies from your system's global Python installation, preventing package conflicts and protecting operating system libraries.

#### On macOS / Linux:

```bash
# 1. Create a virtual environment named .venv
python3 -m venv .venv

# 2. Activate the virtual environment
source .venv/bin/activate
```
*(Your terminal prompt will now display `(.venv)`).*

#### On Windows (PowerShell / Command Prompt):

```powershell
# 1. Create a virtual environment named .venv
python -m venv .venv

# 2. Activate the virtual environment (PowerShell)
.venv\Scripts\Activate.ps1

# Or activate using CMD:
# .venv\Scripts\activate.bat
```
> *Note for PowerShell users:* If you receive an execution policy error, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` once.

### 3. Install Dependencies

With the virtual environment active, install the pinned project requirements:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Verify Active Environment

```bash
which python       # macOS/Linux (should point to .venv/bin/python)
where python       # Windows (should point to .venv\Scripts\python.exe)
```

### 5. Deactivating the Environment

When you are done using the application, deactivate the virtual environment at any time:
```bash
deactivate
```


## 💻 Usage & CLI Reference

All commands are executed via the CLI entrypoint [`src/BE/main.py`](src/BE/main.py):

```bash
python3 src/BE/main.py <platform> [options]
```

### 1. 🐙 GitHub Checker

Analyze any public GitHub profile to find users you follow who do not follow you back.

```bash
# 🔹 Default: Output styled results to the terminal
python3 src/BE/main.py github --username <github_username>

# 🔹 With PAT: Bypass GitHub's 60 req/hr rate limit (up to 5,000 req/hr)
python3 src/BE/main.py github --username <github_username> --github-token <YOUR_GITHUB_TOKEN>

# 🔹 PDF Report: Save findings to a publication-ready PDF document
python3 src/BE/main.py github --username <github_username> --output pdf --file-name github_moles

# 🔹 Excel Report: Save findings to a styled Excel (.xlsx) spreadsheet
python3 src/BE/main.py github --username <github_username> --output excel --file-name github_moles
```

> 💡 **Rate Limits & Automatic Checkpoint Recovery:**
> - **Rate Limits:** GitHub limits unauthenticated API requests to **60 requests/hour** (up to 100 profiles per page request). Passing a free [GitHub Personal Access Token (PAT)](https://github.com/settings/tokens) via `--github-token` raises your quota to **5,000 requests/hour**.
> - **Automatic Checkpoint Resuming:** If you hit GitHub's rate limit, **you don't lose any progress and don't need to start over, you simply have to wait!** The checker automatically saves all already-fetched accounts and the next page number to `snapshots/.checkpoints/`. Once GitHub's hourly quota window resets, re-run the exact same command: it will detect the checkpoint, restore all cached records and seamlessly resume fetching from the exact page where it stopped. Once the full list is successfully retrieved, the checkpoint file is automatically cleared.

### 2. 📸 Instagram Checker

Inspect your Instagram connections safely using your official local data export without sharing passwords or session cookies.

```bash
# 🔹 Default: Output styled results to the terminal
python3 src/BE/main.py instagram --path "/path/to/extracted/instagram_export"

# 🔹 PDF Report: Save findings to a publication-ready PDF document
python3 src/BE/main.py instagram --path "/path/to/extracted/instagram_export" --output pdf --file-name instagram_moles

# 🔹 Excel Report: Save findings to a styled Excel (.xlsx) spreadsheet
python3 src/BE/main.py instagram --path "/path/to/extracted/instagram_export" --output excel --file-name instagram_moles
```

> 💡 **Export Path:** Provide the path to the unzipped export folder containing your `followers_*.json` and `following.json` files (see [How to Export Instagram Data](#-how-to-export-instagram-data) below).

### 3. ⚙️ Command-Line Arguments Reference

```
python3 src/BE/main.py [-h] [--username USERNAME] [--path PATH]
                       [--github-token GITHUB_TOKEN] [--output {terminal,pdf,excel}]
                       [--file-name FILE_NAME]
                       {github,instagram}
```

| Argument | Type | Default | Required For | Description |
| :--- | :--- | :--- | :--- | :--- |
| `platform` | Positional | *None* | **All** | Platform to analyze: `github` or `instagram`. |
| `--username` | String | `None` | `github` | Target GitHub profile username. |
| `--path` | String | `None` | `instagram` | File system path to the extracted Instagram JSON export folder. |
| `--github-token` | String | `None` | *Optional* | GitHub Personal Access Token (PAT) to bypass 60 req/hr rate limit. |
| `--output` | Choice | `terminal` | *Optional* | Output destination format: `terminal`, `pdf` or `excel`. |
| `--file-name` | String | `non_followers_report` | *Optional* | Base name for the export file (exporters automatically append the correct extension). Alias: `--filename`. |


## 🕒 Historical Snapshot Ledger

The application implements an **incremental follower ledger** in [`snapshots/`](snapshots/):

1. **State Preservation**: On every execution, the complete follower list is saved to `snapshots/<platform>_<account_id>_history.json`.
2. **Delta Detection**: On subsequent runs, `SnapshotManager` compares the previous follower set with the new incoming follower set.
3. **Timeline Stamp**: Any username present in the historical record but missing from the current followers list is flagged as having unfollowed you, and the current date is locked into `unfollow_dates`.

#### Example Snapshot Schema:
```json
{
  "followers": [
                  "active_follower_1",
                  "active_follower_2"
                ],

  "unfollow_dates": {
                      "user_who_left_yesterday": "2026-10-17",
                      "user_who_left_last_month": "2026-09-15"
                    }
}
```

## 📥 How to Export Instagram Data

To analyze your Instagram account safely without giving out credentials:

1. Log into **Instagram** in your mobile app or web browser.
2. Navigate to **Settings** > **Accounts Center** ([accountscenter.instagram.com](https://accountscenter.instagram.com)).
3. Select **Your information and permissions** > **Download your information**.
4. Click **Download or transfer information**, choose your Instagram profile, and select **Some of your information**.
5. Select **Followers and following**.
6. **Important:** Under **Format**, choose **JSON** (*HTML format is not supported*).
7. Submit the request. Meta will notify you when your archive is ready for download (usually 5–15 minutes).
8. Unzip the downloaded `.zip` archive and pass the resulting folder path to `--path`.


## 💡 Request a New Platform

Interested in auditing another social network?

We're always looking to expand platform support! Feel free to **[open an issue](https://github.com/FabioS08/Who_is_the_mole/issues/new)** requesting the platform you want, and you will see it added soon!


## 📦 Dependencies & Requirements

- **Python 3.10+** (tested on Python 3.10, 3.11, 3.12, 3.13)
- Key Libraries:
  - [`rich`](https://rich.readthedocs.io/): Terminal formatting, spinners, boxes, and styled tables.
  - [`reportlab`](https://www.reportlab.com/): PDF vector engine for publication-quality reports.
  - [`openpyxl`](https://openpyxl.readthedocs.io/): Formatted Excel spreadsheet engine (.xlsx) with custom typography and hyperlinks.


## 📄 License

This project is licensed under the terms of the **GNU General Public License v3.0 (GPL-3.0)**.  
See the [LICENSE](LICENSE) file for full license terms and conditions.