# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import json
import time
import os
from typing import Dict, Any, Optional
from strands import tool

# Configuration variables (will be set by set_stack_config)
STACK_CONFIG = {
    'stack_name': None,
    'workflow_id': None,
    'role_arn': None,
    's3_bucket': None
}

def set_stack_config(stack_name: str, workflow_id: str, role_arn: str, s3_bucket: str):
    """Set the stack configuration for protein design tools"""
    global STACK_CONFIG
    STACK_CONFIG['stack_name'] = stack_name
    STACK_CONFIG['workflow_id'] = workflow_id
    STACK_CONFIG['role_arn'] = role_arn
    STACK_CONFIG['s3_bucket'] = s3_bucket

@tool
def trigger_aho_workflow(
    protein_sequence: str,
    num_parallel_chains: int = 10,
    num_steps: int = 100
) -> Dict[str, Any]:
    """
    Trigger AWS HealthOmics workflow for protein optimization using directed evolution.

    Args:
        protein_sequence: The amino acid sequence to optimize (string of valid amino acid characters)
        num_parallel_chains: Number of parallel optimization chains to run (default: 10)
        num_steps: Number of optimization steps per chain (default: 100)

    Returns:
        Dictionary containing workflow execution details including run ID and status
    """
    try:
        # Validate configuration
        if not all(STACK_CONFIG.values()):
            return {
                "error": "Stack configuration not initialized. Please run set_stack_config() first.",
                "config": STACK_CONFIG
            }

        # Initialize AWS clients
        omics_client = boto3.client('omics')
        s3_client = boto3.client('s3')

        # Validate protein sequence
        valid_amino_acids = set('ACDEFGHIKLMNPQRSTVWY')
        if not all(aa in valid_amino_acids for aa in protein_sequence.upper()):
            return {
                "error": "Invalid protein sequence. Must contain only valid amino acid characters: ACDEFGHIKLMNPQRSTVWY"
            }

        # Create input file for the workflow
        input_data = {
            "sequence": protein_sequence.upper(),
            "num_parallel_chains": num_parallel_chains,
            "num_steps": num_steps
        }

        # Upload input to S3
        input_key = f"inputs/protein_input_{int(time.time())}.json"
        s3_client.put_object(
            Bucket=STACK_CONFIG['s3_bucket'],
            Key=input_key,
            Body=json.dumps(input_data)
        )

        # Start the HealthOmics workflow
        response = omics_client.start_run(
            workflowId=STACK_CONFIG['workflow_id'],
            roleArn=STACK_CONFIG['role_arn'],
            parameters={
                'input_file': f"s3://{STACK_CONFIG['s3_bucket']}/{input_key}",
                'num_parallel_chains': str(num_parallel_chains),
                'num_steps': str(num_steps)
            },
            outputUri=f"s3://{STACK_CONFIG['s3_bucket']}/outputs/"
        )

        return {
            "status": "success",
            "run_id": response['id'],
            "arn": response['arn'],
            "message": f"Protein optimization workflow started successfully. Run ID: {response['id']}",
            "input_sequence": protein_sequence,
            "num_parallel_chains": num_parallel_chains,
            "num_steps": num_steps
        }

    except Exception as e:
        return {
            "error": f"Failed to trigger workflow: {str(e)}"
        }

@tool
def monitor_aho_workflow(run_id: str) -> Dict[str, Any]:
    """
    Monitor the status of a running AWS HealthOmics workflow.

    Args:
        run_id: The run ID of the workflow to monitor

    Returns:
        Dictionary containing current workflow status and progress information
    """
    try:
        # Initialize AWS client
        omics_client = boto3.client('omics')

        # Get run details
        response = omics_client.get_run(id=run_id)

        # Extract relevant information
        status_info = {
            "run_id": run_id,
            "status": response['status'],
            "workflow_id": response['workflowId'],
            "started_on": response.get('startTime', 'N/A'),
            "completed_on": response.get('stopTime', 'N/A'),
        }

        # Add output location if completed
        if response['status'] == 'COMPLETED':
            status_info['output_uri'] = response.get('outputUri', 'N/A')
            status_info['message'] = "Workflow completed successfully. Results are available in the output URI."
        elif response['status'] == 'RUNNING':
            status_info['message'] = "Workflow is currently running. Please check back later for results."
        elif response['status'] == 'FAILED':
            status_info['message'] = "Workflow failed. Please check the error logs."
            status_info['status_message'] = response.get('statusMessage', 'N/A')
        else:
            status_info['message'] = f"Workflow status: {response['status']}"

        return status_info

    except Exception as e:
        return {
            "error": f"Failed to monitor workflow: {str(e)}",
            "run_id": run_id
        }

@tool
def test_configuration() -> Dict[str, Any]:
    """
    Test the current stack configuration.

    Returns:
        Dictionary containing the current configuration status
    """
    return {
        "status": "configured" if all(STACK_CONFIG.values()) else "not_configured",
        "config": {
            "stack_name": STACK_CONFIG['stack_name'],
            "workflow_id": STACK_CONFIG['workflow_id'],
            "role_arn": "***" if STACK_CONFIG['role_arn'] else None,
            "s3_bucket": STACK_CONFIG['s3_bucket']
        }
    }
