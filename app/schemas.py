from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date

# --- Schémas pour les Rôles ---

class RoleBase(BaseModel):
    nom: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class Role(RoleBase):
    id: int

    class Config:
        from_attributes = True

# --- Schémas pour les Utilisateurs ---

class UserBase(BaseModel):
    email: EmailStr
    nom: str

class UserCreate(UserBase):
    password: str
    role_id: int

class User(UserBase):
    id: int
    is_active: bool
    role: Role

    class Config:
        from_attributes = True


class ClientBase(BaseModel):
    nom_client: str
    contact: Optional[str] = None
    typologie: Optional[str] = None
    localisation: Optional[str] = None

class ClientCreate(ClientBase):
    pass

class Client(ClientBase):
    id: int
    createur_id: int

    class Config:
        from_attributes = True


class User(UserBase):
    id: int
    is_active: bool
    role: Role
    clients_crees: List[Client] = [] # AJOUTEZ CETTE LIGNE

    class Config:
        from_attributes = True


# --- Schémas pour les Produits ---

class ProduitBase(BaseModel):
    nom_produit: str
    marque: Optional[str] = None

class ProduitCreate(ProduitBase):
    pass

class Produit(ProduitBase):
    id: int
    categorie_id: Optional[int] = None # Si vous avez la table categories_produit

    class Config:
        from_attributes = True


# --- Schémas pour l'Authentification (Token) ---

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None


class ReleveStockBase(BaseModel):
    produit_id: int
    quantite_en_stock: int
    est_en_rupture: bool

class LigneCommandeBase(BaseModel):
    produit_id: int
    quantite_commandee: int

# --- Schémas pour les Visites ---

class VisiteBase(BaseModel):
    client_id: int
    observations_generales: Optional[str] = None
    # On ajoutera d'autres champs comme fifo_respecte, etc. plus tard

class VisiteCreate(VisiteBase):
    pass
    releves_stock: Optional[List[ReleveStockBase]] = []
    lignes_commande: Optional[List[LigneCommandeBase]] = []

class Visite(VisiteBase):
    id: int
    merchandiser_id: int
    date_visite: date # Pydantic v2 gère automatiquement date de datetime
    statut_validation: str

    class Config:
        from_attributes = True