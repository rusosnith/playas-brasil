import requests
import fitz  # PyMuPDF
import re
import csv
import os
import time

# Página con listado de PDFs
LISTADO_URL = "https://www2.ima.al.gov.br/laboratorio/relatorios-de-balneabilidade/balneabilidade-de-praias/"
OUTPUT_CSV = "DatosPlaya.csv"

def obtener_ultimo_pdf():
    """Scrapea la página para obtener el link del PDF más reciente"""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    print(f"Abriendo navegador para scrapear {LISTADO_URL}...")
    
    # Configurar Chrome headless
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    try:
        driver.get(LISTADO_URL)
        
        # Esperar a que carguen los links
        time.sleep(3)
        
        # Buscar todos los links a PDFs con su texto/fecha
        links = driver.find_elements(By.TAG_NAME, 'a')
        
        for link in links:
            href = link.get_attribute('href') or ''
            texto = link.text or ''
            
            if '.pdf' in href.lower() and 'reab' in href.lower():
                # Buscar fecha en el texto del link
                fecha_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', texto)
                fecha = fecha_match.group(1) if fecha_match else None
                
                print(f"PDF: {href}")
                print(f"Fecha: {fecha}")
                
                # Retornar el primero (el más reciente)
                return href, fecha
        
        raise Exception("No se encontraron PDFs de REAB en la página")
            
    finally:
        driver.quit()

def descargar_pdf(url, filename="temp.pdf"):
    """Descarga el PDF desde la URL"""
    print(f"Descargando PDF desde {url}...")
    response = requests.get(url)
    response.raise_for_status()
    with open(filename, 'wb') as f:
        f.write(response.content)
    print(f"PDF descargado: {filename}")
    return filename

def extraer_texto_pdf(pdf_path):
    """Extrae todo el texto del PDF usando PyMuPDF"""
    texto_completo = ""
    doc = fitz.open(pdf_path)
    for i, page in enumerate(doc):
        texto = page.get_text()
        if texto:
            texto_completo += texto + "\n"
            print(f"Página {i+1}: {len(texto)} caracteres")
    doc.close()
    return texto_completo

def parsear_coordenada(texto):
    """Convierte coordenada DMS a decimal"""
    numeros = re.findall(r'[\d,.]+', texto)
    direccion = re.search(r'[SNEW]', texto)
    
    if not numeros or len(numeros) < 2 or not direccion:
        return None
    
    grados = float(numeros[0].replace(',', '.'))
    minutos = float(numeros[1].replace(',', '.'))
    segundos = float(numeros[2].replace(',', '.')) if len(numeros) > 2 else 0
    
    decimal = grados + minutos / 60 + segundos / 3600
    if direccion.group() in ['S', 'W']:
        decimal *= -1
    
    return decimal

def extraer_fecha_coleta(texto):
    """Extrae la fecha de coleta del PDF"""
    match = re.search(r'DATA DE COLETA\s*:?\s*(\d{1,2}/\d{1,2}/\d{4})', texto)
    if match:
        return match.group(1)
    return None

def extraer_playas(texto):
    """Extrae datos de playas del texto"""
    playas = []
    
    # Unir líneas y limpiar
    texto_limpio = ' '.join(texto.split())
    
    # Patrón para encontrar cada entrada de playa
    # Número + Praia/Rio + descripción + coordenadas + Não/Sim + temp + hora + categoría
    patron = r'(\d+\.?\d*)\s+(Praia[^-]+|Rio[^-]+|Prainha[^-]+)\s*[-–]\s*([^S]+S)\s*[;e]\s*([^W]+W)\s+(Não|Sim)\s+([\d,]+)\s+(\d+:\d+h)\s+(Própria|Imprópria)'
    
    matches = re.finditer(patron, texto_limpio)
    
    for match in matches:
        numero = match.group(1)
        descripcion = match.group(2).strip()
        lat_raw = match.group(3).strip()
        lng_raw = match.group(4).strip()
        chuva = match.group(5)
        temperatura = match.group(6).replace(',', '.')
        hora = match.group(7)
        categoria = match.group(8)
        
        lat = parsear_coordenada(lat_raw)
        lng = parsear_coordenada(lng_raw)
        
        playas.append({
            'numero': numero,
            'descripcion': descripcion,
            'lat_raw': lat_raw,
            'lng_raw': lng_raw,
            'lat': lat,
            'lng': lng,
            'chuva': chuva,
            'temperatura': temperatura,
            'hora': hora,
            'categoria': categoria
        })
        
    return playas

def guardar_csv(playas, filename):
    """Guarda los datos en CSV"""
    # Guardar en el mismo directorio que el script
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        for p in playas:
            # Formato compatible con el HTML existente
            linea = f"{p['numero']} {p['descripcion']} - {p['lat_raw']} e {p['lng_raw']} {p['chuva']} {p['temperatura']} {p['hora']} {p['categoria']}"
            f.write(linea + '\n')
    
    print(f"\nGuardado: {output_path}")
    print(f"Total playas: {len(playas)}")

def guardar_csv_completo(playas, filename):
    """Guarda los datos en CSV con todas las columnas"""
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename.replace('.csv', '_completo.csv'))
    
    fieldnames = ['numero', 'descripcion', 'lat_raw', 'lng_raw', 'lat', 'lng', 'chuva', 'temperatura', 'hora', 'categoria']
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(playas)
    
    print(f"Guardado (completo): {output_path}")

def main():
    # Obtener URL y fecha del último PDF
    pdf_url, fecha_coleta = obtener_ultimo_pdf()
    
    # Descargar PDF
    pdf_file = descargar_pdf(pdf_url)
    
    try:
        # Extraer texto
        texto = extraer_texto_pdf(pdf_file)
        
        # Si no hay fecha de la página, extraerla del PDF
        if not fecha_coleta:
            fecha_coleta = extraer_fecha_coleta(texto)
        
        # Extraer playas
        playas = extraer_playas(texto)
        
        if playas:
            playas.sort(key=lambda x: float(x['numero']))
            
            guardar_csv(playas, OUTPUT_CSV)
            guardar_csv_completo(playas, OUTPUT_CSV)
            
            # Guardar metadatos
            import json
            from datetime import datetime
            meta_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'metadata.json')
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'fecha_coleta': fecha_coleta,
                    'fecha_actualizacion': datetime.now().strftime('%d/%m/%Y %H:%M'),
                    'pdf_url': pdf_url,
                    'total_playas': len(playas),
                    'proprias': sum(1 for p in playas if p['categoria'] == 'Própria'),
                    'improprias': sum(1 for p in playas if p['categoria'] == 'Imprópria')
                }, f, ensure_ascii=False, indent=2)
            print(f"Guardado: {meta_path}")
            
            propias = sum(1 for p in playas if p['categoria'] == 'Própria')
            print(f"\nResumen: {len(playas)} playas, {propias} próprias, {len(playas)-propias} impróprias")
        else:
            print("No se encontraron playas en el PDF")
            
    finally:
        if os.path.exists(pdf_file):
            os.remove(pdf_file)

if __name__ == "__main__":
    main()
