"""
Agent 5: Reporter
Generates summary reports and metrics
"""

from typing import Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ReporterAgent:
    """Agent responsible for generating reports"""

    def generate_report(self, state: Dict[str, Any]) -> str:
        """
        Generate a comprehensive report of the sync operation
        Returns formatted report string
        """
        logger.info("Generating sync report...")

        try:
            stats = state.get('stats', {})
            errors = state.get('errors', [])
            run_id = state.get('run_id', 'unknown')

            # Build report
            lines = []

            lines.append(f"Run ID: {run_id}")
            lines.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append("")

            lines.append("STATISTICS:")
            lines.append(f"  - S3 Files Found: {stats.get('s3_files_found', 0)}")
            lines.append(f"  - Documents Parsed: {stats.get('documents_parsed', 0)}")
            lines.append(f"  - Documents Embedded: {stats.get('documents_embedded', 0)}")
            lines.append(f"  - Documents Uploaded: {stats.get('documents_uploaded', 0)}")
            lines.append("")

            # Upload results
            upload_results = state.get('upload_results', [])
            if upload_results:
                lines.append("UPLOAD RESULTS:")
                for result in upload_results:
                    status_icon = "✓" if result.get('status') == 'success' else "✗"
                    action = result.get('action', 'unknown')
                    file_name = result.get('file_name', 'unknown')
                    lines.append(f"  {status_icon} {file_name} ({action})")
                lines.append("")

            # Errors
            if errors:
                lines.append(f"ERRORS ({len(errors)}):")
                for i, error in enumerate(errors, 1):
                    lines.append(f"  {i}. {error}")
                lines.append("")

            # Summary
            total_files = stats.get('s3_files_found', 0)
            successful = stats.get('documents_uploaded', 0)
            failed = len(errors)

            if total_files == 0:
                lines.append("STATUS: No new files to process")
            elif successful == total_files and failed == 0:
                lines.append("STATUS: All files processed successfully")
            elif failed > 0:
                lines.append(f"STATUS: Completed with {failed} errors")
            else:
                lines.append("STATUS: Completed")

            report = "\n".join(lines)

            logger.info("Report generated successfully")

            return report

        except Exception as e:
            logger.error(f"Error generating report: {str(e)}", exc_info=True)
            return f"Error generating report: {str(e)}"
