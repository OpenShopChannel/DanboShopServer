from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class AppsModel(db.Model):
    __tablename__ = 'application'

    id = db.Column(db.Integer, primary_key=True)                     # Numeric application ID
    slug = db.Column(db.String, unique=True, nullable=False)         # Unique slug for the application
    date_added = db.Column(db.DateTime, default=datetime.utcnow)     # Date the application was added
    date_updated = db.Column(db.DateTime, default=datetime.utcnow)   # Date the application was updated
    rating = db.Column(db.Integer, default=0)                        # Rating of the application
    downloads = db.Column(db.Integer, default=0)                     # Number of downloads
    category = db.Column(db.String, nullable=False)                  # Category of the application
    version = db.Column(db.Integer, default=0)                       # Version of the application
    theme = db.Column(db.Boolean, default=False)                     # Theme of the application
    title_ids = relationship("TitleIDsModel", back_populates="application")
    meta_data = relationship("MetadataModel", back_populates="application", uselist=False)
    author = relationship("AuthorModel", back_populates="application", uselist=False)
    analytics = relationship("AnalyticsModel", back_populates="application")


class TitleIDsModel(db.Model):
    __tablename__ = 'title_ids'

    application_id = db.Column(db.Integer, ForeignKey('application.id'), primary_key=True)
    sd_title = db.Column(db.String, nullable=False)
    nand_title = db.Column(db.String, nullable=False)
    forwarder_title = db.Column(db.String, nullable=False)


class MetadataModel(db.Model):
    __tablename__ = 'metadata'

    application_id = db.Column(db.Integer, ForeignKey('application.id'), primary_key=True)   # Application ID
    application = relationship("AppsModel", back_populates="metadata")                       # Application
    display_name = db.Column(db.String, nullable=False)                                      # Display name of the application
    display_version = db.Column(db.String, nullable=False)                                   # Display version of the application
    short_description = db.Column(db.String, nullable=True)                                  # Short description of the application
    long_description = db.Column(db.String, nullable=True)                                   # Long description of the application
    contributors = db.Column(db.String, nullable=True)                                       # Contributors of the application
    file_uuid = db.Column(db.String, nullable=True)                                          # File UUID of the application


class AuthorModel(db.Model):
    __tablename__ = 'author'

    id = db.Column(db.Integer, primary_key=True)                         # Numeric author ID
    application = relationship("AppsModel", back_populates="author")     # Application
    display_name = db.Column(db.String, nullable=False)                  # Display name of the author
    description = db.Column(db.String, nullable=True)                    # Description of the author
    url = db.Column(db.String, nullable=True)                            # URL of the author


class AnalyticsModel(db.Model):
    __tablename__ = 'analytics'

    id = db.Column(db.Integer, primary_key=True)                         # Numeric analytic point ID
    application = relationship("AppsModel", back_populates="analytics")  # Application
    date = db.Column(db.DateTime, default=datetime.utcnow)               # Date of the analytic point
    type = db.Column(db.String, nullable=False)                          # Type of the analytic point
    value = db.Column(db.Integer, nullable=False)                        # Value of the analytic point

