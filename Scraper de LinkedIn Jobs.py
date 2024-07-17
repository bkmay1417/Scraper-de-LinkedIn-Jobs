from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, PhotoImage

def scrape_linkedin_jobs(keywords, location, save_path):
    try:
        # Configurar las opciones del navegador Chrome en modo headless
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Inicializar el servicio del driver de Chrome
        s = Service()  # Especifica la ruta al chromedriver si es necesario
        driver = webdriver.Chrome(service=s, options=chrome_options)

        # Construir la URL de búsqueda dinámicamente
        search_url = f"https://www.linkedin.com/jobs/search?keywords={keywords}&location={location}&geoId=&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0"


        # Abrir la página de búsqueda de LinkedIn Jobs
        driver.get(search_url)
        print(f"Abriendo URL: {search_url}")

        scroll_pause_time = 2
        scroll_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            prev_scroll_height = scroll_height
            driver.execute_script(f"window.scrollTo(0, {scroll_height});")
            time.sleep(scroll_pause_time)
            scroll_height = driver.execute_script("return document.body.scrollHeight")
            
            if scroll_height == prev_scroll_height:
                break

        # Esperar a que la página cargue completamente
        WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'ul.jobs-search__results-list li'))
        )
        print("Página cargada completamente.")

        # Encontrar todas las listas de trabajos
        job_listings = driver.find_elements(By.CSS_SELECTOR, 'ul.jobs-search__results-list li')
        print(f"Número de listados encontrados: {len(job_listings)}")

        csv_file = os.path.join(save_path, f'linkedin_jobs_{keywords}.csv')

        # Abrir el archivo CSV en modo escritura
        with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Título del trabajo', 'Ubicación del trabajo', 'Enlace del trabajo'])

            for i, listing in enumerate(job_listings):
                try:
                    # Verificación adicional de la existencia de elementos antes de extraer información
                    job_title_element = listing.find_element(By.CSS_SELECTOR, 'h3.base-search-card__title')
                    job_title = job_title_element.text.strip() if job_title_element else "N/A"
                    
                    company_name_element = listing.find_element(By.CSS_SELECTOR, 'h4.base-search-card__subtitle')
                    company_name = company_name_element.text.strip() if company_name_element else "N/A"
                    
                    job_location_element = listing.find_element(By.CSS_SELECTOR, 'span.job-search-card__location')
                    job_location = job_location_element.text.strip() if job_location_element else "N/A"
                    
                    job_link_element = listing.find_element(By.CSS_SELECTOR, 'a.base-card__full-link')
                    job_link = job_link_element.get_attribute('href') if job_link_element else "N/A"

                    # Escribir en el archivo CSV
                    writer.writerow([job_title, job_location, job_link])
                    print(f"Listado {i+1} procesado: {job_title}, {job_location}, {job_link}")

                except Exception as e:
                    print(f"Error al procesar el listado {i+1}: {e}")

        # Cerrar el navegador al finalizar
        driver.quit()

        messagebox.showinfo("Éxito", f"Los resultados se han guardado en '{csv_file}'.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo completar el scraping: {e}")

def browse_save_path():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        save_path_entry.delete(0, tk.END)
        save_path_entry.insert(0, folder_selected)

def start_scraping():
    keywords = keywords_entry.get()
    location = location_entry.get()
    save_path = save_path_entry.get()
    
    if not keywords or not location or not save_path:
        messagebox.showwarning("Advertencia", "Por favor, complete todos los campos.")
        return
    
    try:
        scrape_linkedin_jobs(keywords, location, save_path)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo completar el scraping: {e}")

app = tk.Tk()
app.title("Scraper de LinkedIn Jobs")

# Determinar la ruta correcta a la imagen
if hasattr(sys, '_MEIPASS'):
    image_path = os.path.join(sys._MEIPASS, "mnm.png")
else:
    image_path = "mnm.png"  # Reemplaza con la ruta a tu imagen en el directorio de trabajo

# Cargar la imagen PNG y ajustar su tamaño
try:
    img = PhotoImage(file=image_path).subsample(5)  # Subsample a factor de 5 (50/10)
except Exception as e:
    messagebox.showerror("Error", f"No se pudo cargar la imagen: {e}")
    img = None

# Keywords
tk.Label(app, text="Trabajo:").grid(row=0, column=0, padx=10, pady=10)
keywords_entry = tk.Entry(app, width=50)
keywords_entry.grid(row=0, column=1, padx=10, pady=10)

# Location
tk.Label(app, text="Ubicación:").grid(row=1, column=0, padx=10, pady=10)
location_entry = tk.Entry(app, width=50)
location_entry.grid(row=1, column=1, padx=10, pady=10)

# Save path
tk.Label(app, text="Guardar en:").grid(row=2, column=0, padx=10, pady=10)
save_path_entry = tk.Entry(app, width=50)
save_path_entry.grid(row=2, column=1, padx=10, pady=10)
tk.Button(app, text="Buscar", command=browse_save_path).grid(row=2, column=2, padx=10, pady=10)

# Start scraping button
tk.Button(app, text="Iniciar scraping", command=start_scraping).grid(row=3, column=0, columnspan=3, padx=10, pady=20)

bottom_frame = tk.Frame(app)
bottom_frame.grid(row=4, column=0, columnspan=3, pady=10)

if img:
    image_label = tk.Label(bottom_frame, image=img)
    image_label.image = img  # Guardar una referencia al objeto PhotoImage
    image_label.pack(side=tk.LEFT, padx=10)

# Enlace a una página web
link_label = tk.Label(bottom_frame, text="Cualquier cosulta aqui", cursor="hand2", fg="blue")
link_label.pack(side=tk.LEFT, padx=10)
link_label.bind("<Button-1>", lambda e: open_webpage())

# Mostrar el texto "By Michael Martinez"
credit_label = tk.Label(bottom_frame, text="By Michael Martinez", font=("Arial", 10, "italic"))
credit_label.pack(side=tk.LEFT, padx=10)

app.mainloop()
