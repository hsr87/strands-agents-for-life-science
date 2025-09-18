import boto3
import json
import os
import uuid
import time
from typing import Dict, Any, Optional
from strands import tool
from urllib.parse import urlparse

# Global configuration that can be set from notebook
_STACK_CONFIG = {}

def set_stack_config(stack_name: str, workflow_id: str = None, role_arn: str = None, s3_bucket: str = None):
    """Set the stack configuration for the tools"""
    global _STACK_CONFIG
    _STACK_CONFIG = {
        'stack_name': stack_name,
        'workflow_id': workflow_id,
        'role_arn': role_arn,
        's3_bucket': s3_bucket
    }

def _get_stack_outputs():
    """Get configuration from CloudFormation stack outputs"""
    try:
        # Use global config if available, otherwise environment variable or default
        stack_name = _STACK_CONFIG.get('stack_name') or os.environ.get('STACK_NAME', 'pppp')
        
        cf_client = boto3.client('cloudformation')
        stack_detail = cf_client.describe_stacks(StackName=stack_name)
        outputs = stack_detail['Stacks'][0].get('Outputs', [])
        
        config = {'s3_bucket': 'asadrad-multimodal-us-east-1'}  # Default bucket
        for output in outputs:
            key = output['OutputKey']
            if key == 'WorkflowId':
                config['workflow_id'] = output['OutputValue']
            elif key == 'WorkflowExecutionRoleArn':
                config['role_arn'] = output['OutputValue']
        
        # Override with global config if set
        if _STACK_CONFIG.get('workflow_id'):
            config['workflow_id'] = _STACK_CONFIG['workflow_id']
        if _STACK_CONFIG.get('role_arn'):
            config['role_arn'] = _STACK_CONFIG['role_arn']
        if _STACK_CONFIG.get('s3_bucket'):
            config['s3_bucket'] = _STACK_CONFIG['s3_bucket']
        
        return config
    except Exception as e:
        print(f"Error getting stack outputs: {e}")
        return {}

@tool
def test_configuration() -> str:
    """Test the configuration retrieval"""
    stack_config = _get_stack_outputs()
    return f"Stack config: {stack_config}"

@tool
def trigger_aho_workflow(
    seed_sequence: str,
    runName: Optional[str] = None,
    outputUri: Optional[str] = None,
    esm_model_files: Optional[str] = None,
    onehotcnn_model_files: Optional[str] = None,
    output_type: Optional[str] = None,
    parallel_chains: Optional[str] = None,
    n_steps: Optional[str] = None,
    max_mutations: Optional[str] = None
) -> str:
    """
    Trigger the AWS HealthOmics workflow for protein design optimization
    
    Args:
        seed_sequence: The input protein sequence to optimize
        runName: Name for the workflow run (optional)
        outputUri: S3 URI where the workflow outputs will be stored (optional)
        esm_model_files: S3 directory storing ESM pLM model files (optional)
        onehotcnn_model_files: S3 directory storing Onehot CNN predictor model files (optional)
        output_type: Output type, can be 'best', 'last', or 'all' variants (optional)
        parallel_chains: Number of MCMC chains to run in parallel (optional)
        n_steps: Number of MCMC steps per chain (optional)
        max_mutations: Maximum number of mutations per variant (optional)
    
    Returns:
        String with workflow run information
    """
    try:
        # Get configuration from CloudFormation stack or environment
        stack_config = _get_stack_outputs()
        DEFAULT_WORKFLOW_ID = stack_config.get('workflow_id')
        DEFAULT_ROLE_ARN = stack_config.get('role_arn')
        DEFAULT_S3_BUCKET = stack_config.get('s3_bucket')
        
        # Get AWS account and region info
        sts_client = boto3.client('sts')
        account_id = sts_client.get_caller_identity()['Account']
        region = boto3.Session().region_name
        
        # Initialize clients
        omics_client = boto3.client('omics')
        
        # Validate inputs
        if not seed_sequence:
            return "Error: seed_sequence is required"
        
        # Validate amino acid sequence
        valid_amino_acids = set('ACDEFGHIKLMNPQRSTVWY')
        if not all(aa in valid_amino_acids for aa in seed_sequence.upper()):
            return "Error: Invalid amino acid sequence. Only standard 20 amino acids are allowed."
        
        if not DEFAULT_WORKFLOW_ID or not DEFAULT_ROLE_ARN or not DEFAULT_S3_BUCKET:
            return "Error: Workflow configuration not properly set. Please check CloudFormation stack outputs."
        
        # Use defaults from environment or provided values
        workflow_id = DEFAULT_WORKFLOW_ID
        role_arn = DEFAULT_ROLE_ARN
        container_image = f"{account_id}.dkr.ecr.{region}.amazonaws.com/protein-design-evoprotgrad:latest"
        
        # Generate unique run name if not provided
        run_name = f"workflow-run-{uuid.uuid4().hex[:8]}"
        
        # Use default S3 output location if not provided
        output_uri = f"s3://{DEFAULT_S3_BUCKET}/outputs/{run_name}/"
        
        # Get all workflow parameters with defaults
        esm_files = esm_model_files or f"s3://{DEFAULT_S3_BUCKET}/models/esm2_t6_8M_UR50D/"
        out_type = output_type or "all"
        
        # Convert numeric parameters
        try:
            p_chains = int(parallel_chains) if parallel_chains else 10
        except (ValueError, TypeError):
            p_chains = 10
            
        try:
            steps = int(n_steps) if n_steps else 100
        except (ValueError, TypeError):
            steps = 100
            
        try:
            mutations = int(max_mutations) if max_mutations else 15
        except (ValueError, TypeError):
            mutations = 15
        
        # Prepare workflow parameters
        workflow_parameters = {
            "container_image": container_image,
            "seed_sequence": seed_sequence.upper(),
            "esm_model_files": esm_files  # Pass S3 path to workflow
        }
        
        # Add optional parameters
        if onehotcnn_model_files:
            workflow_parameters["onehotcnn_model_files"] = onehotcnn_model_files
            
        workflow_parameters["output_type"] = out_type
        workflow_parameters["parallel_chains"] = p_chains
        workflow_parameters["n_steps"] = steps
        workflow_parameters["max_mutations"] = mutations
        
        # Start the workflow run
        response = omics_client.start_run(
            workflowId=workflow_id,
            name=run_name,
            parameters=workflow_parameters,
            outputUri=output_uri,
            roleArn=role_arn
        )
        
        # Format response
        result = f"""Successfully started protein optimization workflow.

Run ID: {response['id']}
Status: {response['status']}
Output URI: {output_uri}

Optimization parameters:
- Seed sequence: {seed_sequence[:20]}... ({len(seed_sequence)} amino acids)
- Parallel chains: {p_chains}
- Steps per chain: {steps}
- Max mutations: {mutations}
- Output type: {out_type}

You can check the status later by asking me to 'monitor workflow run {response['id']}'"""
        
        return result
        
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def monitor_aho_workflow(
    runId: str,
    waitForCompletion: Optional[bool] = None,
    pollIntervalSeconds: Optional[int] = None,
    maxWaitTimeMinutes: Optional[int] = None
) -> str:
    """
    Monitor the status of a running AWS HealthOmics workflow and retrieve results when complete
    
    Args:
        runId: The ID of the HealthOmics workflow run to monitor
        waitForCompletion: Whether to wait for the workflow to complete before returning (optional, defaults to True)
        pollIntervalSeconds: Time between status checks in seconds (optional, defaults to 30)
        maxWaitTimeMinutes: Maximum time to wait for workflow completion in minutes (optional, defaults to 30)
    
    Returns:
        String with workflow status and results if completed
    """
    try:
        # Initialize clients
        omics_client = boto3.client('omics')
        s3_client = boto3.client('s3')
        
        if not runId:
            return "Error: runId parameter is required"
        
        # Get workflow run status
        run_response = omics_client.get_run(id=runId)
        status = run_response.get('status')
        
        # Format response with current status
        response_text = f"Run ID: {runId}\nCurrent Status: {status}\n"
        if run_response.get('name'):
            response_text += f"Run Name: {run_response.get('name')}\n"
        if run_response.get('startTime'):
            response_text += f"Start Time: {run_response.get('startTime').isoformat()}\n"
        
        if status == 'COMPLETED':
            # Include results if completed
            response_text += _get_run_results(run_response, s3_client)
        elif status == 'FAILED':
            response_text += f"Failed with message: {run_response.get('statusMessage')}\n"
        else:
            response_text += "\nThe workflow is still running. You can check again later with the same run ID.\n"
            response_text += f"To check again, ask me to 'monitor workflow run {runId}'."
        
        return response_text
        
    except Exception as e:
        return f"Error monitoring workflow: {str(e)}"


def _get_run_results(run_response: Dict[str, Any], s3_client) -> str:
    """
    Helper function to retrieve workflow results from S3.
    """
    try:
        output_text = f"Completed at: {run_response.get('stopTime').isoformat() if run_response.get('stopTime') else 'Unknown'}\n\n"
        
        # Get output files
        output_uri = run_response.get('outputUri')
        if not output_uri:
            return output_text + "No output URI provided."
            
        # Parse the S3 URI
        parsed_uri = urlparse(output_uri)
        bucket = parsed_uri.netloc
        prefix = parsed_uri.path.lstrip('/')
        
        # List objects in the output location
        try:
            s3_response = s3_client.list_objects_v2(
                Bucket=bucket,
                Prefix=prefix
            )
            
            # Add output files to the response
            output_files = []
            for obj in s3_response.get('Contents', []):
                if obj['Key'].endswith('.json') or obj['Key'].endswith('.txt') or obj['Key'].endswith('.csv'):
                    file_key = obj['Key']
                    file_size = obj['Size']
                    
                    # For small text files, include the content
                    if file_size < 10240 and (file_key.endswith('.json') or file_key.endswith('.txt') or file_key.endswith('.csv')):
                        try:
                            file_obj = s3_client.get_object(Bucket=bucket, Key=file_key)
                            file_content = file_obj['Body'].read().decode('utf-8')
                            
                            output_files.append({
                                'key': file_key,
                                'size': file_size,
                                'content': file_content
                            })
                        except Exception as e:
                            output_files.append({
                                'key': file_key,
                                'size': file_size,
                                'error': str(e)
                            })
                    else:
                        output_files.append({
                            'key': file_key,
                            'size': file_size,
                            'url': f"s3://{bucket}/{file_key}"
                        })
            
            if output_files:
                output_text += "Output files:\n"
                for file in output_files:
                    output_text += f"- {file.get('key')} ({file.get('size')} bytes)\n"
                    if 'content' in file and file.get('key').endswith('de_results.csv'):
                        output_text += f"Results summary:\n{file.get('content')[:1000]}...\n\n"
            else:
                output_text += "No output files found."
        except Exception as e:
            output_text += f"Error listing S3 objects: {str(e)}"
            
        return output_text
        
    except Exception as e:
        return f"Error retrieving results: {str(e)}"
