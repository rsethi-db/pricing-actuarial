# Databricks Deployment Guide

This guide explains how to deploy the Pricing Cell Generation app within Databricks.

## Prerequisites

- Databricks workspace access
- Appropriate permissions to create and run apps
- AI endpoint configured in your workspace

## Deployment Steps

### 1. Environment Setup

Set the following environment variables in your Databricks workspace:

```bash
export DATABRICKS_HOST="your-workspace-host"
export DATABRICKS_WAREHOUSE_HTTP_PATH="/sql/1.0/warehouses/your-warehouse-id"
export DATABRICKS_AI_ENDPOINT="your-ai-endpoint-name"
export PORT=8050
```

### 2. Upload Files

Upload all app files to your Databricks workspace:
- Upload to `/Workspace/Users/{your-username}/pricing_actuarial_app/`

### 3. Install Dependencies

In a Databricks notebook, run:

```python
%pip install -r requirements_databricks.txt
```

### 4. Run the App

In a Databricks notebook:

```python
# Set environment variables
import os
os.environ['DATABRICKS_RUNTIME_VERSION'] = '1.0'  # This enables production mode

# Run the app
exec(open('app.py').read())
```

### 5. Access the App

The app will be available at:
- **Within Databricks**: Use the provided URL from Databricks
- **External**: Use Databricks App deployment for external access

## Configuration

### Environment Variables

The app automatically detects if it's running in Databricks and adjusts settings:

- **Debug mode**: Disabled in Databricks
- **Port**: Uses `PORT` environment variable or defaults to 8050
- **Host**: `0.0.0.0` for proper binding

### Database Configuration

The app uses the following tables:
- `shirlywang_insurance.fa_pricing.fa_product_brochure_parsed`
- `shirlywang_insurance.fa_pricing.fa_product_brochure_endpoint_response`
- `shirlywang_insurance.fa_pricing.fa_product_brochure_pricing_features`

## Production Considerations

1. **Security**: Ensure proper authentication and authorization
2. **Scaling**: Consider using Databricks App deployment for production
3. **Monitoring**: Set up logging and monitoring
4. **Backup**: Regular backup of uploaded files and data

## Troubleshooting

### Common Issues

1. **Port conflicts**: Change the `PORT` environment variable
2. **Permission errors**: Ensure proper workspace permissions
3. **AI endpoint errors**: Verify endpoint name and permissions

### Logs

Check Databricks driver logs for application logs and errors.

## Support

For issues specific to Databricks deployment, check:
- Databricks documentation
- Workspace administrator
- App logs in Databricks
