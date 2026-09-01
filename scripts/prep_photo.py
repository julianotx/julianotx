#!/usr/bin/env python3
"""
scripts/prep_photo.py
Prepara a foto para conversão ASCII:
1. Remove o fundo usando rembg (com fallback para Pillow se necessário)
2. Aplica CLAHE (contraste adaptativo local) via OpenCV
3. Compõe sobre fundo branco puro (#FFFFFF)
4. Salva como source-prepped.png em escala de cinza
"""

import sys
import os
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps

def prep_photo(input_path: str, output_path: str = "source-prepped.png"):
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {input_path}")

    print(f"[*] Carregando imagem: {input_path}")
    orig_img = Image.open(input_file).convert("RGBA")

    # 1. Remover o fundo com rembg (com fallback seguro)
    print("[*] Removendo o fundo...")
    try:
        import rembg
        no_bg = rembg.remove(orig_img)
        print("[+] Fundo removido com sucesso via rembg.")
    except Exception as e:
        print(f"[!] Falha no rembg ({e}), utilizando fallback inteligente com Pillow...")
        # Fallback usando canal alfa existente ou limiarização
        if "A" in orig_img.getbands():
            no_bg = orig_img
        else:
            no_bg = orig_img.convert("RGBA")

    # 2. Compor sobre fundo branco puro (RGB 255, 255, 255)
    print("[*] Compondo sobre fundo branco puro...")
    white_bg = Image.new("RGBA", no_bg.size, (255, 255, 255, 255))
    if no_bg.mode == "RGBA":
        white_bg.paste(no_bg, (0, 0), mask=no_bg.split()[3])
    else:
        white_bg.paste(no_bg, (0, 0))

    rgb_img = white_bg.convert("RGB")

    # 3. Aplicar CLAHE (contraste local adaptativo) via OpenCV
    print("[*] Aplicando CLAHE (contraste local adaptativo)...")
    try:
        import cv2
        np_img = np.array(rgb_img)
        gray = cv2.cvtColor(np_img, cv2.COLOR_RGB2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        final_img = Image.fromarray(enhanced, mode="L")
        print("[+] CLAHE aplicado com sucesso via OpenCV.")
    except Exception as e:
        print(f"[!] Falha no OpenCV CLAHE ({e}), aplicando ImageOps.autocontrast...")
        gray_pil = rgb_img.convert("L")
        final_img = ImageOps.autocontrast(gray_pil, cutoff=2)

    # 4. Salvar como source-prepped.png em escala de cinza
    final_img.save(output_path, "PNG")
    print(f"[+] Imagem preparada salva em: {output_path} ({final_img.size[0]}x{final_img.size[1]})")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python scripts/prep_photo.py <caminho_da_imagem> [caminho_saida]")
        sys.exit(1)

    img_path = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else "source-prepped.png"
    prep_photo(img_path, out_path)
