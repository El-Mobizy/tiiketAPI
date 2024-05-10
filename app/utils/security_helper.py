import re


class SecurityHelper:
    @staticmethod
    def sanitize_input(input_str):
        sanitized_str = str.replace(r'[;\'"\[\]{}()*]', '', input_str)
        sanitized_str = str.replace(r'\\', r'\\\\', sanitized_str)
        sanitized_str = str.replace(r"'", r"\'", sanitized_str)
        sanitized_str = str.replace(r'"', r'\"', sanitized_str)
        return sanitized_str

    @staticmethod
    def escape_html(input_string):
        replacements = {
            '&': '&amp;', '<': '&lt;',
            '>': '&gt;', '"': '&quot;',
            "'": '&#39;'
        }
        return "".join(replacements.get(char, char) for char in input_string)

    @staticmethod
    def validate_email(email):
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        pattern = re.compile(email_pattern)
        return bool(pattern.match(email))
