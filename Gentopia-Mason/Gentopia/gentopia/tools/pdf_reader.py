import PyPDF2
import requests
import arxiv
from gentopia.tools.basetool import *
import os
from pydantic import BaseModel, Field
from typing import Optional, Type

class PDFReaderArgs(BaseModel):
    """
    Argument model for PDFReader.

    Attributes:
        pdf_url (str): The URL of the PDF file to be processed.
    """
    pdf_url: str = Field(..., description="The URL of the PDF file")

class PDFReader(BaseTool):
    """
    Tool for downloading and extracting text from PDF files, with special handling for arXiv links.

    Attributes:
        name (str): Name of the tool.
        description (str): Brief description of the tool's functionality.
        args_schema (Optional[Type[BaseModel]]): Schema for the expected arguments.
    """
    name = "pdf_reader"
    description = "Downloads a PDF file from a URL, reads it, and returns its text content"
    args_schema: Optional[Type[BaseModel]] = PDFReaderArgs

    def get_arxiv_pdf_url(self, arxiv_url: str) -> Optional[str]:
        """
        Retrieves the direct PDF URL for a given arXiv paper link.

        Args:
            arxiv_url (str): The URL of the arXiv paper.

        Returns:
            Optional[str]: Direct URL to the PDF if successful; error message otherwise.
        """
        arxiv_id = arxiv_url.split('/')[-1]  # Extract the arXiv ID from the URL
        try:
            # Search for the paper using the arXiv API
            paper = next(arxiv.Search(id_list=[arxiv_id]).results())
            return paper.pdf_url
        except Exception as e:
            return f"Error retrieving arXiv PDF URL: {str(e)}"
    
    def download_pdf(self, pdf_url: str, local_filename: str) -> str:
        """
        Downloads a PDF from the specified URL and saves it locally.

        Args:
            pdf_url (str): The URL of the PDF to download.
            local_filename (str): The local path where the PDF will be saved.

        Returns:
            str: Local filename if successful; error message otherwise.
        """
        try:
            # Send a GET request to the PDF URL
            with requests.get(pdf_url, stream=True) as r:
                r.raise_for_status()  # Raise an error for bad status codes
                # Write the content to a local file in chunks
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            return local_filename
        except requests.exceptions.RequestException as e:
            return f"Error downloading PDF: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
   
    def _run(self, pdf_url: str) -> str:
        """
        Main method to process the PDF: downloads and extracts text.

        Args:
            pdf_url (str): The URL of the PDF or arXiv paper.

        Returns:
            str: Extracted text content or an error message.
        """
        # Check if the URL is an arXiv link
        if "arxiv.org" in pdf_url:
            pdf_url = self.get_arxiv_pdf_url(pdf_url)
            if "Error" in pdf_url:
                return pdf_url

        local_filename = "downloaded_pdf.pdf"
        download_status = self.download_pdf(pdf_url, local_filename)

        if "Error" in download_status:
            return download_status

        # Extract text from the downloaded PDF
        try:
            with open(local_filename, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                # Iterate through each page and extract text
                for page in reader.pages:
                    extracted_text = page.extract_text()
                    if extracted_text:
                        text += extracted_text
                # Return the first 1000 characters of the extracted text
                return text[:1000] + "..." if text else "No readable text found."
        except PyPDF2.errors.PdfReadError as e:
            return f"Error reading PDF: {str(e)}"
        except Exception as e:
            return f"Unexpected error during PDF reading: {str(e)}"
        finally:
            # Ensure the local file is removed after processing
            if os.path.exists(local_filename):
                os.remove(local_filename)
    
    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        """
        Asynchronous version of the run method. Not implemented.

        Raises:
            NotImplementedError: Always raised as this method is not implemented.
        """
        raise NotImplementedError
