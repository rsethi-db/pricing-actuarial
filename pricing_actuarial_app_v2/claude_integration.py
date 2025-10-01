"""
Claude integration for the pricing actuarial app chatbot using Databricks native Claude.
"""
import os
import logging
from typing import Optional, List, Dict, Any
from databricks import sql
from config import app_config

logger = logging.getLogger(__name__)

class ClaudeChatbot:
    """Claude-powered chatbot for pricing actuarial assistance using Databricks native Claude."""
    
    def __init__(self):
        """Initialize the Claude chatbot using Databricks connection."""
        self.connection = None
        self.cursor = None
        self.conversation_history: List[Dict[str, str]] = []
        self.connection_error = None
        
        try:
            # Try to get token from environment variable first, then from config
            token = os.getenv('DATABRICKS_TOKEN')
            if not token:
                token = app_config.databricks_config.token
            
            # Use Databricks configuration with token
            self.connection = sql.connect(
                server_hostname=app_config.databricks_host,
                http_path=app_config.warehouse_http_path,
                access_token=token
            )
            self.cursor = self.connection.cursor()
            logger.info("Claude chatbot initialized with Databricks connection using token")
        except Exception as e:
            logger.error(f"Failed to initialize Databricks connection: {e}")
            self.connection_error = str(e)
            # Don't raise - allow chatbot to work in fallback mode
        
        # System prompt for pricing actuarial context
        self.system_prompt = """You are an AI assistant specialized in insurance pricing and actuarial analysis. 
        You help users understand:
        - Insurance product pricing methodologies
        - Actuarial concepts and calculations
        - Risk assessment and underwriting
        - Data analysis and statistical modeling
        - Regulatory compliance in insurance
        - Product feature analysis and pricing strategies
        
        You should:
        - Provide clear, accurate explanations of actuarial concepts
        - Help interpret pricing data and trends
        - Suggest analytical approaches for insurance products
        - Explain complex statistical and mathematical concepts in accessible terms
        - Be helpful with data analysis questions
        - Always recommend consulting with qualified actuaries for critical decisions
        
        Keep responses concise but comprehensive, and use examples when helpful."""
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history."""
        self.conversation_history.append({"role": role, "content": content})
        
        # Keep only last 20 messages to manage context length
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
    
    def get_response(self, user_message: str, context_data: Optional[Dict[str, Any]] = None) -> str:
        """Get a response from Claude for the user message using Databricks native Claude."""
        try:
            # Add user message to history
            self.add_message("user", user_message)
            
            # Check if Databricks connection is available
            if not self.connection or not self.cursor:
                return self._get_fallback_response(user_message, context_data)
            
            # Prepare context information if available
            context_info = ""
            if context_data:
                context_info = f"\n\nCurrent context:\n"
                if 'uploaded_files' in context_data:
                    context_info += f"Uploaded files: {context_data['uploaded_files']}\n"
                if 'analysis_results' in context_data:
                    context_info += f"Analysis results available: {context_data['analysis_results']}\n"
                if 'current_step' in context_data:
                    context_info += f"Current analysis step: {context_data['current_step']}\n"
            
            # Prepare the full prompt for Claude
            full_prompt = f"{self.system_prompt}\n\nUser question: {user_message}{context_info}"
            
            # Use Databricks custom OpenAI function
            query = f"""
            SELECT hive_metastore.default.openai_chatgpt(
                '{full_prompt}'
            ) as response
            """
            
            # Execute the query
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            
            if result and result[0]:
                assistant_message = result[0]
                self.add_message("assistant", assistant_message)
                return assistant_message
            else:
                raise Exception("No response received from Claude")
            
        except Exception as e:
            logger.error(f"Error getting Claude response: {e}")
            return self._get_fallback_response(user_message, context_data)
    
    def _get_fallback_response(self, user_message: str, context_data: Optional[Dict[str, Any]] = None) -> str:
        """Provide a sophisticated fallback response with detailed actuarial knowledge."""
        # Add user message to history
        self.add_message("user", user_message)
        
        user_lower = user_message.lower()
        
        # Comprehensive actuarial knowledge base
        if any(word in user_lower for word in ["actuary", "actuaries", "actuarial"]):
            assistant_message = """WHAT ACTUARIES DO IN INSURANCE PRICING:

Actuaries are mathematical professionals who play a crucial role in insurance pricing by:

1. RISK ASSESSMENT & MODELING
   • Analyze historical data to predict future claims
   • Develop statistical models for mortality, morbidity, and other risks
   • Quantify uncertainty and volatility in insurance products
   • Create risk profiles for different customer segments

2. PREMIUM CALCULATION
   • Set competitive yet profitable premium rates
   • Ensure premiums cover expected claims, expenses, and profit margins
   • Develop pricing models based on risk factors (age, health, location, etc.)
   • Balance affordability with financial stability

3. PRODUCT DEVELOPMENT
   • Design new insurance products and coverage options
   • Analyze market trends and customer needs
   • Test product viability through actuarial modeling
   • Ensure regulatory compliance in product design

4. FINANCIAL FORECASTING
   • Project future cash flows and liabilities
   • Calculate reserves needed to pay future claims
   • Perform stress testing and scenario analysis
   • Ensure solvency and regulatory compliance

5. DATA ANALYSIS & INSIGHTS
   • Interpret complex datasets to identify trends
   • Develop predictive models for claims forecasting
   • Analyze customer behavior and risk patterns
   • Provide data-driven recommendations to management

KEY SKILLS: Advanced mathematics, statistics, programming (R/Python/SQL), business acumen, and strong communication skills.

Would you like me to explain any specific aspect of actuarial work in more detail?"""

        elif any(word in user_lower for word in ["pricing", "price", "premium", "rate"]):
            assistant_message = """INSURANCE PRICING METHODOLOGIES:

1. RISK-BASED PRICING
   • Individual risk assessment using multiple factors
   • Statistical modeling to predict claim likelihood
   • Segmentation of customers by risk profile
   • Dynamic pricing based on real-time data

2. ACTUARIAL MODELS
   • MORTALITY TABLES: Life insurance pricing based on death probabilities
   • LOSS RATIOS: Property/casualty pricing using historical loss data
   • FREQUENCY/SEVERITY MODELS: Predicting claim frequency and average cost
   • CREDIBILITY THEORY: Combining internal and external data

3. KEY PRICING FACTORS
   • DEMOGRAPHICS: Age, gender, location, occupation
   • HEALTH STATUS: Medical history, lifestyle factors
   • COVERAGE AMOUNT: Sum insured and benefit levels
   • POLICY TERMS: Deductibles, exclusions, waiting periods

4. PRICING TECHNIQUES
   • EXPERIENCE RATING: Using company's own claims history
   • COMMUNITY RATING: Same price for similar risk profiles
   • MANUAL RATING: Individual assessment for complex risks
   • CREDIBILITY ADJUSTMENTS: Weighting different data sources

5. REGULATORY CONSIDERATIONS
   • Rate filing requirements and approval processes
   • Anti-discrimination laws and fair pricing practices
   • Solvency requirements and capital adequacy
   • Consumer protection and transparency standards

Would you like me to dive deeper into any specific pricing methodology?"""

        elif any(word in user_lower for word in ["risk", "assessment", "underwriting"]):
            assistant_message = """RISK ASSESSMENT IN INSURANCE:

1. RISK IDENTIFICATION
   • MORAL HAZARD: Behavioral changes after purchasing insurance
   • ADVERSE SELECTION: Higher-risk individuals more likely to buy
   • SYSTEMIC RISK: Market-wide factors affecting all policies
   • OPERATIONAL RISK: Internal processes and controls

2. RISK QUANTIFICATION
   • PROBABILITY ANALYSIS: Likelihood of claims occurring
   • SEVERITY ASSESSMENT: Potential financial impact of claims
   • CORRELATION ANALYSIS: How different risks interact
   • STRESS TESTING: Performance under extreme scenarios

3. UNDERWRITING PROCESS
   • APPLICATION REVIEW: Detailed risk assessment
   • MEDICAL UNDERWRITING: Health status evaluation
   • FINANCIAL UNDERWRITING: Income and asset verification
   • RISK CLASSIFICATION: Categorizing applicants by risk level

4. RISK MANAGEMENT TOOLS
   • DIVERSIFICATION: Spreading risk across different segments
   • REINSURANCE: Transferring risk to other insurers
   • RESERVES: Setting aside funds for future claims
   • RISK CONTROLS: Implementing safety measures

5. DATA-DRIVEN RISK ASSESSMENT
   • PREDICTIVE MODELING: Using historical data to predict future claims
   • MACHINE LEARNING: Advanced algorithms for risk scoring
   • REAL-TIME MONITORING: Continuous risk assessment
   • FRAUD DETECTION: Identifying suspicious claims and applications

Would you like me to explain any specific aspect of risk assessment?"""

        elif any(word in user_lower for word in ["hello", "hi", "help", "assist"]):
            assistant_message = """HELLO! I'M YOUR AI PRICING ASSISTANT 🤖

I'm here to help you with all aspects of insurance pricing and actuarial analysis. While I'm currently running in enhanced offline mode, I can provide comprehensive guidance on:

📊 ACTUARIAL ANALYSIS
   • Statistical modeling and risk assessment
   • Mortality and morbidity analysis
   • Reserve calculations and financial forecasting
   • Regulatory compliance and reporting

💰 INSURANCE PRICING
   • Risk-based pricing methodologies
   • Premium calculation techniques
   • Product development and pricing strategies
   • Market analysis and competitive positioning

📈 DATA ANALYSIS
   • Statistical techniques and modeling
   • Predictive analytics and forecasting
   • Data interpretation and insights
   • Performance measurement and monitoring

🔍 RISK MANAGEMENT
   • Underwriting processes and guidelines
   • Risk assessment and classification
   • Fraud detection and prevention
   • Portfolio management and optimization

HOW CAN I HELP YOU TODAY? Feel free to ask about any specific topic, and I'll provide detailed, professional guidance tailored to your needs."""

        else:
            assistant_message = f"""I UNDERSTAND YOU'RE ASKING ABOUT: "{user_message}"

I'm your specialized AI assistant for insurance pricing and actuarial analysis. While I'm currently running in enhanced offline mode, I can provide comprehensive guidance on a wide range of topics including:

🎯 WHAT I CAN HELP WITH:
   • ACTUARIAL CONCEPTS: Mortality tables, loss ratios, credibility theory
   • PRICING METHODOLOGIES: Risk-based pricing, experience rating, manual rating
   • RISK ASSESSMENT: Underwriting, risk classification, portfolio management
   • DATA ANALYSIS: Statistical modeling, predictive analytics, performance metrics
   • REGULATORY COMPLIANCE: Rate filings, solvency requirements, reporting standards
   • PRODUCT DEVELOPMENT: New product design, market analysis, competitive strategies

💡 PRO TIPS:
   • Ask specific questions for detailed explanations
   • Request examples or case studies for complex concepts
   • Inquire about best practices and industry standards
   • Ask for step-by-step processes or methodologies

WHAT SPECIFIC ASPECT WOULD YOU LIKE ME TO EXPLAIN IN DETAIL? I'm here to provide professional, comprehensive guidance tailored to your needs."""

        self.add_message("assistant", assistant_message)
        return assistant_message
    
    def reset_conversation(self) -> None:
        """Reset the conversation history."""
        self.conversation_history = []
        logger.info("Conversation history reset")
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the current conversation."""
        if not self.conversation_history:
            return "No conversation history available."
        
        user_messages = [msg["content"] for msg in self.conversation_history if msg["role"] == "user"]
        return f"Conversation has {len(user_messages)} user messages covering topics like: {', '.join(user_messages[:3])}"

# Global chatbot instance
chatbot_instance = None

def get_chatbot() -> ClaudeChatbot:
    """Get or create the global chatbot instance."""
    global chatbot_instance
    if chatbot_instance is None:
        try:
            chatbot_instance = ClaudeChatbot()
            logger.info("Claude chatbot initialized successfully with Databricks")
        except Exception as e:
            logger.error(f"Failed to initialize Claude chatbot: {e}")
            raise
    return chatbot_instance

def reset_chatbot() -> None:
    """Reset the global chatbot instance."""
    global chatbot_instance
    if chatbot_instance:
        chatbot_instance.reset_conversation()
    logger.info("Chatbot reset")
