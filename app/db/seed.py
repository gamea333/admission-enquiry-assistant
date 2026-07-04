from app.db.models import FAQ, Fee, SchoolClass, TransportRoute, get_session_factory, init_db

GRADE_NAMES = [
    "Nursery",
    "LKG",
    "UKG",
    "Grade 1",
    "Grade 2",
    "Grade 3",
    "Grade 4",
    "Grade 5",
    "Grade 6",
    "Grade 7",
    "Grade 8",
    "Grade 9",
    "Grade 10",
]

# (admission_fee, tuition_fee_annual, transport_fee_annual)
FEE_BY_GRADE = {
    "Nursery": (25_000, 120_000, 36_000),
    "LKG": (25_000, 125_000, 36_000),
    "UKG": (25_000, 130_000, 36_000),
    "Grade 1": (30_000, 145_000, 38_000),
    "Grade 2": (30_000, 150_000, 38_000),
    "Grade 3": (30_000, 155_000, 38_000),
    "Grade 4": (30_000, 160_000, 38_000),
    "Grade 5": (35_000, 170_000, 40_000),
    "Grade 6": (35_000, 180_000, 40_000),
    "Grade 7": (35_000, 185_000, 40_000),
    "Grade 8": (40_000, 195_000, 42_000),
    "Grade 9": (40_000, 205_000, 42_000),
    "Grade 10": (45_000, 215_000, 42_000),
}

# (capacity, seats_filled) — some full, some with open seats
SEAT_DATA = {
    "Nursery": (30, 30),
    "LKG": (30, 28),
    "UKG": (30, 22),
    "Grade 1": (35, 35),
    "Grade 2": (35, 31),
    "Grade 3": (35, 35),
    "Grade 4": (40, 36),
    "Grade 5": (40, 40),
    "Grade 6": (40, 38),
    "Grade 7": (40, 25),
    "Grade 8": (40, 40),
    "Grade 9": (35, 33),
    "Grade 10": (35, 35),
}


def seed_sample_data() -> None:
    init_db()
    session = get_session_factory()()

    try:
        if session.query(SchoolClass).count() > 0:
            return

        for grade in GRADE_NAMES:
            capacity, seats_filled = SEAT_DATA[grade]
            school_class = SchoolClass(
                name=grade,
                section="A",
                capacity=capacity,
                seats_filled=seats_filled,
            )
            session.add(school_class)
            session.flush()

            admission, tuition, transport = FEE_BY_GRADE[grade]
            session.add(
                Fee(
                    class_id=school_class.id,
                    admission_fee=admission,
                    tuition_fee_annual=tuition,
                    transport_fee_annual=transport,
                )
            )

        routes = [
            TransportRoute(
                area_name="Whitefield",
                pickup_point="ITPL Main Gate, Whitefield",
                monthly_fee=3_200,
                available=True,
            ),
            TransportRoute(
                area_name="Marathahalli",
                pickup_point="Marathahalli Bridge (towards ORR)",
                monthly_fee=3_000,
                available=True,
            ),
            TransportRoute(
                area_name="Indiranagar",
                pickup_point="100 Feet Road, near CMH Metro",
                monthly_fee=3_500,
                available=True,
            ),
            TransportRoute(
                area_name="Koramangala",
                pickup_point="5th Block, near Forum Mall",
                monthly_fee=3_400,
                available=False,
            ),
            TransportRoute(
                area_name="HSR Layout",
                pickup_point="Sector 2, BDA Complex",
                monthly_fee=3_300,
                available=True,
            ),
            TransportRoute(
                area_name="Electronic City",
                pickup_point="Phase 1, Infosys Gate 1",
                monthly_fee=3_800,
                available=True,
            ),
            TransportRoute(
                area_name="Jayanagar",
                pickup_point="4th Block, near Ragigudda Temple",
                monthly_fee=3_600,
                available=False,
            ),
            TransportRoute(
                area_name="Hebbal",
                pickup_point="NH-44, near Esteem Mall",
                monthly_fee=3_700,
                available=True,
            ),
            TransportRoute(
                area_name="Sarjapur Road",
                pickup_point="Kaikondrahalli Lake junction",
                monthly_fee=3_500,
                available=True,
            ),
            TransportRoute(
                area_name="Bellandur",
                pickup_point="Outer Ring Road, near Central Mall",
                monthly_fee=3_100,
                available=True,
            ),
        ]
        session.add_all(routes)

        faqs = [
            FAQ(
                category="Uniforms",
                question="What is the school uniform policy?",
                answer=(
                    "Prescribed grey uniform with white shirt, school tie, and black shoes on all school days. "
                    "House T-shirts on Wednesdays. Available at the school store."
                ),
            ),
            FAQ(
                category="Holidays",
                question="How many holidays does the school have?",
                answer=(
                    "Approximately 110 instructional days per term with Dasara, Winter, and Summer breaks. "
                    "Full calendar is shared in the parent handbook each June."
                ),
            ),
            FAQ(
                category="Fees",
                question="Is there a sibling discount?",
                answer="10% tuition discount for the second sibling and 15% for the third child enrolled concurrently.",
            ),
            FAQ(
                category="Extracurriculars",
                question="What activities are offered after school?",
                answer=(
                    "Cricket, football, swimming, chess, robotics, dance, music, and debate clubs "
                    "run 3:15–4:30 PM on weekdays. Registration opens in June."
                ),
            ),
            FAQ(
                category="Campus Visit",
                question="How do I book a campus tour?",
                answer=(
                    "Book Saturdays 9 AM–12 PM at admissions.greenfield.edu.in/visit or call +91 80 4123 5601."
                ),
            ),
            FAQ(
                category="Transport",
                question="Can I change the bus route mid-year?",
                answer=(
                    "Route changes allowed at term start (June/November) if seats exist. "
                    "Submit request to transport office 15 days in advance."
                ),
            ),
            FAQ(
                category="Meals",
                question="Does the school provide lunch?",
                answer="Optional hot lunch subscription with vegetarian and Jain options. Home lunch is also permitted.",
            ),
            FAQ(
                category="Assessment",
                question="Is there an entrance test for Nursery?",
                answer="No written test for Nursery–UKG; a parent-child interaction is conducted instead.",
            ),
            FAQ(
                category="Communication",
                question="How does the school contact parents?",
                answer="Via the Greenfield Parent App, term PTMs, and SMS for urgent alerts.",
            ),
            FAQ(
                category="Withdrawal",
                question="What is the refund policy on withdrawal?",
                answer=(
                    "One month's notice required. Tuition refunded pro-rata; admission fee non-refundable; "
                    "deposit returned after TC and dues clearance."
                ),
            ),
        ]
        session.add_all(faqs)

        session.commit()
    finally:
        session.close()


if __name__ == "__main__":
    seed_sample_data()
    print("Sample data seeded successfully.")
