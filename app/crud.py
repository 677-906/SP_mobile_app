from sqlalchemy.orm import Session
from . import models, schemas, security

# --- CRUD pour les Utilisateurs ---
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(email=user.email, nom=user.nom, password_hash=hashed_password, role_id=user.role_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- CRUD pour les Clients ---
def get_clients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Client).offset(skip).limit(limit).all()

def create_client(db: Session, client: schemas.ClientCreate, user_id: int):
    db_client = models.Client(**client.dict(), createur_id=user_id)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


# --- CRUD pour les Visites ---
def create_visite(db: Session, visite: schemas.VisiteCreate, merchandiser_id: int):
    # On sépare les données de la visite principale des listes de détails
    visite_data = visite.dict(exclude={'releves_stock', 'lignes_commande'})
    
    db_visite = models.Visite(**visite_data, merchandiser_id=merchandiser_id)
    db.add(db_visite)
    db.commit() # On commit une première fois pour que la visite ait un ID
    db.refresh(db_visite)

    # On traite les relevés de stock s'il y en a
    if visite.releves_stock:
        for stock_item in visite.releves_stock:
            db_stock = models.ReleveStock(**stock_item.dict(), visite_id=db_visite.id)
            db.add(db_stock)
    
    # On traite les lignes de commande s'il y en a
    if visite.lignes_commande:
        for commande_item in visite.lignes_commande:
            db_commande = models.LigneCommande(**commande_item.dict(), visite_id=db_visite.id)
            db.add(db_commande)
    
    db.commit() # On commit une seconde fois pour sauvegarder les détails
    db.refresh(db_visite)
    return db_visite



# --- CRUD pour les Produits ---

def get_produit(db: Session, produit_id: int):
    return db.query(models.Produit).filter(models.Produit.id == produit_id).first()

def get_produits(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Produit).offset(skip).limit(limit).all()

def create_produit(db: Session, produit: schemas.ProduitCreate):
    db_produit = models.Produit(**produit.dict())
    db.add(db_produit)
    db.commit()
    db.refresh(db_produit)
    return db_produit