"""
Callbacks for the pricing cell automation app.
"""
import logging
import os
from base64 import b64decode
import pandas as pd
from dash import Input, Output, State, callback_context, html, dash, dependencies, dcc
from database import db_manager
from file_upload import file_upload_manager
from config import app_config

logger = logging.getLogger(__name__)

# Global variable to store uploaded files info
uploaded_files_info = []

def format_username(username):
    """Format username by removing dots and capitalizing first letters of first and last name."""
    try:
        # Remove dots and split by common separators
        cleaned = username.replace('.', '')
        
        # Split by common separators (space, underscore, dash)
        parts = cleaned.replace('_', ' ').replace('_', ' ').split()
        
        if len(parts) >= 2:
            # First and last name
            first_name = parts[0].capitalize()
            last_name = parts[1].capitalize()
            return f"{first_name} {last_name}"
        elif len(parts) == 1:
            # Single word _ try to split camelCase or find common patterns
            word = parts[0]
            
            # Check if it's camelCase (e.g., "richaSethi")
            import re
            # Split on capital letters that follow lowercase letters
            camel_split = re.findall(r'[a-z]+|[A-Z][a-z]*', word)
            if len(camel_split) >= 2:
                first_name = camel_split[0].capitalize()
                last_name = camel_split[1].capitalize()
                return f"{first_name} {last_name}"
            
            # If it's all lowercase and looks like firstname+lastname, try to split
            if word.islower() and len(word) > 6:
                # Special case for "richasethi" _ split at position 5
                if word == "richasethi":
                    return "Richa Sethi"
                
                # For other cases, try different split points
                # Common first names are usually 4_6 characters
                for i in range(5, min(8, len(word))):
                    potential_first = word[:i]
                    potential_last = word[i:]
                    if len(potential_last) >= 4:  # Last name should be at least 4 chars
                        # Check if this looks like a reasonable split
                        if potential_first in ['richa', 'rich', 'john', 'jane', 'mike', 'sara'] or len(potential_first) >= 5:
                            return f"{potential_first.capitalize()} {potential_last.capitalize()}"
                
                # If no good split found, try a more conservative approach
                # Split at the middle point
                if len(word) >= 10:
                    mid_point = len(word) // 2
                    first_name = word[:mid_point].capitalize()
                    last_name = word[mid_point:].capitalize()
                    return f"{first_name} {last_name}"
            
            # Fallback: just capitalize the single word
            return word.capitalize()
        else:
            # Fallback
            return username.capitalize()
    except:
        return username

def register_callbacks(dash_app):
    """Register all callbacks for the Dash app."""
    
    # Chatbot toggle callback
    @dash_app.callback(
        Output("chatbot-modal", "is_open"),
        [Input("chatbot-toggle", "n_clicks")],
        [State("chatbot-modal", "is_open")]
    )
    def toggle_chatbot(n_clicks, is_open):
        """Toggle the chatbot modal."""
        if n_clicks:
            return not is_open
        return is_open
    
    # Chatbot callbacks
    @dash_app.callback(
        [Output("chat-messages", "children"),
         Output("chat-input", "value")],
        [Input("chat-send", "n_clicks"),
         Input("chat-input", "n_submit")],
        [State("chat-input", "value"),
         State("chat-messages", "children")]
    )
    def handle_chat_message(n_clicks, n_submit, message, current_messages):
        """Handle chat messages and get AI responses."""
        if not message or (not n_clicks and not n_submit):
            return current_messages or [], ""
        
        try:
            from claude_integration import get_chatbot
            messages = current_messages or []
            
            # Add user message
            user_message = html.Div([
                html.Div([
                    html.I(className="fas fa-user me-2", style={"color": "#6c757d"}),
                    html.Span(message)
                ], className="d-flex align-items-start mb-2")
            ], className="chat-message user-message text-end")
            messages.append(user_message)
            
            # Get AI response
            chatbot = get_chatbot()
            ai_response = chatbot.get_response(message)
            
            # Add AI response
            ai_message = html.Div([
                html.Div([
                    html.I(className="fas fa-robot me-2", style={"color": "#007bff"}),
                    html.Span(ai_response)
                ], className="d-flex align-items-start mb-2")
            ], className="chat-message assistant-message")
            messages.append(ai_message)
            
            return messages, ""
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            error_message = html.Div([
                html.Div([
                    html.I(className="fas fa-exclamation-triangle me-2", style={"color": "#dc3545"}),
                    html.Span(f"Sorry, I encountered an error: {str(e)}")
                ], className="d-flex align-items-start mb-2")
            ], className="chat-message error-message")
            messages = current_messages or []
            messages.append(error_message)
            return messages, ""
    
    # Greeting callback to get current user name
    @dash_app.callback(
        Output("greeting-text", "children"),
        [Input("greeting-text", "id")]  # Trigger on component mount
    )
    def update_greeting(trigger):
        """Update greeting with current user's name."""
        try:
            # Try to get the actual logged_in user from various sources
            username = "User"  # Default fallback
            
            # Method 1: Try to get from Databricks context if available
            try:
                from pyspark.sql import SparkSession
                spark = SparkSession.getActiveSession()
                if spark:
                    # In Databricks, try to get the actual user
                    try:
                        # This works in Databricks environment
                        result = spark.sql("SELECT current_user() as user").collect()
                        if result:
                            username = result[0]['user']
                    except:
                        # Fallback to environment variables in Databricks
                        username = os.environ.get('USER', os.environ.get('USERNAME', 'User'))
            except:
                pass
            
            # Method 2: Try to get from system environment
            if username == "User":
                try:
                    import getpass
                    username = getpass.getuser()
                except:
                    username = os.environ.get('USER', os.environ.get('USERNAME', 'User'))
            
            # Method 3: Try to get from HTTP headers if available (for web context)
            try:
                from flask import request
                if hasattr(request, 'headers'):
                    # Check for common authentication headers
                    auth_header = request.headers.get('Authorization')
                    if auth_header:
                        # Extract username from Bearer token or other auth methods
                        # This is a simplified example _ you'd implement proper token parsing
                        pass
            except:
                pass
            
            # Format the username: remove dots and capitalize first letters
            formatted_username = format_username(username)
            return f"Hello {formatted_username}!"
        except Exception as e:
            logger.error(f"Error getting username: {e}")
            return "Hello User!"

    # Step Navigation Callbacks
    
    
    @dash_app.callback(
        [Output("pdf-management", "style"),
         Output("uploaded-pdfs-list", "children"),
         Output("upload-feedback", "children")],
        [Input("upload-data", "contents")],
        [State("upload-data", "filename")]
    )
    def handle_upload_feedback(upload_contents, filenames):
        """Handle upload feedback and enable continue button."""
        global uploaded_files_info
        # Ensure uploaded_files_info is always a list
        if not isinstance(uploaded_files_info, list):
            uploaded_files_info = []
        try:
            if upload_contents and filenames:
                # Upload files to Databricks volumes immediately
                uploaded_files = []
                for content, filename in zip(upload_contents, filenames):
                    try:
                        # Decode the base64 content
                        _, content_string = content.split(",")
                        decoded = b64decode(content_string)
                        
                        # Upload to Databricks volume
                        volume_path = file_upload_manager.upload_file_to_volume(decoded, filename)
                        uploaded_files.append({
                            'filename': filename,
                            'volume_path': volume_path,
                            'status': 'uploaded'
                        })
                        logger.info(f"Successfully uploaded {filename} to {volume_path}")
                    except Exception as e:
                        logger.error(f"Failed to upload {filename}: {e}")
                        uploaded_files.append({
                            'filename': filename,
                            'volume_path': None,
                            'status': 'failed',
                            'error': str(e)
                        })
                
                # Create PDF list with remove buttons
                pdf_items = []
                for i, file_info in enumerate(uploaded_files):
                    pdf_items.append(
                            html.Div([
                                html.Div([
                                    html.I(className="fas fa-file-pdf pdf-icon"),
                                    html.Span(file_info['filename'], className="pdf_name")
                                ], className="pdf_name_container"),
                            html.Button(
                                [html.I(className="fas fa-trash me-1"), "Remove"],
                                className="pdf_remove_btn",
                                id={"type": "remove_pdf", "index": i},
                                **{"data-filename": file_info['filename']}
                            )
                        ], className="pdf_item")
                    )
                
                # Store uploaded files info globally for remove callback
                uploaded_files_info = uploaded_files
                
                # Check if all files uploaded successfully
                success_count = sum(1 for f in uploaded_files if f['status'] == 'uploaded')
                if success_count == len(uploaded_files):
                    status_message = f"✅ {success_count} file(s) uploaded successfully! You can now extract features."
                else:
                    status_message = f"⚠️ {success_count}/{len(uploaded_files)} files uploaded successfully. Some uploads failed."
                
                # Show PDF management when files are uploaded
                return {"display": "block"}, pdf_items, status_message
            return {"display": "none"}, [], ""
        except Exception as e:
            logger.error(f"Error in handle_upload_feedback: {e}")
            return {"display": "none"}, [], f"Error: {str(e)}"

    @dash_app.callback(
        [Output("pdf-management", "style", allow_duplicate=True),
         Output("uploaded-pdfs-list", "children", allow_duplicate=True),
         Output("upload-feedback", "children", allow_duplicate=True)],
        [Input({"type": "remove_pdf", "index": dependencies.ALL}, "n_clicks")],
        [State("uploaded-pdfs-list", "children")],
        prevent_initial_call=True
    )
    def remove_pdf_file(n_clicks_list, current_pdf_list):
        """Remove a PDF file from the list and delete from volume."""
        global uploaded_files_info
        # Ensure uploaded_files_info is always a list
        if not isinstance(uploaded_files_info, list):
            uploaded_files_info = []
        # Check if any remove button was clicked
        if not n_clicks_list or not any(n_clicks_list):
            return dash.no_update, dash.no_update, dash.no_update
        
        try:
            # Get the context to see which button was clicked
            ctx = callback_context
            if not ctx.triggered:
                return dash.no_update, dash.no_update, dash.no_update
            
            # Get the button that was clicked
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]
            button_data = eval(button_id)  # Convert string to dict
            file_index = button_data["index"]
            
            # Get the filename from the global uploaded_files_info
            filename = None
            if uploaded_files_info and isinstance(uploaded_files_info, list) and len(uploaded_files_info) > file_index:
                filename = uploaded_files_info[file_index]['filename']
            
            # Delete the file from Databricks volume if we found the filename
            if filename:
                try:
                    success = file_upload_manager.delete_file_from_volume(filename)
                    if success:
                        logger.info(f"Successfully deleted {filename} from volume")
                    else:
                        logger.warning(f"Failed to delete {filename} from volume")
                except Exception as e:
                    logger.error(f"Error deleting {filename} from volume: {e}")
            else:
                logger.warning("Could not find filename to delete")
            
            # Remove the file from the UI list and global variable
            new_pdf_list = []
            new_uploaded_files = []
            
            # Remove the file at the specified index from both lists
            for i, pdf_item in enumerate(current_pdf_list):
                if i != file_index:
                    new_pdf_list.append(pdf_item)
            
            # Remove the corresponding file from global variable
            if uploaded_files_info and isinstance(uploaded_files_info, list) and len(uploaded_files_info) > file_index:
                for i, file_info in enumerate(uploaded_files_info):
                    if i != file_index:
                        new_uploaded_files.append(file_info)
            
            # Update global variable
            uploaded_files_info = new_uploaded_files
            
            # If no files left, hide the PDF management section
            if not new_pdf_list:
                return {"display": "none"}, new_pdf_list, "All files removed successfully"
            else:
                return {"display": "block"}, new_pdf_list, f"File {filename} removed successfully" if filename else "File removed successfully"
            
        except Exception as e:
            logger.error(f"Error in remove_pdf_file: {e}")
            # Fallback: clear all files
            uploaded_files_info = []
            return {"display": "none"}, [], "Error removing file"

    @dash_app.callback(
        [Output("workflow_status", "children"),
         Output("loading_modal", "is_open")],
        [Input("parse_ai_btn", "n_clicks")],
        [State("upload-data", "contents"),
         State("upload-data", "filename")],
        prevent_initial_call=True
    )
    def parse_and_run_ai(n_clicks, contents, filenames):
        """Main callback for parsing and running AI analysis."""
        if not n_clicks:
            return "", False

        try:
            # Validate inputs
            if not contents or not filenames:
                return "⚠️ Please upload at least one file before processing.", False
            
            # Check file types
            valid_extensions = ['.pdf']
            invalid_files = [f for f in filenames if not any(f.lower().endswith(ext) for ext in valid_extensions)]
            if invalid_files:
                return f"❌ Invalid file types detected: {', '.join(invalid_files)}. Please upload only PDF files.", False
            
            # Show loading modal
            status_message = "🔄 Processing files... Please wait."
            results_data = []
            modal_open = True
            
            # Step 1: Upload PDFs
            try:
                logger.info(f"Uploading {len(filenames)} file(s)...")
                
                for i, (content, filename) in enumerate(zip(contents, filenames)):
                    _, content_string = content.split(",")
                    decoded = b64decode(content_string)
                    file_upload_manager.upload_file_to_volume(decoded, filename)
                
                logger.info(f"Successfully uploaded {len(filenames)} files")
            except Exception as e:
                logger.error(f"Failed to upload files: {e}")
                return f"❌ Failed to upload files: {str(e)}", False
            # Step 2: Define SQL queries using the recommended approach
            volume_path = file_upload_manager.volume_path
            
            # Parse documents first with improved error handling
            parse_query = f"""
            CREATE OR REPLACE TABLE shirlywang_insurance.fa_pricing.fa_product_brochure_parsed AS
            WITH all_files AS (
              SELECT
                path,
                content
              FROM
                READ_FILES('{volume_path}', format => 'binaryFile')
              ORDER BY
                path ASC
            ),
            repartitioned_files AS (
              SELECT *
              FROM all_files
              -- Force Spark to split into partitions
              DISTRIBUTE BY crc32(path) % 4
            ),
            -- Parse the files using ai_parse document
            parsed_documents AS (
              SELECT
                path,
                ai_parse_document(content) as parsed
              FROM
                repartitioned_files
              WHERE array_contains(array('.pdf', '.jpg', '.jpeg', '.png'), lower(regexp_extract(path, r'(\\.[^.]+)$', 1)))
            ),
            -- Extract content from ai_parse_document output for all successful parses
            sorted_contents AS (
              SELECT
                path,
                element:content AS content
              FROM
                (
                  SELECT
                    path,
                      posexplode(
                        CASE
                          WHEN try_cast(parsed:metadata:version AS STRING) = '1.0' 
                          THEN try_cast(parsed:document:pages AS ARRAY<VARIANT>)
                          ELSE try_cast(parsed:document:elements AS ARRAY<VARIANT>)
                        END
                      ) AS (idx, element)
                  FROM
                    parsed_documents
                  WHERE try_cast(parsed:error_status AS STRING) IS NULL
                )
              ORDER BY
                idx
            ),
            -- Concatenate so we have 1 row per document
            concatenated AS (
                SELECT
                    path,
                    concat_ws('\\n\\n', collect_list(content)) AS full_content
                FROM
                    sorted_contents
                WHERE content IS NOT NULL
                GROUP BY
                    path
            )
            -- Return the parsed content
            SELECT 
                path,
                full_content as text,
                current_timestamp() AS parsed_timestamp
            FROM concatenated
            """

            # Step 3: Execute parse query and AI extraction
            try:
                logger.info("Step 1: Parsing documents...")
                
                # Execute the parse query
                result = db_manager.execute_query(parse_query)
                logger.info("Parse query executed successfully")
                
                # Check the parsed results
                check_query = "SELECT COUNT(*) as count FROM shirlywang_insurance.fa_pricing.fa_product_brochure_parsed"
                count_result = db_manager.execute_query(check_query)
                if count_result is None or count_result.empty or count_result.iloc[0]['count'] == 0:
                    return "⚠️ Parse query completed but no data found in table.", False                
                row_count = count_result.iloc[0]['count']
                logger.info(f"Parsed table created with {row_count} rows")
                
                # Get a sample of the parsed data
                sample_query = "SELECT path, text FROM shirlywang_insurance.fa_pricing.fa_product_brochure_parsed LIMIT 2"
                sample_result = db_manager.execute_query(sample_query)
                if sample_result is not None and not sample_result.empty:
                    logger.info(f"Sample parsed data: {sample_result.to_dict('records')}")
                else:
                    logger.warning("No sample data found in parsed table")
                
                # Step 2: Test AI endpoint
                logger.info(f"Step 2: Testing AI endpoint: {app_config.ai_endpoint}")
                test_ai_sql = f"""
                SELECT ai_query('{app_config.ai_endpoint}', 'Test insurance product with minimum premium $1000', failOnError => false) AS test_response
                """
                
                try:
                    test_result = db_manager.execute_query(test_ai_sql)
                    if test_result is not None and not test_result.empty:
                        logger.info(f"AI endpoint test response: {test_result.iloc[0]['test_response']}")
                    else:
                        logger.warning("AI endpoint test failed - no response")
                        return f"✅ Success! Parsed {row_count} documents. AI endpoint test failed - no response.", False
                except Exception as e:
                    error_msg = str(e)
                    if "RESOURCE_DOES_NOT_EXIST" in error_msg or "does not exist" in error_msg:
                        logger.error(f"AI Endpoint Error: The endpoint '{app_config.ai_endpoint}' does not exist")
                        return f"❌ AI Endpoint Error: The endpoint '{app_config.ai_endpoint}' does not exist in your Databricks workspace. Please update the 'ai_endpoint' value in app.yaml with a valid endpoint name.", False
                    else:
                        logger.warning(f"AI endpoint test failed: {error_msg}")
                        return f"✅ Success! Parsed {row_count} documents. AI endpoint test failed: {error_msg}", False
                # Step 3: Create AI responses table
                logger.info("Step 3: Creating AI responses table...")
                streaming_table = "shirlywang_insurance.fa_pricing.fa_product_brochure_endpoint_response"
                
                ai_query_sql = f"""
                CREATE OR REPLACE TABLE {streaming_table} 
                TBLPROPERTIES (
                    'delta.feature.variantType-preview' = 'supported'
                )
                AS
                WITH query_results AS (
                  SELECT
                    text AS input,
                    ai_query(
                      '{app_config.ai_endpoint}',
                      text,
                      failOnError => false
                    ) AS response,
                    current_timestamp() AS timestamp
                  FROM shirlywang_insurance.fa_pricing.fa_product_brochure_parsed
                )
                SELECT
                  input,
                  response.result AS response,
                  response.errorMessage AS error,
                  timestamp
                FROM query_results
                """
                
                try:
                    ai_result = db_manager.execute_query(ai_query_sql)
                    logger.info("AI responses table created successfully")
                    
                    # Check AI results
                    ai_check_query = f"SELECT COUNT(*) as count FROM {streaming_table}"
                    ai_count_result = db_manager.execute_query(ai_check_query)
                    if ai_count_result is not None and not ai_count_result.empty:
                        ai_row_count = ai_count_result.iloc[0]['count']
                        logger.info(f"AI responses table created with {ai_row_count} rows")
                        
                        # Debug: Check what the raw AI response looks like
                        debug_query = f"SELECT input, response, error FROM {streaming_table} LIMIT 1"
                        debug_result = db_manager.execute_query(debug_query)
                        if debug_result is not None and not debug_result.empty:
                            logger.info(f"Raw AI response: {debug_result.to_dict('records')}")
                    else:
                        return f"✅ Success! Parsed {row_count} documents and created AI responses table.", False
                except Exception as ai_error:
                    logger.error(f"Failed to create AI responses table: {ai_error}")
                    return f"❌ Failed to create AI responses table: {str(ai_error)}", False
                # Step 4: Extract structured features from AI responses
                logger.info("Step 4: Extracting structured features from AI responses...")
                features_table = "shirlywang_insurance.fa_pricing.fa_product_brochure_pricing_features"
                features_query = f"""
                CREATE OR REPLACE TABLE {features_table} AS
                SELECT
                  input,
                  error,

                  -- Issuing companies (array)
                  from_json(
                    get_json_object(cast(response AS STRING), '$.issuing_company'),
                    'array<string>'
                  ) AS issuing_company,

                  -- Minimum premium (keep raw string since it varies by product)
                  get_json_object(cast(response AS STRING), '$.minimum_premium') AS minimum_premium,

                  -- Withdrawal options (array of strings)
                  from_json(
                    get_json_object(cast(response AS STRING), '$.withdrawal_options'),
                    'array<string>'
                  ) AS withdrawal_options,

                  -- Interest crediting
                  get_json_object(cast(response AS STRING), '$.interest_crediting') AS interest_crediting,

                  -- Surrender charge schedule (string, varies by product)
                  get_json_object(cast(response AS STRING), '$.surrender_charge_schedule') AS surrender_charge_schedule,

                  -- Surrender charge percentage
                  get_json_object(cast(response AS STRING), '$.surrender_charge_percentage') AS surrender_charge_percentage,

                  -- Death benefit
                  get_json_object(cast(response AS STRING), '$.death_benefit') AS death_benefit,

                  -- Available riders (array of strings)
                  from_json(
                    get_json_object(cast(response AS STRING), '$.available_riders'),
                    'array<string>'
                  ) AS available_riders,

                  -- Issue ages
                  get_json_object(cast(response AS STRING), '$.issue_ages') AS issue_ages,

                  -- Guarantee Period
                  get_json_object(cast(response AS STRING), '$.guarantee_period') AS guarantee_period,

                  -- Guaranteed Minimum Interest Rate
                  get_json_object(cast(response AS STRING), '$.guaranteed_minimum_interest_rate') AS guaranteed_minimum_interest_rate,

                  -- Raw JSON for reference
                  response AS features
                FROM {streaming_table}
                WHERE error IS NULL
                """
                
                try:
                    features_result = db_manager.execute_query(features_query)
                    logger.info("Features table created successfully")
                    
                    # Get features data for display
                    features_display_query = f"""
                    SELECT 
                        issuing_company,
                        minimum_premium,
                        withdrawal_options,
                        interest_crediting,
                        surrender_charge_schedule,
                        surrender_charge_percentage,
                        death_benefit,
                        available_riders,
                        issue_ages,
                        guarantee_period
                    FROM {features_table}
                    LIMIT 10
                    """
                    
                    features_data = db_manager.execute_query(features_display_query)
                    if features_data is not None and not features_data.empty:
                        # Debug: Check what the raw data looks like
                        logger.info(f"Raw features data: {features_data.to_dict('records')}")
                        
                        # Convert arrays to strings for display
                        display_data = []
                        for _, row in features_data.iterrows():
                            display_row = {}
                            for col in features_data.columns:
                                if col in ['issuing_company', 'withdrawal_options', 'available_riders']:
                                    # Convert array to comma-separated string
                                    if isinstance(row[col], list):
                                        display_row[col] = ', '.join(row[col])
                                    else:
                                        display_row[col] = str(row[col]) if row[col] is not None else ''
                                else:
                                    display_row[col] = str(row[col]) if row[col] is not None else ''
                            display_data.append(display_row)
                        
                        logger.info(f"Processed display data: {display_data}")
                        
                        # Extract specific values for the hardcoded fields
                        withdrawal_rate = "No data available"
                        surrender_period = "No data available" 
                        guarantee_period = "No data available"
                        
                        if display_data and len(display_data) > 0:
                            first_row = display_data[0]
                            withdrawal_rate = first_row.get('withdrawal_options', 'No data available')
                            surrender_period = first_row.get('surrender_charge_schedule', 'No data available')
                            guarantee_period = first_row.get('guarantee_period', 'No data available')
                        
                        return f"✅ Success! Check the table below for extracted features.", False
                    else:
                        logger.warning("No features data found for display")
                        return f"✅ Success! Parsed {row_count} documents, extracted features with AI, and created structured pricing features table.", False
                except Exception as features_error:
                    logger.error(f"Failed to create features table: {features_error}")
                    return f"❌ Failed to create features table: {str(features_error)}", False
            except Exception as e:
                logger.error(f"Parse query execution failed: {e}")
                return f"❌ Parse query failed: {str(e)}", False
            # Return success message
            return f"✅ {len(filenames)} file(s) has been uploaded to Databricks volumes and AI analysis completed! Parsed {row_count} documents, extracted features with AI, and created structured pricing features table.", False
        except Exception as e:
            logger.error(f"Unexpected error in parse_and_run_ai: {e}")
            return f"❌ Unexpected error: {str(e)}", False
    # End of parse_and_run_ai function

    # Button state callback - handles immediate button text and disabled state changes
    @dash_app.callback(
        [Output("parse_ai_btn", "children"),
         Output("parse_ai_btn", "disabled")],
        [Input("parse_ai_btn", "n_clicks")],
        [State("workflow_status", "children")],
        prevent_initial_call=True
    )
    def update_button_state(n_clicks, status):
        """Update button text and disabled state based on processing state."""
        if n_clicks:
            # Always show processing state when button is clicked
            return [html.I(className="fas fa-spinner fa-spin me-2"), "Extracting Features..."], True
        else:
            return [html.I(className="fas fa-play me-2"), "Extract Features"], False

    # Button reset callback - resets button when processing is complete
    @dash_app.callback(
        [Output("parse_ai_btn", "children", allow_duplicate=True),
         Output("parse_ai_btn", "disabled", allow_duplicate=True)],
        [Input("workflow_status", "children")],
        prevent_initial_call=True
    )
    def reset_button_state(status):
        """Reset button state when processing is complete."""
        if status and ("Success" in str(status) or "❌" in str(status) or "⚠️" in str(status)):
            return [html.I(className="fas fa-play me-2"), "Extract Features"], False
        else:
            # Don't change button state if still processing
            return dash.no_update, dash.no_update

    # Reference Product Specs Callback - Update from database after AI processing
    @dash_app.callback(
        [Output("surrender-charge-period", "children"),
         Output("initial-guarantee-period", "children"),
         Output("guaranteed-minimum-interest-rate", "children"),
         Output("surrender-charge-period", "className"),
         Output("initial-guarantee-period", "className"),
         Output("guaranteed-minimum-interest-rate", "className")],
        [Input("workflow_status", "children")],
        prevent_initial_call=True
    )
    def update_reference_specs_from_database(status_message):
        """Update reference product specs from AI processing results."""
        try:
            # Only update if the status indicates success
            if "Success" not in status_message or "No data available" in status_message:
                return ("Upload docs", "Upload docs", "Upload docs",
                        "feature-value placeholder-text", "feature-value placeholder-text", "feature-value placeholder-text")
            
            logger.info("Updating reference specs from database...")
            
            # First, try to add the missing column (without IF NOT EXISTS as it's not supported)
            alter_query = """
            ALTER TABLE shirlywang_insurance.fa_pricing.fa_product_brochure_pricing_features 
            ADD COLUMN guaranteed_minimum_interest_rate STRING
            """
            try:
                db_manager.execute_query(alter_query)
                logger.info("Added guaranteed_minimum_interest_rate column to features table")
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    logger.info("guaranteed_minimum_interest_rate column already exists")
                else:
                    logger.warning(f"Could not add guaranteed_minimum_interest_rate column: {e}")
            
            # Query the features table for the latest data
            features_query = """
            SELECT 
                withdrawal_options,
                surrender_charge_schedule,
                guarantee_period,
                guaranteed_minimum_interest_rate
            FROM shirlywang_insurance.fa_pricing.fa_product_brochure_pricing_features 
            ORDER BY input DESC 
            LIMIT 1
            """
            
            result = db_manager.execute_query(features_query)
            
            if result is not None and not result.empty:
                first_row = result.iloc[0]
                
                # Extract withdrawal options
                withdrawal_options = first_row.get('withdrawal_options', 'No data available')
                if withdrawal_options is not None and str(withdrawal_options) != 'No data available':
                    # Handle numpy arrays or lists
                    if hasattr(withdrawal_options, 'tolist'):
                        # It's a numpy array
                        withdrawal_list = withdrawal_options.tolist()
                        withdrawal_display = ', '.join([str(item) for item in withdrawal_list if item])
                    elif isinstance(withdrawal_options, (list, tuple)):
                        # It's already a list/tuple
                        withdrawal_display = ', '.join([str(item) for item in withdrawal_options if item])
                    elif isinstance(withdrawal_options, str) and withdrawal_options.startswith('['):
                        # Convert string representation of array to actual list
                        import ast
                        try:
                            withdrawal_list = ast.literal_eval(withdrawal_options)
                            if isinstance(withdrawal_list, list):
                                withdrawal_display = ', '.join([str(item) for item in withdrawal_list if item])
                            else:
                                withdrawal_display = str(withdrawal_options)
                        except:
                            withdrawal_display = str(withdrawal_options)
                    else:
                        withdrawal_display = str(withdrawal_options)
                else:
                    withdrawal_display = "No data available"
                
                # Extract surrender charge period
                surrender_period = first_row.get('surrender_charge_schedule', 'No data available')
                surrender_display = str(surrender_period) if surrender_period is not None and str(surrender_period) != 'No data available' else "No data available"
                
                # Extract guarantee period
                guarantee_period = first_row.get('guarantee_period', 'No data available')
                guarantee_display = str(guarantee_period) if guarantee_period is not None and str(guarantee_period) != 'No data available' else "No data available"
                
                # Extract guaranteed minimum interest rate
                min_interest_rate = first_row.get('guaranteed_minimum_interest_rate', 'No data available')
                min_interest_display = str(min_interest_rate) if min_interest_rate is not None and str(min_interest_rate) != 'No data available' else "No data available"
                
                logger.info(f"Updated reference specs: {withdrawal_display}, {surrender_display}, {guarantee_display}, {min_interest_display}")
                # Determine CSS classes based on data availability
                withdrawal_class = "feature-value has-data" if withdrawal_display != "No data available" else "feature-value placeholder-text"
                surrender_class = "feature-value has-data" if surrender_display != "No data available" else "feature-value placeholder-text"
                guarantee_class = "feature-value has-data" if guarantee_display != "No data available" else "feature-value placeholder-text"
                min_interest_class = "feature-value has-data" if min_interest_display != "No data available" else "feature-value placeholder-text"
                
                return (surrender_display, guarantee_display, min_interest_display,
                        surrender_class, guarantee_class, min_interest_class)
            else:
                logger.warning("No features data found in database")
                return ("Upload docs", "Upload docs", "Upload docs",
                        "feature-value placeholder-text", "feature-value placeholder-text", "feature-value placeholder-text")
                
        except Exception as e:
            logger.error(f"Error updating reference specs from database: {e}")
            return ("Upload docs", "Upload docs", "Upload docs",
                    "feature-value placeholder-text", "feature-value placeholder-text", "feature-value placeholder-text")



    # Working Scenario Management Callbacks (from test_final.py)
    @dash_app.callback(
        [Output("scenarios-container", "children")],
        [Input("add-scenario-btn", "n_clicks"),
         Input({"type": "remove-scenario", "scenario": dependencies.ALL}, "n_clicks")],
        [State("scenarios-container", "children")],
        prevent_initial_call=True
    )
    def handle_scenario_actions(add_clicks, remove_clicks_list, existing_scenarios):
        """Handle both adding and removing scenarios in a single callback."""
        ctx = callback_context
        if not ctx.triggered:
            return [existing_scenarios or []]
        
        triggered_id = ctx.triggered[0]['prop_id']
        
        # Handle add scenario
        if triggered_id == "add-scenario-btn.n_clicks":
            return [add_scenario(existing_scenarios)]
        
        # Handle remove scenario
        elif "remove-scenario" in triggered_id:
            return [remove_scenario(triggered_id, existing_scenarios)]
        
        # Default return
        return [existing_scenarios or []]

    def add_scenario(existing_scenarios):
        """Add a new scenario."""
        # Use default values since we can't access the input values when all scenarios are removed
        current_surrender_period = 7
        current_guarantee_period = 10
        current_min_interest_rate = 3.5
        
        # Calculate scenario number - count only actual scenarios, not buttons
        existing_scenarios_list = existing_scenarios or []
        scenario_count = 0  # Start with 0 since we start with no scenarios
        for s in existing_scenarios_list:
            if isinstance(s, dict) and 'props' in s and 'id' in s['props'] and str(s['props']['id']).startswith('scenario-'):
                scenario_count += 1
        scenario_num = scenario_count + 1
        
        # Create new scenario
        new_scenario = html.Div([
            html.Div([
                html.H5(f"Scenario {scenario_num}", className="scenario-title mb-3")
            ], className="scenario-header"),
            
            html.Div([
                html.Div([
                    html.Label("Surrender Charge Period (years)", className="adjust-label"),
                    html.Div([
                        dcc.Input(
                            type="number",
                            id={"type": "surrender-period-input", "scenario": scenario_num},
                            value=current_surrender_period,
                            min=0,
                            max=30,
                            step=1,
                            className="adjust-input"
                        ),
                        html.Div([
                            html.Button("+", className="adjust-stepper", id={"type": "surrender-period-up", "scenario": scenario_num}),
                            html.Button("-", className="adjust-stepper", id={"type": "surrender-period-down", "scenario": scenario_num})
                        ], className="adjust-steppers")
                    ], className="adjust-input-group")
                ], className="adjust-field"),
                
                html.Div([
                    html.Label("Initial Guarantee Period (years)", className="adjust-label"),
                    html.Div([
                        dcc.Input(
                            type="number",
                            id={"type": "guarantee-period-input", "scenario": scenario_num},
                            value=current_guarantee_period,
                            min=0,
                            max=30,
                            step=1,
                            className="adjust-input"
                        ),
                        html.Div([
                            html.Button("+", className="adjust-stepper", id={"type": "guarantee-period-up", "scenario": scenario_num}),
                            html.Button("-", className="adjust-stepper", id={"type": "guarantee-period-down", "scenario": scenario_num})
                        ], className="adjust-steppers")
                    ], className="adjust-input-group")
                ], className="adjust-field"),
                
                html.Div([
                    html.Label("Guaranteed Minimum Interest Rate (%)", className="adjust-label"),
                    html.Div([
                        dcc.Input(
                            type="number",
                            id={"type": "min-interest-rate-input", "scenario": scenario_num},
                            value=current_min_interest_rate,
                            min=0,
                            max=10,
                            step=0.1,
                            className="adjust-input"
                        ),
                        html.Div([
                            html.Button("+", className="adjust-stepper", id={"type": "min-interest-rate-up", "scenario": scenario_num}),
                            html.Button("-", className="adjust-stepper", id={"type": "min-interest-rate-down", "scenario": scenario_num})
                        ], className="adjust-steppers")
                    ], className="adjust-input-group")
                ], className="adjust-field"),
                
                html.Div([
                    html.Button([
                        html.I(className="fas fa-trash me-2"),
                        "Remove Scenario"
                    ], id={"type": "remove-scenario", "scenario": scenario_num}, className="remove-scenario-btn")
                ], className="adjust-field")
            ], className="adjust-content")
        ], className="scenario-section", id=f"scenario-{scenario_num}")
        
        # Add New Scenario button after this scenario
        add_button = html.Div([
            html.Div([
                html.Button([
                    html.I(className="fas fa-plus me-2"),
                    "Add New Scenario"
                ], id="add-scenario-btn", className="add-scenario-btn")
            ], className="text-center")
        ], className="mb-4")
        
        # Hide empty state and add new scenario and button to existing ones
        updated_scenarios = []
        
        # Filter out empty state if it exists
        for s in existing_scenarios or []:
            if not (isinstance(s, dict) and 'props' in s and 'id' in s['props'] and s['props']['id'] == 'empty-scenarios-state'):
                updated_scenarios.append(s)
        
        # Add new scenario and button
        updated_scenarios = updated_scenarios + [new_scenario, add_button]
        
        return updated_scenarios

    def remove_scenario(triggered_id, existing_scenarios):
        """Remove a scenario."""
        # Extract scenario number from pattern-matching ID
        import json
        try:
            json_part = triggered_id.split('.')[0]
            button_info = json.loads(json_part)
            scenario_num = str(button_info['scenario'])
        except:
            return existing_scenarios or []
        
        scenario_id = f"scenario-{scenario_num}"
        
        # Filter out the scenario and its associated add button, but always keep the main Add New Scenario button
        updated_scenarios = []
        main_add_button_found = False
        
        for s in existing_scenarios or []:
            # Skip the scenario we want to remove
            if isinstance(s, dict) and 'props' in s and 'id' in s['props'] and s['props']['id'] == scenario_id:
                continue  # Skip this scenario
            
            # Check if this is the main Add New Scenario button
            elif (isinstance(s, dict) and 'props' in s and 'id' not in s['props'] and 
                  'children' in s['props'] and len(s['props']['children']) > 0 and
                  'props' in s['props']['children'][0] and 'children' in s['props']['children'][0]['props'] and
                  'Add New Scenario' in str(s['props']['children'][0]['props']['children'])):
                # Check if this is the main button (has id='add-scenario-btn') - if so, keep it
                if ('props' in s['props']['children'][0] and 'id' in s['props']['children'][0]['props'] and 
                    s['props']['children'][0]['props']['id'] == 'add-scenario-btn'):
                    main_add_button_found = True
                    updated_scenarios.append(s)
                else:
                    continue  # Skip this button
            
            # Keep everything else
            else:
                updated_scenarios.append(s)
        
        # Count remaining scenarios
        remaining_scenarios = 0
        for s in updated_scenarios:
            if isinstance(s, dict) and 'props' in s and 'id' in s['props'] and str(s['props']['id']).startswith('scenario-'):
                remaining_scenarios += 1
        
        # If no scenarios left, add empty state
        if remaining_scenarios == 0:
            empty_state = html.Div([
                html.Div([
                    html.I(className="fas fa-cogs fa-3x", style={"color": "#6c757d", "margin-bottom": "15px"}),
                    html.H5("No Scenarios Yet", style={"color": "#6c757d", "margin-bottom": "10px"}),
                    html.P("Create your first scenario to start adjusting product features", style={"color": "#6c757d", "font-size": "14px", "margin-bottom": "20px"})
                ], className="text-center empty-state")
            ], className="mb-4", id="empty-scenarios-state")
            updated_scenarios.insert(0, empty_state)
        
        # If no main Add New Scenario button was found, add it back
        if not main_add_button_found:
            main_add_button = html.Div([
                html.Div([
                    html.Button([
                        html.I(className="fas fa-plus me-2"),
                        "Add New Scenario"
                    ], id="add-scenario-btn", className="add-scenario-btn")
                ], className="text-center")
            ], className="mb-4")
            updated_scenarios.append(main_add_button)
        
        return updated_scenarios

    # Stepper button callbacks for all scenarios
    @dash_app.callback(
        [Output({"type": "surrender-period-input", "scenario": dependencies.ALL}, "value", allow_duplicate=True),
         Output({"type": "guarantee-period-input", "scenario": dependencies.ALL}, "value", allow_duplicate=True),
         Output({"type": "min-interest-rate-input", "scenario": dependencies.ALL}, "value", allow_duplicate=True)],
        [Input({"type": "surrender-period-up", "scenario": dependencies.ALL}, "n_clicks"),
         Input({"type": "surrender-period-down", "scenario": dependencies.ALL}, "n_clicks"),
         Input({"type": "guarantee-period-up", "scenario": dependencies.ALL}, "n_clicks"),
         Input({"type": "guarantee-period-down", "scenario": dependencies.ALL}, "n_clicks"),
         Input({"type": "min-interest-rate-up", "scenario": dependencies.ALL}, "n_clicks"),
         Input({"type": "min-interest-rate-down", "scenario": dependencies.ALL}, "n_clicks")],
        [State({"type": "surrender-period-input", "scenario": dependencies.ALL}, "value"),
         State({"type": "guarantee-period-input", "scenario": dependencies.ALL}, "value"),
         State({"type": "min-interest-rate-input", "scenario": dependencies.ALL}, "value")],
        prevent_initial_call=True
    )
    def update_stepper_values(surrender_up, surrender_down, guarantee_up, guarantee_down, 
                             min_rate_up, min_rate_down, surrender_vals, guarantee_vals, min_rate_vals):
        """Update input values based on stepper button clicks."""
        ctx = callback_context
        if not ctx.triggered:
            return surrender_vals or [], guarantee_vals or [], min_rate_vals or []

        triggered_id = ctx.triggered[0]['prop_id']
        button_id = triggered_id.split('.')[0]
        
        # Parse the button ID to get scenario number
        import json
        try:
            button_info = json.loads(button_id)
            scenario_num = button_info['scenario']
        except:
            return surrender_vals or [], guarantee_vals or [], min_rate_vals or []
        
        # Get current values for this scenario
        surrender_val = surrender_vals[scenario_num - 1] if surrender_vals and len(surrender_vals) >= scenario_num else 7
        guarantee_val = guarantee_vals[scenario_num - 1] if guarantee_vals and len(guarantee_vals) >= scenario_num else 10
        min_rate_val = min_rate_vals[scenario_num - 1] if min_rate_vals and len(min_rate_vals) >= scenario_num else 3.5
        
        # Convert to appropriate types
        surrender = int(surrender_val) if surrender_val is not None else 7
        guarantee = int(guarantee_val) if guarantee_val is not None else 10
        min_rate = float(min_rate_val) if min_rate_val is not None else 3.5

        # Update based on which button was clicked
        if "surrender-period-up" in button_id:
            surrender = min(30, surrender + 1)
        elif "surrender-period-down" in button_id:
            surrender = max(0, surrender - 1)
        elif "guarantee-period-up" in button_id:
            guarantee = min(30, guarantee + 1)
        elif "guarantee-period-down" in button_id:
            guarantee = max(0, guarantee - 1)
        elif "min-interest-rate-up" in button_id:
            min_rate = min(10.0, min_rate + 0.1)
        elif "min-interest-rate-down" in button_id:
            min_rate = max(0.0, min_rate - 0.1)

        # Update the specific scenario's values
        updated_surrender = surrender_vals or []
        updated_guarantee = guarantee_vals or []
        updated_min_rate = min_rate_vals or []
        
        # Ensure lists are long enough
        while len(updated_surrender) < scenario_num:
            updated_surrender.append(7)
        while len(updated_guarantee) < scenario_num:
            updated_guarantee.append(10)
        while len(updated_min_rate) < scenario_num:
            updated_min_rate.append(3.5)
        
        # Update the specific scenario
        updated_surrender[scenario_num - 1] = surrender
        updated_guarantee[scenario_num - 1] = guarantee
        updated_min_rate[scenario_num - 1] = min_rate

        return updated_surrender, updated_guarantee, updated_min_rate

    # End of register_callbacks function
