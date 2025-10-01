# 🔐 Databricks Authentication Troubleshooting

If you're seeing "No valid authentication settings!" error, here's how to fix it:

## 🚨 Quick Fix

The chatbot will work in **offline mode** even without Databricks authentication, but for full AI capabilities, follow these steps:

### Option 1: Re-authenticate with Databricks
```bash
# Re-authenticate with your Databricks workspace
databricks auth login --host https://e2-demo-field-eng.cloud.databricks.com
```

### Option 2: Check Current Authentication
```bash
# Check if you're already authenticated
databricks auth profiles
```

### Option 3: Use Personal Access Token
```bash
# If CLI auth isn't working, use a personal access token
databricks auth login --host https://e2-demo-field-eng.cloud.databricks.com --token
```

## 🔍 What's Happening

The chatbot tries to use Databricks native Claude via SQL queries, but needs proper authentication to access your Databricks workspace.

## ✅ Current Status

- **App is running** ✅ - Use the URL provided by Databricks
- **Chatbot UI is working** ✅ - Click "AI Assistant" button
- **Offline mode active** ⚠️ - Limited responses without Databricks auth
- **Full AI mode** ❌ - Requires Databricks authentication

## 🎯 Benefits of Fixing Authentication

- **Full Claude AI responses** - Powered by Claude-3-Sonnet
- **Context-aware analysis** - Understands your uploaded data
- **Advanced actuarial insights** - Specialized for insurance pricing
- **Real-time processing** - No API rate limits

## 🛠️ Alternative: Use External Claude API

If Databricks authentication continues to be problematic, you can switch to external Claude API:

1. Get API key from https://console.anthropic.com/
2. Set environment variable: `export ANTHROPIC_API_KEY='your-key'`
3. Modify `claude_integration.py` to use external API

## 📞 Need Help?

The chatbot will still provide helpful responses in offline mode, but for the full AI experience, ensure your Databricks authentication is working properly.

