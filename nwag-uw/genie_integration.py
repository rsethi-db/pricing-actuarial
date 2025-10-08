"""
Databricks Genie API integration for natural language data queries.
Based on: https://github.com/vivian-xie-db/genie_space_pg
"""
import logging
import os
from databricks.sdk import WorkspaceClient

logger = logging.getLogger(__name__)


class GenieChat:
    """Handle Genie Space conversations using Databricks Genie API."""
    
    def __init__(self, space_id: str = None):
        """
        Initialize Genie chat client.
        
        Args:
            space_id: Genie Space ID (from URL: /genie/rooms/{space_id})
        """
        try:
            self.workspace_client = WorkspaceClient()
            # Get space_id from environment or parameter
            self.space_id = space_id or os.environ.get('GENIE_SPACE_ID', '01f0a3bc10ba1357bde100a5f8527509')
            logger.info(f"Initialized GenieChat with space_id: {self.space_id}")
        except Exception as e:
            logger.error(f"Failed to initialize WorkspaceClient: {e}")
            self.workspace_client = None
    
    def start_conversation(self, prompt: str) -> dict:
        """
        Start a new conversation with Genie.
        
        Args:
            prompt: User's question
            
        Returns:
            dict with conversation_id, response text, and any SQL/data
        """
        if not self.workspace_client:
            return {
                'error': 'Genie client not initialized. Please check Databricks authentication.',
                'response': 'Unable to connect to Genie. Please ensure you have proper Databricks credentials configured.'
            }
        
        try:
            logger.info(f"Starting conversation with prompt: {prompt}")
            
            # Start conversation and wait for response
            response = self.workspace_client.genie.start_conversation_and_wait(
                space_id=self.space_id,
                content=prompt
            )
            
            return self._process_genie_response(response)
            
        except Exception as e:
            logger.error(f"Error starting conversation: {e}")
            return {
                'error': str(e),
                'response': f'Sorry, I encountered an error: {str(e)}'
            }
    
    def continue_conversation(self, conversation_id: str, prompt: str) -> dict:
        """
        Continue an existing conversation with follow-up question.
        
        Args:
            conversation_id: ID from previous conversation
            prompt: Follow-up question
            
        Returns:
            dict with response text and any SQL/data
        """
        if not self.workspace_client:
            return {
                'error': 'Genie client not initialized',
                'response': 'Unable to connect to Genie.'
            }
        
        try:
            logger.info(f"Continuing conversation {conversation_id} with: {prompt}")
            
            # Create message and wait for response
            response = self.workspace_client.genie.create_message_and_wait(
                space_id=self.space_id,
                conversation_id=conversation_id,
                content=prompt
            )
            
            return self._process_genie_response(response)
            
        except Exception as e:
            logger.error(f"Error continuing conversation: {e}")
            return {
                'error': str(e),
                'response': f'Sorry, I encountered an error: {str(e)}'
            }
    
    def _process_genie_response(self, response) -> dict:
        """
        Process Genie API response and extract relevant information.
        
        Args:
            response: Genie API response object
            
        Returns:
            dict with processed response data
        """
        result = {
            'conversation_id': response.conversation_id if hasattr(response, 'conversation_id') else None,
            'response': '',
            'sql': None,
            'data': None,
            'error': None
        }
        
        try:
            # Process attachments (text responses, queries, etc.)
            if hasattr(response, 'attachments') and response.attachments:
                for attachment in response.attachments:
                    # Text response
                    if hasattr(attachment, 'text') and attachment.text:
                        result['response'] += attachment.text.content + '\n'
                        logger.info(f"Genie text response: {attachment.text.content}")
                    
                    # Query/SQL response
                    elif hasattr(attachment, 'query') and attachment.query:
                        query_info = attachment.query
                        result['sql'] = query_info.query if hasattr(query_info, 'query') else None
                        
                        if hasattr(query_info, 'description'):
                            result['response'] += query_info.description + '\n'
                        
                        logger.info(f"Genie generated SQL: {result['sql']}")
                        
                        # Get query results if available
                        if hasattr(response, 'query_result') and response.query_result:
                            result['data'] = self._get_query_result(response.query_result.statement_id)
            
            # Fallback if no response text
            if not result['response']:
                result['response'] = 'I processed your query. Please check the results below.'
                
        except Exception as e:
            logger.error(f"Error processing Genie response: {e}")
            result['error'] = str(e)
            result['response'] = f'Received response but encountered processing error: {str(e)}'
        
        return result
    
    def _get_query_result(self, statement_id: str):
        """
        Fetch query results using statement ID.
        
        Args:
            statement_id: SQL statement execution ID
            
        Returns:
            Query results as list of dicts
        """
        try:
            result = self.workspace_client.statement_execution.get_statement(statement_id)
            
            if not result or not hasattr(result, 'result'):
                return None
            
            # Convert to list of dicts
            if hasattr(result, 'manifest') and hasattr(result.manifest, 'schema'):
                columns = [col.name for col in result.manifest.schema.columns]
                data = []
                
                if hasattr(result.result, 'data_array'):
                    for row in result.result.data_array:
                        data.append(dict(zip(columns, row)))
                
                return data
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching query result: {e}")
            return None


# Singleton instance
_genie_chat = None


def get_genie_chat() -> GenieChat:
    """Get or create GenieChat singleton instance."""
    global _genie_chat
    if _genie_chat is None:
        _genie_chat = GenieChat()
    return _genie_chat
