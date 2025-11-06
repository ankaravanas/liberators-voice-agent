# 🎙️ Voice Agent Integration Examples

**Live Server**: https://web-voice-automation.up.railway.app

## Complete Integration Examples

### vAPI (Voice AI Platform)

```json
{
  "model": {
    "provider": "openai",
    "model": "gpt-4",
    "messages": [
      {
        "role": "system",
        "content": "You are a business automation consultant. When users ask you to analyze a website, use the analyze_website function to provide comprehensive automation recommendations."
      }
    ],
    "functions": [
      {
        "name": "analyze_website",
        "description": "Analyze a business website for AI automation opportunities and send detailed report",
        "parameters": {
          "type": "object",
          "properties": {
            "url": {
              "type": "string",
              "description": "The business website URL to analyze (e.g., https://example.com)"
            }
          },
          "required": ["url"]
        },
        "server": {
          "url": "https://web-voice-automation.up.railway.app",
          "method": "POST"
        }
      }
    ]
  },
  "voice": {
    "provider": "11labs",
    "voiceId": "21m00Tcm4TlvDq8ikWAM"
  },
  "firstMessage": "Hi! I'm an AI automation consultant. I can analyze any business website and identify specific automation opportunities. Just give me a website URL and I'll provide a comprehensive analysis!"
}
```

### Bland AI Integration

```python
import requests
import json

class BusinessAutomationAgent:
    def __init__(self):
        self.mcp_server = "https://web-voice-automation.up.railway.app"
    
    def analyze_website_for_automation(self, url: str) -> str:
        """
        Analyze a business website for automation opportunities
        """
        try:
            response = requests.post(
                self.mcp_server,
                json={
                    "tool": "voice_agent_website_analysis",
                    "arguments": {"url": url}
                },
                timeout=120  # 2 minutes for complete analysis
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('result', 'Analysis completed successfully')
            else:
                return f"I couldn't analyze that website. Please check the URL and try again."
                
        except Exception as e:
            return f"I encountered an error analyzing the website. Please try again in a moment."

# Bland AI webhook handler
def handle_bland_webhook(request):
    agent = BusinessAutomationAgent()
    
    # Extract URL from user's speech
    user_message = request.json.get('transcript', '')
    
    # Simple URL extraction (you might want more sophisticated parsing)
    import re
    url_pattern = r'https?://[^\s]+|www\.[^\s]+|[^\s]+\.[a-z]{2,}'
    urls = re.findall(url_pattern, user_message.lower())
    
    if urls:
        url = urls[0]
        if not url.startswith('http'):
            url = f"https://{url}"
        
        result = agent.analyze_website_for_automation(url)
        return {"response": result}
    else:
        return {"response": "Please provide a website URL for me to analyze. For example, say 'analyze liberators.ai' or 'check out example.com'"}
```

### Retell AI Integration

```javascript
// Retell AI function for business website analysis
async function analyzeBusinessWebsite(args) {
    const { url } = args;
    
    try {
        const response = await fetch('https://web-voice-automation.up.railway.app', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tool: 'voice_agent_website_analysis',
                arguments: { url: url }
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            return result.result || 'Website analysis completed successfully.';
        } else {
            return 'I had trouble analyzing that website. Please check the URL and try again.';
        }
    } catch (error) {
        console.error('Analysis error:', error);
        return 'I encountered an error during the analysis. Please try again in a moment.';
    }
}

// Retell AI configuration
const retellConfig = {
    agent_name: "Business Automation Consultant",
    voice_id: "11labs-voice-id",
    language: "en-US",
    response_engine: {
        type: "retell-llm",
        llm_websocket_url: "wss://your-websocket-url",
    },
    functions: [
        {
            name: "analyze_website",
            description: "Analyze a business website for automation opportunities",
            parameters: {
                type: "object",
                properties: {
                    url: {
                        type: "string",
                        description: "Website URL to analyze"
                    }
                },
                required: ["url"]
            },
            handler: analyzeBusinessWebsite
        }
    ],
    begin_message: "Hello! I'm your AI automation consultant. I can analyze any business website and identify specific opportunities for AI automation. Just give me a website URL to get started!"
};
```

### Custom Voice Agent (Python)

```python
import asyncio
import websockets
import json
import requests
from typing import Dict, Any

class VoiceAutomationAgent:
    def __init__(self):
        self.mcp_server = "https://web-voice-automation.up.railway.app"
        self.system_prompt = """
        You are an expert AI automation consultant. When users provide website URLs,
        use the website analysis tool to provide comprehensive automation recommendations.
        Speak in a friendly, professional tone suitable for business conversations.
        """
    
    async def handle_voice_input(self, websocket, path):
        """Handle incoming voice requests"""
        async for message in websocket:
            try:
                data = json.loads(message)
                
                if data.get('type') == 'analyze_website':
                    url = data.get('url')
                    result = await self.analyze_website(url)
                    
                    response = {
                        'type': 'analysis_result',
                        'result': result,
                        'timestamp': data.get('timestamp')
                    }
                    
                    await websocket.send(json.dumps(response))
                    
            except Exception as e:
                error_response = {
                    'type': 'error',
                    'message': f'Sorry, I encountered an error: {str(e)}'
                }
                await websocket.send(json.dumps(error_response))
    
    async def analyze_website(self, url: str) -> str:
        """Analyze website using MCP server"""
        try:
            response = requests.post(
                self.mcp_server,
                json={
                    "tool": "voice_agent_website_analysis",
                    "arguments": {"url": url}
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('result', 'Analysis completed')
            else:
                return "I couldn't analyze that website. Please try a different URL."
                
        except Exception as e:
            return "I encountered an error during analysis. Please try again."
    
    def start_server(self, host='localhost', port=8765):
        """Start the voice agent WebSocket server"""
        print(f"Starting voice automation agent on {host}:{port}")
        start_server = websockets.serve(self.handle_voice_input, host, port)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    agent = VoiceAutomationAgent()
    agent.start_server()
```

## Voice Agent Conversation Examples

### Example 1: Business Website Analysis

**User**: "Can you analyze the website liberators.ai for automation opportunities?"

**Voice Agent Response**: "I've completed a comprehensive analysis of Liberators AI's website. They're in the technology industry. I identified 3 key automation opportunities: 1. AI-Powered Lead Qualification - automated prospect scoring and routing with 40% faster response times, 2. Intelligent Content Personalization - dynamic website content based on visitor behavior with 25% higher conversion rates, 3. Automated Client Onboarding - streamlined project setup and documentation with 60% time savings. I've sent a detailed report to their email at contact@liberators.ai. The analysis has been completed and logged for follow-up."

### Example 2: E-commerce Site Analysis

**User**: "Check out shopify.com and tell me about automation possibilities"

**Voice Agent Response**: "I've analyzed Shopify's website and identified excellent automation opportunities. They're in the e-commerce platform industry. Here are 3 key automation opportunities: 1. Smart Inventory Management - AI-powered stock optimization and reorder automation with 30% reduction in stockouts, 2. Automated Customer Support - intelligent chatbots for common queries with 24/7 availability and 70% faster resolution times, 3. Dynamic Pricing Optimization - real-time price adjustments based on market conditions with 15-20% revenue increase potential. I found their business email and sent a comprehensive report. The lead has been captured for follow-up discussions."

### Example 3: Error Handling

**User**: "Analyze invalidwebsite123.com"

**Voice Agent Response**: "I couldn't analyze the website invalidwebsite123.com. The site might be down or blocking automated access. Please check if the URL is correct and try again, or provide a different website for analysis."

## Integration Tips

### 1. URL Extraction from Speech
```python
import re

def extract_url_from_speech(text: str) -> str:
    """Extract URL from user speech"""
    # Remove common speech patterns
    text = text.lower()
    text = re.sub(r'\b(analyze|check|look at|visit)\b', '', text)
    
    # Find URL patterns
    url_patterns = [
        r'https?://[^\s]+',
        r'www\.[^\s]+',
        r'[a-zA-Z0-9-]+\.[a-z]{2,}(?:/[^\s]*)?'
    ]
    
    for pattern in url_patterns:
        urls = re.findall(pattern, text)
        if urls:
            url = urls[0].strip('.,!?')
            if not url.startswith('http'):
                url = f"https://{url}"
            return url
    
    return None
```

### 2. Response Processing
```python
def format_for_voice(analysis_result: str) -> str:
    """Format analysis result for voice output"""
    # Remove technical jargon
    # Add pauses for better speech flow
    # Highlight key numbers and benefits
    
    formatted = analysis_result.replace('AI automation', 'A I automation')
    formatted = formatted.replace('%', ' percent')
    formatted = formatted.replace('24/7', 'twenty four seven')
    
    return formatted
```

### 3. Error Handling for Voice
```python
def get_voice_friendly_error(error_type: str) -> str:
    """Return voice-friendly error messages"""
    errors = {
        'invalid_url': "I couldn't access that website. Please check the URL and try again.",
        'timeout': "The analysis is taking longer than expected. Please try again in a moment.",
        'api_error': "I'm having trouble with the analysis right now. Please try again shortly.",
        'no_content': "I couldn't find enough content on that website to analyze. Please try a different site."
    }
    
    return errors.get(error_type, "I encountered an unexpected error. Please try again.")
```

## Testing Your Integration

### Quick Test Script
```python
import requests

def test_voice_agent_integration():
    """Test the MCP server integration"""
    
    test_url = "https://liberators.ai"
    
    try:
        response = requests.post(
            "https://web-voice-automation.up.railway.app",
            json={
                "tool": "voice_agent_website_analysis",
                "arguments": {"url": test_url}
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Integration working!")
            print(f"Response: {result.get('result', 'No result')[:200]}...")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_voice_agent_integration()
```

## Production Considerations

### Rate Limiting
- The MCP server handles one analysis at a time per request
- Consider implementing queuing for high-volume voice agents
- Monitor Railway usage and scaling

### Response Times
- Full analysis takes 30-120 seconds
- Voice agents should inform users about processing time
- Consider timeout handling (2-3 minutes max)

### Error Recovery
- Always provide fallback responses
- Log errors for debugging
- Graceful degradation when APIs are unavailable

### Voice Optimization
- Format numbers and percentages for speech
- Use natural language patterns
- Add appropriate pauses in long responses
- Test with actual voice synthesis

Your voice agent is now ready to provide powerful business automation analysis! 🎉
