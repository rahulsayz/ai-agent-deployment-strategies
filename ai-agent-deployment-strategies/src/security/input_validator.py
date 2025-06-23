import hashlib
import hmac
import jwt
import time
from cryptography.fernet import Fernet
from typing import Dict, List, Optional
import re

class AIAgentSecurity:
    def __init__(self, secret_key: str, encryption_key: str):
        self.secret_key = secret_key
        self.cipher_suite = Fernet(encryption_key.encode())
        self.blocked_patterns = self.load_security_patterns()
        self.rate_limits = {}
    
    def load_security_patterns(self) -> List[str]:
        """Load patterns for input validation and security scanning."""
        return [
            r'<script.*?>.*?</script>',  # XSS prevention
            r'(union|select|insert|update|delete|drop)\s+',  # SQL injection
            r'\.\.\/|\.\.\\',  # Path traversal
            r'eval\s*\(',  # Code injection
            r'exec\s*\(',  # Command injection
        ]
    
    def validate_input(self, user_input: str, user_id: str) -> Dict:
        """Comprehensive input validation and security scanning."""
        validation_result = {
            "is_valid": True,
            "security_violations": [],
            "sanitized_input": user_input
        }
        
        # Check for malicious patterns
        for pattern in self.blocked_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                validation_result["is_valid"] = False
                validation_result["security_violations"].append(f"Blocked pattern detected: {pattern}")
        
        # PII detection and redaction
        pii_result = self.detect_and_redact_pii(user_input)
        if pii_result["pii_detected"]:
            validation_result["sanitized_input"] = pii_result["redacted_text"]
            self.log_security_event("PII_DETECTED", user_id, pii_result["pii_types"])
        
        # Rate limiting check
        if not self.check_rate_limit(user_id):
            validation_result["is_valid"] = False
            validation_result["security_violations"].append("Rate limit exceeded")
        
        # Input length validation
        if len(user_input) > 10000:  # 10KB limit
            validation_result["is_valid"] = False
            validation_result["security_violations"].append("Input too long")
        
        return validation_result
    
    def detect_and_redact_pii(self, text: str) -> Dict:
        """Detect and redact personally identifiable information."""
        pii_patterns = {
            'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        }
        
        redacted_text = text
        detected_types = []
        
        for pii_type, pattern in pii_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                detected_types.append(pii_type)
                redacted_text = re.sub(pattern, f'[{pii_type.upper()}_REDACTED]', redacted_text)
        
        return {
            "pii_detected": bool(detected_types),
            "pii_types": detected_types,
            "redacted_text": redacted_text
        }
    
    def check_rate_limit(self, user_id: str, limit: int = 100, window: int = 3600) -> bool:
        """Implement rate limiting per user."""
        current_time = time.time()
        
        if user_id not in self.rate_limits:
            self.rate_limits[user_id] = []
        
        # Remove old requests outside the time window
        self.rate_limits[user_id] = [
            req_time for req_time in self.rate_limits[user_id]
            if current_time - req_time < window
        ]
        
        # Check if under limit
        if len(self.rate_limits[user_id]) >= limit:
            return False
        
        # Add current request
        self.rate_limits[user_id].append(current_time)
        return True
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data for storage."""
        return self.cipher_suite.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data for processing."""
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
    
    def generate_access_token(self, user_id: str, permissions: List[str], 
                            expires_in: int = 3600) -> str:
        """Generate JWT access token for API authentication."""
        payload = {
            'user_id': user_id,
            'permissions': permissions,
            'exp': time.time() + expires_in,
            'iat': time.time()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def validate_access_token(self, token: str) -> Optional[Dict]:
        """Validate JWT access token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def log_security_event(self, event_type: str, user_id: str, details: Dict):
        """Log security events for monitoring and compliance."""
        security_log = {
            'timestamp': time.time(),
            'event_type': event_type,
            'user_id': user_id,
            'details': details,
            'severity': self.get_event_severity(event_type)
        }
        
        # Send to security monitoring system
        self.send_to_security_monitoring(security_log)
    
    def get_event_severity(self, event_type: str) -> str:
        """Determine severity level for security events."""
        high_severity_events = ['INJECTION_ATTEMPT', 'UNAUTHORIZED_ACCESS', 'DATA_BREACH']
        medium_severity_events = ['RATE_LIMIT_EXCEEDED', 'INVALID_TOKEN']
        
        if event_type in high_severity_events:
            return 'HIGH'
        elif event_type in medium_severity_events:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def send_to_security_monitoring(self, security_log: Dict):
        """Send security events to monitoring system."""
        # Implement integration with your security monitoring platform
        # Examples: Splunk, ELK Stack, AWS CloudTrail, etc.
        print(f"Security Event: {security_log}")