import re

from sqlalchemy.orm import Session, joinedload

from app.db.models import FAQ, Fee, SchoolClass, TransportRoute

GRADE_ALIASES: dict[str, str] = {
    "nursery": "Nursery",
    "lkg": "LKG",
    "ukg": "UKG",
    "grade 1": "Grade 1",
    "grade 2": "Grade 2",
    "grade 3": "Grade 3",
    "grade 4": "Grade 4",
    "grade 5": "Grade 5",
    "grade 6": "Grade 6",
    "grade 7": "Grade 7",
    "grade 8": "Grade 8",
    "grade 9": "Grade 9",
    "grade 10": "Grade 10",
    "class 1": "Grade 1",
    "class 2": "Grade 2",
    "class 3": "Grade 3",
    "class 4": "Grade 4",
    "class 5": "Grade 5",
    "class 6": "Grade 6",
    "class 7": "Grade 7",
    "class 8": "Grade 8",
    "class 9": "Grade 9",
    "class 10": "Grade 10",
}


def get_all_classes(db: Session) -> list[SchoolClass]:
    return db.query(SchoolClass).order_by(SchoolClass.id).all()


def get_class_by_name(db: Session, name: str) -> SchoolClass | None:
    return db.query(SchoolClass).filter(SchoolClass.name.ilike(f"%{name}%")).first()


def extract_class_name(query: str, db: Session) -> str | None:
    lowered = query.lower()
    for alias, canonical in GRADE_ALIASES.items():
        if alias in lowered:
            return canonical

    match = re.search(r"grade\s*(\d{1,2})", lowered)
    if match:
        return f"Grade {int(match.group(1))}"

    for school_class in get_all_classes(db):
        if school_class.name.lower() in lowered:
            return school_class.name
    return None


def extract_area_name(query: str, db: Session) -> str | None:
    lowered = query.lower()
    areas = db.query(TransportRoute.area_name).distinct().all()
    for (area,) in areas:
        if area.lower() in lowered:
            return area
    return None


def get_fees_for_class(db: Session, class_name: str) -> dict | None:
    school_class = get_class_by_name(db, class_name)
    if not school_class:
        return None

    fee = db.query(Fee).filter(Fee.class_id == school_class.id).first()
    if not fee:
        return None

    return {
        "class_name": school_class.name,
        "section": school_class.section,
        "admission_fee": fee.admission_fee,
        "tuition_fee_annual": fee.tuition_fee_annual,
        "transport_fee_annual": fee.transport_fee_annual,
    }


def get_seat_availability(db: Session, class_name: str) -> dict | None:
    school_class = get_class_by_name(db, class_name)
    if not school_class:
        return None

    return {
        "class_name": school_class.name,
        "section": school_class.section,
        "capacity": school_class.capacity,
        "seats_filled": school_class.seats_filled,
        "seats_available": school_class.seats_available,
        "is_full": school_class.is_full,
    }


def get_transport_for_area(db: Session, area_name: str) -> list[dict]:
    routes = (
        db.query(TransportRoute)
        .filter(TransportRoute.area_name.ilike(f"%{area_name}%"))
        .order_by(TransportRoute.pickup_point)
        .all()
    )
    return [
        {
            "area_name": route.area_name,
            "pickup_point": route.pickup_point,
            "monthly_fee": route.monthly_fee,
            "available": route.available,
        }
        for route in routes
    ]


def search_faq(db: Session, keyword: str, limit: int = 5) -> list[dict]:
    pattern = f"%{keyword}%"
    faqs = (
        db.query(FAQ)
        .filter(FAQ.question.ilike(pattern) | FAQ.answer.ilike(pattern))
        .limit(limit)
        .all()
    )
    return [
        {
            "category": faq.category,
            "question": faq.question,
            "answer": faq.answer,
        }
        for faq in faqs
    ]


def get_classes_with_available_seats(db: Session) -> list[SchoolClass]:
    return (
        db.query(SchoolClass)
        .filter(SchoolClass.seats_filled < SchoolClass.capacity)
        .order_by(SchoolClass.name)
        .all()
    )


def get_all_fees(db: Session) -> list[Fee]:
    return db.query(Fee).options(joinedload(Fee.school_class)).all()


def get_transport_routes(db: Session, available_only: bool = False) -> list[TransportRoute]:
    query = db.query(TransportRoute).order_by(TransportRoute.area_name)
    if available_only:
        query = query.filter(TransportRoute.available.is_(True))
    return query.all()
