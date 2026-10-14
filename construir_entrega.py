import os
import sys
import subprocess
import zipfile
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENTREGA_DIR = os.path.join(BASE_DIR, "entrega")
IMAGENS_DIR = os.path.join(ENTREGA_DIR, "imagens")
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

os.makedirs(IMAGENS_DIR, exist_ok=True)
print("Base directory:", BASE_DIR)
print("Entrega directory:", ENTREGA_DIR)
