"""
Callbacks for the pricing cell automation app.
"""
import logging
import time
from base64 import b64decode
import pandas as pd
from dash import Input, Output, State, callback_context, html
from database import db_manager
from file_upload import file_upload_manager

logger = logging.getLogger(__name__)

def register_callbacks(dash_app):
    """Register all callbacks for the Dash app."""
    
    # Step Navigation Callbacks
    @dash_app.callback(
        [Output("step1", "style"),
         Output("step2", "style"),
         Output("step1-controls", "style"),
         Output("step2-controls", "style")],
        [Input("continue-to-step2", "n_clicks"),
         Input("back-to-step1", "n_clicks")],
        [State("upload-data", "contents")]
    )
    def navigate_steps(continue_clicks, back_clicks, upload_contents):
        """Handle navigation between steps."""
        ctx = callback_context
        
        if not ctx.triggered:
            # Initial state - show step 1
            return ({"display": "block"}, {"display": "none"}, 
                   {"display": "block"}, {"display": "none"})
        
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if trigger_id == "continue-to-step2":
            # Move to step 2
            return ({"display": "none"}, {"display": "block"}, 
                   {"display": "none"}, {"display": "block"})
        elif trigger_id == "back-to-step1":
            # Move back to step 1
            return ({"display": "block"}, {"display": "none"}, 
                   {"display": "block"}, {"display": "none"})
        
        # Default to step 1
        return ({"display": "block"}, {"display": "none"}, 
               {"display": "block"}, {"display": "none"})
    
    @dash_app.callback(
        [Output("continue-to-step2", "disabled"),
         Output("pdf-management", "style"),
         Output("uploaded-pdfs-list", "children"),
         Output("step1-status", "children")],
        [Input("upload-data", "contents")],
        [State("upload-data", "filename")]
    )
    def handle_upload_feedback(upload_contents, filenames):
        """Handle upload feedback and enable continue button."""
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
                    status_icon = "✅" if file_info['status'] == 'uploaded' else "❌"
                    status_text = "Uploaded to volumes" if file_info['status'] == 'uploaded' else f"Upload failed: {file_info.get('error', 'Unknown error')}"
                    
                    pdf_items.append(
                        html.Div([
                            html.Div([
                                html.I(className="fas fa-file-pdf pdf-icon"),
                                html.Span(file_info['filename'], className="pdf-name"),
                                html.Span(f"{status_icon} {status_text}", className="pdf-status-text")
                            ]),
                            html.Button(
                                [html.I(className="fas fa-trash me-1"), "Remove"],
                                className="pdf-remove-btn",
                                id={"type": "remove-pdf", "index": i}
                            )
                        ], className="pdf-item")
                    )
                
                # Check if all files uploaded successfully
                success_count = sum(1 for f in uploaded_files if f['status'] == 'uploaded')
                if success_count == len(uploaded_files):
                    status_message = f"✅ {success_count} file(s) uploaded successfully to Databricks volumes! You can now proceed to Step 2."
                else:
                    status_message = f"⚠️ {success_count}/{len(uploaded_files)} files uploaded successfully. Some uploads failed."
                
                return False, {"display": "block"}, pdf_items, status_message
            return True, {"display": "none"}, [], ""
        except Exception as e:
            logger.error(f"Error in handle_upload_feedback: {e}")
            return True, {"display": "none"}, [], f"Error: {str(e)}"

    @dash_app.callback(
        [Output("workflow-status", "children"),
         Output("workflow-results", "data"),
         Output("export-btn", "disabled"),
         Output("loading-modal", "is_open"),
         Output("progress-bar", "value"),
         Output("progress-text", "children"),
         Output("results-section", "style")],
        [Input("parse-ai-btn", "n_clicks")],
        [State("upload-data", "contents"),
         State("upload-data", "filename")]
    )
    def parse_and_run_ai(n_clicks, contents, filenames):
        """Main callback for parsing and running AI analysis."""
        if not n_clicks:
            return "", [], True, False, 0, "", {"display": "none"}

        try:
            # Validate inputs
            if not contents or not filenames:
                return "⚠️ Please upload at least one file before processing.", [], True, False, 0, "", {"display": "none"}
            
            # Check file types
            valid_extensions = ['.pdf']
            invalid_files = [f for f in filenames if not any(f.lower().endswith(ext) for ext in valid_extensions)]
            if invalid_files:
                return f"❌ Invalid file types detected: {', '.join(invalid_files)}. Please upload only PDF files.", [], True, False, 0, "", {"display": "none"}
            
            # Show loading modal with initial progress
            status_message = "🔄 Processing files... Please wait."
            results_data = []
            export_disabled = True
            modal_open = True
            progress_value = 10
            progress_text = "Starting file upload..."
            
            # Step 1: Upload PDFs
            try:
                progress_value = 20
                progress_text = f"Uploading {len(filenames)} file(s)..."
                
                for i, (content, filename) in enumerate(zip(contents, filenames)):
                    _, content_string = content.split(",")
                    decoded = b64decode(content_string)
                    file_upload_manager.upload_file_to_volume(decoded, filename)
                    # Update progress for each file
                    progress_value = 20 + (i + 1) * 10 // len(filenames)
                    progress_text = f"Uploaded {i + 1}/{len(filenames)} files..."
                
                logger.info(f"Successfully uploaded {len(filenames)} files")
            except Exception as e:
                logger.error(f"Failed to upload files: {e}")
                return f"❌ Failed to upload files: {str(e)}", [], True, False, 0, "", {"display": "none"}

            # Step 2: Define SQL queries
            volume_path = file_upload_manager.volume_path
            
            parse_query = f"""
            CREATE OR REPLACE TABLE shirlywang_insurance.fa_pricing.fa_product_brochure_uploaded_parsed AS
            WITH all_files AS (
                SELECT path, content
                FROM READ_FILES('{volume_path}', format => 'binaryFile')
                ORDER BY path ASC
            ),
            parsed_documents AS (
                SELECT path, ai_parse_document(content) AS parsed
                FROM all_files
            ),
            pages_exploded AS (
                SELECT path, page:content AS content
                FROM parsed_documents
                LATERAL VIEW posexplode(TRY_CAST(parsed:document:pages AS ARRAY<VARIANT>)) AS page_idx, page
                WHERE parsed:document:pages IS NOT NULL
            ),
            concatenated AS (
                SELECT path, CONCAT_WS('\\n\\n', COLLECT_LIST(content)) AS full_content
                FROM pages_exploded
                GROUP BY path
            )
            SELECT * FROM concatenated
            """

            batch_table = "shirlywang_insurance.fa_pricing.fa_product_brochure_uploaded_agentbricks_response"
            ai_query_sql = f"""
            CREATE OR REPLACE TABLE {batch_table} TBLPROPERTIES ('delta.feature.variantType-preview' = 'supported') AS
            SELECT
                full_content AS input,
                ai_query('kie-b06809e4-endpoint', full_content, failOnError => false) AS response,
                current_timestamp() AS timestamp
            FROM shirlywang_insurance.fa_pricing.fa_product_brochure_uploaded_parsed
            WHERE full_content IS NOT NULL
            """
            
            # Add a test query to check if AI endpoint is working
            test_ai_sql = """
            SELECT ai_query('kie-b06809e4-endpoint', 'Test insurance product with minimum premium $1000', failOnError => false) AS test_response
            """

            features_table = "shirlywang_insurance.fa_pricing.fa_product_uploaded_brochures_pricing_features"
            
            # Create table if it doesn't exist
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {features_table} (
                input STRING,
                issuing_company ARRAY<STRING>,
                min_premium STRING,
                withdrawal_options ARRAY<STRING>,
                interest_crediting STRING,
                surrender_charge_schedule STRING,
                death_benefit STRING,
                available_riders ARRAY<STRING>,
                issue_ages STRING,
                guarantee_period STRING
            )
            """
            
            # Insert data directly into the existing table - using correct JSON path parsing
            insert_data_sql = f"""
            INSERT INTO {features_table}
            SELECT
                input,
                from_json(
                    get_json_object(cast(response.result AS STRING), '$.issuing_company'),
                    'array<string>'
                ) AS issuing_company,
                get_json_object(cast(response.result AS STRING), '$.minimum_premium') AS min_premium,
                from_json(
                    get_json_object(cast(response.result AS STRING), '$.withdrawal_options'),
                    'array<string>'
                ) AS withdrawal_options,
                get_json_object(cast(response.result AS STRING), '$.interest_crediting') AS interest_crediting,
                get_json_object(cast(response.result AS STRING), '$.surrender_charge_schedule') AS surrender_charge_schedule,
                get_json_object(cast(response.result AS STRING), '$.death_benefit') AS death_benefit,
                from_json(
                    get_json_object(cast(response.result AS STRING), '$.available_riders'),
                    'array<string>'
                ) AS available_riders,
                get_json_object(cast(response.result AS STRING), '$.issue_ages') AS issue_ages,
                get_json_object(cast(response.result AS STRING), '$.guarantee_period') AS guarantee_period
            FROM {batch_table}
            WHERE response IS NOT NULL
            """

            # Query the existing table
            preview_sql = f"SELECT * FROM {features_table} ORDER BY input LIMIT 20"
            
            # Add debugging queries to check what's happening
            debug_count_sql = f"SELECT COUNT(*) as total_rows FROM {features_table}"
            debug_schema_sql = f"DESCRIBE {features_table}"
            debug_batch_data_sql = f"SELECT input, response FROM {batch_table} LIMIT 1"

            # Step 3: Execute all queries
            try:
                progress_value = 40
                progress_text = "Parsing documents with AI..."
                
                # First test the AI endpoint
                logger.info("Testing AI endpoint...")
                test_result = db_manager.execute_query(test_ai_sql)
                if test_result is not None and not test_result.empty:
                    logger.info(f"AI endpoint test response: {test_result.iloc[0]['test_response']}")
                else:
                    logger.warning("AI endpoint test failed - no response")
                
                queries = [parse_query, ai_query_sql, debug_batch_data_sql, create_table_sql, insert_data_sql, debug_count_sql, debug_schema_sql, preview_sql]
                results = db_manager.execute_multiple_queries(queries)
                
                progress_value = 70
                progress_text = "Processing AI responses..."
                
                logger.info("Successfully executed all database queries")
                
                # Debug: Check what the debug queries returned
                if len(results) >= 7:
                    batch_data_result = results[2]  # debug_batch_data_sql
                    count_result = results[4]  # debug_count_sql
                    schema_result = results[5]  # debug_schema_sql
                    preview_result = results[6]  # preview_sql
                    
                    if batch_data_result is not None and not batch_data_result.empty:
                        logger.info(f"Batch table sample data: {batch_data_result.iloc[0].to_dict()}")
                    else:
                        logger.warning("Could not get batch table sample data")
                    
                    if count_result is not None and not count_result.empty:
                        total_rows = count_result.iloc[0]['total_rows']
                        logger.info(f"Total rows in {features_table}: {total_rows}")
                    else:
                        logger.warning("Could not get row count from features table")
                    
                    if schema_result is not None and not schema_result.empty:
                        logger.info(f"Table schema: {schema_result.to_dict('records')}")
                    else:
                        logger.warning("Could not get table schema")
            except Exception as e:
                logger.error(f"Database query execution failed: {e}")
                return f"❌ Database operation failed: {str(e)}", [], True, False, 0, "", {"display": "none"}
            
            # Get the preview results (last query)
            df = results[-1]
            
            progress_value = 90
            progress_text = "Finalizing results..."
            
            # Debug: Log the results
            logger.info(f"Preview query returned {len(df) if df is not None else 0} rows")
            if df is not None and not df.empty:
                logger.info(f"Sample data: {df.head().to_dict()}")
            else:
                logger.warning("No data returned from preview query")
                
                # Check intermediate tables
                try:
                    check_parsed = db_manager.execute_query("SELECT COUNT(*) as count FROM shirlywang_insurance.fa_pricing.fa_product_brochure_uploaded_parsed")
                    logger.info(f"Parsed table has {check_parsed.iloc[0]['count'] if check_parsed is not None else 0} rows")
                    
                    check_batch = db_manager.execute_query("SELECT COUNT(*) as count FROM shirlywang_insurance.fa_pricing.fa_product_brochure_uploaded_agentbricks_response")
                    logger.info(f"Batch table has {check_batch.iloc[0]['count'] if check_batch is not None else 0} rows")
                    
                    # Check if AI responses are NULL
                    check_responses = db_manager.execute_query("SELECT COUNT(*) as null_count FROM shirlywang_insurance.fa_pricing.fa_product_brochure_uploaded_agentbricks_response WHERE response IS NULL")
                    logger.info(f"NULL responses: {check_responses.iloc[0]['null_count'] if check_responses is not None else 0}")
                    
                    # Check sample AI responses
                    sample_responses = db_manager.execute_query("SELECT response FROM shirlywang_insurance.fa_pricing.fa_product_brochure_uploaded_agentbricks_response LIMIT 1")
                    if sample_responses is not None and not sample_responses.empty:
                        logger.info(f"Sample AI response: {sample_responses.iloc[0]['response']}")
                    else:
                        logger.warning("No AI responses found")
                    
                except Exception as e:
                    logger.error(f"Error checking intermediate tables: {e}")
            
            if df is not None and not df.empty:
                # Convert arrays to strings for DataTable display
                array_cols = ["issuing_company", "withdrawal_options", "available_riders"]
                for col in array_cols:
                    if col in df.columns:
                        df[col] = df[col].apply(lambda x: ", ".join(x) if isinstance(x, list) else "")

                status_message = f"✅ Workflow completed successfully! {len(df)} rows processed."
                results_data = df.to_dict("records")
                export_disabled = False
                progress_value = 100
                progress_text = f"Complete! {len(df)} rows processed successfully."
                results_style = {"display": "block"}
            else:
                status_message = "⚠️ No results found. Please check your uploaded files."
                results_data = []
                export_disabled = True
                progress_value = 100
                progress_text = "Complete - No results found."
                results_style = {"display": "none"}

            return status_message, results_data, export_disabled, False, progress_value, progress_text, results_style

        except Exception as e:
            logger.exception("Workflow failed")
            error_message = f"❌ Workflow failed: {str(e)}"
            return error_message, [], True, False, 0, "Error occurred during processing", {"display": "none"}

    @dash_app.callback(
        Output("upload-feedback", "children"),
        [Input("upload-data", "contents")],
        [State("upload-data", "filename")]
    )
    def update_upload_feedback(contents, filenames):
        """Update upload feedback when files are selected."""
        if contents and filenames:
            file_count = len(filenames)
            file_names = ", ".join(filenames[:3])  # Show first 3 files
            if file_count > 3:
                file_names += f" and {file_count - 3} more files"
            
            import dash_bootstrap_components as dbc
            return dbc.Alert(
                f"📁 {file_count} file(s) selected: {file_names}",
                color="success",
                className="mb-0"
            )
        return ""

    @dash_app.callback(
        Output("workflow-results", "export_format"),
        [Input("export-btn", "n_clicks")]
    )
    def handle_export(n_clicks):
        """Handle export button click."""
        if n_clicks:
            return "csv"
        return "none"

    @dash_app.callback(
        [Output("step-nav-1", "className"),
         Output("step-nav-2", "className"),
         Output("step-nav-3", "className"),
         Output("step-nav-4", "className")],
        [Input("continue-to-step2", "n_clicks"),
         Input("back-to-step1", "n_clicks"),
         Input("parse-ai-btn", "n_clicks")],
        [State("upload-data", "contents")]
    )
    def update_step_navigation(continue_clicks, back_clicks, parse_clicks, upload_contents):
        """Update step navigation classes based on current step."""
        ctx = callback_context
        
        if not ctx.triggered:
            # Initial state - step 1 active if files uploaded, otherwise pending
            if upload_contents:
                return ("step-item active", "step-item pending", "step-item pending", "step-item pending")
            return ("step-item pending", "step-item pending", "step-item pending", "step-item pending")
        
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if trigger_id == "continue-to-step2":
            # Move to step 2 - step 1 completed, step 2 active
            return ("step-item completed", "step-item active", "step-item pending", "step-item pending")
        elif trigger_id == "back-to-step1":
            # Move back to step 1 - step 1 active, others pending
            return ("step-item active", "step-item pending", "step-item pending", "step-item pending")
        elif trigger_id == "parse-ai-btn":
            # After AI processing - step 1 completed, step 2 completed, step 3 active
            return ("step-item completed", "step-item completed", "step-item active", "step-item pending")
        
        # Default to step 1 active if files uploaded
        if upload_contents:
            return ("step-item active", "step-item pending", "step-item pending", "step-item pending")
        return ("step-item pending", "step-item pending", "step-item pending", "step-item pending")
