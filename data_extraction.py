import os
from config import get_settings
from llama_cloud_services import LlamaParse
import asyncio


def data_extractor() -> None:
    """
    Processes PDFs and extracts text into separate markdown files, preserving directory structure.
    Skips PDFs if the corresponding markdown file already exists.
    """
    # Initialize the parser
    parser = LlamaParse(
        api_key=get_settings().llama_parse_key,
        num_workers=4,
        verbose=True,
        language="en"
    )

    # Define input and output root directories
    input_root = "knowledge_base/class_12/vistas"
    output_root = "extracted_data/class_12/vistas"
    os.makedirs(output_root, exist_ok=True)

    async def process_pdfs():
        pdf_files = []
        output_paths = []
        for file in os.listdir(input_root):
            if file.endswith(".pdf"):
                chapter_name = os.path.splitext(file)[0]
                output_path = os.path.join(output_root, f"{chapter_name}.md")
                if not os.path.exists(output_path):
                    pdf_files.append(os.path.join(input_root, file))
                    output_paths.append(output_path)
        if not pdf_files:
            print("All PDFs already parsed. No new files to process.")
            return
        results = await parser.aparse(pdf_files)
        for output_path, pdf_content in zip(output_paths, results):
            md_text = ""
            for page in pdf_content.pages:
                md_text += page.md + "\n\n"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(md_text)

    asyncio.run(process_pdfs())

if __name__ == "__main__":
    data_extractor()
