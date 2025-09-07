"""
Text utility functions for VisionScribe.
"""

import re
import string
from typing import List, Dict, Any, Optional, Set
from collections import Counter, defaultdict
import logging


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove special characters that might be OCR artifacts
    text = re.sub(r'[^\w\s\-\.\(\)\[\]\{\}:;#@\$%\^&\*\+=<>\/\?!\'\"~`|\\]', '', text)
    
    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")
    
    # Normalize ellipsis
    text = text.replace('...', '...').replace('..', '...')
    
    return text.strip()


def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    """Extract code blocks from text."""
    code_blocks = []
    
    # Pattern to match code blocks (indented or fenced)
    patterns = [
        r'^```[a-zA-Z]*\n(.*?)\n```',  # Fenced code blocks
        r'^(   |\t)([^\n]*\n)*',       # Indented code blocks
        r'`([^`]+)`'                   # Inline code
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
        for match in matches:
            code_block = match.group(1) if len(match.groups()) > 1 else match.group(0)
            if code_block:
                code_blocks.append({
                    'code': code_block,
                    'type': determine_code_type(code_block)
                })
    
    return code_blocks


def determine_code_type(code: str) -> str:
    """Determine the type of code snippet."""
    # Check for common programming languages
    language_indicators = {
        'python': ['def ', 'import ', 'from ', 'class ', 'lambda ', 'yield '],
        'javascript': ['function ', 'const ', 'let ', 'var ', '=> ', 'console.log'],
        'java': ['public class', 'private class', 'import java', 'public static'],
        'cpp': ['#include', 'using namespace', 'int main', 'std::'],
        'html': ['<html', '<div', '<span', '<script', '<style'],
        'css': ['{', '}', 'color:', 'font:', 'margin:'],
        'sql': ['SELECT', 'INSERT INTO', 'UPDATE', 'DELETE FROM'],
        'shell': ['#!/', 'echo', 'cd ', 'ls ', 'mv ']
    }
    
    code_lower = code.lower()
    
    for language, indicators in language_indicators.items():
        for indicator in indicators:
            if indicator.lower() in code_lower:
                return language
    
    return 'unknown'


def extract_file_paths(text: str) -> List[str]:
    """Extract file paths from text."""
    patterns = [
        r'[\'"]?(/[^\'"\s]+|[^\'"\s]+\.[a-zA-Z]{2,6})[\'"]?',  # Unix/Windows paths
        r'[\'"]?(\.[/\\][^\'"\s]+|[^\'"\s]+[/\\][^\'"\s]+)[\'"]?',  # Relative paths
    ]
    
    file_paths = []
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        file_paths.extend(matches)
    
    return list(set(file_paths))  # Remove duplicates


def extract_urls(text: str) -> List[str]:
    """Extract URLs from text."""
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]*'
    return re.findall(url_pattern, text)


def extract_emails(text: str) -> List[str]:
    """Extract email addresses from text."""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, text)


def extract_numbers(text: str) -> List[str]:
    """Extract numbers from text."""
    # Integers, floats, and scientific notation
    patterns = [
        r'\b\d+\b',  # Integers
        r'\b\d+\.\d+\b',  # Floats
        r'\b\d+[eE][+-]?\d+\b',  # Scientific notation
        r'0[xX][0-9a-fA-F]+',  # Hexadecimal
        r'0[bB][01]+',  # Binary
    ]
    
    numbers = []
    for pattern in patterns:
        numbers.extend(re.findall(pattern, text))
    
    return numbers


def extract_keywords(text: str, max_keywords: int = 20, min_length: int = 3) -> List[str]:
    """Extract keywords from text."""
    # Tokenize text
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Filter words
    stop_words = get_stop_words()
    filtered_words = [
        word for word in words 
        if word not in stop_words 
        and len(word) >= min_length 
        and not word.isdigit()
    ]
    
    # Count word frequencies
    word_counts = Counter(filtered_words)
    
    # Return top keywords
    return [word for word, count in word_counts.most_common(max_keywords)]


def get_stop_words() -> Set[str]:
    """Get set of common stop words."""
    return {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 
        'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 
        'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 
        'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 
        'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'his', 
        'hers', 'ours', 'theirs', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 
        'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 
        'will', 'would', 'shall', 'should', 'may', 'might', 'must', 'can', 'could', 
        'here', 'there', 'when', 'where', 'why', 'how', 'what', 'which', 'who', 
        'whom', 'whose', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 
        'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 
        'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'
    }


def extract_commands(text: str) -> List[Dict[str, str]]:
    """Extract command-like text from text."""
    commands = []
    
    # Common command patterns
    patterns = [
        r'\$[^\s]+',  # Shell commands
        r'>[^\s]+',   # Commands
        r'[a-zA-Z_-]+[=:][^\s]+',  # Key=value pairs
        r'npm [^\n]+',  # npm commands
        r'yarn [^\n]+',  # yarn commands
        r'python [^\n]+',  # python commands
        r'pip [^\n]+',  # pip commands
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.MULTILINE)
        for match in matches:
            commands.append({
                'command': match.strip(),
                'type': classify_command(match)
            })
    
    return commands


def classify_command(command: str) -> str:
    """Classify type of command."""
    command_lower = command.lower()
    
    if command_lower.startswith('$'):
        return 'shell'
    elif command_lower.startswith('npm'):
        return 'npm'
    elif command_lower.startswith('yarn'):
        return 'yarn'
    elif command_lower.startswith('python'):
        return 'python'
    elif command_lower.startswith('pip'):
        return 'pip'
    elif '=' in command or ':' in command:
        return 'assignment'
    else:
        return 'unknown'


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text."""
    return ' '.join(text.split())


def truncate_text(text: str, max_length: int, suffix: str = '...') -> str:
    """Truncate text to maximum length."""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences."""
    # Simple sentence splitting
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if s.strip()]


def calculate_text_complexity(text: str) -> Dict[str, float]:
    """Calculate text complexity metrics."""
    sentences = split_into_sentences(text)
    words = re.findall(r'\b\w+\b', text.lower())
    
    if not sentences or not words:
        return {}
    
    # Calculate various metrics
    avg_sentence_length = len(words) / len(sentences)
    avg_word_length = sum(len(word) for word in words) / len(words)
    unique_words = len(set(words))
    vocabulary_richness = unique_words / len(words)
    
    return {
        'avg_sentence_length': avg_sentence_length,
        'avg_word_length': avg_word_length,
        'vocabulary_richness': vocabulary_richness,
        'total_sentences': len(sentences),
        'total_words': len(words),
        'unique_words': unique_words
    }


def detect_programming_language(text: str) -> str:
    """Detect programming language from text."""
    language_patterns = {
        'python': [r'def\s+\w+', r'import\s+\w+', r'from\s+\w+\s+import', r'class\s+\w+'],
        'javascript': [r'function\s+\w+\s*\(', r'const\s+\w+\s*=', r'let\s+\w+\s*=', r'var\s+\w+\s*='],
        'java': [r'public\s+class\s+\w+', r'private\s+class\s+\w+', r'public\s+static\s+void'],
        'cpp': [r'#include\s*<\w+>', r'using\s+namespace', r'int\s+main'],
        'html': [r'<[a-zA-Z][^>]*>', r'</[a-zA-Z][^>]*>', r'<[a-zA-Z][^>]*/>'],
        'css': [r'[a-zA-Z-]+\s*{', r'}', r':\s*[a-zA-Z-]+'],
        'sql': [r'SELECT\s+.*\s+FROM', r'INSERT\s+INTO', r'UPDATE\s+\w+\s+SET'],
        'bash': [r'#!/bin/bash', r'#!/bin/sh', r'echo\s+[\'"]', r'ls\s+-'],
    }
    
    text_lower = text.lower()
    
    for language, patterns in language_patterns.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return language
    
    return 'unknown'


def remove_comments(text: str, language: str = 'unknown') -> str:
    """Remove comments from code text."""
    if language == 'python':
        # Remove single-line and multi-line comments
        text = re.sub(r'#.*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'""".*?"""', '', text, flags=re.DOTALL)
        text = re.sub(r"'''.*?'''", '', text, flags=re.DOTALL)
    elif language == 'javascript':
        # Remove single-line and multi-line comments
        text = re.sub(r'//.*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    elif language == 'java' or language == 'cpp':
        # Remove single-line and multi-line comments
        text = re.sub(r'//.*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    
    return text


def format_text_by_language(text: str, language: str = 'unknown') -> str:
    """Format text according to language conventions."""
    if language == 'python':
        # Python-specific formatting
        lines = text.split('\n')
        formatted_lines = []
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                formatted_lines.append('')
                continue
            
            # Handle dedents
            if stripped.startswith(('return', 'break', 'continue', 'pass')):
                if indent_level > 0:
                    indent_level -= 1
            
            formatted_lines.append('    ' * indent_level + stripped)
            
            # Handle indents
            if stripped.endswith(':'):
                indent_level += 1
        
        return '\n'.join(formatted_lines)
    
    return text