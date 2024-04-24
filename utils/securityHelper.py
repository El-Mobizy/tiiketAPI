import re
import secrets

class SecurityHelper:
    @staticmethod
    def sanitize_input(input_string):
        """Sanitize user input to prevent SQL injection"""
        return re.sub(r'[;\'"]', '', input_string)

    @staticmethod
    def escape_html(input_string):
        """Escape HTML characters to prevent XSS"""
        return input_string.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

    @staticmethod
    def generate_csrf_token():
        """Generate a CSRF token"""
        return secrets.token_urlsafe(32)  # Generate a random URL-safe token

    @staticmethod
    def validate_csrf_token(request_token, session_token):
        """Validate CSRF token"""
        return request_token == session_token
