#!/usr/bin/env python3
"""
Voice Agent MCP Server - Single tool for complete business automation analysis
Combines all functionality into one powerful tool optimized for voice agents
"""

import os
import sys
import re
import json
import requests
import base64
from typing import Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from fastmcp import FastMCP

# Load environment variables
load_dotenv(find_dotenv())

# CORS middleware for web deployment
cors_middleware = Middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=[
        "mcp-protocol-version",
        "mcp-session-id", 
        "Authorization",
        "Content-Type",
        "Accept",
        "X-Requested-With"
    ],
    expose_headers=["mcp-session-id"],
    allow_credentials=False,
)

# Initialize FastMCP server
mcp = FastMCP("voice-agent-automation")

# Global variables for caching last analysis results
_last_html_report = None
_last_company_name = None
_last_analysis_timestamp = None


@mcp.tool()
def voice_agent_website_analysis(url: str) -> str:
    """
    Complete business website analysis optimized for voice agents.
    
    This single tool performs comprehensive business automation analysis:
    1. Analyzes website using FireCrawl v2 API
    2. Extracts business information and contact details  
    3. Uses OpenAI GPT-4o to identify 3 automation opportunities
    4. Generates professional HTML report
    5. Sends report via Gmail API (OAuth2)
    6. Silently captures lead in ClickUp
    7. Returns voice-friendly summary
    
    Perfect for voice agents - simple input (URL), simple output (speaking text).
    All complexity is handled internally with proper error handling.
    
    Args:
        url: The business website URL to analyze
        
    Returns:
        Simple text summary perfect for voice agents to speak to users
    """
    
    try:
        print(f"🔍 Starting analysis for: {url}", file=sys.stderr)
        
        # Step 1: Analyze website with FireCrawl
        crawl_result = firecrawl_analyze_url(url)
        
        if not crawl_result.get('success'):
            return f"I couldn't analyze the website {url}. The site might be down or blocking automated access. Please try a different website or check if the URL is correct."
        
        # Step 2: Extract business data
        business_data = crawl_result.get('data', {})
        business_info = business_data.get('business_info', {})
        company_name = business_info.get('company_name', 'the business')
        emails_found = business_data.get('emails_found', [])
        
        print(f"🏢 Found company: {company_name}", file=sys.stderr)
        
        # Step 3: Generate AI analysis with OpenAI GPT-4o
        print(f"🤖 Generating AI analysis...", file=sys.stderr)
        analysis_result = analyze_and_generate_html_report(crawl_result)
        
        if not analysis_result.get('success'):
            return f"I analyzed the website for {company_name}, but couldn't generate detailed automation recommendations. The basic analysis shows they're in the {business_info.get('industry', 'business')} industry. You might want to try again or contact them directly."
        
        # Step 4: Send email report (if email found)
        html_report = analysis_result.get('html_report', '')
        
        # Cache report data for potential manual email sending
        global _last_html_report, _last_company_name, _last_analysis_timestamp
        _last_html_report = html_report
        _last_company_name = company_name
        _last_analysis_timestamp = datetime.utcnow().isoformat()
        
        email_sent = False
        
        if emails_found and html_report:
            primary_email = emails_found[0]
            print(f"📧 Sending report to {primary_email}", file=sys.stderr)
            email_result = send_html_email(html_report, primary_email, f"AI Automation Opportunities Report - {company_name}")
            email_sent = email_result.get('success', False)
        
        # Step 5: Generate voice-friendly response
        opportunities = analysis_result.get('analysis', {}).get('opportunities', [])
        
        # Create speaking summary
        summary_parts = []
        summary_parts.append(f"I've completed a comprehensive analysis of {company_name}'s website.")
        
        if business_info.get('industry'):
            summary_parts.append(f"They're in the {business_info.get('industry')} industry.")
        
        if len(opportunities) >= 3:
            summary_parts.append("I identified 3 key automation opportunities: ")
            for i, opp in enumerate(opportunities[:3], 1):
                title = opp.get('title', f'Opportunity {i}')
                impact = opp.get('impact', 'significant business benefits')
                summary_parts.append(f"{i}. {title} - {impact}")
        
        if email_sent and emails_found:
            summary_parts.append(f"I've sent a detailed report to their email at {emails_found[0]}.")
        elif emails_found:
            summary_parts.append(f"I found their email {emails_found[0]} but couldn't send the report automatically.")
        else:
            summary_parts.append("I couldn't find any email addresses on their website for automatic report delivery.")
        
        summary_parts.append("The analysis has been completed and logged for follow-up.")
        
        print("✅ Analysis completed successfully", file=sys.stderr)
        return " ".join(summary_parts)
        
    except Exception as e:
        print(f"❌ Voice agent analysis error: {str(e)}", file=sys.stderr)
        return f"I encountered an error while analyzing the website {url}. This could be due to the website being temporarily unavailable or blocking automated access. Please try again in a few minutes or with a different website."


@mcp.tool()
def send_report_to_email(email: str) -> str:
    """
    Send the HTML report from the most recent website analysis to a provided email address.
    
    This tool should be used when the voice agent couldn't find an email during analysis
    but the user has provided one manually. It sends the cached report from the last
    analysis performed by voice_agent_website_analysis.
    
    Args:
        email: The recipient's email address
        
    Returns:
        Simple confirmation message that the report was sent or error message if failed
    """
    
    global _last_html_report, _last_company_name, _last_analysis_timestamp
    
    try:
        # Check if we have a cached report
        if not _last_html_report or not _last_company_name:
            return "No recent analysis report found. Please run the website analysis first before sending a report."
        
        # Send the cached report
        result = send_html_email(
            _last_html_report, 
            email, 
            f"AI Automation Opportunities Report - {_last_company_name}"
        )
        
        if result.get('success'):
            return f"Successfully sent the automation report for {_last_company_name} to {email}."
        else:
            return f"Failed to send the report to {email}. Please check the email address and try again."
            
    except Exception as e:
        print(f"❌ Send report error: {str(e)}", file=sys.stderr)
        return f"An error occurred while sending the report to {email}. Please try again."


def firecrawl_analyze_url(url: str) -> Dict[str, Any]:
    """Analyze a business website using FireCrawl API."""
    
    # FireCrawl v2 API endpoint
    api_url = "https://api.firecrawl.dev/v2/scrape"
    
    # Headers with FireCrawl API key
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {os.getenv('FIRECRAWL_API_KEY')}"
    }
    
    # v2 API payload format
    payload = {
        'url': url,
        'formats': ['markdown'],
        'onlyMainContent': True,
        'timeout': 60000  # 60 seconds
    }
    
    try:
        # Make the API request
        response = requests.post(api_url, json=payload, headers=headers, timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            # v2 API response structure
            if data.get('success'):
                crawl_data = data.get('data', {})
                markdown_content = crawl_data.get('markdown', '')
                metadata = crawl_data.get('metadata', {})
                title = metadata.get('title', '') or crawl_data.get('title', '')
                
                # Extract email addresses
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}\b'
                emails_found = list(set(re.findall(email_pattern, markdown_content)))
                
                # Extract business information
                business_info = extract_business_info(markdown_content, title)
                
                # Silent ClickUp lead capture
                capture_clickup_lead(business_info, url, emails_found)
                
                return {
                    'success': True,
                    'url': url,
                    'timestamp': datetime.utcnow().isoformat(),
                    'data': {
                        'title': title,
                        'content': markdown_content,
                        'emails_found': emails_found,
                        'business_info': business_info,
                        'word_count': len(markdown_content.split())
                    }
                }
            else:
                return {
                    'success': False,
                    'error': f'FireCrawl API returned success=false: {data.get("error", "Unknown error")}',
                    'url': url
                }
        else:
            return {
                'success': False,
                'error': f'FireCrawl API request failed with status {response.status_code}',
                'url': url,
                'response': response.text[:500]
            }
            
    except requests.exceptions.Timeout:
        return {'success': False, 'error': 'Request timed out', 'url': url}
    except Exception as e:
        return {'success': False, 'error': f'Unexpected error: {str(e)}', 'url': url}


def extract_business_info(content: str, title: str) -> Dict[str, Any]:
    """Extract business information from website content."""
    content_lower = content.lower()
    
    # Extract company name from title
    company_name = title.split("-")[0].strip() if title else "Unknown Company"
    
    # Detect industry
    industries = {
        "technology": ["software", "tech", "digital", "app", "platform", "saas", "development"],
        "consulting": ["consulting", "advisory", "strategy", "expert", "professional services"],
        "ecommerce": ["shop", "store", "buy", "sell", "product", "ecommerce", "retail"],
        "healthcare": ["health", "medical", "doctor", "patient", "clinic", "hospital"],
        "finance": ["finance", "banking", "investment", "financial", "accounting"],
        "marketing": ["marketing", "advertising", "campaign", "brand", "promotion", "seo"],
        "education": ["education", "learning", "course", "training", "school"],
        "manufacturing": ["manufacturing", "production", "factory", "supply"]
    }
    
    industry = "general"
    for ind, keywords in industries.items():
        if any(keyword in content_lower for keyword in keywords):
            industry = ind
            break
    
    # Extract services
    services = []
    service_patterns = [
        r"we (provide|offer|deliver|specialize in) ([^.!?]+)",
        r"our services include ([^.!?]+)",
        r"services:([^.!?]+)"
    ]
    
    for pattern in service_patterns:
        matches = re.findall(pattern, content_lower)
        for match in matches:
            if isinstance(match, tuple):
                services.extend([s.strip() for s in match[1].split(",")])
            else:
                services.extend([s.strip() for s in match.split(",")])
    
    # Extract technologies
    tech_keywords = ["ai", "automation", "crm", "erp", "analytics", "cloud", "api", "database"]
    technologies = [tech for tech in tech_keywords if tech in content_lower]
    
    # Extract phone numbers (more conservative patterns)
    phone_patterns = [
        r'\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',  # US format
        r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'  # Simple 10-digit format
    ]
    
    phone_numbers = []
    for pattern in phone_patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            if isinstance(match, tuple):
                phone = ''.join(match)
            else:
                phone = match.strip()
            # Only include if it looks like a real phone number (10-11 digits)
            if phone and 10 <= len(re.sub(r'[^\d]', '', phone)) <= 11:
                phone_numbers.append(phone)
    
    phone_numbers = list(set(phone_numbers))[:2]  # Top 2 unique phone numbers
    
    # Extract addresses (basic patterns)
    address_patterns = [
        r'\d+\s+[A-Za-z0-9\s,.-]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Way|Place|Pl)(?:\s+[A-Za-z0-9\s,.-]+)?',
        r'\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Way|Place|Pl)',
    ]
    
    addresses = []
    for pattern in address_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        addresses.extend([addr.strip() for addr in matches])
    
    addresses = list(set(addresses))[:2]  # Top 2 unique addresses
    
    # Extract person names (conservative patterns to avoid false positives)
    name_patterns = [
        r'(?:CEO|President|Founder|Director|Manager|Owner)[\s:]+([A-Z][a-z]+\s+[A-Z][a-z]+)',
        r'([A-Z][a-z]+\s+[A-Z][a-z]+)[\s,]+(?:CEO|President|Founder|Director|Manager|Owner)',
    ]
    
    person_names = []
    for pattern in name_patterns:
        matches = re.findall(pattern, content)
        for name in matches:
            name = name.strip()
            # Filter out common false positives
            if name and not any(word in name.lower() for word in ['dear', 'business', 'company', 'team', 'staff']):
                person_names.append(name)
    
    person_names = list(set(person_names))[:2]  # Top 2 unique names
    
    return {
        "company_name": company_name,
        "industry": industry,
        "services": services[:5],  # Top 5 services
        "technologies": technologies,
        "phone_numbers": phone_numbers,
        "addresses": addresses,
        "person_names": person_names
    }


def analyze_and_generate_html_report(business_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze business data and generate professional HTML report using OpenAI GPT-4o."""
    
    if not business_data.get('success'):
        return {
            'success': False,
            'error': 'Invalid business data provided - firecrawl_analyze_url must be run first'
        }
    
    try:
        # Extract business information
        data = business_data.get('data', {})
        content = data.get('content', '')
        business_info = data.get('business_info', {})
        company_name = business_info.get('company_name', 'Business')
        
        # Prepare analysis prompt for OpenAI
        analysis_prompt = f"""
You are an expert AI automation consultant. Analyze this business and identify exactly 3 specific AI automation opportunities.

BUSINESS INFORMATION:
- Company: {company_name}
- Industry: {business_info.get('industry', 'General')}
- Services: {', '.join(business_info.get('services', []))}
- Technologies: {', '.join(business_info.get('technologies', []))}

WEBSITE CONTENT ANALYSIS:
{content[:2500]}

ANALYSIS REQUIREMENTS:
Identify exactly 3 AI automation opportunities that are:
- Practical and implementable
- Aligned with their business model
- Focused on ROI within 6-12 months
- Specific to their industry and operations
- Do NOT mention any pricing, costs, or fees in your recommendations

Return ONLY valid JSON in this exact format:
{{
    "opportunities": [
        {{
            "title": "Specific automation solution name",
            "description": "Detailed description of what this automation does",
            "impact": "Specific business benefits and time/cost savings",
            "implementation": "Step-by-step implementation approach with tools",
            "roi_estimate": "Specific ROI calculation and timeframe",
            "priority": "High/Medium/Low"
        }}
    ],
    "overall_assessment": "Business automation readiness assessment",
    "recommended_next_steps": "Specific actionable next steps"
}}
"""
        
        # Call OpenAI API
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            return {'success': False, 'error': 'OPENAI_API_KEY not configured'}
        
        openai_response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {openai_api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'gpt-4o',
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are an expert AI automation consultant. Provide detailed, practical automation recommendations in valid JSON format only.'
                    },
                    {
                        'role': 'user',
                        'content': analysis_prompt
                    }
                ],
                'temperature': 0.7,
                'max_tokens': 2000
            },
            timeout=60
        )
        
        if openai_response.status_code != 200:
            return {
                'success': False,
                'error': f'OpenAI API failed: {openai_response.status_code}',
                'details': openai_response.text
            }
        
        # Parse OpenAI response
        ai_result = openai_response.json()
        ai_content = ai_result.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        # Extract JSON from AI response
        try:
            json_start = ai_content.find('{')
            json_end = ai_content.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                analysis_data = json.loads(ai_content[json_start:json_end])
            else:
                raise ValueError("No valid JSON found in AI response")
        except (json.JSONDecodeError, ValueError):
            # Fallback analysis
            analysis_data = {
                "opportunities": [
                    {
                        "title": "Process Automation Implementation",
                        "description": "Automate repetitive manual processes to improve efficiency",
                        "impact": "25-35% time savings on routine operations",
                        "implementation": "Workflow automation tools and custom integrations",
                        "roi_estimate": "3-6 months payback period",
                        "priority": "High"
                    },
                    {
                        "title": "AI-Powered Customer Service",
                        "description": "Implement intelligent chatbots and automated support systems",
                        "impact": "24/7 availability with 60% faster response times",
                        "implementation": "AI chatbot platform with existing system integration",
                        "roi_estimate": "Immediate cost savings on support staff",
                        "priority": "Medium"
                    },
                    {
                        "title": "Automated Data Analytics",
                        "description": "Real-time business intelligence and automated reporting",
                        "impact": "Data-driven decision making and trend identification",
                        "implementation": "Analytics platform with automated dashboards",
                        "roi_estimate": "6-12 months strategic value",
                        "priority": "Medium"
                    }
                ],
                "overall_assessment": "Strong potential for AI automation implementation with multiple high-impact opportunities",
                "recommended_next_steps": "Begin with process mapping and prioritize highest-ROI automation opportunities"
            }
        
        # Generate HTML report
        html_report = generate_html_report(analysis_data, business_info, business_data.get('url', ''))
        
        return {
            'success': True,
            'timestamp': datetime.utcnow().isoformat(),
            'business_url': business_data.get('url', ''),
            'company_name': company_name,
            'analysis': analysis_data,
            'html_report': html_report,
            'report_size_kb': len(html_report.encode('utf-8')) / 1024
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Analysis failed: {str(e)}',
            'timestamp': datetime.utcnow().isoformat()
        }


def generate_html_report(analysis: Dict[str, Any], business_info: Dict[str, Any], url: str) -> str:
    """Generate professional HTML report."""
    company_name = business_info.get('company_name', 'Business')
    opportunities = analysis.get('opportunities', [])
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Automation Opportunities Report - {company_name}</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #333; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%); color: white; padding: 40px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 2.2em; font-weight: 300; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
        .content {{ padding: 40px; }}
        .business-summary {{ background: #f8f9fa; padding: 25px; border-radius: 10px; margin-bottom: 30px; border-left: 5px solid #3498db; }}
        .business-summary h2 {{ color: #2c3e50; margin-top: 0; }}
        .opportunity {{ border: 1px solid #e0e0e0; border-radius: 10px; padding: 25px; margin: 20px 0; background: white; box-shadow: 0 3px 10px rgba(0,0,0,0.1); }}
        .opportunity h3 {{ color: #2c3e50; margin-top: 0; border-bottom: 2px solid #3498db; padding-bottom: 8px; }}
        .priority {{ display: inline-block; padding: 4px 12px; border-radius: 15px; font-size: 0.85em; font-weight: bold; margin-bottom: 15px; }}
        .high {{ background: #e74c3c; color: white; }}
        .medium {{ background: #f39c12; color: white; }}
        .low {{ background: #95a5a6; color: white; }}
        .metric {{ background: #ecf0f1; padding: 12px; border-radius: 6px; margin: 10px 0; }}
        .metric strong {{ color: #2c3e50; }}
        .assessment {{ background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%); color: white; padding: 25px; border-radius: 10px; margin: 25px 0; }}
        .next-steps {{ background: #d5f4e6; border: 1px solid #27ae60; border-radius: 10px; padding: 20px; margin-top: 25px; }}
        .next-steps h3 {{ color: #27ae60; margin-top: 0; }}
        .footer {{ background: #2c3e50; color: white; text-align: center; padding: 20px; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AI Automation Opportunities Report</h1>
            <p>Comprehensive Analysis for {company_name}</p>
            <p>Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <div class="content">
            <div class="business-summary">
                <h2>Business Overview</h2>
                <p><strong>Company:</strong> {company_name}</p>
                <p><strong>Industry:</strong> {business_info.get('industry', 'General').title()}</p>
                <p><strong>Website:</strong> {url}</p>
                <p><strong>Services:</strong> {', '.join(business_info.get('services', ['Not specified']))}</p>
                <p><strong>Technologies:</strong> {', '.join(business_info.get('technologies', ['Not specified']))}</p>
            </div>
            
            <div class="assessment">
                <h2>Overall Assessment</h2>
                <p>{analysis.get('overall_assessment', 'This business shows strong potential for AI automation implementation.')}</p>
            </div>
            
            <h2>AI Automation Opportunities</h2>"""
    
    # Add each opportunity
    for i, opp in enumerate(opportunities, 1):
        priority_class = opp.get('priority', 'Medium').lower()
        html += f"""
            <div class="opportunity">
                <h3>{i}. {opp.get('title', 'Automation Opportunity')}</h3>
                <span class="priority {priority_class}">{opp.get('priority', 'Medium')} Priority</span>
                
                <div class="metric">
                    <strong>Description:</strong> {opp.get('description', 'No description provided')}
                </div>
                <div class="metric">
                    <strong>Expected Impact:</strong> {opp.get('impact', 'Positive business impact expected')}
                </div>
                <div class="metric">
                    <strong>Implementation:</strong> {opp.get('implementation', 'Custom implementation approach')}
                </div>
                <div class="metric">
                    <strong>ROI Estimate:</strong> {opp.get('roi_estimate', 'ROI analysis needed')}
                </div>
            </div>"""
    
    html += f"""
            <div class="next-steps">
                <h3>Recommended Next Steps</h3>
                <p>{analysis.get('recommended_next_steps', 'Contact our automation specialists to discuss implementation.')}</p>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>Liberators AI</strong> - Your Business, Automated with AI</p>
            <p>Contact us: <a href="mailto:andreas@liberators.ai" style="color: #74b9ff;">andreas@liberators.ai</a> | Visit: <a href="https://liberators.ai" style="color: #74b9ff;">liberators.ai</a></p>
            <p style="font-size: 0.8em; margin-top: 15px;">Report generated: {datetime.utcnow().strftime('%B %d, %Y at %I:%M %p UTC')}</p>
        </div>
    </div>
</body>
</html>"""
    
    return html


def send_html_email(html_report: str, recipient_email: str, subject: str = "AI Automation Opportunities Report") -> Dict[str, Any]:
    """Send HTML email report via Gmail API using OAuth2."""
    
    if not html_report or not recipient_email:
        return {
            'success': False,
            'error': 'html_report and recipient_email are required'
        }
    
    try:
        # Gmail OAuth2 configuration
        gmail_user = os.getenv('GMAIL_USER')
        client_id = os.getenv('GMAIL_CLIENT_ID')
        client_secret = os.getenv('GMAIL_CLIENT_SECRET')
        refresh_token = os.getenv('GMAIL_REFRESH_TOKEN')
        
        if not all([gmail_user, client_id, client_secret, refresh_token]):
            return {
                'success': False,
                'error': 'Gmail OAuth2 credentials not configured. Set GMAIL_USER, GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, and GMAIL_REFRESH_TOKEN'
            }
        
        # Get access token using OAuth2 credentials
        token_response = requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'client_id': client_id,
                'client_secret': client_secret,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token'
            },
            timeout=30
        )
        
        if token_response.status_code != 200:
            return {
                'success': False,
                'error': f'OAuth2 token refresh failed: {token_response.text[:200]}'
            }
        
        access_token = token_response.json().get('access_token')
        
        # Create email message for Gmail API
        email_content = f"""To: {recipient_email}
From: Andreas from Liberators AI <{gmail_user}>
Subject: {subject}
Content-Type: text/html; charset=utf-8

{html_report}"""
        
        # Encode email for Gmail API
        encoded_message = base64.urlsafe_b64encode(email_content.encode('utf-8')).decode('utf-8')
        
        # Send via Gmail API using OAuth2 access token
        gmail_response = requests.post(
            'https://gmail.googleapis.com/gmail/v1/users/me/messages/send',
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            },
            json={'raw': encoded_message},
            timeout=30
        )
        
        if gmail_response.status_code == 200:
            gmail_data = gmail_response.json()
            return {
                'success': True,
                'timestamp': datetime.utcnow().isoformat(),
                'recipient': recipient_email,
                'subject': subject,
                'message_id': gmail_data.get('id', ''),
                'method': 'Gmail API',
                'report_size_kb': len(html_report.encode('utf-8')) / 1024
            }
        else:
            return {
                'success': False,
                'error': f'Gmail API failed: {gmail_response.status_code} - {gmail_response.text[:200]}',
                'timestamp': datetime.utcnow().isoformat(),
                'recipient': recipient_email
            }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Gmail API error: {str(e)}',
            'timestamp': datetime.utcnow().isoformat(),
            'recipient': recipient_email
        }


def capture_clickup_lead(business_info: Dict[str, Any], url: str, emails_found: List[str] = None) -> None:
    """Silently capture lead in ClickUp with detailed information and custom fields."""
    try:
        clickup_api_key = os.getenv('CLICKUP_API_KEY')
        clickup_list_id = os.getenv('CLICKUP_LIST_ID')
        if clickup_api_key and clickup_list_id:
            
            # Build detailed description
            company_name = business_info.get('company_name', 'Unknown Business')
            industry = business_info.get('industry', 'Unknown')
            services = business_info.get('services', [])
            technologies = business_info.get('technologies', [])
            
            description_parts = [
                f"🚀 Lead from Voice Agent AI automation analysis",
                f"📅 Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
                f"🌐 Website: {url}",
                f"🏢 Industry: {industry.title()}",
            ]
            
            if services:
                description_parts.append(f"⚙️ Services: {', '.join(services[:3])}")
            
            if technologies:
                description_parts.append(f"💻 Technologies: {', '.join(technologies)}")
            
            if emails_found:
                description_parts.append(f"📧 Emails Found: {', '.join(emails_found[:2])}")
            
            if business_info.get('phone_numbers'):
                description_parts.append(f"📞 Phone Numbers: {', '.join(business_info['phone_numbers'][:2])}")
            
            if business_info.get('addresses'):
                description_parts.append(f"📍 Addresses: {', '.join(business_info['addresses'][:1])}")
            
            if business_info.get('person_names'):
                description_parts.append(f"👤 Contact Names: {', '.join(business_info['person_names'][:2])}")
            
            description = '\n'.join(description_parts)
            
            # Prepare custom fields
            custom_fields = []
            
            # Website field
            custom_fields.append({
                "id": "a2c503df-2704-4819-92d8-80d6402e447d",
                "value": url
            })
            
            # Email field (first email found)
            if emails_found:
                custom_fields.append({
                    "id": "5b234a2d-29d0-4dc0-8270-55c068506971", 
                    "value": emails_found[0]
                })
            
            # Business Address field (first address found)
            if business_info.get('addresses'):
                custom_fields.append({
                    "id": "f2e60192-4b43-4a70-a341-fdc297f18813",
                    "value": business_info['addresses'][0]
                })
            
            # Phone Number field (first phone found)
            if business_info.get('phone_numbers'):
                custom_fields.append({
                    "id": "f693c583-6831-460c-a642-47752992a321",
                    "value": business_info['phone_numbers'][0]
                })
            
            # Person Name field (first person found)
            if business_info.get('person_names'):
                custom_fields.append({
                    "id": "066ba11b-4d1e-4fa0-ade7-897f0d5e912d",
                    "value": business_info['person_names'][0]
                })
            
            # Build task data
            task_data = {
                'name': company_name,
                'description': description
            }
            
            # Add custom fields if any were found
            if custom_fields:
                task_data['custom_fields'] = custom_fields
            
            response = requests.post(
                f'https://api.clickup.com/api/v2/list/{clickup_list_id}/task',
                headers={
                    'Authorization': clickup_api_key,
                    'Content-Type': 'application/json'
                },
                json=task_data,
                timeout=15
            )
            
            # Silent operation - only log to Railway logs for debugging, never visible to user
            if response.status_code == 200:
                # Success - completely silent to user
                pass
            else:
                # Log error details only to Railway logs (stderr) for debugging
                print(f"ClickUp API Error {response.status_code}: {response.text}", file=sys.stderr)
                print(f"Task data sent: {json.dumps(task_data, indent=2)}", file=sys.stderr)
            
    except Exception as e:
        # Log exception only to Railway logs for debugging
        print(f"ClickUp Exception: {str(e)}", file=sys.stderr)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    mcp.run(transport="streamable-http", port=port, host="0.0.0.0", middleware=[cors_middleware])