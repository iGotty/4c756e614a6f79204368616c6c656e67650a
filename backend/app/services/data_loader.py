# app/services/data_loader.py
import json
import os
from typing import Dict, List, Optional
from pathlib import Path

class DataLoader:
    """
    Singleton para cargar y gestionar los datos desde archivos JSON.
    Compatible con Azure App Service y entorno local.
    """
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataLoader, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.clinicians: Dict[str, Dict] = {}
            self.users: Dict[str, Dict] = {}
            self.interactions: List[Dict] = []
            self._initialized = True
            self._data_loaded = False
            
            # Detectar si estamos en Azure
            self.is_azure = os.environ.get('WEBSITE_INSTANCE_ID') is not None
            print(f"🌐 Running on Azure: {self.is_azure}")
    
    def load_all_data(self):
        """
        Carga todos los datos desde los archivos JSON.
        """
        if self._data_loaded:
            return
            
        # Buscar la carpeta data
        data_dir = self._find_data_directory()
        if not data_dir:
            print("⚠️ No se encontró la carpeta 'data'")
            # En Azure, intentar crear datos de ejemplo si no se encuentran
            if self.is_azure:
                print("🔧 Intentando cargar datos de ejemplo para Azure...")
                self._load_sample_data()
            return
            
        print(f"📁 Usando carpeta de datos: {data_dir}")
        
        # Cargar cada archivo
        self._load_clinicians(data_dir)
        self._load_users(data_dir)
        self._load_interactions(data_dir)
        
        self._data_loaded = True
    
    def _find_data_directory(self) -> Optional[Path]:
        """
        Busca la carpeta 'data' en varias ubicaciones posibles.
        Incluye rutas específicas de Azure.
        """
        # Posibles ubicaciones de la carpeta data
        possible_paths = [
            Path("data"),  # En el directorio actual
            Path("../data"),  # Un nivel arriba
            Path("backend/data"),  # Dentro de backend
            Path(os.path.dirname(os.path.abspath(__file__))).parent.parent / "data",  # Relativo al archivo
        ]
        
        # Rutas específicas de Azure
        if self.is_azure:
            azure_paths = [
                Path("/home/site/wwwroot/data"),
                Path("/home/site/wwwroot/backend/data"),
                Path("/home/site/wwwroot/app/data"),
                Path("/tmp/8ddc3bbcaba541e/data"),  # Directorio temporal de Azure
            ]
            possible_paths = azure_paths + possible_paths
        
        print("🔍 Buscando carpeta 'data' en las siguientes ubicaciones:")
        for path in possible_paths:
            print(f"  - Verificando: {path}")
            if path.exists() and path.is_dir():
                print(f"  ✅ Encontrada!")
                # Listar archivos en el directorio
                try:
                    files = list(path.glob("*.json"))
                    print(f"  📋 Archivos JSON encontrados: {[f.name for f in files]}")
                except Exception as e:
                    print(f"  ❌ Error listando archivos: {e}")
                return path.resolve()
            else:
                print(f"  ❌ No existe")
        
        # Si estamos en Azure, intentar buscar archivos JSON en cualquier lugar
        if self.is_azure:
            print("🔍 Búsqueda adicional en Azure...")
            root_path = Path("/home/site/wwwroot")
            if root_path.exists():
                json_files = list(root_path.rglob("*.json"))
                print(f"📋 Archivos JSON encontrados en wwwroot: {len(json_files)}")
                for jf in json_files[:10]:  # Mostrar primeros 10
                    print(f"  - {jf}")
                
                # Buscar específicamente nuestros archivos
                for jf in json_files:
                    if jf.name in ["clinicians.json", "users.json", "interactions.json"]:
                        print(f"✅ Encontrado {jf.name} en: {jf.parent}")
                        return jf.parent
        
        return None
    
    def _load_clinicians(self, data_dir: Path):
        """
        Carga los datos de clínicos desde clinicians.json
        """
        file_path = data_dir / "clinicians.json"
        
        if not file_path.exists():
            print(f"⚠️ No se encontró {file_path}")
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                clinicians_list = json.load(f)
            
            # Convertir lista a diccionario usando clinician_id como clave
            self.clinicians = {}
            for clinician in clinicians_list:
                clinician_id = clinician.get('clinician_id', f'clin_{len(self.clinicians)}')
                self.clinicians[clinician_id] = clinician
            
            print(f"✅ Cargados {len(self.clinicians)} clínicos")
            
        except Exception as e:
            print(f"❌ Error cargando clínicos: {str(e)}")
    
    def _load_users(self, data_dir: Path):
        """
        Carga los datos de usuarios desde users.json
        """
        file_path = data_dir / "users.json"
        
        if not file_path.exists():
            print(f"⚠️ No se encontró {file_path}")
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                users_list = json.load(f)
            
            # Convertir lista a diccionario
            self.users = {}
            for user in users_list:
                user_id = user.get('user_id', f'user_{len(self.users)}')
                self.users[user_id] = user
            
            print(f"✅ Cargados {len(self.users)} usuarios")
            
        except Exception as e:
            print(f"❌ Error cargando usuarios: {str(e)}")
    
    def _load_interactions(self, data_dir: Path):
        """
        Carga los datos de interacciones desde interactions.json
        """
        file_path = data_dir / "interactions.json"
        
        if not file_path.exists():
            print(f"⚠️ No se encontró {file_path}")
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.interactions = json.load(f)
            
            print(f"✅ Cargadas {len(self.interactions)} interacciones")
            
        except Exception as e:
            print(f"❌ Error cargando interacciones: {str(e)}")
    
    def _load_sample_data(self):
        """
        Carga datos de ejemplo mínimos para testing en Azure
        """
        print("📦 Cargando datos de ejemplo...")
        
        # Datos de ejemplo mínimos
        self.clinicians = {
            "clin_sample_001": {
                "clinician_id": "clin_sample_001",
                "clinician_name": "Dr. Sarah Johnson",
                "profile_features": {
                    "gender": "female",
                    "languages": ["English", "Spanish"],
                    "years_experience": 8,
                    "specialties": ["anxiety", "depression"],
                    "age_groups_served": ["adults"]
                },
                "availability_features": {
                    "immediate_availability": True,
                    "accepting_new_patients": True,
                    "availability_score": 0.8
                },
                "basic_info": {
                    "full_name": "Dr. Sarah Johnson",
                    "license_states": ["CA", "NY"],
                    "appointment_types": ["therapy", "medication"]
                }
            }
        }
        
        self.users = {
            "user_sample_001": {
                "user_id": "user_sample_001",
                "registration_type": "basic",
                "stated_preferences": {
                    "state": "CA",
                    "appointment_type": "therapy",
                    "clinical_needs": ["anxiety"]
                }
            }
        }
        
        self.interactions = []
        
        print(f"✅ Datos de ejemplo cargados: {len(self.clinicians)} clínicos, {len(self.users)} usuarios")
        self._data_loaded = True
    
    def get_clinician(self, clinician_id: str) -> Optional[Dict]:
        """
        Obtiene un clínico por ID.
        """
        if not self._data_loaded:
            self.load_all_data()
        return self.clinicians.get(clinician_id)
    
    def get_clinicians_for_matching(self) -> List[Dict]:
        """
        Retorna la lista de clínicos para el proceso de matching.
        """
        if not self._data_loaded:
            self.load_all_data()
        return list(self.clinicians.values())
    
    def get_stats(self) -> Dict[str, int]:
        """
        Retorna estadísticas de los datos cargados
        """
        if not self._data_loaded:
            self.load_all_data()
        
        return {
            "clinicians": len(self.clinicians),
            "users": len(self.users),
            "interactions": len(self.interactions),
            "is_azure": self.is_azure,
            "data_loaded": self._data_loaded
        }

# Instancia global del cargador de datos
data_loader = DataLoader()