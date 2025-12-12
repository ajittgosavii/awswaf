"""
Multi-Account AWS Scanner
Scans multiple AWS accounts and aggregates results for portfolio assessments
"""

import streamlit as st
import boto3
from typing import Dict, List, Optional
from datetime import datetime
from portfolio_data_model import merge_auto_detected_answers


def run_multi_account_scan(
    assessment: Dict,
    aws_helper=None,
    auto_detector=None
) -> Dict:
    """
    Run AWS infrastructure scan across multiple accounts in portfolio
    
    Args:
        assessment: Portfolio assessment dictionary
        aws_helper: AWS helper instance (provides get_account_session)
        auto_detector: WAFAutoDetector instance
    
    Returns:
        Updated assessment with scan results
    """
    
    accounts = assessment.get('accounts', [])
    
    if not accounts:
        st.error("❌ No accounts configured in portfolio")
        return assessment
    
    if len(accounts) == 1:
        st.warning("⚠️ Portfolio has only 1 account. Consider using single-account assessment.")
    
    st.info(f"🔍 Starting portfolio scan: {len(accounts)} accounts")
    
    # Initialize storage
    scan_results_by_account = {}
    auto_detected_by_account = {}
    errors_by_account = {}
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Scan each account
    for idx, account in enumerate(accounts):
        account_id = account['account_id']
        account_name = account.get('account_name', account_id)
        regions = account.get('regions', ['us-east-1'])
        
        # Update progress
        progress = (idx / len(accounts))
        progress_bar.progress(progress)
        status_text.text(f"Scanning {account_name} ({idx + 1}/{len(accounts)})...")
        
        try:
            # Get account-specific session
            session = _get_account_session(account, aws_helper)
            
            if not session:
                raise Exception(f"Failed to establish session for {account_name}")
            
            # Run scan for this account
            st.write(f"📡 Scanning {account_name} in regions: {', '.join(regions)}")
            
            scan_results = _scan_account(session, regions, account_name)
            scan_results_by_account[account_id] = scan_results
            
            # Auto-detect answers if detector provided
            if auto_detector and scan_results:
                st.write(f"🤖 Auto-detecting answers for {account_name}...")
                auto_detected = auto_detector.detect_all_answers(scan_results)
                auto_detected_by_account[account_id] = auto_detected
                
                detected_count = len(auto_detected)
                st.success(f"✅ {account_name}: {detected_count} questions auto-detected")
            else:
                st.info(f"ℹ️ {account_name}: Scan complete (no auto-detection)")
            
        except Exception as e:
            error_msg = str(e)
            st.error(f"❌ {account_name}: {error_msg}")
            errors_by_account[account_id] = error_msg
            scan_results_by_account[account_id] = {'error': error_msg}
    
    # Complete progress
    progress_bar.progress(1.0)
    status_text.text("✅ Portfolio scan complete!")
    
    # Store results in assessment
    assessment['scan_results_by_account'] = scan_results_by_account
    assessment['auto_detected_by_account'] = auto_detected_by_account
    
    if errors_by_account:
        assessment['scan_errors'] = errors_by_account
    
    # Merge auto-detected answers
    if auto_detected_by_account:
        st.info("🔀 Merging auto-detected answers across accounts...")
        merged_answers = merge_auto_detected_answers(
            auto_detected_by_account,
            accounts
        )
        assessment['auto_detected'] = merged_answers
        
        total_detected = len(merged_answers)
        st.success(f"✅ Merged results: {total_detected} questions auto-detected")
    
    # Update timestamps
    assessment['scan_completed_at'] = datetime.now().isoformat()
    assessment['updated_at'] = datetime.now().isoformat()
    
    # Summary
    successful_scans = len([r for r in scan_results_by_account.values() if 'error' not in r])
    failed_scans = len(errors_by_account)
    
    st.success(
        f"🎉 Portfolio scan complete!\n\n"
        f"✅ Successful: {successful_scans} accounts\n"
        f"❌ Failed: {failed_scans} accounts"
    )
    
    return assessment


def _get_account_session(account: Dict, aws_helper=None):
    """
    Get boto3 session for specific account
    
    Uses either:
    1. AWS helper's assume_role method (preferred)
    2. Role ARN with STS assume_role
    3. Default credentials
    """
    
    account_id = account['account_id']
    role_arn = account.get('role_arn')
    
    # Try using AWS helper if provided
    if aws_helper and hasattr(aws_helper, 'assume_role'):
        try:
            return aws_helper.assume_role(role_arn, f"WAFScan-{account_id}")
        except Exception as e:
            st.warning(f"⚠️ AWS helper failed: {e}")
    
    # Try direct STS assume_role
    if role_arn:
        try:
            sts = boto3.client('sts')
            response = sts.assume_role(
                RoleArn=role_arn,
                RoleSessionName=f"WAFAdvisorScan-{account_id}",
                DurationSeconds=3600
            )
            
            credentials = response['Credentials']
            return boto3.Session(
                aws_access_key_id=credentials['AccessKeyId'],
                aws_secret_access_key=credentials['SecretAccessKey'],
                aws_session_token=credentials['SessionToken']
            )
        except Exception as e:
            st.warning(f"⚠️ STS assume_role failed: {e}")
    
    # Fallback to default session
    st.warning(f"⚠️ Using default credentials for {account_id}")
    return boto3.Session()


def _scan_account(session, regions: List[str], account_name: str) -> Dict:
    """
    Scan single account across specified regions
    
    Returns scan results with resource counts and findings
    """
    
    scan_results = {
        'account_name': account_name,
        'scanned_at': datetime.now().isoformat(),
        'regions': regions,
        'resources': {},
        'total_resources': 0,
    }
    
    for region in regions:
        try:
            # EC2 instances
            ec2 = session.client('ec2', region_name=region)
            instances = ec2.describe_instances()
            instance_count = sum(
                len(r['Instances']) 
                for r in instances.get('Reservations', [])
            )
            
            # S3 (global service, query once)
            if region == regions[0]:
                s3 = session.client('s3')
                buckets = s3.list_buckets()
                bucket_count = len(buckets.get('Buckets', []))
            else:
                bucket_count = 0
            
            # RDS databases
            rds = session.client('rds', region_name=region)
            databases = rds.describe_db_instances()
            db_count = len(databases.get('DBInstances', []))
            
            # Lambda functions
            lambda_client = session.client('lambda', region_name=region)
            functions = lambda_client.list_functions()
            lambda_count = len(functions.get('Functions', []))
            
            # VPCs
            vpcs = ec2.describe_vpcs()
            vpc_count = len(vpcs.get('Vpcs', []))
            
            # Store results
            region_resources = {
                'ec2_instances': instance_count,
                's3_buckets': bucket_count,
                'rds_databases': db_count,
                'lambda_functions': lambda_count,
                'vpcs': vpc_count,
            }
            
            scan_results['resources'][region] = region_resources
            scan_results['total_resources'] += sum(region_resources.values())
            
        except Exception as e:
            st.warning(f"⚠️ Error scanning {region}: {e}")
            scan_results['resources'][region] = {'error': str(e)}
    
    return scan_results


def scan_single_account_quick(
    account_id: str,
    regions: List[str] = None,
    session = None
) -> Dict:
    """
    Quick scan of single account (lightweight version for testing)
    
    Args:
        account_id: AWS account ID
        regions: List of regions to scan
        session: Boto3 session (optional)
    
    Returns:
        Scan results dictionary
    """
    
    if not session:
        session = boto3.Session()
    
    if not regions:
        regions = ['us-east-1']
    
    return _scan_account(session, regions, account_id)


def validate_account_access(account: Dict) -> Dict:
    """
    Validate that we can access an AWS account
    
    Returns:
        {
            'accessible': bool,
            'error': str (if not accessible),
            'account_id': str (confirmed account ID)
        }
    """
    
    result = {
        'accessible': False,
        'error': None,
        'account_id': None
    }
    
    try:
        role_arn = account.get('role_arn')
        
        if role_arn:
            # Try to assume role
            sts = boto3.client('sts')
            response = sts.assume_role(
                RoleArn=role_arn,
                RoleSessionName='WAFAdvisorValidation',
                DurationSeconds=900  # 15 minutes
            )
            
            # Get caller identity with assumed role
            temp_session = boto3.Session(
                aws_access_key_id=response['Credentials']['AccessKeyId'],
                aws_secret_access_key=response['Credentials']['SecretAccessKey'],
                aws_session_token=response['Credentials']['SessionToken']
            )
            
            sts_client = temp_session.client('sts')
            identity = sts_client.get_caller_identity()
            
            result['accessible'] = True
            result['account_id'] = identity['Account']
        else:
            # Use default credentials
            sts = boto3.client('sts')
            identity = sts.get_caller_identity()
            
            result['accessible'] = True
            result['account_id'] = identity['Account']
    
    except Exception as e:
        result['error'] = str(e)
    
    return result


# Example usage
if __name__ == "__main__":
    # Test account validation
    test_account = {
        'account_id': '123456789012',
        'account_name': 'Test Account',
        'role_arn': 'arn:aws:iam::123456789012:role/WAFAdvisorRole',
        'regions': ['us-east-1']
    }
    
    validation = validate_account_access(test_account)
    print(f"Access validation: {validation}")
