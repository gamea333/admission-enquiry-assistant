from datetime import datetime

from app.db.models import AdmissionDeadline, FAQ, Program, get_engine, get_session_factory, init_db


def seed_sample_data() -> None:
    init_db()
    session = get_session_factory()()

    try:
        if session.query(Program).count() > 0:
            return

        programs = [
            Program(
                name="Bachelor of Computer Science",
                degree="BSc",
                duration_years=3.0,
                tuition_fee=45000,
                eligibility="12th grade with Mathematics; minimum 60% aggregate",
                intake_month="August",
            ),
            Program(
                name="Master of Business Administration",
                degree="MBA",
                duration_years=2.0,
                tuition_fee=75000,
                eligibility="Bachelor's degree with 50% aggregate; valid entrance exam score",
                intake_month="July",
            ),
            Program(
                name="Bachelor of Engineering",
                degree="BE",
                duration_years=4.0,
                tuition_fee=55000,
                eligibility="12th grade with Physics, Chemistry, Mathematics; JEE or equivalent",
                intake_month="August",
            ),
        ]
        session.add_all(programs)

        deadlines = [
            AdmissionDeadline(
                program_name="Bachelor of Computer Science",
                round="Early",
                deadline_date=datetime(2026, 5, 15),
            ),
            AdmissionDeadline(
                program_name="Bachelor of Computer Science",
                round="Regular",
                deadline_date=datetime(2026, 7, 1),
            ),
            AdmissionDeadline(
                program_name="Master of Business Administration",
                round="Round 1",
                deadline_date=datetime(2026, 4, 30),
            ),
        ]
        session.add_all(deadlines)

        faqs = [
            FAQ(
                category="Application",
                question="How do I apply for admission?",
                answer="Complete the online application form on the admissions portal, upload required documents, and pay the application fee.",
            ),
            FAQ(
                category="Fees",
                question="Are scholarships available?",
                answer="Yes. Merit-based and need-based scholarships are available. Details are on the financial aid page.",
            ),
            FAQ(
                category="Documents",
                question="What documents are required?",
                answer="Academic transcripts, identity proof, passport-size photograph, and entrance exam scorecard (if applicable).",
            ),
        ]
        session.add_all(faqs)

        session.commit()
    finally:
        session.close()


if __name__ == "__main__":
    seed_sample_data()
    print("Sample data seeded successfully.")
