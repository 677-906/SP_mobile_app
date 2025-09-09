from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta

from . import models, schemas, crud, security, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="API Source du Pays")

# --- Dépendances ---
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# DÉPENDANCE DE SÉCURITÉ (logiquement placée ici)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider les identifiants",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = security.verify_token(token, credentials_exception)
    user = crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

# --- Routes pour l'Authentification ---
@app.post("/token", response_model=schemas.Token, tags=["Authentification"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou mot de passe incorrect")
    
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# --- Routes pour les Utilisateurs ---
@app.post("/users/", response_model=schemas.User, tags=["Utilisateurs"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")
    return crud.create_user(db=db, user=user)

@app.get("/users/me/", response_model=schemas.User, tags=["Utilisateurs"])
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# --- Routes pour les Clients (protégées) ---
@app.post("/clients/", response_model=schemas.Client, tags=["Clients"])
def create_client(client: schemas.ClientCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.create_client(db=db, client=client, user_id=current_user.id)

@app.get("/clients/", response_model=List[schemas.Client], tags=["Clients"])
def read_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    clients = crud.get_clients(db, skip=skip, limit=limit)
    return clients

# --- Routes pour les Rôles ---
@app.post("/roles/", response_model=schemas.Role, tags=["Rôles"])
def create_role(role: schemas.RoleCreate, db: Session = Depends(get_db)):
    db_role = db.query(models.Role).filter(models.Role.nom == role.nom).first()
    if db_role:
        raise HTTPException(status_code=400, detail="Ce rôle existe déjà")
    new_role = models.Role(**role.dict())
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role

@app.get("/roles/", response_model=List[schemas.Role], tags=["Rôles"])
def read_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    roles = db.query(models.Role).offset(skip).limit(limit).all()
    return roles


# --- Routes pour les Visites (protégées) ---
@app.post("/visites/", response_model=schemas.Visite, tags=["Visites"])
def create_visite(
    visite: schemas.VisiteCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    # On vérifie que l'utilisateur est bien un merchandiser (ou un rôle supérieur)
    if not current_user.merchandiser_profile:
        raise HTTPException(status_code=403, detail="Seul un merchandiser peut créer une visite")
    
    return crud.create_visite(db=db, visite=visite, merchandiser_id=current_user.merchandiser_profile.id)



# --- Routes pour les Produits (protégées) ---

@app.post("/produits/", response_model=schemas.Produit, tags=["Produits"])
def create_produit(
    produit: schemas.ProduitCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # On protège la route
):
    # On pourrait ajouter une logique pour vérifier que seul un admin peut créer des produits
    return crud.create_produit(db=db, produit=produit)

@app.get("/produits/", response_model=List[schemas.Produit], tags=["Produits"])
def read_produits(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # On protège la route
):
    produits = crud.get_produits(db, skip=skip, limit=limit)
    return produits