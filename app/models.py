from sqlalchemy import (
    Column, Integer, String, Boolean, Float, Text,
    DateTime, ForeignKey, Enum
)
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base
import enum


# ----------------------------
# Enums
# ----------------------------

class ImpactStatus(enum.Enum):
    new = "new"
    under_review = "under_review"
    accepted = "accepted"
    mitigated = "mitigated"
    not_applicable = "not_applicable"


# ----------------------------
# Products
# ----------------------------

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    vendor = Column(String, nullable=False)
    version = Column(String, nullable=True)
    cpe_uri = Column(String, nullable=True)
    tags = Column(Text, nullable=True)   # store as JSON string
    active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    impacts = relationship("Impact", back_populates="product")

    def __repr__(self):
        return f"<Product {self.vendor} {self.name} {self.version}>"


# ----------------------------
# CVEs
# ----------------------------

class CVE(Base):
    __tablename__ = "cves"

    id = Column(Integer, primary_key=True)
    cve_id = Column(String, unique=True, nullable=False)

    summary = Column(Text)
    cvss_v3_score = Column(Float)
    cvss_v3_vector = Column(String)

    published_date = Column(DateTime)
    last_modified_date = Column(DateTime)

    epss_score = Column(Float, nullable=True)
    kev_flag = Column(Boolean, default=False)

    raw_json = Column(Text)

    cpe_entries = relationship("CVECPE", back_populates="cve")
    impacts = relationship("Impact", back_populates="cve")


# ----------------------------
# CPE entries (CVE → CPE mappings)
# ----------------------------

class CVECPE(Base):
    __tablename__ = "cve_cpes"

    id = Column(Integer, primary_key=True)
    cve_id = Column(String, ForeignKey("cves.cve_id"))
    cpe_uri = Column(String, nullable=False)
    vulnerable = Column(Boolean, default=True)
    version_start = Column(String, nullable=True)
    version_start_incl = Column(Boolean, default=True)
    version_end = Column(String, nullable=True)
    version_end_incl = Column(Boolean, default=True)

    cve = relationship("CVE", back_populates="cpe_entries")


# ----------------------------
# Impacts (CVE hits your product)
# ----------------------------

class CPEDictionary(Base):
    __tablename__ = "cpe_dictionary"

    id = Column(Integer, primary_key=True)
    cpe_uri = Column(String, unique=True, index=True)
    vendor = Column(String)
    product = Column(String)
    version = Column(String)
    deprecated = Column(Boolean, default=False)
    raw_json = Column(Text)


class Impact(Base):
    __tablename__ = "impacts"

    id = Column(Integer, primary_key=True)

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    cve_id = Column(String, ForeignKey("cves.cve_id"), nullable=False)

    status = Column(Enum(ImpactStatus), default=ImpactStatus.new)

    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow,
                       onupdate=datetime.utcnow)

    notes = Column(Text, nullable=True)

    product = relationship("Product", back_populates="impacts")
    cve = relationship("CVE", back_populates="impacts")
