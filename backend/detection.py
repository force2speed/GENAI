#!/usr/bin/env python3
"""
Flask API for Fake Information Detection
A clean, production-ready API for detecting fake information in text
"""

import os
import re
import time
import json
import logging
import warnings
import requests
import numpy as np
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Any
from urllib.parse import urlparse

# Flask
from flask import Flask, request, jsonify
from flask_cors import CORS

# Web scraping
from bs4 import BeautifulSoup
from urllib3.util.retry import Retry

# Google Generative AI
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class Config:
    """Pipeline configuration with robust defaults."""
    
    # Model settings - Updated to use available model
    gemini_model: str = "gemini-2.5-flash"  # Latest stable model
    
    # Scoring thresholds
    fake_score_threshold: float = 0.6
    reliable_threshold: float = 0.4
    
    # Request settings
    request_timeout: int = 5
    max_retries: int = 2
    max_content_length: int = 5000
    max_urls_to_process: int = 3
    
    # Processing limits
    max_claims_per_text: int = 10
    rate_limit_delay: float = 1.0
    
    # Gemini API settings
    temperature: float = 0.05
    max_output_tokens: int = 2000
    top_p: float = 0.9
    top_k: int = 40

# =============================================================================
# URL PROCESSOR
# =============================================================================

class URLProcessor:
    """Handles URL extraction and content scraping."""
    
    def __init__(self, config: Config):
        self.config = config
        
        # Configure session with retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=config.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text."""
        url_patterns = [
            r'https?://[^\s<>"{}|\\^`\[\]]+',
            r'www\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?'
        ]
        
        urls = []
        for pattern in url_patterns:
            matches = re.findall(pattern, text)
            urls.extend(matches)
        
        # Normalize URLs
        normalized_urls = []
        for url in urls:
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            normalized_urls.append(url)
        
        # Remove duplicates and limit count
        unique_urls = list(set(normalized_urls))
        return unique_urls[:self.config.max_urls_to_process]
    
    def scrape_url(self, url: str) -> Dict[str, Any]:
        """Safely scrape a single URL."""
        result = {
            'url': url,
            'title': None,
            'content': None,
            'domain': None,
            'success': False,
            'error': None
        }
        
        try:
            # Parse domain
            parsed = urlparse(url)
            result['domain'] = parsed.netloc
            
            # Make request
            response = self.session.get(
                url,
                timeout=self.config.request_timeout,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                result['error'] = 'Not HTML content'
                return result
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title_tag = soup.find('title')
            if title_tag:
                result['title'] = title_tag.get_text().strip()
            
            # Extract content
            content_selectors = [
                'main', 'article', '[role="main"]',
                '.content', '#content', '.post-content'
            ]
            
            content_text = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content_text = ' '.join([elem.get_text() for elem in elements])
                    break
            
            # Fallback to paragraphs
            if not content_text.strip():
                paragraphs = soup.find_all('p')
                content_text = ' '.join([p.get_text() for p in paragraphs])
            
            # Clean and limit content
            content_text = re.sub(r'\s+', ' ', content_text).strip()
            if len(content_text) > self.config.max_content_length:
                content_text = content_text[:self.config.max_content_length]
            
            result['content'] = content_text
            result['success'] = bool(content_text.strip())
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def process_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Process multiple URLs."""
        results = []
        
        for url in urls:
            result = self.scrape_url(url)
            results.append(result)
            time.sleep(self.config.rate_limit_delay)
        
        return results

# =============================================================================
# GEMINI-POWERED CLAIM EXTRACTOR
# =============================================================================

class GeminiClaimExtractor:
    """Extract factual claims using Gemini AI."""
    
    def __init__(self, config: Config, api_key: str):
        self.config = config
        if not api_key:
            raise ValueError("Gemini API key is required")
        
        logger.info(f"Initializing GeminiClaimExtractor with API key: {api_key[:10]}...")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(config.gemini_model)
        logger.info(f"Gemini model {config.gemini_model} initialized successfully")
    
    def extract_claims(self, text: str, scraped_content: List[Dict] = None) -> List[str]:
        """Extract factual claims from text using Gemini AI."""
        
        # ENHANCED: Handle very short texts as direct claims
        text_stripped = text.strip()
        if len(text_stripped) < 100 and len(text_stripped) > 5:
            # For short text, treat the entire text as a potential claim
            # But still run through Gemini for validation
            logger.info(f"Short text detected ({len(text_stripped)} chars), treating as direct claim")
        
        # Prepare context from scraped content
        context_text = ""
        if scraped_content:
            relevant_content = []
            for content in scraped_content[:2]:  # Limit to top 2 sources
                if content['success'] and content['content']:
                    relevant_content.append(f"Source ({content['domain']}): {content['content'][:500]}...")
            
            if relevant_content:
                context_text = f"\n\nAdditional context from URLs:\n" + "\n".join(relevant_content)
        
        prompt = f"""
        You are an expert fact-checker and misinformation analyst. Your task is to extract all verifiable factual claims from the given text that could potentially be fact-checked.

        ## TEXT TO ANALYZE:
        "{text}"
        {context_text}

        ## INSTRUCTIONS:
        Extract statements that make specific, verifiable factual assertions. Focus on:

        *INCLUDE these types of claims:*
        • Statistical data and percentages
        • Research findings and study results
        • Historical events and dates
        • Scientific facts and discoveries
        • Medical or health claims
        • Financial figures and economic data
        • Geographical or demographic information
        • Claims about specific people, organizations, or institutions
        • Statements about existence or non-existence of things
        • Categorical assertions ("X is Y", "X doesn't exist", etc.)

        *EXCLUDE these types of statements:*
        • Personal opinions ("I think...", "In my view...")
        • Future predictions ("This will happen...")
        • Subjective descriptions ("beautiful", "terrible")
        • Questions or rhetorical statements
        • General advice or recommendations
        • Emotional expressions

        *SPECIAL HANDLING:*
        • For very short texts (under 100 characters), if the entire text is a factual claim, extract it as-is
        • Don't ignore claims just because they're short or simple
        • Absolute statements ("X doesn't exist", "Y is fake") should be extracted

        ## OUTPUT FORMAT:
        Return exactly {self.config.max_claims_per_text} or fewer of the most significant, fact-checkable claims as a JSON array:

        ["First specific factual claim", "Second verifiable assertion", "Third statistical claim"]

        ## QUALITY CRITERIA:
        - Each claim should be a complete, standalone statement
        - Claims should be specific enough to be fact-checked
        - Prioritize claims with numbers, statistics, or specific details
        - Remove redundant or overlapping claims
        - Focus on the most consequential assertions
        - If the text is a single claim, return it in the array

        Respond with ONLY the JSON array, no additional text.
        """
        
        try:
            logger.info("Calling Gemini API to extract claims...")
            logger.info(f"Input text: {text[:100]}...")
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.config.temperature,
                    max_output_tokens=self.config.max_output_tokens,
                    top_p=self.config.top_p,
                    top_k=self.config.top_k
                )
            )
            
            # Extract JSON from response
            response_text = response.text.strip()
            logger.info(f"Gemini response: {response_text[:200]}...")
            
            # CRITICAL FIX: Check if response is empty or blocked
            if not response_text or len(response_text) < 5:
                logger.warning("Gemini returned empty or very short response, using fallback")
                if len(text.strip()) < 200 and len(text.strip()) > 5:
                    logger.info("Using original text as claim (empty Gemini response)")
                    return [text.strip()]
                return []
            
            # Try to find JSON array in the response
            json_match = re.search(r'\[.*?\]', response_text, re.DOTALL)
            if json_match:
                try:
                    claims = json.loads(json_match.group(0))
                    if isinstance(claims, list):
                        # Filter and clean claims
                        valid_claims = []
                        for claim in claims:
                            if isinstance(claim, str) and len(claim.strip()) > 10:
                                valid_claims.append(claim.strip())
                        
                        return valid_claims[:self.config.max_claims_per_text]
                except json.JSONDecodeError:
                    pass
            
            # Fallback: try to extract claims from lines
            lines = response_text.split('\n')
            claims = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith(('-', '*', '•')) and len(line) > 20:
                    # Remove quotes and numbering
                    clean_line = re.sub(r'^["\d\.\-\s]*', '', line).strip(' "')
                    if clean_line and len(clean_line) > 10:
                        claims.append(clean_line)
            
            # ENHANCED: If no claims found and text is short, use the original text as claim
            if not claims and len(text.strip()) < 200 and len(text.strip()) > 5:
                logger.info("No claims extracted, using original short text as claim")
                claims = [text.strip()]
            
            return claims[:self.config.max_claims_per_text]
            
        except Exception as e:
            logger.error(f"Error extracting claims: {str(e)}", exc_info=True)
            # CRITICAL FIX: Use fallback even on exception for short texts
            if len(text.strip()) < 200 and len(text.strip()) > 5:
                logger.warning(f"Using original text as claim due to exception: {text.strip()}")
                return [text.strip()]
            return []

# =============================================================================
# ENHANCED GEMINI VALIDATOR
# =============================================================================

class EnhancedGeminiValidator:
    """Advanced Gemini-based validation with sophisticated prompting."""
    
    def __init__(self, config: Config, api_key: str):
        self.config = config
        if not api_key:
            raise ValueError("Gemini API key is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(config.gemini_model)
    
    def validate_claim(self, claim: str, context: str = None) -> Dict[str, Any]:
        """Validate a claim using advanced fact-checking prompts."""
        
        context_section = ""
        if context and context.strip():
            context_section = f"""
            
            Available Context:
            {context[:1000]}...
            """
        
        prompt = f"""
        You are a world-class fact-checker and misinformation analyst with expertise in evaluating information credibility across all domains. Analyze the following claim with the highest standards of journalistic integrity.

        ## CLAIM TO EVALUATE:
        "{claim}"
        {context_section}

        ## COMPREHENSIVE EVALUATION FRAMEWORK:

        *1. FACTUAL ACCURACY (40% weight)*
        - Is this claim supported by peer-reviewed research, authoritative sources, or verified data?
        - Does it align with current scientific consensus or established facts?
        - Are there credible contradicting sources?

        *2. SOURCE CREDIBILITY (25% weight)*
        - What is the implied or stated source of this information?
        - Are the sources authoritative, independent, and transparent?
        - Is there potential bias, conflict of interest, or agenda?

        *3. PLAUSIBILITY & CONTEXT (20% weight)*
        - Is the claim realistic given current knowledge and capabilities?
        - Does it align with established scientific principles or logical reasoning?
        - Are the numbers, timeframes, and scope reasonable?

        *4. EVIDENCE QUALITY (10% weight)*
        - Is the supporting evidence sufficient, relevant, and recent?
        - Are methodologies sound and sample sizes adequate?
        - Has the evidence been independently verified or replicated?

        *5. RED FLAGS DETECTION (5% weight)*
        - Extraordinary claims without extraordinary evidence
        - Sensational or emotionally charged language
        - Missing crucial details or context
        - Correlation presented as causation
        - Cherry-picked data or misrepresented statistics

        ## SCORING GUIDELINES:
        - *0.9-1.0*: Exceptionally well-documented, multiple authoritative sources, scientific consensus
        - *0.8-0.9*: Strong evidence, reputable sources, minimal uncertainties
        - *0.7-0.8*: Good evidence, credible sources, some minor gaps
        - *0.6-0.7*: Moderate evidence, mixed source quality, notable uncertainties
        - *0.5-0.6*: Weak evidence, questionable sources, significant doubts
        - *0.4-0.5*: Poor evidence, unreliable sources, major concerns
        - *0.3-0.4*: Very poor evidence, dubious sources, contradicts known facts
        - *0.2-0.3*: Highly suspicious, likely false, lacks credible support
        - *0.0-0.2*: Demonstrably false, contradicts established science, clear misinformation

        ## REQUIRED OUTPUT FORMAT:
        json
        {{
            "credibility_score": [precise decimal 0.0-1.0],
            "explanation": "[detailed 2-3 sentence analysis of why this score was assigned]",
            "confidence": "[high/medium/low - your confidence in this assessment]",
            "red_flags": ["list", "of", "specific", "concerning", "elements"],
            "supporting_factors": ["list", "of", "credible", "or", "positive", "elements"],
            "evidence_quality": "[excellent/good/fair/poor/none]",
            "source_assessment": "[authoritative/credible/mixed/questionable/unreliable]"
        }}
        

        Provide a thorough, objective, and evidence-based evaluation. Be precise with your scoring and specific in identifying both strengths and weaknesses.
        """
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.config.temperature,
                    max_output_tokens=self.config.max_output_tokens,
                    top_p=self.config.top_p,
                    top_k=self.config.top_k
                )
            )
            
            # Parse JSON response
            response_text = response.text.strip()
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                try:
                    result = json.loads(json_match.group(0))
                    
                    # Validate and sanitize the result
                    validated_result = {
                        'credibility_score': max(0.0, min(1.0, float(result.get('credibility_score', 0.5)))),
                        'explanation': str(result.get('explanation', 'Analysis completed'))[:500],
                        'confidence': str(result.get('confidence', 'medium')).lower(),
                        'red_flags': result.get('red_flags', [])[:5],  # Limit to 5 red flags
                        'supporting_factors': result.get('supporting_factors', [])[:5],  # Limit to 5 factors
                        'evidence_quality': str(result.get('evidence_quality', 'unknown')).lower(),
                        'source_assessment': str(result.get('source_assessment', 'unknown')).lower(),
                        'claim': claim
                    }
                    
                    return validated_result
                    
                except (json.JSONDecodeError, ValueError, TypeError) as e:
                    logger.warning(f"JSON parsing error: {e}")
            
            # If JSON parsing fails, extract score from text
            score_patterns = [
                r'credibility[_\s]score[:\s](\d+\.?\d*)',
                r'score[:\s](\d+\.?\d)',
                r'(\d+\.?\d*)[/\s](?:out of|/)?\s(?:10|1\.0|1)'
            ]
            
            extracted_score = 0.5
            for pattern in score_patterns:
                match = re.search(pattern, response_text, re.IGNORECASE)
                if match:
                    score = float(match.group(1))
                    if score > 1:
                        score = score / 10.0 if score <= 10 else 0.5
                    extracted_score = max(0.0, min(1.0, score))
                    break
            
            return {
                'credibility_score': extracted_score,
                'explanation': response_text[:300] + "..." if len(response_text) > 300 else response_text,
                'confidence': 'low',
                'red_flags': [],
                'supporting_factors': [],
                'evidence_quality': 'unknown',
                'source_assessment': 'unknown',
                'claim': claim
            }
            
        except Exception as e:
            logger.error(f"Error validating claim: {str(e)}")
            return {
                'credibility_score': 0.5,
                'explanation': f'Validation failed: {str(e)[:100]}',
                'confidence': 'low',
                'red_flags': ['validation_error'],
                'supporting_factors': [],
                'evidence_quality': 'unknown',
                'source_assessment': 'unknown',
                'claim': claim
            }
    
    def detect_stance(self, text: str, claim: str) -> Dict[str, Any]:
        """Detect stance using sophisticated analysis."""
        
        prompt = f"""
        You are an expert in discourse analysis and rhetorical examination. Analyze how the given text relates to a specific claim using advanced linguistic and contextual analysis.

        ## TEXT TO ANALYZE:
        "{text[:1000]}..."

        ## TARGET CLAIM:
        "{claim}"

        ## ANALYTICAL FRAMEWORK:

        *PRIMARY TASK*: Determine the stance relationship between the text and the specific claim.

        *STANCE CATEGORIES:*
        1. *SUPPORT*: Text explicitly or implicitly agrees with, endorses, reinforces, or provides evidence for the claim
        2. *REFUTE*: Text explicitly or implicitly contradicts, disputes, challenges, or provides counter-evidence to the claim
        3. *NEUTRAL*: Text acknowledges the claim but maintains objectivity without taking a clear position
        4. *UNRELATED*: Text does not address, mention, or relate to the claim in any meaningful way

        *ANALYSIS INDICATORS:*
        - *Language tone*: Positive, negative, or neutral framing
        - *Evidential support*: Does text provide supporting or contradicting evidence?
        - *Contextual positioning*: How is the claim presented within the broader narrative?
        - *Implicit bias*: Subtle indicators of author's position
        - *Rhetorical devices*: Use of persuasive language, emphasis, or dismissal

        *CONFIDENCE ASSESSMENT:*
        - *0.9-1.0*: Extremely clear and explicit stance indicators
        - *0.8-0.9*: Strong and consistent stance signals
        - *0.7-0.8*: Clear stance with good supporting evidence
        - *0.6-0.7*: Moderate stance with some ambiguity
        - *0.5-0.6*: Weak or mixed signals
        - *0.3-0.5*: Unclear or contradictory indicators
        - *0.0-0.3*: Very ambiguous or no clear stance

        ## REQUIRED OUTPUT FORMAT:
        json
        {{
            "stance": "[support/refute/neutral/unrelated]",
            "confidence": [precise decimal 0.0-1.0],
            "explanation": "[detailed 2-3 sentence analysis of the stance relationship]",
            "key_phrases": ["specific", "textual", "evidence", "supporting", "stance"],
            "reasoning": "[step-by-step logical analysis of how you reached this conclusion]",
            "context_influence": "[how broader context affects the stance interpretation]"
        }}
        

        Focus on specific textual evidence and provide clear reasoning for your stance assessment. Be precise and objective in your analysis.
        """
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.config.temperature,
                    max_output_tokens=self.config.max_output_tokens,
                    top_p=self.config.top_p,
                    top_k=self.config.top_k
                )
            )
            
            response_text = response.text.strip()
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                try:
                    result = json.loads(json_match.group(0))
                    
                    # Validate stance
                    stance = str(result.get('stance', 'neutral')).lower()
                    if stance not in ['support', 'refute', 'neutral', 'unrelated']:
                        stance = 'neutral'
                    
                    validated_result = {
                        'stance': stance,
                        'confidence': max(0.0, min(1.0, float(result.get('confidence', 0.5)))),
                        'explanation': str(result.get('explanation', 'Stance analysis completed'))[:300],
                        'key_phrases': result.get('key_phrases', [])[:5],
                        'reasoning': str(result.get('reasoning', ''))[:300],
                        'context_influence': str(result.get('context_influence', ''))[:200],
                        'claim': claim
                    }
                    
                    return validated_result
                    
                except (json.JSONDecodeError, ValueError, TypeError):
                    pass
            
            # Extract stance from text if JSON fails
            response_lower = response_text.lower()
            
            if any(word in response_lower for word in ['support', 'agree', 'endorse', 'confirm']):
                stance = 'support'
            elif any(word in response_lower for word in ['refute', 'contradict', 'dispute', 'deny']):
                stance = 'refute'
            elif any(word in response_lower for word in ['unrelated', 'irrelevant', 'no mention']):
                stance = 'unrelated'
            else:
                stance = 'neutral'
            
            # Extract confidence
            conf_match = re.search(r'confidence[:\s](\d+\.?\d)', response_text, re.IGNORECASE)
            confidence = 0.6
            if conf_match:
                conf_val = float(conf_match.group(1))
                confidence = conf_val / 10.0 if conf_val > 1 else conf_val
                confidence = max(0.0, min(1.0, confidence))
            
            return {
                'stance': stance,
                'confidence': confidence,
                'explanation': response_text[:200] + "..." if len(response_text) > 200 else response_text,
                'key_phrases': [],
                'reasoning': 'Extracted from non-JSON response',
                'context_influence': 'Unable to analyze context',
                'claim': claim
            }
            
        except Exception as e:
            logger.error(f"Error detecting stance: {str(e)}")
            return {
                'stance': 'neutral',
                'confidence': 0.5,
                'explanation': f'Stance detection failed: {str(e)[:100]}',
                'key_phrases': [],
                'reasoning': 'Error in analysis',
                'context_influence': 'Unable to analyze due to error',
                'claim': claim
            }

# =============================================================================
# ENHANCED FAKE INFO DETECTOR
# =============================================================================

class EnhancedFakeInfoDetector:
    """Enhanced pipeline using only Gemini AI for all analysis."""
    
    def __init__(self, gemini_api_key: str):
        self.config = Config()
        
        # Initialize components
        logger.info("Initializing Enhanced Fake Information Detector...")
        self.url_processor = URLProcessor(self.config)
        self.claim_extractor = GeminiClaimExtractor(self.config, gemini_api_key)
        self.validator = EnhancedGeminiValidator(self.config, gemini_api_key)
        logger.info("Initialization complete!")
    
    def analyze_text(self, text: str, scrape_urls: bool = True) -> Dict[str, Any]:
        """Comprehensive analysis using only Gemini AI."""
        logger.info(f"Analyzing text ({len(text)} characters)...")
        
        # Initialize results with enhanced structure
        results = {
            'extracted_claims': [],
            'claim_validations': [],
            'stance_detections': [],
            'final_fake_score': 0.5,
            'assessment': 'mixed_credibility',
            'confidence_level': 'medium',
            'urls_processed': [],
            'processing_info': {},
            'risk_factors': [],
            'credibility_indicators': []
        }
        
        try:
            # Step 1: Extract URLs
            urls = self.url_processor.extract_urls(text)
            logger.info(f"Found {len(urls)} URLs")
            
            # Step 2: Scrape URLs if requested
            scraped_content = []
            if scrape_urls and urls:
                scraped_content = self.url_processor.process_urls(urls)
                results['urls_processed'] = scraped_content
            
            # Step 3: Extract claims using Gemini
            claims = self.claim_extractor.extract_claims(text, scraped_content)
            results['extracted_claims'] = claims
            logger.info(f"Extracted {len(claims)} claims")
            
            # Step 4: Validate claims with enhanced analysis
            validations = []
            context = ' '.join([c['content'] for c in scraped_content if c['success']])
            
            for i, claim in enumerate(claims):
                logger.info(f"Validating claim {i+1}/{len(claims)}")
                validation = self.validator.validate_claim(claim, context)
                validations.append(validation)
                time.sleep(self.config.rate_limit_delay)
            
            results['claim_validations'] = validations
            
            # Step 5: Detect stances with advanced analysis
            stances = []
            for i, claim in enumerate(claims):
                logger.info(f"Analyzing stance {i+1}/{len(claims)}")
                stance = self.validator.detect_stance(text, claim)
                stances.append(stance)
                time.sleep(self.config.rate_limit_delay)
            
            results['stance_detections'] = stances
            
            # Step 6: Enhanced fake score calculation
            final_score, assessment, confidence, risk_factors, credibility_indicators = self._calculate_enhanced_fake_score(
                validations, stances, scraped_content, text
            )
            
            results['final_fake_score'] = final_score
            results['assessment'] = assessment
            results['confidence_level'] = confidence
            results['risk_factors'] = risk_factors
            results['credibility_indicators'] = credibility_indicators
            
            # Step 7: Comprehensive processing info
            results['processing_info'] = {
                'urls_found': len(urls),
                'urls_scraped_successfully': sum(1 for c in scraped_content if c['success']),
                'claims_extracted': len(claims),
                'avg_credibility': np.mean([v['credibility_score'] for v in validations]) if validations else 0.5,
                'credibility_std': np.std([v['credibility_score'] for v in validations]) if validations else 0.0,
                'high_confidence_validations': sum(1 for v in validations if v.get('confidence') == 'high'),
                'total_red_flags': sum(len(v.get('red_flags', [])) for v in validations),
                'supporting_factors_count': sum(len(v.get('supporting_factors', [])) for v in validations)
            }
            
            logger.info(f"Enhanced analysis complete! Score: {final_score:.3f} ({assessment}) - Confidence: {confidence}")
            
        except Exception as e:
            logger.error(f"Error during enhanced analysis: {str(e)}")
            results['processing_info']['error'] = str(e)
            results['risk_factors'].append('analysis_error')
        
        return results
    
    def _calculate_enhanced_fake_score(self, validations: List[Dict], stances: List[Dict], 
                                     scraped_content: List[Dict], original_text: str) -> Tuple[float, str, str, List[str], List[str]]:
        """Calculate enhanced fake information score with detailed analysis."""
        
        if not validations:
            return 0.5, 'mixed_credibility', 'low', ['no_claims_found'], []
        
        risk_factors = []
        credibility_indicators = []
        
        # 1. Credibility Analysis (40% weight)
        credibility_scores = [v['credibility_score'] for v in validations]
        avg_credibility = np.mean(credibility_scores)
        credibility_std = np.std(credibility_scores)
        
        credibility_factor = 1 - avg_credibility
        
        # ENHANCED: Boost fake score for unreliable sources
        unreliable_sources = sum(1 for v in validations if v.get('source_assessment') in ['unreliable', 'questionable'])
        if unreliable_sources > 0:
            # Add 0.2 to credibility_factor for each unreliable source (capped at +0.4)
            credibility_factor = min(1.0, credibility_factor + (unreliable_sources * 0.2))
            risk_factors.append(f'unreliable_sources_{unreliable_sources}')
        
        # Check for extremely low credibility claims
        very_low_credibility = sum(1 for score in credibility_scores if score < 0.3)
        if very_low_credibility > 0:
            risk_factors.append(f'very_low_credibility_claims_{very_low_credibility}')
        
        # Check for high credibility claims
        high_credibility = sum(1 for score in credibility_scores if score > 0.7)
        if high_credibility > 0:
            credibility_indicators.append(f'high_credibility_claims_{high_credibility}')
        
        # 2. Stance Analysis (25% weight)
        # FIXED: Inverted logic - if text supports a false claim, it should increase fake score
        stance_weights = {'support': 1.0, 'neutral': 0.5, 'unrelated': 0.3, 'refute': 0.0}
        stance_scores = []
        
        support_count = refute_count = neutral_count = 0
        
        for stance in stances:
            stance_type = stance['stance']
            confidence = stance.get('confidence', 0.5)
            weight = stance_weights.get(stance_type, 0.5)
            stance_scores.append(weight * confidence)
            
            if stance_type == 'support':
                support_count += 1
            elif stance_type == 'refute':
                refute_count += 1
            elif stance_type == 'neutral':
                neutral_count += 1
        
        avg_stance_score = np.mean(stance_scores) if stance_scores else 0.5
        
        # Analyze stance patterns
        if refute_count > support_count:
            risk_factors.append('contradictory_stances')
        elif support_count > 0 and refute_count == 0:
            credibility_indicators.append('consistent_support')
        
        # 3. Red Flags Analysis (20% weight)
        total_red_flags = sum(len(v.get('red_flags', [])) for v in validations)
        red_flag_factor = min(1.0, total_red_flags / 10.0)  # Normalize to 0-1
        
        if total_red_flags > 5:
            risk_factors.append(f'high_red_flags_{total_red_flags}')
        
        # 4. Supporting Factors Analysis (boost credibility)
        total_supporting = sum(len(v.get('supporting_factors', [])) for v in validations)
        supporting_factor = min(1.0, total_supporting / 10.0)
        
        if total_supporting > 3:
            credibility_indicators.append(f'supporting_evidence_{total_supporting}')
        
        # 5. URL Analysis (10% weight)
        url_factor = 0.5
        if scraped_content:
            failed_scrapes = sum(1 for c in scraped_content if not c['success'])
            total_urls = len(scraped_content)
            url_factor = failed_scrapes / total_urls if total_urls > 0 else 0.5
            
            if failed_scrapes > total_urls * 0.5:
                risk_factors.append('suspicious_urls')
        
        # 6. Confidence Analysis (5% weight)
        high_confidence_validations = sum(1 for v in validations if v.get('confidence') == 'high')
        confidence_factor = 1 - (high_confidence_validations / len(validations))
        
        if high_confidence_validations == 0:
            risk_factors.append('low_validation_confidence')
        elif high_confidence_validations == len(validations):
            credibility_indicators.append('high_validation_confidence')
        
        # Calculate weighted fake score
        fake_score = (
            0.40 * credibility_factor +
            0.25 * avg_stance_score +
            0.20 * red_flag_factor +
            0.10 * url_factor +
            0.05 * confidence_factor
        )
        
        # Apply supporting factors bonus (reduce fake score)
        fake_score = max(0.0, fake_score - (supporting_factor * 0.15))
        
        # Ensure score is in valid range
        fake_score = max(0.0, min(1.0, fake_score))
        
        # Determine assessment with enhanced categories
        if fake_score >= 0.8:
            assessment = 'highly_likely_fake'
        elif fake_score >= self.config.fake_score_threshold:  # 0.65
            assessment = 'likely_fake'
        elif fake_score >= 0.40:  # Lowered from 0.45 for better accuracy
            assessment = 'mixed_credibility'
        elif fake_score >= self.config.reliable_threshold:  # 0.30
            assessment = 'likely_reliable'
        else:
            assessment = 'highly_reliable'
        
        # Determine overall confidence level
        if credibility_std < 0.2 and high_confidence_validations > len(validations) * 0.7:
            confidence_level = 'high'
        elif credibility_std < 0.4 and high_confidence_validations > len(validations) * 0.3:
            confidence_level = 'medium'
        else:
            confidence_level = 'low'
        
        # Add text-specific risk factors
        text_lower = original_text.lower()
        if any(phrase in text_lower for phrase in ['breaking news', 'urgent', 'shocking', 'you won\'t believe']):
            risk_factors.append('sensational_language')
        
        if re.search(r'\d+%', original_text) and not any(phrase in text_lower for phrase in ['study', 'research', 'survey']):
            risk_factors.append('unsourced_statistics')
        
        return fake_score, assessment, confidence_level, risk_factors, credibility_indicators

# =============================================================================
# FLASK APP
# =============================================================================

app = Flask(__name__)

# Configure CORS to allow requests from your frontend
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://frontend-truthscope123.web.app",
            "https://frontend-truthscope123.firebaseapp.com",
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:5000"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})


# Global detector instance, initialized from environment variable
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    logger.error('GEMINI_API_KEY environment variable not set. Detector will not be initialized.')
    detector = None
else:
    detector = EnhancedFakeInfoDetector(GEMINI_API_KEY)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'detector_initialized': detector is not None,
        'api_version': '2.0',
        'gemini_model': 'gemini-2.0-flash-exp',
        'features': ['gemini_2_0_flash_exp', 'advanced_prompting', 'enhanced_scoring', 'detailed_risk_assessment']
    })

@app.route('/analyze', methods=['POST'])
def analyze_text():
    """Analyze text for fake information."""
    global detector
    
    if detector is None:
        return jsonify({'error': 'Detector not initialized. Call /initialize first'}), 400
    
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'text field is required'}), 400
        
        text = data['text']
        scrape_urls = data.get('scrape_urls', True)
        
        if not text.strip():
            return jsonify({'error': 'Text cannot be empty'}), 400
        
        # Analyze the text
        results = detector.analyze_text(text, scrape_urls)
        
        return jsonify({
            'status': 'success',
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/analyze/quick', methods=['POST'])
def analyze_text_quick():
    """Quick analysis without URL scraping."""
    global detector
    
    if detector is None:
        return jsonify({'error': 'Detector not initialized. Call /initialize first'}), 400
    
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'text field is required'}), 400
        
        text = data['text']
        
        if not text.strip():
            return jsonify({'error': 'Text cannot be empty'}), 400
        
        # Analyze without URL scraping for faster response
        results = detector.analyze_text(text, scrape_urls=False)
        
        # Return enhanced simplified response
        simplified_results = {
            'final_fake_score': results['final_fake_score'],
            'assessment': results['assessment'],
            'confidence_level': results['confidence_level'],
            'claims_count': len(results['extracted_claims']),
            'avg_credibility': results['processing_info'].get('avg_credibility', 0.5),
            'risk_factors': results['risk_factors'],
            'credibility_indicators': results['credibility_indicators'],
            'red_flags_total': results['processing_info'].get('total_red_flags', 0),
            'high_confidence_validations': results['processing_info'].get('high_confidence_validations', 0)
        }
        
        return jsonify({
            'status': 'success',
            'results': simplified_results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in quick analyze endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/analyze/detailed', methods=['POST'])
def analyze_text_detailed():
    """Comprehensive analysis with all details."""
    global detector
    
    if detector is None:
        return jsonify({'error': 'Detector not initialized. Call /initialize first'}), 400
    
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'text field is required'}), 400
        
        text = data['text']
        scrape_urls = data.get('scrape_urls', True)
        
        if not text.strip():
            return jsonify({'error': 'Text cannot be empty'}), 400
        
        # Full comprehensive analysis
        results = detector.analyze_text(text, scrape_urls)
        
        return jsonify({
            'status': 'success',
            'results': results,
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'comprehensive'
        })
        
    except Exception as e:
        logger.error(f"Error in detailed analyze endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("Enhanced Fake Information Detection API v2.0")
    print("===========================================")
    print("Powered by Google Gemini 2.0 Flash Experimental")
    print("\nAdvanced Features:")
    print("  • State-of-the-art Gemini 2.0 Flash Experimental model")
    print("  • Advanced multi-criteria claim extraction")
    print("  • Sophisticated credibility assessment framework")
    print("  • Enhanced stance detection with discourse analysis")
    print("  • Comprehensive risk factor identification")
    print("  • Evidence quality and source credibility evaluation")
    print("  • Context-aware analysis with detailed reasoning")
    print("\nAvailable endpoints:")
    print("  GET  /health - Health check with model information")
    print("  POST /initialize - Initialize with Gemini API key")
    print("  POST /analyze - Legacy full analysis endpoint")
    print("  POST /analyze/quick - Fast analysis without URL scraping")
    print("  POST /analyze/detailed - Comprehensive analysis with all features")
    print("\nStarting server...")
    
    app.run(debug=True, host='0.0.0.0', port=5000)