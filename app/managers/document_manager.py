"""Manager for document operations."""
from typing import Optional, Tuple
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class DocumentManager:
    """Manages document operations.
    
    This class handles:
    - Opening and saving documents
    - File format conversion (TXT, DOCX, PDF)
    - Document state tracking
    - Auto-save functionality
    """

    SUPPORTED_FORMATS = {
        'txt': 'Text Files (*.txt)',
        'docx': 'Word Documents (*.docx)',
        'pdf': 'PDF Files (*.pdf)',
    }

    def __init__(self, auto_save_enabled: bool = False, auto_save_interval: int = 300):
        """Initialize the document manager.
        
        Args:
            auto_save_enabled: Whether auto-save is enabled
            auto_save_interval: Auto-save interval in seconds
        """
        self.current_file: Optional[str] = None
        self.modified = False
        self.auto_save_enabled = auto_save_enabled
        self.auto_save_interval = auto_save_interval
        logger.info("DocumentManager initialized")

    def new_document(self):
        """Create a new document."""
        self.current_file = None
        self.modified = False
        logger.info("New document created")

    def open_document(self, file_path: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Open a document from file.
        
        Args:
            file_path: Path to file to open
            
        Returns:
            Tuple of (success, content, error_message)
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return False, None, f"File not found: {file_path}"

            ext = path.suffix.lower().lstrip('.')
            
            if ext == 'txt':
                content = self._read_text_file(file_path)
            elif ext == 'docx':
                content = self._read_docx_file(file_path)
            elif ext == 'pdf':
                content = self._read_pdf_file(file_path)
            else:
                return False, None, f"Unsupported file format: {ext}"

            self.current_file = file_path
            self.modified = False
            logger.info(f"Opened document: {file_path}")
            return True, content, None

        except Exception as e:
            error_msg = f"Error opening file: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, None, error_msg

    def save_document(self, content: str, file_path: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """Save document to file.
        
        Args:
            content: Document content to save
            file_path: Optional path to save to (uses current_file if None)
            
        Returns:
            Tuple of (success, error_message)
        """
        save_path = file_path or self.current_file
        
        if not save_path:
            return False, "No file path specified"

        try:
            path = Path(save_path)
            ext = path.suffix.lower().lstrip('.')
            
            if ext == 'txt':
                self._write_text_file(save_path, content)
            elif ext == 'docx':
                self._write_docx_file(save_path, content)
            elif ext == 'pdf':
                self._write_pdf_file(save_path, content)
            else:
                return False, f"Unsupported file format: {ext}"

            self.current_file = save_path
            self.modified = False
            logger.info(f"Saved document: {save_path}")
            return True, None

        except Exception as e:
            error_msg = f"Error saving file: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg

    def mark_modified(self):
        """Mark document as modified."""
        self.modified = True

    def is_modified(self) -> bool:
        """Check if document has unsaved changes.
        
        Returns:
            True if document is modified
        """
        return self.modified

    def get_file_filter(self) -> str:
        """Get file filter string for file dialogs.
        
        Returns:
            Filter string for supported formats
        """
        filters = []
        filters.append("All Supported Files (*.txt *.docx *.pdf)")
        filters.extend(self.SUPPORTED_FORMATS.values())
        filters.append("All Files (*)")
        return ";;".join(filters)

    # Private helper methods for file I/O
    
    def _read_text_file(self, file_path: str) -> str:
        """Read a text file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _write_text_file(self, file_path: str, content: str):
        """Write a text file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def _read_docx_file(self, file_path: str) -> str:
        """Read a DOCX file."""
        try:
            from docx import Document
            doc = Document(file_path)
            return '\n'.join([para.text for para in doc.paragraphs])
        except ImportError:
            raise ImportError("python-docx is required for DOCX support")

    def _write_docx_file(self, file_path: str, content: str):
        """Write a DOCX file."""
        try:
            from docx import Document
            doc = Document()
            for line in content.split('\n'):
                doc.add_paragraph(line)
            doc.save(file_path)
        except ImportError:
            raise ImportError("python-docx is required for DOCX support")

    def _read_pdf_file(self, file_path: str) -> str:
        """Read a PDF file."""
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            text = []
            for page in reader.pages:
                text.append(page.extract_text())
            return '\n'.join(text)
        except ImportError:
            raise ImportError("pypdf is required for PDF support")

    def _write_pdf_file(self, file_path: str, content: str):
        """Write a PDF file."""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            c = canvas.Canvas(file_path, pagesize=letter)
            y = 750
            for line in content.split('\n'):
                c.drawString(50, y, line)
                y -= 20
                if y < 50:
                    c.showPage()
                    y = 750
            c.save()
        except ImportError:
            raise ImportError("reportlab is required for PDF support")
