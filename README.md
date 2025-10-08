# 🛠️ GUÍA DETERMINADA DE RECONSTRUCCIÓN - MINI-CRUD FLASK (SENIOR) 🛠️
# Objetivo: Eliminar fallos de Concurrencia, SQL Injection y Acoplamiento Fuerte.
# Fecha de Creación: 2025-10-04

# ---------------------------------------------------------------------
## FASE 1: FUNDACIÓN Y SEGURIDAD (Thread-Safety) 💥
# Corrección del Fallo CATASTRÓFICO: Conexión Global (mydb)

### 1.1 Estructura Mínima
# Crea las carpetas base:
# - database/
# - models/
# - repositories/
# - services/
# - routes/

### 1.2 Configuración Segura
# Acción: ELIMINAR credenciales hardcodeadas (host, user, password) de app.py.
# Implementar: Archivo .env y librería 'python-dotenv'.
# Regla: Las credenciales NUNCA van en el código fuente.

### 1.3 El Arreglo Thread-Safe
# Acción: Eliminar variables globales 'mydb' y 'cursor'.
# Implementar: Función get_db_connection() y hook @app.teardown_appcontext.

# database/connection.py
from flask import g
# ... importa tu driver (mysql.connector)

def get_db_connection():
    if 'db_conn' not in g:
        # Crea una nueva conexión aislada por cada petición
        g.db_conn = mysql.connector.connect(...) 
        # Opcional, pero recomendado: cursor(dictionary=True)
    return g.db_conn

# app.py
@app.teardown_appcontext
def close_db_connection(exception):
    # GARANTÍA: Esto se ejecuta al final de CADA petición HTTP.
    conn = g.pop('db_conn', None)
    if conn is not None:
        if exception:
            conn.rollback() # Si hubo un error en CUALQUIER capa
        else:
            conn.commit()  # Si todo salió bien
        conn.close()
# Resultado: Cada usuario tiene su propia transacción aislada.


# ---------------------------------------------------------------------
## FASE 2: DEFINICIÓN DE CONTRATOS (Modelos y Tipado) 🧠
# Objetivo: Eliminar el 'dict' flotante y establecer tipado estricto.

### 2.1 Herramientas
# Usar: Pydantic (para validación de entrada/salida).

### 2.2 Tipos de Modelos (models/cat_models.py)
# Define la estructura y el tipo de dato que ESPERAS.

from pydantic import BaseModel, Field

class CatBase(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    color: str
    color_eye: str

# Modelos de Entrada (Llega del usuario)
class CatCreate(CatBase):
    pass 

# Modelo de Dominio/Salida (Lo que la DB devuelve)
class CatModel(CatBase):
    id: int
    # Permite que se cree a partir de una fila de DB
    class Config:
        orm_mode = True 
        
# ---------------------------------------------------------------------
## FASE 3: CAPA DE DATOS (Repositories) 💾
# Regla: SÓLO sabe de SQL y de inyección de conexión.

### 3.1 Estructura y Inyección
# repositories/cat_repo.py
from models.cat_models import CatModel # Importa tu modelo

class CatRepository:
    def get_by_id(self, conn, cat_id: int) -> CatModel | None:
        # Acepta la conexión (conn) como argumento.
        # NUNCA la crea aquí.
        
    def insert(self, conn, cat_data: CatCreate):
        # ...

### 3.2 Seguridad Determinada (SQL Parametrizado)
# Acción: Asegurar que el 100% de las consultas son seguras.
# Error a evitar: NO usar f-strings o %s para ensamblar el string.

    def insert(self, conn, cat_data: CatCreate):
        sql = 'INSERT INTO cat (color_eye, color, name) values (%s, %s, %s)'
        # Los valores se pasan SIEMPRE como tupla/lista SEPARADA
        values = (cat_data.color_eye, cat_data.color, cat_data.name)
        
        cursor = conn.cursor()
        cursor.execute(sql, values) # Forma correcta y segura.
        # NO se hace conn.commit() aquí. Lo hará el teardown.

### 3.3 Mapeo de Datos
# Acción: Convertir la fila de DB (dict) a un objeto CatModel tipado antes de devolverlo.
# Regla: El Servicio SIEMPRE recibe un objeto tipado (CatModel), NUNCA un dict.


# ---------------------------------------------------------------------
## FASE 4: CAPA DE NEGOCIO (Services) 🧠
# Regla: SÓLO sabe de lógica de negocio y excepciones customizadas.

### 4.1 Inyección de Repositorio
# services/cat_service.py
from repositories.cat_repo import CatRepository
# Define tus excepciones customizadas:
class CatNotFoundError(Exception): pass 

class CatService:
    def __init__(self, repo: CatRepository):
        self.repo = repo

### 4.2 Lógica de Negocio
    def create_cat(self, conn, cat_data: CatCreate):
        # 1. Lógica (Service): Si la regla es: "No se permiten gatos llamados 'Godzilla'"
        if cat_data.name.lower() == 'godzilla':
            raise ValueError("Nombre prohibido")
            
        # 2. Persistencia (Llama al Repository, le pasa la conexión)
        return self.repo.insert(conn, cat_data)

    def get_cat(self, conn, cat_id: int):
        cat = self.repo.get_by_id(conn, cat_id)
        if not cat:
            raise CatNotFoundError(f"Gato con ID {cat_id} no encontrado.")
        return cat


# ---------------------------------------------------------------------
## FASE 5: CAPA DE PRESENTACIÓN (Routes) 🚦
# Regla: SÓLO sabe de HTTP, llamar al servicio, y manejar excepciones.

### 5.1 La Ruta Limpia
# routes/cat_routes.py
from database.connection import get_db_connection
from services.cat_service import CatService, CatNotFoundError
from models.cat_models import CatCreate
from pydantic import ValidationError # Para manejar fallos de Pydantic

@app.route('/cats', methods=['POST'])
def create_cat_route():
    try:
        # 1. Validación de Entrada (Pydantic)
        cat_data = CatCreate(**request.json)
        
        # 2. Obtener Dependencias
        conn = get_db_connection() # Conexión aislada para este hilo
        repo = CatRepository()
        service = CatService(repo)
        
        # 3. Llamada al Servicio (Cerebro)
        new_cat = service.create_cat(conn, cat_data)
        
        # 4. Respuesta (JSON serializa el modelo Pydantic)
        return new_cat.json(), 201 
        
    except ValidationError as e:
        # Fallo de validación de Pydantic
        return jsonify({"error": "Datos de entrada inválidos", "details": e.errors()}), 400
        
    except CatNotFoundError:
        # Excepción customizada del Servicio
        return jsonify({"error": "Operación fallida, gato no encontrado"}), 404
    
    except Exception as e:
        # Manejo de error genérico (y el teardown hace ROLLBACK automáticamente)
        return jsonify({"error": "Error interno del servidor"}), 500
