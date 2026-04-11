"""
Enhanced Password Validators for Nyaradzo Backend
==================================================
Provides stronger password validation beyond Django defaults.
"""

import re
from django.contrib.auth.password_validation import (
    UserAttributeSimilarityValidator,
    MinimumLengthValidator,
    CommonPasswordValidator,
    NumericPasswordValidator,
)
from django.core.exceptions import ValidationError


class StrongPasswordValidator:
    """
    Validate that a password meets strong security requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    
    def __init__(self, min_length=8):
        self.min_length = min_length
    
    def validate(self, password, user=None):
        """Validate password strength."""
        errors = []
        
        # Check length
        if len(password) < self.min_length:
            errors.append(
                f"Password must be at least {self.min_length} characters long. "
                f"(Current: {len(password)} characters)"
            )
        
        # Check for uppercase
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter (A-Z).")
        
        # Check for lowercase
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter (a-z).")
        
        # Check for digit
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one digit (0-9).")
        
        # Check for special characters
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
            errors.append(
                "Password must contain at least one special character "
                "(!@#$%^&*()_+-=[]{}:;'\",./<>?/\\|`~)"
            )
        
        # Check for common patterns
        common_patterns = [
            r'(.)\1{2,}',  # Repeated characters (aaa)
            r'(abc|bcd|cde|def|efg)',  # Sequential letters
            r'(012|123|234|345)',  # Sequential numbers
        ]
        
        for pattern in common_patterns:
            if re.search(pattern, password.lower()):
                errors.append("Password contains common patterns (aaa, abc, 123, etc)")
                break
        
        if errors:
            raise ValidationError(errors)
    
    def get_help_text(self):
        """Return help text for users."""
        return (
            "Your password must contain at least 8 characters, including: "
            "uppercase letters, lowercase letters, numbers, and special characters. "
            "Avoid repeating characters or sequential patterns."
        )


class NoVariationPasswordValidator:
    """
    Prevent passwords that only have one type of character variation.
    E.g., reject 'AAAAAAAA' or '12345678'.
    """
    
    def validate(self, password, user=None):
        """Validate password has character variation."""
        errors = []
        
        # Count different character types
        has_uppercase = any(c.isupper() for c in password)
        has_lowercase = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        variation_count = sum([has_uppercase, has_lowercase, has_digit, has_special])
        
        if variation_count < 2:
            errors.append(
                "Password must contain at least 2 different types of characters "
                "(uppercase, lowercase, numbers, special characters)."
            )
        
        if errors:
            raise ValidationError(errors)
    
    def get_help_text(self):
        """Return help text for users."""
        return (
            "Your password must use at least 2 different character types: "
            "uppercase, lowercase, numbers, or special characters."
        )
