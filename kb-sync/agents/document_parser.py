"""
Agent 2: Document Parser
Parses markdown files and extracts metadata and content
"""

import re
from typing import Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DocumentParserAgent:
    """Agent responsible for parsing markdown documents"""

    def parse_markdown(self, s3_file: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse markdown content and extract structured data
        Returns parsed document with metadata
        """
        content = s3_file['content']
        file_name = s3_file['file_name']

        logger.info(f"Parsing document: {file_name}")

        try:
            parsed_doc = {
                'file_name': file_name,
                's3_key': s3_file['s3_key'],
                'etag': s3_file['etag'],
                'last_modified': s3_file['last_modified'],
                'size_bytes': s3_file['size_bytes'],
                'raw_content': content,
                'parsed_at': datetime.now().isoformat()
            }

            # Extract title (first H1)
            title_match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
            parsed_doc['title'] = title_match.group(1).strip() if title_match else file_name

            # Extract error ID
            error_id_match = re.search(r'\*\*Error ID\*\*\s*\|\s*(.+?)\s*\|', content)
            parsed_doc['error_id'] = error_id_match.group(1).strip() if error_id_match else None

            # Extract error name
            error_name_match = re.search(r'\*\*Error Name\*\*\s*\|\s*(.+?)\s*\|', content)
            parsed_doc['error_name'] = error_name_match.group(1).strip() if error_name_match else None

            # Extract category
            category_match = re.search(r'\*\*Category\*\*\s*\|\s*(.+?)\s*\|', content)
            parsed_doc['category'] = category_match.group(1).strip() if category_match else None

            # Extract severity
            severity_match = re.search(r'\*\*Severity\*\*\s*\|\s*(.+?)\s*\|', content)
            parsed_doc['severity'] = severity_match.group(1).strip() if severity_match else None

            # Extract quick summary
            summary_match = re.search(r'### 🎯 Quick Summary\s*\n\s*\*\*What happens\*\*:\s*(.+?)(?=\n\s*\*\*|$)', content, re.DOTALL)
            parsed_doc['quick_summary'] = summary_match.group(1).strip() if summary_match else None

            # Extract tags
            tags_match = re.search(r'`([^`]+)`(?:\s+`([^`]+)`)*', content)
            if tags_match:
                tags = re.findall(r'`([^`]+)`', content)
                parsed_doc['tags'] = [tag.strip() for tag in tags if tag.strip()]
            else:
                parsed_doc['tags'] = []

            # Extract sections for better chunking
            sections = {}

            # Symptoms section
            symptoms_match = re.search(r'### 🔍 Symptoms\s*\n(.*?)(?=###|\Z)', content, re.DOTALL)
            sections['symptoms'] = symptoms_match.group(1).strip() if symptoms_match else ""

            # Error messages section
            error_messages_match = re.search(r'### 💬 Error Messages\s*\n(.*?)(?=###|\Z)', content, re.DOTALL)
            sections['error_messages'] = error_messages_match.group(1).strip() if error_messages_match else ""

            # Root cause section
            root_cause_match = re.search(r'### 🔬 Root Cause Analysis\s*\n(.*?)(?=###|\Z)', content, re.DOTALL)
            sections['root_cause'] = root_cause_match.group(1).strip() if root_cause_match else ""

            # Resolution steps section
            resolution_match = re.search(r'### 🛠️ Resolution Steps\s*\n(.*?)(?=###|\Z)', content, re.DOTALL)
            sections['resolution_steps'] = resolution_match.group(1).strip() if resolution_match else ""

            # Prevention section
            prevention_match = re.search(r'### 🛡️ Prevention Strategies\s*\n(.*?)(?=###|\Z)', content, re.DOTALL)
            sections['prevention'] = prevention_match.group(1).strip() if prevention_match else ""

            parsed_doc['sections'] = sections

            # Create text for embedding (structured summary)
            embedding_text = self._create_embedding_text(parsed_doc)
            parsed_doc['embedding_text'] = embedding_text

            logger.info(f"Successfully parsed: {file_name}")
            logger.debug(f"Extracted metadata: error_id={parsed_doc.get('error_id')}, "
                        f"category={parsed_doc.get('category')}, tags={len(parsed_doc.get('tags', []))}")

            return parsed_doc

        except Exception as e:
            logger.error(f"Error parsing document {file_name}: {str(e)}", exc_info=True)
            raise

    def _create_embedding_text(self, parsed_doc: Dict[str, Any]) -> str:
        """
        Create optimized text for embedding
        Combines key information in a structured way
        """
        parts = []

        # Title and metadata
        if parsed_doc.get('title'):
            parts.append(f"Title: {parsed_doc['title']}")

        if parsed_doc.get('error_id'):
            parts.append(f"Error ID: {parsed_doc['error_id']}")

        if parsed_doc.get('error_name'):
            parts.append(f"Error Name: {parsed_doc['error_name']}")

        if parsed_doc.get('category'):
            parts.append(f"Category: {parsed_doc['category']}")

        if parsed_doc.get('quick_summary'):
            parts.append(f"Summary: {parsed_doc['quick_summary']}")

        # Add key sections
        sections = parsed_doc.get('sections', {})

        if sections.get('symptoms'):
            parts.append(f"Symptoms: {sections['symptoms'][:500]}")  # First 500 chars

        if sections.get('error_messages'):
            parts.append(f"Error Messages: {sections['error_messages'][:500]}")

        if sections.get('root_cause'):
            parts.append(f"Root Cause: {sections['root_cause'][:500]}")

        if sections.get('resolution_steps'):
            parts.append(f"Resolution: {sections['resolution_steps'][:1000]}")  # More space for resolution

        # Tags
        if parsed_doc.get('tags'):
            parts.append(f"Tags: {', '.join(parsed_doc['tags'])}")

        return "\n\n".join(parts)
