# db/__init__.py

# 1. Componentes base (Motor y Sesión)
from .base import Base, engine, SessionLocal

# 2. Tablas independientes (Padres)
# Company debe ir antes que Branch para que la llave foránea funcione
from .company import Company
from .user import User

# 3. Tablas dependientes de Nivel 1 (Hijos)
from .branch import Branch

# 4. Tablas dependientes de Nivel 2 (Nietos)
# Stock e Invoice dependen de Branch, así que van al final
from .stock import Stock
from .invoice import Invoice, InvoiceItem