import logging
import os
import re
import subprocess
from datetime import datetime
from urllib.parse import urlparse

import typer
from rich.console import Console

console = Console()

# Create a logger at the module level
logger = logging.getLogger(__name__)

app = typer.Typer(rich_markup_mode="markdown")


def validate_url(value: str) -> bool:
    """
    Validate if the given string is a valid URL.

    Args:
        value (str): The URL to validate.

    Returns:
        bool: True if the URL is valid, False otherwise.
    """
    try:
        result = urlparse(value)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def generate_output_name(url: str) -> str:
    """
    Generate a meaningful output name based on the URL, always including the domain name.

    Args:
        url (str): The URL to generate the output name from.

    Returns:
        str: A string representing the output name.
    """
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    path_parts = parsed_url.path.split("/")

    # Remove empty parts and the first part (which is usually empty)
    path_parts = [part for part in path_parts if part]

    if path_parts:
        # Use the last part of the path as the base name
        base_name = path_parts[-1]
    else:
        # If no path parts, use 'index' as the base name
        base_name = "index"

    # Remove any file extension
    base_name = os.path.splitext(base_name)[0]

    # Replace any non-alphanumeric characters with underscores
    base_name = re.sub(r"\W+", "_", base_name)

    # Add a timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    return f"{domain}_{base_name}_{timestamp}.pdf"


def configure_logging(debug: bool):
    """
    Configure logging based on the debug flag.

    Args:
        debug (bool): Whether to enable debug logging.
    """
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


def execute_wkhtmltopdf(url: str, output: str) -> None:
    """
    Execute wkhtmltopdf to convert the HTML to PDF.

    Args:
        url (str): The URL of the webpage to convert.
        output (str): The path where the PDF will be saved.

    Raises:
        subprocess.CalledProcessError: If wkhtmltopdf execution fails.
    """
    cmd = [
        "wkhtmltopdf",
        "--page-size",
        "A4",
        "--margin-top",
        "0.75in",
        "--margin-right",
        "0.75in",
        "--margin-bottom",
        "0.75in",
        "--margin-left",
        "0.75in",
        "--encoding",
        "UTF-8",
        "--no-stop-slow-scripts",
        "--javascript-delay",
        "1000",
        url,
        output,
    ]

    logger.debug(f"Executing command: {' '.join(cmd)}")

    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    stdout, stderr = process.communicate()

    if stdout:
        logger.info(f"wkhtmltopdf stdout: {stdout.strip()}")
    if stderr:
        logger.warning(f"wkhtmltopdf stderr: {stderr.strip()}")

    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, cmd, output=stderr)


@app.command()
def html_to_pdf(
    url: str = typer.Argument(..., help="URL of the webpage to convert"),
    output: str = typer.Option(None, "--output", "-o", help="Output PDF file path"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug logging"),
):
    """
    Convert HTML to PDF using wkhtmltopdf.

    Args:
        url (str): The URL of the webpage to convert.
        output (str): The path where the PDF will be saved (default: generated based on URL).
        debug (bool): Enable debug logging (default: False).
    """
    configure_logging(debug)

    if not validate_url(url):
        console.print(
            f"[bold red]Error:[/bold red] Invalid URL '[yellow]{url}[/yellow]'"
        )
        raise typer.Exit(code=1)

    if output is None:
        output = generate_output_name(url)
        console.print(
            f"[bold blue]Info:[/bold blue] Using generated output name: [cyan]{output}[/cyan]"
        )

    try:
        execute_wkhtmltopdf(url, output)
        console.print(
            f"[bold green]Success![/bold green] PDF successfully generated: [cyan]{output}[/cyan]"
        )
    except subprocess.CalledProcessError as cpe:
        console.print(f"[bold red]wkhtmltopdf error:[/bold red] {cpe.output}")
        logger.error(f"wkhtmltopdf error: {cpe.output}")
        raise typer.Exit(code=cpe.returncode)
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred:[/bold red] {str(e)}")
        logger.exception("An unexpected error occurred")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
