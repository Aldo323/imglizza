#!/usr/bin/env python3
"""
Optimizador de imágenes con integración Git
Para repositorio imglizza con auto-commit y push
"""

import os
import subprocess
import glob
import time
from PIL import Image
from pathlib import Path

class GitImageOptimizer:
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.original_folder = os.path.join(repo_path, "originales", "Anillos")
        self.optimized_folder = os.path.join(repo_path, "optimizadas", "Anillos")
        self.processed_files = []
        
        # Configuración para ecommerce
        self.sizes_config = {
            'thumb': {'size': (300, 300), 'quality': 70},
            'medium': {'size': (800, 800), 'quality': 80},
            'large': {'size': (1200, 1200), 'quality': 85}
        }
    
    def setup_git_structure(self):
        """Configurar estructura de carpetas y .gitignore"""
        print("🔧 Configurando estructura del repositorio...")
        
        # Crear carpetas necesarias
        os.makedirs(self.original_folder, exist_ok=True)
        for size in self.sizes_config.keys():
            os.makedirs(os.path.join(self.optimized_folder, size), exist_ok=True)
        
        # Crear/actualizar .gitignore
        gitignore_path = os.path.join(self.repo_path, ".gitignore")
        gitignore_content = """# Imágenes originales (muy pesadas)
originales/
*.png
*.jpg
*.jpeg

# Solo trackear optimizadas
!optimizadas/
optimizadas/**/*.webp
optimizadas/**/*.jpg

# Logs y temporales
*.log
__pycache__/
.DS_Store
Thumbs.db
"""
        
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        
        print("✅ Estructura configurada")
    
    def move_existing_images(self):
        """Mover imágenes existentes a la carpeta 'originales'"""
        anillos_path = os.path.join(self.repo_path, "Anillos")
        
        if os.path.exists(anillos_path):
            print("📦 Moviendo imágenes existentes a 'originales'...")
            
            # Buscar imágenes en la carpeta Anillos actual
            image_files = glob.glob(os.path.join(anillos_path, "*.png"))
            
            for image_path in image_files:
                filename = os.path.basename(image_path)
                destination = os.path.join(self.original_folder, filename)
                
                try:
                    os.rename(image_path, destination)
                    print(f"   ✅ Movido: {filename}")
                except Exception as e:
                    print(f"   ❌ Error moviendo {filename}: {e}")
            
            # Eliminar carpeta Anillos vacía si es posible
            try:
                if not os.listdir(anillos_path):
                    os.rmdir(anillos_path)
                    print("📁 Carpeta 'Anillos' original eliminada")
            except:
                pass
    
    def optimize_image(self, image_path):
        """Optimizar una imagen en todos los tamaños"""
        filename = Path(image_path).stem
        original_size_mb = os.path.getsize(image_path) / (1024 * 1024)
        
        print(f"🖼️  Optimizando: {filename} ({original_size_mb:.2f} MB)")
        
        try:
            with Image.open(image_path) as img:
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                for size_name, config in self.sizes_config.items():
                    # Crear imagen redimensionada
                    img_resized = img.copy()
                    img_resized.thumbnail(config['size'], Image.Resampling.LANCZOS)
                    
                    # Guardar en WebP (mejor compresión)
                    webp_path = os.path.join(self.optimized_folder, size_name, f"{filename}.webp")
                    img_resized.save(webp_path, 'WEBP', quality=config['quality'], optimize=True)
                    
                    # Guardar también en JPG (fallback)
                    jpg_path = os.path.join(self.optimized_folder, size_name, f"{filename}.jpg")
                    img_resized.save(jpg_path, 'JPEG', quality=config['quality'], optimize=True)
                    
                    webp_size = os.path.getsize(webp_path) / 1024
                    jpg_size = os.path.getsize(jpg_path) / 1024
                    
                    print(f"   ✅ {size_name}: {webp_size:.0f}KB (webp), {jpg_size:.0f}KB (jpg)")
                    
                    # Agregar a lista de archivos procesados
                    self.processed_files.extend([webp_path, jpg_path])
                
                return True
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def process_all_images(self):
        """Procesar todas las imágenes"""
        print("🚀 Procesando imágenes...")
        
        image_files = glob.glob(os.path.join(self.original_folder, "*.png"))
        
        if not image_files:
            print("❌ No se encontraron imágenes PNG en 'originales/Anillos'")
            return False
        
        print(f"📊 Encontradas {len(image_files)} imágenes")
        
        success_count = 0
        for image_path in image_files:
            if self.optimize_image(image_path):
                success_count += 1
        
        print(f"\n✅ Procesadas exitosamente: {success_count}/{len(image_files)}")
        return success_count > 0
    
    def git_commit_and_push(self):
        """Hacer commit y push de las imágenes optimizadas"""
        print("\n🔄 Subiendo cambios a GitHub...")
        
        try:
            # Cambiar al directorio del repositorio
            os.chdir(self.repo_path)
            
            # Agregar archivos optimizados
            subprocess.run(['git', 'add', 'optimizadas/'], check=True)
            subprocess.run(['git', 'add', '.gitignore'], check=True)
            
            # Commit
            commit_message = f"Optimizar imágenes - {len(self.processed_files)} archivos procesados"
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            
            # Push
            result = subprocess.run(['git', 'push'], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Cambios subidos exitosamente a GitHub")
                return True
            else:
                print(f"❌ Error en push: {result.stderr}")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Error Git: {e}")
            return False
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            return False
    
    def update_urls_info(self):
        """Mostrar información sobre las nuevas URLs"""
        print("\n" + "="*60)
        print("📋 NUEVAS URLs PARA TU APLICACIÓN .NET")
        print("="*60)
        print("Reemplaza tu URL base por:")
        print("https://raw.githubusercontent.com/Aldo323/imglizza/main/optimizadas/Anillos/")
        print()
        print("Ejemplos de uso:")
        print("• Thumbnail: ...optimizadas/Anillos/thumb/[codigo].webp")
        print("• Medium:    ...optimizadas/Anillos/medium/[codigo].webp")  
        print("• Large:     ...optimizadas/Anillos/large/[codigo].webp")
        print("• Fallback:  ...optimizadas/Anillos/medium/[codigo].jpg")
    
    def run_full_optimization(self):
        """Ejecutar proceso completo de optimización"""
        print("🎯 OPTIMIZADOR CON GIT INTEGRATION")
        print("="*50)
        print(f"📂 Repositorio: {self.repo_path}")
        
        start_time = time.time()
        
        # 1. Configurar estructura
        self.setup_git_structure()
        
        # 2. Mover imágenes existentes
        self.move_existing_images()
        
        # 3. Optimizar imágenes
        if not self.process_all_images():
            print("❌ No se pudieron procesar las imágenes")
            return
        
        # 4. Subir a GitHub
        if self.git_commit_and_push():
            print("🎉 ¡Proceso completado exitosamente!")
        else:
            print("⚠️  Imágenes optimizadas pero no se pudieron subir a GitHub")
        
        # 5. Mostrar información de URLs
        self.update_urls_info()
        
        end_time = time.time()
        print(f"\n⏱️  Tiempo total: {end_time - start_time:.1f} segundos")

def main():
    # Tu ruta específica
    repo_path = r"C:\Users\Lenovo\Pictures\imglizza"
    
    if not os.path.exists(repo_path):
        print(f"❌ El directorio {repo_path} no existe")
        return
    
    if not os.path.exists(os.path.join(repo_path, '.git')):
        print(f"❌ {repo_path} no es un repositorio Git")
        return
    
    # Crear y ejecutar optimizador
    optimizer = GitImageOptimizer(repo_path)
    optimizer.run_full_optimization()

if __name__ == "__main__":
    main()