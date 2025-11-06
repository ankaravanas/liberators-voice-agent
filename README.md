# Voice Agent MCP Server

A powerful MCP server optimized for voice agents, providing complete business automation analysis in a single tool call.

## 🚀 Live Server

**https://web-voice-automation.up.railway.app**

## 🎯 Perfect for Voice Agents

Single tool call: `voice_agent_website_analysis`
- **Input**: Just a URL string
- **Output**: Voice-friendly text summary
- **Works with**: vAPI, Bland AI, Retell AI, and other voice platforms

## What It Does

1. **Website Analysis** - FireCrawl v2 API extracts business information
2. **AI Analysis** - OpenAI GPT-5 identifies 3 automation opportunities  
3. **Professional Report** - Generates HTML report with recommendations
4. **Email Delivery** - Automatically sends report to business email
5. **Lead Capture** - Silently logs lead in ClickUp
6. **Voice Summary** - Returns simple text for voice agents to speak

## Quick Integration

### vAPI
```json
{
  "functions": [{
    "name": "analyze_website",
    "server": {"url": "https://web-voice-automation.up.railway.app"}
  }]
}
```

### Bland AI / Retell AI
```python
import requests

response = requests.post(
    "https://web-voice-automation.up.railway.app",
    json={
        "tool": "voice_agent_website_analysis",
        "arguments": {"url": "https://example.com"}
    }
)
```

## Environment Variables

Set these in Railway dashboard:

```bash
FIRECRAWL_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
GMAIL_USER=your_email@gmail.com
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret
GMAIL_REFRESH_TOKEN=your_refresh_token
CLICKUP_API_KEY=your_clickup_key
CLICKUP_LIST_ID=your_list_id
```

## API Setup

- **FireCrawl**: Get key at [firecrawl.dev](https://firecrawl.dev)
- **OpenAI**: Get key at [platform.openai.com](https://platform.openai.com)
- **Gmail**: See [GMAIL_OAUTH2_SETUP.md](GMAIL_OAUTH2_SETUP.md)
- **ClickUp**: Get API key from ClickUp Settings > Apps

## Example Response

**Input**: `{"tool": "voice_agent_website_analysis", "arguments": {"url": "https://acmecorp.com"}}`

**Output**: 
> "I've completed a comprehensive analysis of Acme Corp's website. They're in the technology industry. I identified 3 key automation opportunities: 1. Process Automation - 25% time savings on routine operations, 2. AI Customer Service - 60% faster response times, 3. Data Analytics - improved decision making. I've sent a detailed report to their email at contact@acmecorp.com. The analysis has been completed and logged for follow-up."

## Local Development

```bash
git clone https://github.com/ankaravanas/liberators-voice-agent.git
cd liberators-voice-agent
pip install -r requirements.txt
cp .env.example .env  # Edit with your API keys
python voice_agent_mcp_server.py
```

## Testing

```bash
# Test live server
curl -X POST https://web-voice-automation.up.railway.app \
  -H "Content-Type: application/json" \
  -d '{"tool": "voice_agent_website_analysis", "arguments": {"url": "https://liberators.ai"}}'

# Test locally
curl -X POST http://localhost:8000 \
  -H "Content-Type: application/json" \
  -d '{"tool": "voice_agent_website_analysis", "arguments": {"url": "https://liberators.ai"}}'
```

## Files

- `voice_agent_mcp_server.py` - Main server
- `requirements.txt` - Dependencies
- `railway.json` - Railway deployment config
- `VOICE_AGENT_EXAMPLES.md` - Detailed integration examples
- `GMAIL_OAUTH2_SETUP.md` - Gmail setup guide

Railway auto-deploys from GitHub. Just push changes and they go live automatically.

Built for voice agents. Simple, powerful, production-ready.