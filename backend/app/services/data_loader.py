# app/services/data_loader.py
import json
import os
from typing import Dict, List, Optional
from pathlib import Path

class DataLoader:
    """
    Singleton para cargar y gestionar los datos desde archivos JSON.
    """
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataLoader, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.clinicians: Dict[str, Dict] = {}  # Cambiado a diccionario
            self.users: Dict[str, Dict] = {}
            self.interactions: List[Dict] = []
            self._initialized = True
            self._data_loaded = False
    
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
        """
        # Posibles ubicaciones de la carpeta data
        possible_paths = [
            Path("data"),  # En el directorio actual
            Path("../data"),  # Un nivel arriba
            Path("backend/data"),  # Dentro de backend
            Path(os.path.dirname(os.path.abspath(__file__))).parent.parent / "data",  # Relativo al archivo
        ]
        
        for path in possible_paths:
            if path.exists() and path.is_dir():
                return path.resolve()
        
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
    
    def get_clinician(self, clinician_id: str) -> Optional[Dict]:
        """
        Obtiene un clínico por ID.
        """
        return self.clinicians.get(clinician_id)
    
    def get_clinicians_for_matching(self) -> List[Dict]:
        """
        Retorna la lista de clínicos para el proceso de matching.
        """
        if not self._data_loaded:
            self.load_all_data()
        return list(self.clinicians.values())

# Instancia global del cargador de datos
data_loader = DataLoader()