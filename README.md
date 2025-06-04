# Microsoft Rewards Agent

An AI-powered search automation tool that combines Microsoft Edge browser automation with Google's Gemini AI to perform intelligent, randomized searches on Bing.

## Features

- **AI-Generated Queries**: Uses Google Gemini to create natural, diverse search queries
- **Edge Automation**: Seamless Microsoft Edge browser control with Selenium
- **Human-like Behavior**: Simulates natural browsing patterns with random delays and mouse movements
- **Comprehensive Logging**: CSV output with detailed search metrics
- **Error Recovery**: Automatic recovery from browser crashes and network issues
- **Rich Console Output**: Colorful progress indicators and status updates
- **Configurable Parameters**: Customizable search categories, delays, and cycles

## Quick Start

### 1. Installation

```bash
# Clone or download the project
cd msrewardsagent

# Run the setup script
python setup.py
```

### 2. Configuration

The setup script will prompt you for your Google Gemini API key. You can also manually edit the `.env` file:

```env
GEMINI_API_KEY=your_actual_api_key_here
EDGE_DRIVER_PATH=auto
DEBUG_MODE=False
LOG_LEVEL=INFO
MAX_SEARCH_CYCLES=10
MIN_DELAY=5
MAX_DELAY=45
```

### 3. Run the Agent

```bash
python ai_search_agent.py
```

## Getting a Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key and paste it when prompted during setup

## Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Your Google Gemini API key | Required |
| `EDGE_DRIVER_PATH` | Path to Edge driver (auto-download if 'auto') | `auto` |
| `DEBUG_MODE` | Enable debug logging | `False` |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |
| `MAX_SEARCH_CYCLES` | Number of search cycles to perform | `10` |
| `MIN_DELAY` | Minimum delay between searches (seconds) | `5` |
| `MAX_DELAY` | Maximum delay between searches (seconds) | `45` |

## Search Categories

The AI generates queries across diverse categories:

- **Technology & Science**: Latest tech trends, scientific discoveries
- **Current Events**: News, trending topics, world events
- **Entertainment**: Movies, music, pop culture
- **Sports & Health**: Fitness, sports news, health tips
- **Food & Travel**: Recipes, destinations, cultural experiences
- **Education & History**: Learning resources, historical facts
- **Nature & Environment**: Wildlife, climate, conservation

## Query Types

- **Questions**: "How does...", "What is...", "Why does..."
- **Definitions**: Technical terms, concepts, explanations
- **Fact Searches**: Specific information, statistics
- **Comparisons**: "X vs Y", product comparisons
- **News Searches**: Current events, breaking news

## Output Files

### CSV Log
- `search_log_YYYYMMDD_HHMMSS.csv`: Detailed search results
- Columns: timestamp, query, search_url, status, execution_time, category, query_type

### Application Log
- `search_agent.log`: Debug and error information

## Human-like Features

- **Variable Typing Speed**: Mimics natural typing patterns
- **Mouse Movements**: Random cursor movements during browsing
- **Page Scrolling**: Natural scrolling behavior
- **Smart Delays**: Randomized pauses between actions
- **Mixed Input Methods**: Alternates between keyboard and clicks

## Error Handling

- **Browser Recovery**: Automatic restart on crashes
- **API Retry Logic**: Exponential backoff for API failures
- **Input Validation**: Query sanitization and safety checks
- **Comprehensive Logging**: Detailed error reporting

## Safety Features

- **Content Filtering**: Blocks inappropriate content generation
- **Rate Limiting**: Respects API and search limits
- **Anti-Detection**: Stealth browsing techniques
- **Safe Defaults**: Conservative safety settings

## Troubleshooting

### Common Issues

**"GEMINI_API_KEY not set"**
- Ensure your API key is correctly set in the `.env` file
- Verify the key is valid and has appropriate permissions

**"Failed to initialize Edge browser"**
- Install Microsoft Edge browser
- Check if Edge WebDriver is accessible
- Try setting `EDGE_DRIVER_PATH` to a specific path

**"Search timeout"**
- Check internet connection
- Increase timeout values in the code
- Verify Bing is accessible

### Debug Mode

Enable debug mode for detailed logging:

```env
DEBUG_MODE=True
LOG_LEVEL=DEBUG
```

## Legal Notice

This tool is for educational and personal use only. Users are responsible for:
- Complying with Microsoft's Terms of Service
- Respecting rate limits and fair usage policies
- Ensuring searches are appropriate and legal
- Following applicable laws and regulations

## Project Structure

```
msrewardsagent/
├── ai_search_agent.py      # Main application
├── config.py               # Configuration utilities
├── setup.py               # Setup script
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── README.md             # This file
├── logs/                 # Application logs
├── data/                 # Search data
└── reports/              # Generated reports
```

## Dependencies

- **selenium**: Browser automation
- **google-generativeai**: Google Gemini AI
- **webdriver-manager**: Automatic driver management
- **colorama**: Console colors
- **pandas**: Data processing
- **fake-useragent**: User agent rotation
- **python-dotenv**: Environment variables

## Version Requirements

- Python 3.10+
- Microsoft Edge Browser
- Windows/macOS/Linux

## Contributing

This is a personal automation tool. Feel free to fork and modify for your own use cases.

## License

This project is provided as-is for educational purposes. Use responsibly and in accordance with all applicable terms of service and laws.
