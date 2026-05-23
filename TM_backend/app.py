# app.py

from flask_cors import CORS
from flask import Flask, jsonify, request
from datetime import datetime, timedelta
import random
import time
from collections import defaultdict

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# ========================================
# IN-MEMORY DATA STORAGE
# ========================================
# This list will store all our logs
logs = []

# ========================================
# HELPER DATA
# ========================================

# Sample data for generating realistic logs
USERS = ['alice', 'bob', 'charlie', 'diana', 'admin', 'root', 'john', 'sarah']
NORMAL_ACTIONS = ['login', 'view_dashboard', 'update_profile', 'view_report', 'logout']
ADMIN_ACTIONS = ['delete_user', 'modify_permissions', 'view_logs', 'backup_database', 'change_settings']
LOCATIONS = ['New York', 'London', 'Tokyo', 'Paris', 'Sydney', 'Berlin', 'Mumbai', 'Toronto']
IP_PREFIXES = ['192.168.1', '10.0.0', '172.16.0', '203.0.113']

# ========================================
# UTILITY FUNCTIONS
# ========================================

def generate_ip():
    """Generate a random IP address"""
    prefix = random.choice(IP_PREFIXES)
    last_octet = random.randint(1, 254)
    return f"{prefix}.{last_octet}"

def get_timestamp(offset_minutes=0):
    """Get current timestamp or offset by minutes"""
    time = datetime.now() + timedelta(minutes=offset_minutes)
    return time.strftime('%Y-%m-%d %H:%M:%S')

# ========================================
# NORMAL LOG GENERATION - FIXED VERSION
# ========================================

def generate_normal_log():
    """
    Generate a single normal/legitimate log entry
    FIXED: Ensures logs won't accidentally trigger threat detection
    """
    # Use current time with random offset to avoid clustering
    time_offset = random.randint(-120, 0)  # Random time in last 2 hours
    
    # Pick a random user
    user = random.choice(USERS)
    
    # Normal users should NOT be admin for normal logs
    # This prevents admin_misuse false positives
    if user in ['admin', 'root']:
        user = random.choice(['alice', 'bob', 'charlie', 'diana', 'john', 'sarah'])
    
    # Pick a varied action (not too repetitive)
    action = random.choice(NORMAL_ACTIONS)
    
    # Generate timestamp during NORMAL hours (avoid 2-4 AM)
    current_time = datetime.now() + timedelta(minutes=time_offset)
    
    # If generated time is between 2-4 AM, shift to daytime
    if 2 <= current_time.hour <= 4:
        current_time = current_time.replace(hour=random.randint(9, 18))  # 9 AM - 6 PM
    
    log = {
        'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S'),
        'user': user,
        'action': action,
        'status': 'success',  # Normal logs are always successful
        'ip': generate_ip(),  # Random IP each time
        'location': random.choice(LOCATIONS),  # Random location
        'data_transferred_mb': round(random.uniform(0.1, 5.0), 2),  # Small amounts
        'threat_type': 'normal'
    }
    return log

# ========================================
# THREAT LOG GENERATION FUNCTIONS
# ========================================

def generate_brute_force_logs(count=10):
    """
    Generate brute force attack logs
    Characteristics: Multiple failed login attempts from same IP in short time
    """
    attack_logs = []
    attacker_ip = generate_ip()
    target_user = random.choice(USERS)
    attacker_location = random.choice(LOCATIONS)
    
    for i in range(count):
        log = {
            'timestamp': get_timestamp(offset_minutes=-count + i),
            'user': target_user,
            'action': 'login',
            'status': 'failed',  # Multiple failures indicate brute force
            'ip': attacker_ip,  # Same IP for all attempts
            'location': attacker_location,
            'data_transferred_mb': 0.01,
            'threat_type': 'brute_force',
            'attempt_number': i + 1
        }
        attack_logs.append(log)
    
    return attack_logs

def generate_data_exfiltration_logs(count=3):
    """
    Generate data exfiltration logs
    Characteristics: Unusually high data transfer volumes
    """
    attack_logs = []
    suspicious_user = random.choice(USERS)
    suspicious_ip = generate_ip()
    location = random.choice(LOCATIONS)
    
    for i in range(count):
        log = {
            'timestamp': get_timestamp(offset_minutes=-count + i),
            'user': suspicious_user,
            'action': 'download_file',
            'status': 'success',
            'ip': suspicious_ip,
            'location': location,
            'data_transferred_mb': round(random.uniform(500, 2000), 2),  # Very high data transfer
            'threat_type': 'data_exfiltration',
            'file_name': f'sensitive_data_{i}.zip'
        }
        attack_logs.append(log)
    
    return attack_logs

def generate_impossible_travel_logs(count=2):
    """
    Generate impossible travel logs
    Characteristics: Same user accessing from different locations in impossibly short time
    """
    attack_logs = []
    user = random.choice(USERS)
    
    # First login from one location
    log1 = {
        'timestamp': get_timestamp(offset_minutes=-30),
        'user': user,
        'action': 'login',
        'status': 'success',
        'ip': generate_ip(),
        'location': 'New York',
        'data_transferred_mb': 0.5,
        'threat_type': 'impossible_travel'
    }
    attack_logs.append(log1)
    
    # Second login from distant location just 10 minutes later
    log2 = {
        'timestamp': get_timestamp(offset_minutes=-20),
        'user': user,
        'action': 'login',
        'status': 'success',
        'ip': generate_ip(),
        'location': 'Tokyo',  # Different continent
        'data_transferred_mb': 0.5,
        'threat_type': 'impossible_travel'
    }
    attack_logs.append(log2)
    
    return attack_logs

def generate_suspicious_behavior_logs(count=5):
    """
    Generate suspicious user behavior logs
    Characteristics: Activity at unusual hours (e.g., 2-4 AM)
    """
    attack_logs = []
    suspicious_user = random.choice(USERS)
    suspicious_ip = generate_ip()
    location = random.choice(LOCATIONS)
    
    for i in range(count):
        # Create timestamp for unusual hours (2-4 AM)
        unusual_time = datetime.now().replace(hour=random.randint(2, 4), minute=random.randint(0, 59))
        
        log = {
            'timestamp': unusual_time.strftime('%Y-%m-%d %H:%M:%S'),
            'user': suspicious_user,
            'action': random.choice(['access_database', 'view_confidential', 'download_file']),
            'status': 'success',
            'ip': suspicious_ip,
            'location': location,
            'data_transferred_mb': round(random.uniform(10, 50), 2),
            'threat_type': 'suspicious_behavior',
            'hour': unusual_time.hour
        }
        attack_logs.append(log)
    
    return attack_logs

def generate_admin_misuse_logs(count=15):
    """
    Generate admin misuse logs
    Characteristics: Admin performing excessive actions in short time
    """
    attack_logs = []
    admin_user = 'admin'
    admin_ip = generate_ip()
    admin_location = random.choice(LOCATIONS)
    
    for i in range(count):
        log = {
            'timestamp': get_timestamp(offset_minutes=-count + i),
            'user': admin_user,
            'action': random.choice(ADMIN_ACTIONS),
            'status': 'success',
            'ip': admin_ip,
            'location': admin_location,
            'data_transferred_mb': round(random.uniform(1, 10), 2),
            'threat_type': 'admin_misuse',
            'action_count': i + 1
        }
        attack_logs.append(log)
    
    return attack_logs

def generate_background_activity_logs(count=10):
    """
    Generate background/automated activity logs
    Characteristics: Repeated scheduled tasks at regular intervals
    """
    attack_logs = []
    bot_user = random.choice(USERS)
    bot_ip = generate_ip()
    task_location = random.choice(LOCATIONS)
    
    for i in range(count):
        log = {
            'timestamp': get_timestamp(offset_minutes=-(count * 5) + (i * 5)),  # Every 5 minutes
            'user': bot_user,
            'action': 'run_scheduled_task',
            'status': 'success',
            'ip': bot_ip,
            'location': task_location,
            'data_transferred_mb': 0.1,
            'threat_type': 'background_activity',
            'task_name': 'auto_backup_script',
            'interval_minutes': 5
        }
        attack_logs.append(log)
    
    return attack_logs
# ========================================
# DETECTION SYSTEM - UNIFIED & FIXED
# ========================================

def parse_timestamp(timestamp_str):
    """Convert timestamp string to datetime object"""
    try:
        return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
    except:
        return datetime.now()

def get_time_window_logs(all_logs, reference_time, minutes=30):
    """Get logs within a specific time window"""
    window_logs = []
    for log in all_logs:
        try:
            log_time = parse_timestamp(log['timestamp'])
            time_diff = abs((reference_time - log_time).total_seconds() / 60)
            if time_diff <= minutes:
                window_logs.append(log)
        except:
            continue
    return window_logs

def detect_brute_force(current_log, all_logs):
    """Detect brute force attacks - ONLY on failed logins"""
    if current_log.get('action') != 'login':
        return None
    if current_log.get('status') != 'failed':
        return None
    
    current_ip = current_log.get('ip')
    current_time = parse_timestamp(current_log['timestamp'])
    recent_logs = get_time_window_logs(all_logs, current_time, minutes=30)
    
    failed_attempts = 0
    for log in recent_logs:
        if (log.get('action') == 'login' and 
            log.get('status') == 'failed' and 
            log.get('ip') == current_ip):
            failed_attempts += 1
    
    if failed_attempts > 5:
        anomaly_score = min(0.7 + (failed_attempts - 6) * 0.075, 1.0)
        
        return {
            'threat_detected': True,
            'threat_type': 'brute_force',
            'anomaly_score': round(anomaly_score, 2),
            'reason': f'Detected {failed_attempts} failed login attempts from IP {current_ip} within 30 minutes',
            'recommendation': f'Block IP address {current_ip} and notify security team. Implement account lockout policy.',
            'metadata': {
                'failed_attempts': failed_attempts,
                'target_ip': current_ip
            }
        }
    
    return None

def detect_data_exfiltration(current_log, all_logs):
    """Detect data exfiltration - ONLY for very large transfers"""
    data_transferred = current_log.get('data_transferred_mb', 0)
    
    if data_transferred > 300:
        if data_transferred >= 1000:
            anomaly_score = 1.0
        else:
            anomaly_score = 0.7 + ((data_transferred - 300) / 700) * 0.3
        
        return {
            'threat_detected': True,
            'threat_type': 'data_exfiltration',
            'anomaly_score': round(anomaly_score, 2),
            'reason': f'Unusually high data transfer detected: {data_transferred} MB by user {current_log.get("user")}',
            'recommendation': f'Investigate user {current_log.get("user")} activity. Review downloaded files and restrict data transfer permissions.',
            'metadata': {
                'data_transferred_mb': data_transferred
            }
        }
    
    return None

def detect_impossible_travel(current_log, all_logs):
    """Detect impossible travel - ONLY for geographically impossible scenarios"""
    if current_log.get('action') != 'login':
        return None
    if current_log.get('status') != 'success':
        return None
    
    current_user = current_log.get('user')
    current_location = current_log.get('location')
    current_time = parse_timestamp(current_log['timestamp'])
    recent_logs = get_time_window_logs(all_logs, current_time, minutes=60)
    
    different_locations = []
    for log in recent_logs:
        if (log.get('action') == 'login' and 
            log.get('user') == current_user and 
            log.get('location') != current_location and
            log.get('status') == 'success' and
            log.get('timestamp') != current_log.get('timestamp')):
            different_locations.append({
                'location': log.get('location'),
                'timestamp': log.get('timestamp')
            })
    
    if len(different_locations) > 0:
        other_location = different_locations[0]['location']
        
        return {
            'threat_detected': True,
            'threat_type': 'impossible_travel',
            'anomaly_score': 0.85,
            'reason': f'User {current_user} logged in from {current_location} and {other_location} within 60 minutes',
            'recommendation': f'Suspend account {current_user} immediately. Require multi-factor authentication and password reset.',
            'metadata': {
                'locations': [current_location, other_location]
            }
        }
    
    return None

def detect_suspicious_behavior(current_log, all_logs):
    """Detect suspicious behavior - ONLY for actual off-hours (2-4 AM)"""
    try:
        timestamp = parse_timestamp(current_log['timestamp'])
        hour = timestamp.hour
    except:
        return None
    
    if 2 <= hour <= 4:
        sensitive_actions = ['access_database', 'view_confidential', 'download_file']
        
        if current_log.get('action') in sensitive_actions:
            anomaly_score = 0.8
        else:
            anomaly_score = 0.6
        
        return {
            'threat_detected': True,
            'threat_type': 'suspicious_behavior',
            'anomaly_score': anomaly_score,
            'reason': f'User {current_log.get("user")} performed action "{current_log.get("action")}" at unusual hour: {hour}:00',
            'recommendation': f'Verify if user {current_log.get("user")} was authorized for off-hours access. Review session logs.',
            'metadata': {
                'hour': hour
            }
        }
    
    return None

def detect_admin_misuse(current_log, all_logs):
    """Detect admin privilege misuse - ONLY for excessive admin actions"""
    current_user = current_log.get('user')
    
    if current_user not in ['admin', 'root']:
        return None
    
    current_time = parse_timestamp(current_log['timestamp'])
    recent_logs = get_time_window_logs(all_logs, current_time, minutes=20)
    
    admin_action_count = 0
    for log in recent_logs:
        if log.get('user') == current_user:
            admin_action_count += 1
    
    if admin_action_count > 10:
        anomaly_score = min(0.7 + (admin_action_count - 11) * 0.03, 1.0)
        
        return {
            'threat_detected': True,
            'threat_type': 'admin_misuse',
            'anomaly_score': round(anomaly_score, 2),
            'reason': f'Admin user {current_user} performed {admin_action_count} actions within 20 minutes',
            'recommendation': f'Review all actions by {current_user}. Verify if bulk operations were authorized. Consider temporary privilege suspension.',
            'metadata': {
                'action_count': admin_action_count
            }
        }
    
    return None

def detect_background_activity(current_log, all_logs):
    """Detect automated/bot activity - ONLY for highly repetitive patterns"""
    current_user = current_log.get('user')
    current_action = current_log.get('action')
    
    similar_logs = []
    for log in all_logs:
        if (log.get('user') == current_user and 
            log.get('action') == current_action):
            similar_logs.append(log)
    
    if len(similar_logs) < 8:  # Increased threshold
        return None
    
    similar_logs.sort(key=lambda x: parse_timestamp(x['timestamp']))
    
    intervals = []
    for i in range(len(similar_logs) - 1):
        try:
            time1 = parse_timestamp(similar_logs[i]['timestamp'])
            time2 = parse_timestamp(similar_logs[i + 1]['timestamp'])
            interval = (time2 - time1).total_seconds() / 60
            if interval > 0:
                intervals.append(interval)
        except:
            continue
    
    if len(intervals) >= 5:
        avg_interval = sum(intervals) / len(intervals)
        is_consistent = all(abs(interval - avg_interval) < 0.5 for interval in intervals)
        
        if is_consistent and avg_interval <= 5:
            return {
                'threat_detected': True,
                'threat_type': 'background_activity',
                'anomaly_score': 0.75,
                'reason': f'Detected automated behavior: User {current_user} performing "{current_action}" every {round(avg_interval, 1)} minutes ({len(similar_logs)} times)',
                'recommendation': f'Verify if {current_user} is a legitimate service account. Check for compromised credentials or unauthorized automation.',
                'metadata': {
                    'interval_minutes': round(avg_interval, 1),
                    'occurrence_count': len(similar_logs)
                }
            }
    
    return None

def generate_advanced_explanation(log, threat_type):
    """Generate ranked explanations with impact scores"""
    factors = []

    data = log.get('data_transferred_mb', 0)
    if data > 300:
        impact = min(data / 2000, 1.0)
        factors.append({
            "factor": "High Data Transfer",
            "value": f"{data} MB",
            "impact": round(impact, 2)
        })

    if log.get('status') == 'failed':
        factors.append({
            "factor": "Authentication Failure",
            "value": "Login failed",
            "impact": 0.7
        })

    try:
        hour = parse_timestamp(log['timestamp']).hour
        if 2 <= hour <= 4:
            factors.append({
                "factor": "Unusual Access Time",
                "value": f"{hour}:00 hours",
                "impact": 0.6
            })
    except:
        pass

    if log.get('user') in ['admin', 'root']:
        factors.append({
            "factor": "Privileged Account Usage",
            "value": log.get('user'),
            "impact": 0.65
        })

    if threat_type == 'impossible_travel':
        factors.append({
            "factor": "Location Anomaly",
            "value": log.get('location'),
            "impact": 0.85
        })

    factors.sort(key=lambda x: x['impact'], reverse=True)

    return {
        "top_factors": factors[:2] if factors else [{"factor": "Normal activity", "value": "N/A", "impact": 0.1}],
        "all_factors": factors[:3] if factors else []
    }

def calculate_base_anomaly_score(log):
    """Calculate a base anomaly score for truly normal logs"""
    score = 0.1
    
    if log.get('status') == 'failed':
        score += 0.05
    
    data_transferred = log.get('data_transferred_mb', 0)
    if 50 < data_transferred <= 300:
        score += 0.05
    
    return min(round(score, 2), 0.2)

def detect_threat(current_log, all_logs):
    """Main detection function - FIXED to avoid false positives"""
    detection_results = [
        detect_brute_force(current_log, all_logs),
        detect_data_exfiltration(current_log, all_logs),
        detect_impossible_travel(current_log, all_logs),
        detect_suspicious_behavior(current_log, all_logs),
        detect_admin_misuse(current_log, all_logs),
        detect_background_activity(current_log, all_logs)
    ]
    
    detected_threats = [result for result in detection_results if result is not None]
    
    if detected_threats:
        detected_threats.sort(key=lambda x: x['anomaly_score'], reverse=True)
        result = detected_threats[0]
        result['log'] = current_log
        result['explanation'] = generate_advanced_explanation(current_log, result['threat_type'])
        return result
    
    return {
        'threat_detected': False,
        'threat_type': 'normal',
        'anomaly_score': calculate_base_anomaly_score(current_log),
        'reason': 'Normal activity detected',
        'recommendation': 'No action required',
        'log': current_log,
        'metadata': {},
        'explanation': generate_advanced_explanation(current_log, 'normal')
    }

# ========================================
# ATTACK TIMELINE & IMPACT SIMULATION
# ========================================

def generate_attack_timeline(alert):
    """
    Generate step-by-step attack progression timeline
    Returns list of timeline steps showing attack evolution
    
    Args:
        alert: Detection result dictionary
    
    Returns:
        List of timeline steps with stage, time, description, severity
    """
    threat_type = alert.get('threat_type')
    anomaly_score = alert.get('anomaly_score', 0.5)
    user = alert.get('log', {}).get('user', 'unknown')
    is_admin = user in ['admin', 'root']
    
    # Base time progression (faster for high anomaly scores)
    time_multiplier = 0.5 if anomaly_score >= 0.8 else 1.0
    
    timeline = []
    
    # ===== BRUTE FORCE TIMELINE =====
    if threat_type == 'brute_force':
        failed_attempts = alert.get('metadata', {}).get('failed_attempts', 10)
        target_ip = alert.get('metadata', {}).get('target_ip', 'unknown')
        
        timeline = [
            {
                'stage': 1,
                'time': '0 min',
                'description': f'Initial failed login attempt detected from IP {target_ip}',
                'severity': 'low',
                'action': 'Reconnaissance phase - attacker testing credentials'
            },
            {
                'stage': 2,
                'time': f'{int(5 * time_multiplier)} min',
                'description': f'Rapid succession of failed logins ({failed_attempts} attempts)',
                'severity': 'medium',
                'action': 'Automated credential stuffing attack in progress'
            },
            {
                'stage': 3,
                'time': f'{int(15 * time_multiplier)} min',
                'description': 'Attack intensity increasing - dictionary/brute force patterns detected',
                'severity': 'high',
                'action': 'Attacker using automated tools to crack password'
            },
            {
                'stage': 4,
                'time': f'{int(25 * time_multiplier)} min',
                'description': 'Potential password database breach - unusual credential combinations tested',
                'severity': 'high',
                'action': 'Risk of account takeover imminent'
            },
            {
                'stage': 5,
                'time': f'{int(40 * time_multiplier)} min' if anomaly_score < 0.9 else f'{int(20 * time_multiplier)} min',
                'description': 'Successful login achieved' if anomaly_score >= 0.9 else 'Account lockout triggered - attack neutralized',
                'severity': 'critical' if anomaly_score >= 0.9 else 'high',
                'action': 'Full system access gained' if anomaly_score >= 0.9 else 'Preventive measures activated'
            }
        ]
    
    # ===== DATA EXFILTRATION TIMELINE =====
    elif threat_type == 'data_exfiltration':
        data_size = alert.get('metadata', {}).get('data_transferred_mb', 500)
        
        timeline = [
            {
                'stage': 1,
                'time': '0 min',
                'description': f'User {user} initiated unusual file access patterns',
                'severity': 'low',
                'action': 'Scanning sensitive directories and databases'
            },
            {
                'stage': 2,
                'time': f'{int(10 * time_multiplier)} min',
                'description': f'Large data aggregation detected ({data_size:.2f} MB)',
                'severity': 'medium',
                'action': 'Collecting and compressing sensitive information'
            },
            {
                'stage': 3,
                'time': f'{int(20 * time_multiplier)} min',
                'description': 'Data encryption and packaging in progress',
                'severity': 'high',
                'action': 'Preparing stolen data for transfer'
            },
            {
                'stage': 4,
                'time': f'{int(35 * time_multiplier)} min',
                'description': f'Outbound data transfer initiated to external server',
                'severity': 'critical',
                'action': 'Active data exfiltration in progress'
            },
            {
                'stage': 5,
                'time': f'{int(50 * time_multiplier)} min' if not is_admin else f'{int(30 * time_multiplier)} min',
                'description': 'Data successfully exfiltrated' if anomaly_score >= 0.8 else 'Transfer interrupted by DLP system',
                'severity': 'critical' if anomaly_score >= 0.8 else 'high',
                'action': f'{data_size:.2f} MB of sensitive data compromised' if anomaly_score >= 0.8 else 'Partial data loss prevented'
            }
        ]
    
    # ===== IMPOSSIBLE TRAVEL TIMELINE =====
    elif threat_type == 'impossible_travel':
        locations = alert.get('metadata', {}).get('locations', ['Location A', 'Location B'])
        
        timeline = [
            {
                'stage': 1,
                'time': '0 min',
                'description': f'Legitimate login from {locations[0]}',
                'severity': 'low',
                'action': 'Normal user authentication'
            },
            {
                'stage': 2,
                'time': f'{int(15 * time_multiplier)} min',
                'description': 'Credential theft suspected - unusual access patterns detected',
                'severity': 'medium',
                'action': 'Possible phishing or malware infection'
            },
            {
                'stage': 3,
                'time': f'{int(30 * time_multiplier)} min',
                'description': f'Simultaneous login attempt from {locations[1]} (physically impossible)',
                'severity': 'high',
                'action': 'Account compromise confirmed - credentials stolen'
            },
            {
                'stage': 4,
                'time': f'{int(45 * time_multiplier)} min',
                'description': 'Attacker accessing sensitive resources from compromised account',
                'severity': 'critical',
                'action': 'Privilege escalation attempts detected'
            },
            {
                'stage': 5,
                'time': f'{int(60 * time_multiplier)} min' if not is_admin else f'{int(40 * time_multiplier)} min',
                'description': 'Full account takeover - lateral movement initiated' if is_admin else 'Limited access breach contained',
                'severity': 'critical' if is_admin else 'high',
                'action': 'Network-wide compromise risk' if is_admin else 'Single account compromised'
            }
        ]
    
    # ===== SUSPICIOUS BEHAVIOR TIMELINE =====
    elif threat_type == 'suspicious_behavior':
        hour = alert.get('metadata', {}).get('hour', 3)
        
        timeline = [
            {
                'stage': 1,
                'time': '0 min',
                'description': f'Off-hours login detected at {hour}:00 AM',
                'severity': 'low',
                'action': 'Unusual time access - potential insider threat'
            },
            {
                'stage': 2,
                'time': f'{int(10 * time_multiplier)} min',
                'description': 'Accessing confidential files outside normal work hours',
                'severity': 'medium',
                'action': 'Data browsing and downloading sensitive information'
            },
            {
                'stage': 3,
                'time': f'{int(25 * time_multiplier)} min',
                'description': 'Unusual query patterns - searching for specific sensitive data',
                'severity': 'high',
                'action': 'Targeted data collection indicating malicious intent'
            },
            {
                'stage': 4,
                'time': f'{int(40 * time_multiplier)} min',
                'description': 'Attempting to disable logging and audit trails',
                'severity': 'critical',
                'action': 'Cover-up activities - clear evidence of malicious behavior'
            },
            {
                'stage': 5,
                'time': f'{int(60 * time_multiplier)} min',
                'description': 'Insider threat confirmed - data theft and evidence destruction',
                'severity': 'critical',
                'action': 'Significant data breach by authorized user'
            }
        ]
    
    # ===== ADMIN MISUSE TIMELINE =====
    elif threat_type == 'admin_misuse':
        action_count = alert.get('metadata', {}).get('action_count', 15)
        
        timeline = [
            {
                'stage': 1,
                'time': '0 min',
                'description': f'Admin {user} initiating elevated privilege operations',
                'severity': 'low',
                'action': f'Rapid succession of admin commands ({action_count} actions)'
            },
            {
                'stage': 2,
                'time': f'{int(8 * time_multiplier)} min',
                'description': 'Unusual admin activity pattern - automated or scripted behavior',
                'severity': 'medium',
                'action': 'Mass permission changes and user modifications'
            },
            {
                'stage': 3,
                'time': f'{int(15 * time_multiplier)} min',
                'description': 'Creating backdoor accounts and escalating privileges',
                'severity': 'high',
                'action': 'Establishing persistent unauthorized access'
            },
            {
                'stage': 4,
                'time': f'{int(25 * time_multiplier)} min',
                'description': 'Disabling security controls and monitoring systems',
                'severity': 'critical',
                'action': 'Eliminating detection mechanisms'
            },
            {
                'stage': 5,
                'time': f'{int(35 * time_multiplier)} min',
                'description': 'Complete system compromise - full admin control established',
                'severity': 'critical',
                'action': 'Attacker has unrestricted access to entire infrastructure'
            }
        ]
    
    # ===== BACKGROUND ACTIVITY TIMELINE =====
    elif threat_type == 'background_activity':
        interval = alert.get('metadata', {}).get('interval_minutes', 5)
        occurrences = alert.get('metadata', {}).get('occurrence_count', 10)
        
        timeline = [
            {
                'stage': 1,
                'time': '0 min',
                'description': f'Automated task detected - executing every {interval} minutes',
                'severity': 'low',
                'action': 'Bot or script activity identified'
            },
            {
                'stage': 2,
                'time': f'{int(15 * time_multiplier)} min',
                'description': f'Persistent automation confirmed ({occurrences} repetitions)',
                'severity': 'medium',
                'action': 'Potential compromised service account or malware'
            },
            {
                'stage': 3,
                'time': f'{int(30 * time_multiplier)} min',
                'description': 'Automated data collection and reconnaissance in progress',
                'severity': 'high',
                'action': 'Systematically mapping network resources'
            },
            {
                'stage': 4,
                'time': f'{int(50 * time_multiplier)} min',
                'description': 'Establishing command & control communication channel',
                'severity': 'critical',
                'action': 'Malware beaconing to external server'
            },
            {
                'stage': 5,
                'time': f'{int(70 * time_multiplier)} min',
                'description': 'Advanced persistent threat (APT) established in network',
                'severity': 'critical',
                'action': 'Long-term compromise - requires full incident response'
            }
        ]
    
    # ===== DEFAULT/UNKNOWN TIMELINE =====
    else:
        timeline = [
            {
                'stage': 1,
                'time': '0 min',
                'description': 'Anomalous activity detected',
                'severity': 'low',
                'action': 'Initiating threat analysis'
            },
            {
                'stage': 2,
                'time': '15 min',
                'description': 'Suspicious pattern confirmed',
                'severity': 'medium',
                'action': 'Escalating for investigation'
            },
            {
                'stage': 3,
                'time': '30 min',
                'description': 'Security breach identified',
                'severity': 'high',
                'action': 'Containment procedures initiated'
            },
            {
                'stage': 4,
                'time': '45 min',
                'description': 'Threat impact assessment ongoing',
                'severity': 'high',
                'action': 'Evaluating damage scope'
            },
            {
                'stage': 5,
                'time': '60 min',
                'description': 'Incident response activated',
                'severity': 'critical',
                'action': 'Full remediation required'
            }
        ]
    
    return timeline


def generate_impact_summary(alert, timeline):
    """
    Generate comprehensive impact summary based on attack timeline
    
    Args:
        alert: Detection result dictionary
        timeline: Attack timeline from generate_attack_timeline()
    
    Returns:
        Dictionary with impact analysis
    """
    threat_type = alert.get('threat_type')
    anomaly_score = alert.get('anomaly_score', 0.5)
    user = alert.get('log', {}).get('user', 'unknown')
    is_admin = user in ['admin', 'root']
    
    # Get final stage from timeline
    final_stage = timeline[-1] if timeline else {}
    final_severity = final_stage.get('severity', 'medium')
    
    # Determine impact level (considering anomaly score and user privileges)
    if anomaly_score >= 0.95 or (anomaly_score >= 0.85 and is_admin):
        impact_level = 'critical'
    elif anomaly_score >= 0.82 or final_severity == 'critical':
        impact_level = 'high'
    elif anomaly_score >= 0.68 or final_severity == 'high':
        impact_level = 'medium'
    else:
        impact_level = 'low'
    
    # Calculate time to critical based on timeline
    critical_stages = [s for s in timeline if s.get('severity') == 'critical']
    if critical_stages:
        time_to_critical = critical_stages[0].get('time', 'unknown')
    else:
        time_to_critical = 'Not reached'
    
    # Generate impact description based on threat type
    impact_descriptions = {
        'brute_force': {
            'critical': f'Complete account compromise of user "{user}". Attacker gained unauthorized access and can perform any action as this user. Immediate credential reset and access revocation required across all systems.',
            'high': f'Account "{user}" under active brute force attack. While not yet compromised, continued attempts pose imminent risk. Account lockout and IP blocking implemented.',
            'medium': f'Failed brute force attempt against "{user}". Attack was detected and blocked, but indicates targeted reconnaissance. Password policy review recommended.',
            'low': f'Minor failed login attempts for "{user}". Likely automated scanning. Standard monitoring sufficient.'
        },
        'data_exfiltration': {
            'critical': f'Massive data breach confirmed. {alert.get("metadata", {}).get("data_transferred_mb", 500):.2f} MB of sensitive data successfully exfiltrated by "{user}". Data includes customer records, financial information, and intellectual property. Legal and regulatory reporting required.',
            'high': f'Significant unauthorized data transfer detected ({alert.get("metadata", {}).get("data_transferred_mb", 300):.2f} MB). Partial data loss likely. Immediate investigation to determine scope of breach required.',
            'medium': f'Suspicious large data download by "{user}". Transfer partially blocked by DLP systems. Data classification and access review needed.',
            'low': f'Unusual but contained data transfer activity. No confirmed data loss. User behavior monitoring increased.'
        },
        'impossible_travel': {
            'critical': f'Account "{user}" fully compromised through credential theft. Attacker actively using stolen credentials from multiple geographic locations. {"Admin privileges compromised - network-wide threat." if is_admin else "User-level access breach - contained to single account."}',
            'high': f'Credential compromise confirmed for "{user}". Simultaneous access from impossible locations detected. Account disabled pending investigation.',
            'medium': f'Possible shared credentials or VPN anomaly for "{user}". Suspicious but not confirmed compromise. Additional verification required.',
            'low': f'Geographic access anomaly detected. Likely VPN or proxy usage. Standard verification procedures applied.'
        },
        'suspicious_behavior': {
            'critical': f'Confirmed insider threat. User "{user}" conducted extensive unauthorized data access during off-hours, attempted to disable audit logs, and exfiltrated sensitive information. Criminal investigation warranted.',
            'high': f'Highly suspicious off-hours activity by "{user}". Accessed confidential data outside normal work patterns. Potential insider threat or compromised account.',
            'medium': f'Unusual activity timing for "{user}". Off-hours access detected but business justification possible. Manager verification requested.',
            'low': f'Minor deviation from normal work hours. Likely legitimate remote work. Standard monitoring continued.'
        },
        'admin_misuse': {
            'critical': f'Complete system compromise through admin privilege abuse. User "{user}" created backdoor accounts, disabled security controls, and gained unrestricted system access. Full infrastructure at risk. Emergency incident response activated.',
            'high': f'Admin account "{user}" exhibiting malicious behavior pattern. Mass privilege escalations and unauthorized system changes detected. Immediate access revocation required.',
            'medium': f'Excessive admin activity by "{user}". {alert.get("metadata", {}).get("action_count", 10)} privileged operations in short timeframe. Requires justification and audit review.',
            'low': f'Elevated admin activity detected. Likely legitimate bulk operations. Standard change management review.'
        },
        'background_activity': {
            'critical': f'Advanced Persistent Threat (APT) confirmed. Automated malware beaconing every {alert.get("metadata", {}).get("interval_minutes", 5)} minutes detected from "{user}" account. Command & control communication established. Network-wide compromise likely.',
            'high': f'Malicious automation detected on "{user}" account. Persistent bot activity indicates compromised credentials or malware infection. System quarantine required.',
            'medium': f'Suspicious automated behavior from "{user}". Regular interval activity ({alert.get("metadata", {}).get("interval_minutes", 5)} min) suggests script or bot. Verification needed.',
            'low': f'Automated task detected. Likely legitimate service account or scheduled job. Standard review procedures.'
        }
    }
    
    # Get appropriate description
    descriptions = impact_descriptions.get(threat_type, {
        'critical': 'Critical security incident requiring immediate response.',
        'high': 'High severity threat requiring urgent investigation.',
        'medium': 'Medium severity issue requiring review.',
        'low': 'Low severity anomaly - monitoring continued.'
    })
    
    impact_description = descriptions.get(impact_level, descriptions.get('medium'))
    
    # Define affected assets based on threat type and severity
    affected_assets = []
    
    if threat_type == 'brute_force':
        affected_assets = [
            f'User account: {user}',
            f'Authentication system',
            f'Login infrastructure'
        ]
        if impact_level in ['critical', 'high']:
            affected_assets.extend([
                f'All resources accessible by {user}',
                'Session management system'
            ])
    
    elif threat_type == 'data_exfiltration':
        affected_assets = [
            f'User account: {user}',
            'Database systems',
            'File storage servers'
        ]
        if impact_level in ['critical', 'high']:
            affected_assets.extend([
                'Customer data repository',
                'Financial records',
                'Intellectual property',
                'Data Loss Prevention (DLP) systems'
            ])
            if is_admin:
                affected_assets.append('Entire data warehouse')
    
    elif threat_type == 'impossible_travel':
        affected_assets = [
            f'User account: {user}',
            'Authentication tokens',
            'Session cookies'
        ]
        if impact_level in ['critical', 'high']:
            affected_assets.extend([
                'Single Sign-On (SSO) systems',
                'Connected applications'
            ])
            if is_admin:
                affected_assets.extend([
                    'Admin console',
                    'Infrastructure management tools',
                    'All connected systems'
                ])
    
    elif threat_type == 'suspicious_behavior':
        affected_assets = [
            f'User account: {user}',
            'Accessed confidential files',
            'Audit logging system'
        ]
        if impact_level in ['critical', 'high']:
            affected_assets.extend([
                'Sensitive data repositories',
                'Security monitoring systems',
                'Data integrity'
            ])
    
    elif threat_type == 'admin_misuse':
        affected_assets = [
            f'Admin account: {user}',
            'User management system',
            'Permission infrastructure'
        ]
        if impact_level in ['critical', 'high']:
            affected_assets.extend([
                'Security policies',
                'Access control lists (ACLs)',
                'Audit systems',
                'Backup systems',
                'All user accounts',
                'Entire infrastructure'
            ])
    
    elif threat_type == 'background_activity':
        affected_assets = [
            f'User/service account: {user}',
            'Automated task scheduler'
        ]
        if impact_level in ['critical', 'high']:
            affected_assets.extend([
                'Network communication channels',
                'Endpoint security systems',
                'Command & control infrastructure (external)',
                'All networked systems',
                'Data repositories'
            ])
    
    # Build comprehensive impact summary
    impact_summary = {
        'impact_level': impact_level,
        'impact_description': impact_description,
        'time_to_critical': time_to_critical,
        'affected_assets': affected_assets,
        'final_stage_severity': final_severity,
        'business_impact': {
            'financial': _calculate_financial_impact(impact_level, threat_type, is_admin),
            'operational': _calculate_operational_impact(impact_level, threat_type),
            'reputational': _calculate_reputational_impact(impact_level, threat_type),
            'compliance': _calculate_compliance_impact(impact_level, threat_type)
        },
        'recovery_time_estimate': _estimate_recovery_time(impact_level, threat_type),
        'required_actions': _get_required_actions(impact_level, threat_type, user)
    }
    
    return impact_summary


def _calculate_financial_impact(impact_level, threat_type, is_admin):
    """Calculate estimated financial impact"""
    base_costs = {
        'critical': 'Estimated $500K - $2M+ (data breach, incident response, legal fees, regulatory fines)',
        'high': 'Estimated $100K - $500K (investigation, remediation, potential customer compensation)',
        'medium': 'Estimated $10K - $100K (internal investigation, security improvements)',
        'low': 'Estimated $1K - $10K (monitoring and minor security updates)'
    }
    
    impact = base_costs.get(impact_level, 'Unknown')
    
    if threat_type == 'data_exfiltration' and impact_level in ['critical', 'high']:
        impact += ' PLUS potential GDPR/CCPA fines up to 4% of annual revenue'
    
    if is_admin and impact_level == 'critical':
        impact += ' MULTIPLIED by full system compromise factor'
    
    return impact


def _calculate_operational_impact(impact_level, threat_type):
    """Calculate operational business impact"""
    impacts = {
        'critical': 'Severe disruption - potential system shutdown, complete service interruption, extensive recovery operations',
        'high': 'Significant disruption - partial system downtime, reduced functionality, emergency response required',
        'medium': 'Moderate disruption - isolated service impact, degraded performance, scheduled maintenance required',
        'low': 'Minimal disruption - continued normal operations with enhanced monitoring'
    }
    return impacts.get(impact_level, 'Unknown impact')


def _calculate_reputational_impact(impact_level, threat_type):
    """Calculate reputational damage"""
    impacts = {
        'critical': 'Severe - public disclosure likely required, major customer trust loss, media attention expected, long-term brand damage',
        'high': 'Significant - customer notification required, trust erosion, potential media coverage',
        'medium': 'Moderate - internal stakeholder concern, selective customer notification possible',
        'low': 'Minimal - internal incident, no external notification required'
    }
    
    if threat_type == 'data_exfiltration':
        return impacts.get(impact_level, 'Unknown') + ' (Data breach amplifies reputational damage)'
    
    return impacts.get(impact_level, 'Unknown impact')


def _calculate_compliance_impact(impact_level, threat_type):
    """Calculate regulatory/compliance implications"""
    impacts = {
        'critical': 'Mandatory breach notification to regulators within 72 hours. Full audit and compliance review required. Potential regulatory sanctions.',
        'high': 'Likely regulatory notification required. Compliance assessment needed. Audit trail documentation mandatory.',
        'medium': 'Internal compliance review required. Document for annual audit. Update risk register.',
        'low': 'Standard logging sufficient. Include in routine compliance reporting.'
    }
    
    if threat_type in ['data_exfiltration', 'impossible_travel']:
        return impacts.get(impact_level, 'Unknown') + ' GDPR/HIPAA/PCI-DSS implications possible.'
    
    return impacts.get(impact_level, 'Unknown')


def _estimate_recovery_time(impact_level, threat_type):
    """Estimate time to full recovery"""
    times = {
        'critical': '7-30 days (full incident response, forensics, remediation, system rebuild)',
        'high': '2-7 days (investigation, containment, remediation, verification)',
        'medium': '4-48 hours (analysis, targeted fixes, testing)',
        'low': '1-4 hours (review, minor adjustments, continued monitoring)'
    }
    return times.get(impact_level, 'Unknown')


def _get_required_actions(impact_level, threat_type, user):
    """Get list of required immediate actions"""
    actions = []
    
    if impact_level == 'critical':
        actions = [
            '🚨 IMMEDIATE: Activate incident response team',
            f'🔒 IMMEDIATE: Disable user account "{user}" across all systems',
            '📞 IMMEDIATE: Notify CISO and executive leadership',
            '🔍 URGENT: Begin forensic investigation',
            '📋 URGENT: Document all evidence and actions',
            '⚖️ URGENT: Contact legal counsel',
            '📢 Within 24h: Prepare breach notification (if applicable)',
            '🛡️ Within 48h: Implement emergency security controls'
        ]
    elif impact_level == 'high':
        actions = [
            f'🔒 IMMEDIATE: Suspend account "{user}" pending investigation',
            '🚨 URGENT: Notify security team',
            '🔍 URGENT: Investigate scope and impact',
            '📋 Within 24h: Complete incident report',
            '🛡️ Within 48h: Implement containment measures',
            '📊 Within 72h: Risk assessment and remediation plan'
        ]
    elif impact_level == 'medium':
        actions = [
            f'⚠️ PRIORITY: Review activity for user "{user}"',
            '🔍 Within 12h: Investigate anomaly',
            '📋 Within 24h: Document findings',
            '🛡️ Within 48h: Implement preventive controls',
            '📊 Within 1 week: Update security policies'
        ]
    else:  # low
        actions = [
            f'📊 Monitor user "{user}" activity',
            '📋 Document incident in security log',
            '🔍 Review in next security meeting',
            '🛡️ Consider security awareness training'
        ]
    
    # Add threat-specific actions
    if threat_type == 'brute_force' and impact_level in ['critical', 'high']:
        actions.append('🔐 Force password reset for all users in same department')
        actions.append('🚫 Implement rate limiting on authentication endpoints')
    
    if threat_type == 'data_exfiltration':
        actions.append('📊 Audit all recent data access by affected user')
        actions.append('🔒 Review and restrict data export permissions')
    
    if threat_type == 'impossible_travel':
        actions.append('🔑 Enable MFA for all users if not already active')
        actions.append('🌐 Review VPN and remote access logs')
    
    if threat_type == 'admin_misuse':
        actions.append('👑 Audit all admin accounts and permissions')
        actions.append('📜 Review change management logs')
    
    return actions


# ========================================
# API ENDPOINTS
# ========================================

@app.route('/')
def home():
    """Home endpoint with API information"""
    return jsonify({
        'message': 'Synthetic Log Generator API - SOC Analyst Training Platform',
        'version': '3.0',
        'endpoints': {
            'GET /logs': 'Retrieve all logs',
            'GET /alerts': 'Get detected threats with timeline & impact analysis',
            'GET /analysis': 'Get full analysis of all logs',
            'POST /simulate-attack': 'Simulate specific attack type',
            'POST /generate-realistic-mix': 'Generate realistic SOC environment (recommended)',
            'DELETE /logs': 'Clear all logs'
        },
        'threat_types': [
            'brute_force',
            'data_exfiltration',
            'impossible_travel',
            'suspicious_behavior',
            'admin_misuse',
            'background_activity'
        ],
        'recommended_workflow': [
            '1. Clear existing logs',
            '2. Generate realistic mix (15-20% threat rate)',
            '3. Analyze detected threats',
            '4. Simulate specific attack for deep dive',
            '5. Review impact timeline and recommendations'
        ]
    })

@app.route('/logs', methods=['GET'])
def get_logs():
    """Return all stored logs"""
    return jsonify({
        'total_logs': len(logs),
        'logs': logs
    }), 200

@app.route('/logs', methods=['DELETE'])
def clear_logs():
    """Clear all logs from memory"""
    global logs
    logs = []
    return jsonify({
        'message': 'All logs cleared',
        'total_logs': 0
    }), 200

@app.route('/generate-normal', methods=['POST'])
def generate_normal():
    """Generate and store normal logs with variety to avoid false positives"""
    data = request.get_json() or {}
    count = data.get('count', 10)
    
    new_logs = []
    
    # Generate logs with time spacing to avoid patterns
    for i in range(count):
        # Add random delay between logs (avoid regular intervals)
        time.sleep(0.01)  # Small delay to ensure different timestamps
        
        log = generate_normal_log()
        
        # Add some randomness to break patterns
        # Vary the time offset for each log
        base_time = datetime.now()
        random_offset = random.randint(-120 + i*2, -60 + i*2)  # Spread over time
        log['timestamp'] = (base_time + timedelta(minutes=random_offset)).strftime('%Y-%m-%d %H:%M:%S')
        
        new_logs.append(log)
    
    # Add to storage
    logs.extend(new_logs)
    
    return jsonify({
        'message': f'Generated {count} normal logs',
        'logs_generated': count,
        'total_logs': len(logs)
    }), 201

@app.route('/simulate-attack', methods=['POST'])
def simulate_attack():
    """Generate and store attack logs based on threat type"""
    # Get threat type from request body
    data = request.get_json()
    
    if not data or 'threat_type' not in data:
        return jsonify({
            'error': 'Please specify threat_type in request body',
            'valid_types': [
                'brute_force',
                'data_exfiltration',
                'impossible_travel',
                'suspicious_behavior',
                'admin_misuse',
                'background_activity'
            ]
        }), 400
    
    threat_type = data['threat_type']
    count = data.get('count', None)  # Optional: custom count
    
    # Generate logs based on threat type
    new_logs = []
    
    if threat_type == 'brute_force':
        new_logs = generate_brute_force_logs(count or 10)
    
    elif threat_type == 'data_exfiltration':
        new_logs = generate_data_exfiltration_logs(count or 3)
    
    elif threat_type == 'impossible_travel':
        new_logs = generate_impossible_travel_logs(count or 2)
    
    elif threat_type == 'suspicious_behavior':
        new_logs = generate_suspicious_behavior_logs(count or 5)
    
    elif threat_type == 'admin_misuse':
        new_logs = generate_admin_misuse_logs(count or 15)
    
    elif threat_type == 'background_activity':
        new_logs = generate_background_activity_logs(count or 10)
    
    else:
        return jsonify({
            'error': f'Invalid threat_type: {threat_type}',
            'valid_types': [
                'brute_force',
                'data_exfiltration',
                'impossible_travel',
                'suspicious_behavior',
                'admin_misuse',
                'background_activity'
            ]
        }), 400
    
    # Add to storage
    logs.extend(new_logs)
    
    return jsonify({
        'message': f'Generated {len(new_logs)} {threat_type} logs',
        'threat_type': threat_type,
        'logs_generated': len(new_logs),
        'total_logs': len(logs),
        'generated_logs': new_logs
    }), 201

@app.route('/alerts', methods=['GET'])
def get_alerts():
    """Analyze all logs and return ONLY DETECTED THREATS"""
    if not logs:
        return jsonify({
            'message': 'No logs available for analysis',
            'total_logs': 0,
            'threats_detected': 0,
            'alerts': []
        }), 200
    
    alerts = []
    for log in logs:
        detection_result = detect_threat(log, logs)
        
        # CRITICAL: Only include actual threats
        if detection_result.get('threat_detected') == True:
            timeline = generate_attack_timeline(detection_result)
            impact = generate_impact_summary(detection_result, timeline)
            
            detection_result['attack_timeline'] = timeline
            detection_result['impact'] = impact
            
            alerts.append(detection_result)
    
    threat_summary = defaultdict(int)
    for alert in alerts:
        threat_summary[alert['threat_type']] += 1
    
    severity_distribution = defaultdict(int)
    for alert in alerts:
        impact_level = alert.get('impact', {}).get('impact_level', 'unknown')
        severity_distribution[impact_level] += 1
    
    return jsonify({
        'message': 'Threat detection completed with impact analysis',
        'total_logs_analyzed': len(logs),
        'threats_detected': len(alerts),
        'threat_summary': dict(threat_summary),
        'severity_distribution': dict(severity_distribution),
        'alerts': alerts
    }), 200

@app.route('/analysis', methods=['GET'])
def get_full_analysis():
    """
    Analyze all logs and return complete analysis including normal logs
    """
    if not logs:
        return jsonify({
            'message': 'No logs available for analysis',
            'total_logs': 0,
            'analysis': []
        }), 200
    
    # Run detection on all logs
    analysis_results = []
    for log in logs:
        detection_result = detect_threat(log, logs)
        
        # Only add timeline/impact for detected threats
        if detection_result['threat_detected']:
            timeline = generate_attack_timeline(detection_result)
            impact = generate_impact_summary(detection_result, timeline)
            detection_result['attack_timeline'] = timeline
            detection_result['impact'] = impact
        
        analysis_results.append(detection_result)
    
    # Sort by anomaly score (highest first)
    analysis_results.sort(key=lambda x: x['anomaly_score'], reverse=True)
    
    # Calculate statistics
    total_threats = sum(1 for result in analysis_results if result['threat_detected'])
    avg_anomaly_score = sum(result['anomaly_score'] for result in analysis_results) / len(analysis_results)
    
    # Threat distribution
    threat_distribution = defaultdict(int)
    for result in analysis_results:
        threat_distribution[result['threat_type']] += 1
    
    return jsonify({
        'message': 'Full analysis completed',
        'statistics': {
            'total_logs': len(logs),
            'threats_detected': total_threats,
            'normal_logs': len(logs) - total_threats,
            'average_anomaly_score': round(avg_anomaly_score, 2),
            'threat_distribution': dict(threat_distribution)
        },
        'analysis': analysis_results
    }), 200

@app.route('/generate-realistic-mix', methods=['POST'])
def generate_realistic_mix():
    """
    Generate a realistic mix of normal logs with occasional threats
    Simulates real-world SOC environment with VARIED severity levels
    """
    data = request.get_json() or {}
    total_count = data.get('count', 50)
    threat_percentage = data.get('threat_percentage', 15)  # 15% threats by default
    
    new_logs = []
    
    # Calculate how many should be threats
    threat_count = int(total_count * threat_percentage / 100)
    normal_count = total_count - threat_count
    
    print(f"Generating {normal_count} normal logs and {threat_count} threat scenarios...")
    
    # ===== GENERATE NORMAL LOGS =====
    for i in range(normal_count):
        # Create timestamp during BUSINESS HOURS ONLY (9 AM - 6 PM)
        base_time = datetime.now()
        
        # Random day offset (last 7 days)
        day_offset = random.randint(-7, 0)
        
        # Business hours: 9 AM - 6 PM
        safe_hour = random.randint(9, 18)
        safe_minute = random.randint(0, 59)
        safe_second = random.randint(0, 59)
        
        safe_time = base_time.replace(
            hour=safe_hour, 
            minute=safe_minute, 
            second=safe_second
        ) + timedelta(days=day_offset)
        
        # Pick ONLY non-admin users for normal logs
        safe_users = ['alice', 'bob', 'charlie', 'diana', 'john', 'sarah']
        
        # Create truly normal log
        log = {
            'timestamp': safe_time.strftime('%Y-%m-%d %H:%M:%S'),
            'user': random.choice(safe_users),
            'action': random.choice(NORMAL_ACTIONS),
            'status': 'success',
            'ip': generate_ip(),
            'location': random.choice(LOCATIONS),
            'data_transferred_mb': round(random.uniform(0.1, 4.5), 2),
            'threat_type': 'normal'
        }
        
        new_logs.append(log)
    
    # ===== GENERATE VARIED THREAT SCENARIOS =====
    threat_types = ['brute_force', 'data_exfiltration', 'impossible_travel', 
                    'suspicious_behavior', 'admin_misuse', 'background_activity']
    
    # Generate threats with RANDOM severity distribution
    generated_threat_count = 0
    
    while generated_threat_count < threat_count:
        # Pick random threat type
        threat_type = random.choice(threat_types)
        
        # Generate threat with VARIED INTENSITY for mixed severity
        if threat_type == 'brute_force':
            # Vary the number of attempts for different severity
            intensity = random.choice([
                6,   # Low severity (6 attempts → score ~0.70)
                8,   # Medium severity (8 attempts → score ~0.85)
                12   # High severity (12 attempts → score ~1.0)
            ])
            threat_logs = generate_brute_force_logs(intensity)
            
        elif threat_type == 'data_exfiltration':
            # Vary data size for different severity
            # We need to generate custom logs here for varied sizes
            intensity = random.choice([
                350,   # Medium severity (350 MB → score ~0.72)
                600,   # High severity (600 MB → score ~0.83)
                1200   # Critical severity (1200 MB → score ~1.0)
            ])
            
            # Generate single custom data exfiltration log
            suspicious_user = random.choice(USERS)
            suspicious_ip = generate_ip()
            
            threat_logs = [{
                'timestamp': get_timestamp(offset_minutes=random.randint(-120, -10)),
                'user': suspicious_user,
                'action': 'download_file',
                'status': 'success',
                'ip': suspicious_ip,
                'location': random.choice(LOCATIONS),
                'data_transferred_mb': intensity,
                'threat_type': 'data_exfiltration',
                'file_name': f'sensitive_data_{random.randint(1,999)}.zip'
            }]
            
        elif threat_type == 'impossible_travel':
            # Impossible travel is always high severity (0.85)
            threat_logs = generate_impossible_travel_logs(2)
            
        elif threat_type == 'suspicious_behavior':
            # Vary the number of suspicious actions
            intensity = random.choice([
                1,  # Low severity (single incident)
                3,  # Medium severity
                5   # High severity
            ])
            threat_logs = generate_suspicious_behavior_logs(intensity)
            
        elif threat_type == 'admin_misuse':
            # Vary the action count for different severity
            intensity = random.choice([
                11,  # Low severity (11 actions → score ~0.70)
                15,  # Medium severity (15 actions → score ~0.82)
                20   # High severity (20 actions → score ~0.97)
            ])
            threat_logs = generate_admin_misuse_logs(intensity)
            
        else:  # background_activity
            # Vary repetition count
            intensity = random.choice([
                8,   # Low severity (8 repetitions)
                10,  # Medium severity
                15   # High severity
            ])
            threat_logs = generate_background_activity_logs(intensity)
        
        # Add these threat logs
        new_logs.extend(threat_logs)
        generated_threat_count += len(threat_logs)
        
        # Prevent infinite loop - stop if we've generated enough
        if generated_threat_count >= threat_count * 1.5:
            break
    
    # Shuffle to mix normal and threat logs realistically
    random.shuffle(new_logs)
    
    # Add to storage
    logs.extend(new_logs)
    
    # Count actual threats that will be detected
    actual_threat_logs = [log for log in new_logs if log.get('threat_type') != 'normal']
    
    return jsonify({
        'message': f'Generated realistic mix with varied severity levels',
        'logs_generated': len(new_logs),
        'normal_logs': normal_count,
        'threat_scenarios': len(actual_threat_logs),
        'total_logs': len(logs),
        'severity_note': 'Threats generated with varied intensity for mixed severity levels'
    }), 201

@app.route('/alerts/summary', methods=['GET'])
def get_alerts_summary():
    """
    Get a summary of alerts with counts and severity levels
    NOW INCLUDES: Impact-based severity classification
    """
    if not logs:
        return jsonify({
            'message': 'No logs available',
            'summary': {}
        }), 200
    
    # Run detection
    critical_alerts = []
    high_alerts = []
    medium_alerts = []
    low_alerts = []
    
    for log in logs:
        detection_result = detect_threat(log, logs)
        
        if detection_result['threat_detected']:
            # Generate timeline and impact
            timeline = generate_attack_timeline(detection_result)
            impact = generate_impact_summary(detection_result, timeline)
            
            detection_result['attack_timeline'] = timeline
            detection_result['impact'] = impact
            
            # Classify by impact level
            impact_level = impact.get('impact_level', 'low')
            
            if impact_level == 'critical':
                critical_alerts.append(detection_result)
            elif impact_level == 'high':
                high_alerts.append(detection_result)
            elif impact_level == 'medium':
                medium_alerts.append(detection_result)
            else:
                low_alerts.append(detection_result)
    
    return jsonify({
        'summary': {
            'total_logs': len(logs),
            'total_threats': len(critical_alerts) + len(high_alerts) + len(medium_alerts) + len(low_alerts),
            'critical_count': len(critical_alerts),
            'high_count': len(high_alerts),
            'medium_count': len(medium_alerts),
            'low_count': len(low_alerts),
        },
        'critical_alerts': critical_alerts,
        'high_alerts': high_alerts,
        'medium_alerts': medium_alerts,
        'low_alerts': low_alerts
    }), 200

# ========================================
# RUN THE APP
# ========================================

if __name__ == '__main__':
    # Generate some initial normal logs
    for _ in range(20):
        logs.append(generate_normal_log())
    
    print("=" * 50)
    print("Synthetic Log Generator API Starting...")
    print(f"Initial logs generated: {len(logs)}")
    print("=" * 50)
    
    # Run the Flask app
    app.run(debug=True, port=5000)