#!/usr/bin/env python3
"""Seed mock reviews for demo vehicles.

Requires seed_db.py to have been run first (vehicles + owner users must exist).
Creates 3–4 additional renter users and 10–15 reviews.
"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import SessionLocal
from backend.models import Review, User, Vehicle

MOCK_RENTERS = [
    {"email": "alice@club-mobilite.test", "name": "Alice Moreau"},
    {"email": "bob@club-mobilite.test", "name": "Bob Nguyen"},
    {"email": "charlie@club-mobilite.test", "name": "Charlie Durand"},
    {"email": "diana@club-mobilite.test", "name": "Diana Faure"},
]

MOCK_REVIEWS = [
    # (renter_email, vehicle_plate, rating_vehicle, rating_owner, comment)
    ("alice@club-mobilite.test",   "AB-123-CD", 5.0, 4.5, "Voiture impeccable, démarrage facile. Propriétaire très disponible."),
    ("bob@club-mobilite.test",     "AB-123-CD", 4.5, 5.0, "Parfait pour le week-end. Plein fait à temps. Merci Dupont!"),
    ("charlie@club-mobilite.test", "AB-123-CD", 4.0, 4.0, "Bon état général. Légère odeur de tabac mais rien de grave."),
    ("diana@club-mobilite.test",   "EF-456-GH", 5.0, 5.0, "Yaris automatique top pour la ville. Lefèvre est adorable."),
    ("alice@club-mobilite.test",   "EF-456-GH", 4.5, 4.5, "Très bien, voiture propre et économique. Je recommande!"),
    ("bob@club-mobilite.test",     "IJ-789-KL", 4.0, 4.0, "Golf robuste, idéale pour long trajet. RAS."),
    ("charlie@club-mobilite.test", "IJ-789-KL", 4.5, 4.5, "Rousseau réactif au téléphone. Clés rendues sans souci."),
    ("diana@club-mobilite.test",   "IJ-789-KL", 3.5, 4.0, "L'égratignure mentionnée est plus visible qu'attendu mais voiture fiable."),
    ("alice@club-mobilite.test",   "MN-012-OP", 5.0, 4.0, "Karoq super confortable! Idéal pour week-end famille."),
    ("bob@club-mobilite.test",     "QR-345-ST", 5.0, 5.0, "SpaceTourer parfait pour déménagement. Simon top proprio."),
    ("charlie@club-mobilite.test", "QR-345-ST", 4.5, 5.0, "7 places vraiment utilisées, confort premium top niveau."),
    ("diana@club-mobilite.test",   "UV-678-WX", 4.0, 4.5, "Trafic utilitaire fonctionnel pour notre déménagement. Merci Lambert."),
    ("alice@club-mobilite.test",   "UV-678-WX", 3.5, 4.0, "Clim en panne comme annoncé. Utilitaire mais basique."),
]


def seed():
    db = SessionLocal()

    # Create mock renters
    renter_map = {}
    for r in MOCK_RENTERS:
        user = db.query(User).filter(User.email == r["email"]).first()
        if not user:
            user = User(email=r["email"], name=r["name"], created_at=datetime.utcnow())
            db.add(user)
            db.flush()
            print(f"  created renter: {user.email}")
        renter_map[r["email"]] = user

    db.flush()

    # Create reviews
    created = 0
    for (renter_email, plate, rv, ro, comment) in MOCK_REVIEWS:
        renter = renter_map.get(renter_email)
        v = db.query(Vehicle).filter(Vehicle.plate == plate).first()
        if not v:
            print(f"  skip review — vehicle {plate} not found")
            continue
        if v.owner_id is None:
            print(f"  skip review — vehicle {plate} has no owner_id")
            continue

        # Avoid duplicates
        existing = db.query(Review).filter(
            Review.vehicle_id == v.id,
            Review.reviewer_id == renter.id,
        ).first()
        if existing:
            continue

        review = Review(
            vehicle_id=v.id,
            reviewer_id=renter.id,
            reviewee_id=v.owner_id,
            rating_vehicle=rv,
            rating_owner=ro,
            comment=comment,
            created_at=datetime.utcnow(),
        )
        db.add(review)
        created += 1

    db.commit()

    # Recalculate vehicle aggregate ratings
    from sqlalchemy import func
    for v in db.query(Vehicle).all():
        agg = db.query(func.avg(Review.rating_vehicle), func.count(Review.id)).filter(
            Review.vehicle_id == v.id
        ).first()
        if agg[1] > 0:
            v.rating = round(agg[0], 2)
            v.nb_reviews = agg[1]

    db.commit()
    db.close()
    print(f"Reviews seed complete — {created} reviews created.")


if __name__ == "__main__":
    seed()
