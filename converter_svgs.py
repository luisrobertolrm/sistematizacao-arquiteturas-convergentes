import os
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGENS_DIR = os.path.join(BASE_DIR, "entrega", "imagens")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

def svg_to_png(svg_name, png_name, width=1050, height=730):
    svg_path = os.path.join(IMAGENS_DIR, svg_name)
    png_path = os.path.join(IMAGENS_DIR, png_name)
    html_temp = os.path.join(IMAGENS_DIR, f"temp_{svg_name}.html")
    
    with open(svg_path, "r", encoding="utf-8") as f:
        svg_code = f.read()

    html_content = f"""<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:white;overflow:hidden;">
  <div style="width:{width}px;height:{height}px;">
    {svg_code}
  </div>
</body>
</html>"""

    with open(html_temp, "w", encoding="utf-8") as f:
        f.write(html_content)

    cmd = [
        CHROME,
        "--headless=new",
        "--disable-gpu",
        f"--window-size={width},{height}",
        f"--screenshot={png_path}",
        html_temp
    ]
    subprocess.run(cmd, check=True)
    if os.path.exists(html_temp):
        os.remove(html_temp)
    print(f"Generated {png_name} (size: {os.path.getsize(png_path)} bytes)")

if __name__ == "__main__":
    svg_to_png("arquitetura_sistema.svg", "arquitetura_sistema.png", width=1050, height=730)
    svg_to_png("fluxo_cognitivo_langgraph.svg", "fluxo_cognitivo_langgraph.png", width=950, height=400)
