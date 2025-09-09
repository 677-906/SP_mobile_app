# Fichier: app/models.py

import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey, Date, Time
)
from sqlalchemy.orm import relationship
from .database import Base

# --- DOMAINE: SÉCURITÉ & AUTHENTIFICATION ---

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    
    # Relation vers User
    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    
    role_id = Column(Integer, ForeignKey('roles.id'))
    
    # --- RELATIONS BIDIRECTIONNELLES ---
    role = relationship("Role", back_populates="users")
    
    # CORRECTION : Ces lignes créent les 'properties' attendues par les autres classes
    merchandiser_profile = relationship("Merchandiser", back_populates="user", uselist=False)
    superviseur_profile = relationship("Superviseur", back_populates="user", uselist=False)
    clients_crees = relationship("Client", back_populates="createur")

# --- DOMAINE: MÉTIER & ORGANISATION ---

class Superviseur(Base):
    __tablename__ = 'superviseurs'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    
    # Cette relation attend 'superviseur_profile' dans User
    user = relationship("User", back_populates="superviseur_profile")
    merchandisers = relationship("Merchandiser", back_populates="manager")


class Merchandiser(Base):
    __tablename__ = 'merchandisers' # Le nom de la table devient 'merchandisers'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    zone_geographique = Column(String(100))
    
    manager_id = Column(Integer, ForeignKey('superviseurs.id'))
    
    manager = relationship("Superviseur", back_populates="merchandisers")
    user = relationship("User", back_populates="merchandiser_profile")
    visites = relationship("Visite", back_populates="merchandiser")
# --- DOMAINE: DONNÉES DE RÉFÉRENCE MÉTIER ---

class Client(Base):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True, index=True)
    nom_client = Column(String(200), nullable=False)
    contact = Column(String(100))
    typologie = Column(String(100))
    localisation = Column(String(255))
    
    createur_id = Column(Integer, ForeignKey('users.id'))
    
    # Ces relations attendent 'clients_crees' dans User et 'visites' dans Visite
    createur = relationship("User", back_populates="clients_crees")
    visites = relationship("Visite", back_populates="client")

class Produit(Base):
    __tablename__ = 'produits'
    id = Column(Integer, primary_key=True, index=True)
    nom_produit = Column(String(200), nullable=False)
    marque = Column(String(100))

# --- DOMAINE: PROCESSUS OPÉRATIONNEL ---

class Visite(Base):
    __tablename__ = 'visites'
    id = Column(Integer, primary_key=True, index=True)
    merchandiser_id = Column(Integer, ForeignKey('merchandisers.id'))
    client_id = Column(Integer, ForeignKey('clients.id'))
    
    date_visite = Column(Date, default=datetime.date.today)
    heure_arrivee = Column(Time)
    heure_depart = Column(Time)
    statut_validation = Column(String, default='soumis')
    observations_generales = Column(Text)
    
    merchandiser = relationship("Merchandiser", back_populates="visites")
    client = relationship("Client", back_populates="visites")
    
    # ON MET À JOUR LES RELATIONS DE LA VISITE
    releves_stock = relationship("ReleveStock", back_populates="visite")
    lignes_commande = relationship("LigneCommande", back_populates="visite")


# --- NOUVELLE CLASSE ReleveStock ---
class ReleveStock(Base):
    __tablename__ = 'releves_stock'
    id = Column(Integer, primary_key=True, index=True)
    visite_id = Column(Integer, ForeignKey('visites.id'))
    produit_id = Column(Integer, ForeignKey('produits.id'))
    
    quantite_en_stock = Column(Integer)
    est_en_rupture = Column(Boolean, default=False)
    
    # Relations
    visite = relationship("Visite", back_populates="releves_stock")
    produit = relationship("Produit")


# --- NOUVELLE CLASSE LigneCommande ---
class LigneCommande(Base):
    __tablename__ = 'lignes_commande'
    id = Column(Integer, primary_key=True, index=True)
    visite_id = Column(Integer, ForeignKey('visites.id'))
    produit_id = Column(Integer, ForeignKey('produits.id'))
    
    quantite_commandee = Column(Integer)
    
    # Relations
    visite = relationship("Visite", back_populates="lignes_commande")
    produit = relationship("Produit")