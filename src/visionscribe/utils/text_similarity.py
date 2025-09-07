"""
Text similarity utilities for VisionScribe.
"""

import re
import math
from typing import List, Dict, Any
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_text_similarity(text1: str, text2: str, method: str = 'cosine') -> float:
    """Calculate similarity between two texts."""
    if not text1 or not text2:
        return 0.0
    
    # Clean texts
    text1 = clean_text(text1)
    text2 = clean_text(text2)
    
    if method == 'cosine':
        return _cosine_similarity(text1, text2)
    elif method == 'jaccard':
        return _jaccard_similarity(text1, text2)
    elif method == 'levenshtein':
        return _levenshtein_similarity(text1, text2)
    elif method == 'word_overlap':
        return _word_overlap_similarity(text1, text2)
    else:
        return _cosine_similarity(text1, text2)


def clean_text(text: str) -> str:
    """Clean text for similarity calculation."""
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove special characters but keep alphanumeric and common punctuation
    text = re.sub(r'[^\w\s\-\.\(\)\[\]\{\}:;#@\$%\^&\*\+=<>\/\?!\'\"~`|\\]', '', text)
    
    # Convert to lowercase
    text = text.lower()
    
    return text


def _cosine_similarity(text1: str, text2: str) -> float:
    """Calculate cosine similarity using TF-IDF."""
    try:
        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        
        # Calculate cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        return float(similarity)
    except Exception:
        return 0.0


def _jaccard_similarity(text1: str, text2: str) -> float:
    """Calculate Jaccard similarity."""
    # Tokenize texts
    words1 = set(text1.split())
    words2 = set(text2.split())
    
    # Calculate intersection and union
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    if union == 0:
        return 0.0
    
    return intersection / union


def _levenshtein_similarity(text1: str, text2: str) -> float:
    """Calculate Levenshtein similarity."""
    # Simple implementation of Levenshtein distance
    m, n = len(text1), len(text2)
    
    # Create matrix
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Initialize matrix
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    
    # Fill matrix
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i-1] == text2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
    
    # Convert distance to similarity
    max_len = max(m, n)
    if max_len == 0:
        return 1.0
    
    return 1 - (dp[m][n] / max_len)


def _word_overlap_similarity(text1: str, text2: str) -> float:
    """Calculate word overlap similarity."""
    words1 = text1.split()
    words2 = text2.split()
    
    if not words1 or not words2:
        return 0.0
    
    # Calculate overlap
    overlap = len(set(words1).intersection(set(words2)))
    total = len(set(words1).union(set(words2)))
    
    return overlap / total if total > 0 else 0.0


def calculate_similarity_matrix(texts: List[str], method: str = 'cosine') -> np.ndarray:
    """Calculate similarity matrix for multiple texts."""
    n = len(texts)
    similarity_matrix = np.zeros((n, n))
    
    for i in range(n):
        for j in range(n):
            if i == j:
                similarity_matrix[i][j] = 1.0
            else:
                similarity_matrix[i][j] = calculate_text_similarity(texts[i], texts[j], method)
    
    return similarity_matrix


def find_similar_pairs(texts: List[str], threshold: float = 0.8, method: str = 'cosine') -> List[tuple]:
    """Find similar text pairs above threshold."""
    similar_pairs = []
    
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            similarity = calculate_text_similarity(texts[i], texts[j], method)
            if similarity >= threshold:
                similar_pairs.append((i, j, similarity))
    
    # Sort by similarity
    similar_pairs.sort(key=lambda x: x[2], reverse=True)
    
    return similar_pairs


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from text using TF-IDF."""
    # Simple keyword extraction using TF-IDF
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Count word frequencies
    word_counts = Counter(words)
    
    # Filter out stop words and short words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'his', 'hers', 'ours', 'theirs'}
    
    filtered_words = [(word, count) for word, count in word_counts.items() 
                     if word not in stop_words and len(word) > 2]
    
    # Sort by frequency and return top keywords
    keywords = [word for word, count in sorted(filtered_words, key=lambda x: x[1], reverse=True)[:max_keywords]]
    
    return keywords


def normalize_text_similarity(similarity: float) -> float:
    """Normalize similarity score to 0-1 range."""
    return max(0.0, min(1.0, similarity))