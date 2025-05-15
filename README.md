# Yahoo Auctions Parser

A comprehensive parser for Yahoo Auctions Japan with:
- HTML parsing
- API client
- Proxy support
- CSV export
- Google Sheets integration

## Features
- Multi-keyword search
- Item filtering
- Quantity detection
- Condition status detection
- Price conversion
- Debug mode with HTML output

## Requirements
- Python 3.8+
- See requirements.txt

## Installation
1. Clone the repository:
   ```bash
   git clone <your-repository>
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and configure it:
   ```bash
   cp .env.example .env
   ```
## First Setup
1. Copy the example file:
```bash
cp .env.example .env
```
2. Fill in your actual values in `.env`
3. Never commit `.env` to version control!


## Configuration
### Proxy Settings
Example `.env` configuration:
```env
PROXY_1=http://user:pass@ip:port
PROXY_2=http://user:pass@ip:port
PROXY_SOCKS5=socks5://user:pass@ip:port
```

### User-Agents
Add multiple User-Agents for rotation:
```env
USER_AGENT_1=Mozilla/5.0 (...)
USER_AGENT_2=Mozilla/5.0 (...)
```

### Google Sheets Integration
```env
# Google Sheets integration
GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json
GOOGLE_SHEETS_EMAIL=your_email@.com

# Currency conversion
YEN_TO_EUR=165  # Exchange rate
```

## Usage
Run the main script:
```bash
python parse_auctions.py
```

## Debug Mode
Set `DEBUG_MODE=True` in `.env` to generate HTML debug files.

## License
This project is licensed under the [MIT License](https://opensource.org/licenses/MIT). 
