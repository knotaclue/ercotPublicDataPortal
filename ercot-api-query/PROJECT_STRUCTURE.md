# Project Structure

Complete overview of all files and directories in the ERCOT API Query Tool project.

## 📁 Directory Tree

```
ercot-api-query/
│
├── ercot_query.py              # Main executable script
├── .env                         # Your credentials (create from .env.template)
├── .env.template               # Template for environment variables
├── .gitignore                  # Git ignore rules (protects secrets)
├── requirements.txt            # Python dependencies
│
├── README.md                   # Main documentation
├── QUICKSTART.md               # 5-minute getting started guide
├── TROUBLESHOOTING.md          # Common issues and solutions
├── EXAMPLES.md                 # Practical usage examples
├── CHANGELOG.md                # Version history and updates
├── PROJECT_STRUCTURE.md        # This file
├── LICENSE                     # MIT License
│
├── queries/                    # Query configuration directory
│   ├── realtime_system_load.json
│   ├── settlement_point_prices.json
│   └── wind_power_production.json
│
└── output/                     # API responses stored here
    ├── .gitkeep
    └── (your JSON output files will be here)
```

---

## 📄 File Descriptions

### Core Files

#### `ercot_query.py`
**Purpose**: Main Python script that handles all API interactions

**What it does**:
- Loads credentials from `.env` file
- Authenticates with ERCOT API
- Manages access token refresh (30-minute expiry)
- Reads query configurations from JSON files
- Makes API requests with flexible parameters
- Saves responses to JSON files
- Provides comprehensive error handling and logging

**Key features**:
- Extensively commented for non-developers
- Object-oriented design with ERCOTAPIClient class
- Automatic token management
- Command-line interface

**Usage**:
```bash
python3 ercot_query.py --config queries/yourquery.json
```

---

#### `.env` (You create this)
**Purpose**: Stores your API credentials securely

**Contains**:
```bash
ERCOT_USERNAME=your_username
ERCOT_PASSWORD=your_password
ERCOT_SUBSCRIPTION_KEY=your_subscription_key
ERCOT_BASE_URL=https://data.ercot.com
```

**Important**:
- ⚠️ **NEVER commit this file to git**
- Create it by copying `.env.template`
- Keep it in the project root directory
- Protected by `.gitignore`

---

#### `.env.template`
**Purpose**: Template for creating your `.env` file

**What to do**:
1. Copy to `.env`: `cp .env.template .env`
2. Edit `.env` with your actual credentials
3. Keep `.env.template` as reference

**Why it exists**:
- Can be safely committed to git (no secrets)
- Shows required environment variables
- Provides documentation for each variable

---

#### `requirements.txt`
**Purpose**: Lists Python package dependencies

**Contains**:
```
requests>=2.31.0        # HTTP library for API calls
python-dotenv>=1.0.0    # Loads .env variables
```

**Installation**:
```bash
pip3 install -r requirements.txt
```

**Why it matters**:
- Ensures correct package versions
- Makes setup reproducible
- Standard Python practice

---

#### `.gitignore`
**Purpose**: Tells git which files NOT to track

**Protects**:
- `.env` file (your secrets!)
- Python cache files (`__pycache__/`)
- Virtual environments (`venv/`)
- IDE files (`.vscode/`, `.idea/`)
- Output files (optional)

**Critical for security**:
- Prevents accidentally committing credentials
- Keeps repository clean
- Standard for Python projects

---

### Documentation Files

#### `README.md`
**Purpose**: Main project documentation

**Sections**:
- Overview and features
- Installation instructions
- Configuration guide
- Usage examples
- Troubleshooting quick reference
- API documentation links

**When to read**: First time setup and general reference

---

#### `QUICKSTART.md`
**Purpose**: Get started in 5 minutes

**Contains**:
- Minimal setup steps
- First query example
- Quick reference pattern

**When to read**: Want to start immediately without reading everything

---

#### `TROUBLESHOOTING.md`
**Purpose**: Solutions to common problems

**Organized by**:
- Authentication issues
- Configuration issues
- API request issues
- Python/dependency issues
- Output issues
- Debugging tips

**When to read**: Something isn't working

---

#### `EXAMPLES.md`
**Purpose**: Practical usage examples and workflows

**Contains**:
- Basic query examples
- Advanced query examples
- Workflow examples (cron jobs, batch processing)
- Parameter reference
- Best practices
- Testing tips

**When to read**: Want to see how to use the tool for specific scenarios

---

#### `CHANGELOG.md`
**Purpose**: Track version history and changes

**Format**:
- Version numbers
- Release dates
- Added/Changed/Fixed features
- Upgrade instructions

**When to read**: After pulling updates from git

---

#### `PROJECT_STRUCTURE.md`
**Purpose**: This file - explains every file in the project

**When to read**: Want to understand what each file does

---

#### `LICENSE`
**Purpose**: MIT License terms

**What it means**:
- Free to use, modify, distribute
- No warranty
- Keep copyright notice

---

### Query Configuration Files

#### `queries/realtime_system_load.json`
**Purpose**: Example query for actual system load data

**Demonstrates**:
- Basic endpoint usage
- Date range parameters
- Output file specification

**Template for**: Load data queries

---

#### `queries/settlement_point_prices.json`
**Purpose**: Example query for pricing data

**Demonstrates**:
- Additional parameters (settlementPoint)
- Location-specific queries

**Template for**: Price queries at specific locations

---

#### `queries/wind_power_production.json`
**Purpose**: Example query for wind generation data

**Demonstrates**:
- Renewable energy queries
- Regional filtering

**Template for**: Generation data queries

---

### Directories

#### `queries/`
**Purpose**: Store all your query configuration files

**Usage**:
- Add new JSON files here for different queries
- Organize by category if needed (e.g., `queries/prices/`, `queries/load/`)
- Keep examples as templates

**Best practices**:
- Use descriptive filenames
- One configuration per file
- Comment-free JSON (comments not allowed in JSON)

---

#### `output/`
**Purpose**: Where API responses are saved

**Characteristics**:
- Created automatically if doesn't exist
- `.gitkeep` ensures directory exists in git
- JSON files saved here by default

**Organization tips**:
```
output/
├── 2025/
│   ├── january/
│   │   ├── system_load.json
│   │   └── prices.json
│   └── february/
│       └── ...
└── raw/
    └── ...
```

**Note**: By default, output files are not committed to git (see `.gitignore`)

---

## 🔍 File Relationships

### How Files Work Together

```
1. You edit:              .env
                          queries/myquery.json

2. You run:               python3 ercot_query.py --config queries/myquery.json

3. Script reads:          .env (credentials)
                          queries/myquery.json (what to query)
                          requirements.txt (dependencies already installed)

4. Script uses:           requests library (API calls)
                          python-dotenv (load .env)

5. Script writes:         output/yourfile.json
                          (console output with status messages)

6. Git tracks:            All files EXCEPT .env and output/
```

---

## 🚀 Quick Reference

### To Start a New Query

1. **Copy an example**:
   ```bash
   cp queries/realtime_system_load.json queries/my_query.json
   ```

2. **Edit your query**:
   ```bash
   nano queries/my_query.json
   ```

3. **Run it**:
   ```bash
   python3 ercot_query.py --config queries/my_query.json
   ```

### To Understand Something

| What you want to know | Read this file |
|----------------------|----------------|
| How to get started quickly | QUICKSTART.md |
| Detailed setup | README.md |
| How to fix an error | TROUBLESHOOTING.md |
| Example queries | EXAMPLES.md |
| What a file does | PROJECT_STRUCTURE.md (this file) |
| What changed | CHANGELOG.md |
| How the code works | ercot_query.py (inline comments) |

---

## 📝 Maintenance

### Files You Should Edit

✅ **Safe to edit**:
- `.env` (your credentials)
- `queries/*.json` (your query configurations)
- `README.md` (if you want to customize)

✅ **You should create**:
- New files in `queries/` directory
- New directories in `output/` for organization

❌ **Don't edit unless you know what you're doing**:
- `ercot_query.py` (unless modifying the code)
- `.gitignore` (unless you understand git)
- `requirements.txt` (unless adding dependencies)

❌ **Never edit**:
- `.env.template` (it's a template for others)

---

## 🔄 Updating from Git

When you pull updates:

```bash
git pull origin main
```

**What gets updated**:
- `ercot_query.py` (code improvements)
- Documentation files
- Example queries
- Dependencies (check requirements.txt)

**What doesn't change**:
- Your `.env` file (not in git)
- Your custom queries in `queries/`
- Your output files in `output/`

**After updating**:
1. Check `CHANGELOG.md` for changes
2. Run `pip3 install -r requirements.txt` if requirements changed
3. Compare your queries with updated examples if needed

---

## 💡 Tips

1. **Keep examples**: Don't delete the example query files - use them as templates

2. **Organize queries**: Create subdirectories in `queries/` if you have many:
   ```
   queries/
   ├── daily/
   ├── weekly/
   └── historical/
   ```

3. **Backup .env**: Keep a secure backup of your credentials

4. **Version control**: Commit your custom query configurations to git:
   ```bash
   git add queries/my_custom_query.json
   git commit -m "Add custom query for X"
   ```

5. **Documentation**: If you create useful queries, document them in your own notes or contribute back!

---

**Questions about any file?** Check its corresponding documentation section above or open an issue on GitHub!
