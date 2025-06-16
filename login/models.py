from sqlalchemy import  Column, ForeignKey, String, Boolean, DECIMAL, Integer, DateTime, Text, func # type: ignore
from datetime import datetime
from sqlalchemy.orm import relationship # type: ignore
from login.database import Base

class CompanyInCharge(Base):
    __tablename__ = "company_in_charge"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), default="null")
    official_email = Column(String(255), unique=True, default="Null")
    country_code = Column(String(3), default="+91")
    mobile_number = Column(String(15), default="Null")
    designation = Column(String(255), default="null")
    password = Column(String(128), default="null")
    confirm_password = Column(String(128), default="null")
    linkedin_profile = Column(String(255), nullable=True)
    company_person_name = Column(String(255), default="Null")
    agreed_to_terms = Column(Boolean, default=True)
    token = Column(String(255), nullable=True)
    is_online = Column(Boolean, default=False)

class UniversityInCharge(Base):
    __tablename__ = "university_in_charge"

    id = Column(Integer, primary_key=True, index=True)
    clg_id = Column(Integer, unique=True, nullable=True, default=None)
    university_name = Column(String(255), default="null")
    official_email = Column(String(255), unique=True, default="Null")
    country_code = Column(String(3), default="+91")
    mobile_number = Column(String(15), default="Null")
    designation = Column(String(255), default="null")
    password = Column(String(128), default="null")
    confirm_password = Column(String(128), default="null")
    linkedin_profile = Column(String(255), nullable=True)
    college_person_name = Column(String(255), default="Null")
    agreed_to_terms = Column(Boolean, default=True)
    token = Column(String(255), nullable=True)
    is_online = Column(Boolean, default=False)

class OnlineStatus(Base):
    __tablename__ = "online_status"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255),unique=True, default="Null")
    is_online = Column(Boolean, default=False)
    last_seen = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"{self.email} - {'Online' if self.is_online else 'Offline'}"
    
class new_user(Base):
    __tablename__ = "new_user"

    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String(255), nullable=False)
    lastname = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    country_code = Column(String(255), nullable=False)
    phonenumber = Column(String(255), nullable=False)
    gender = Column(String(255), default="other")
    password = Column(String(128), nullable=False)
    confirm_password = Column(String(128), default="null")
    course = Column(String(255), default="")
    educations = Column(String(255), default="")
    percentage = Column(String(255), default="")
    preferred_destination = Column(String(255), default="")
    start_date = Column(String(255), default="")
    mode_study = Column(String(255), default="")
    entrance = Column(Boolean, default=False)
    passport = Column(Boolean, default=False)
    is_online = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    token = Column(String(255), default="NULL")
    agreed_to_terms = Column(Boolean, default=False)

class JobSeeker(Base):
    __tablename__ = "jobseeker"
    
    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String(255), nullable=False)
    lastname = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phonenumber = Column(String(255), nullable=False)
    # designation = Column(String(255), default="null")
    experience = Column(Integer, nullable=True)
    linkedin_profile = Column(String(255), nullable=True)
    password = Column(String(255), nullable=False)
    confirm_password = Column(String(128), default="null")
    country_code = Column(String(255), nullable=False)
    token = Column(String(255), default="NULL")
    agreed_to_terms = Column(Boolean, default=False)
    is_online = Column(Boolean, default=False)

class Forgot(Base):
    __tablename__ = "forgot"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Verify(Base):
    __tablename__ = "verify"

    id = Column(Integer, primary_key=True, index=True)
    otp = Column(String(4), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Forgot2(Base):
    __tablename__ = "forgot2"
   
    id = Column(Integer, primary_key=True, index=True)
    password = Column(String(128), default="null")
    confirm_password = Column(String(128), default="null")

class Consultant(Base):
    __tablename__ = "consultant"

    id = Column(Integer, primary_key=True, index=True)
    consultant_name = Column(String(255), default="null")
    official_email = Column(String(255), unique=True, default="Null")
    country_code = Column(String(3), default="+91")
    mobile_number = Column(String(15), default="Null")
    designation = Column(String(255), default="null")
    password = Column(String(128), default="null")
    confirm_password = Column(String(255), default="null")
    linkedin_profile = Column(String(255), nullable=True)
    consultant_person_name = Column(String(255), default="Null")
    agreed_to_terms = Column(Boolean, default=True)
    token = Column(String(255), nullable=True)
    is_online = Column(Boolean, default=False)


class Contact(Base):
    __tablename__ = "contact"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    website = Column(String(255), nullable=True)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Question(Base):
    __tablename__ = "login_question" 

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    answers = relationship("Answer", back_populates="question")


class Answer(Base):
    __tablename__ = "login_answer"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey('login_question.id'), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    question = relationship("Question", back_populates="answers")

class Subscriber(Base):
    __tablename__ = 'subscribers'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    subscribed_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Subscriber(email={self.email}, subscribed_at={self.subscribed_at})>"
    
class Subscriber1(Base):
    __tablename__ = 'subscribers1'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    subscribed_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Subscriber(email={self.email}, subscribed_at={self.subscribed_at})>"

class AdmissionReview(Base):
    __tablename__ = "admission_reviews"

    id = Column(Integer, primary_key=True, index=True)
    college_name = Column(String(255))
    other_college_name = Column(String(255), nullable=True)
    course_name = Column(String(255))
    other_course_name = Column(String(255), nullable=True)
    student_name = Column(String(255))
    email = Column(String(255))
    country_code = Column(String(5), default="IN")
    phone_number = Column(String(20))
    gender = Column(String(10))
    linkedin_profile = Column(String(255), nullable=True)
    course_fees = Column(DECIMAL(10, 2))
    year = Column(Integer)
    referral_code = Column(String(50), nullable=True)
    apply = Column(String(20), default="applied")
    anvil_reservation_benefits = Column(Boolean)
    benefit = Column(String(20), default="Benefits")
    gd_pi_admission = Column(Boolean)
    class_size = Column(Integer)
    opted_hostel = Column(Boolean)
    college_provides_placements = Column(Boolean)
    hostel_fees = Column(DECIMAL(12, 2), nullable=True, default=0.00)
    average_package = Column(DECIMAL(10, 2), nullable=True)
    admission_process = Column(Text)
    course_curriculum_faculty = Column(Text)
    fees_structure_scholarship = Column(Text)
    liked_things = Column(Text)
    disliked_things = Column(Text)
    profile_photo = Column(String(255), nullable=True)
    campus_photos = Column(String(255), nullable=True)
    certificate_id_card = Column(String(255), nullable=True)
    graduation_certificate = Column(String(255), nullable=True)
    agree_terms = Column(Boolean, default=True)

class Unregister_Colleges(Base):
    __tablename__ = "unregister_colleges"

    id = Column(Integer, primary_key=True, index=True)
    university_name = Column(String(255), default="null")
    official_email = Column(String(255), unique=True, default="Null")
    country_code = Column(String(3), default="+91")
    mobile_number = Column(String(15), default="Null")
    designation = Column(String(255), default="null")
    password = Column(String(128), default="null")
    confirm_password = Column(String(128), default="null")
    linkedin_profile = Column(String(255), nullable=True)
    college_person_name = Column(String(255), default="Null")
    agreed_to_terms = Column(Boolean, default=True)
    token = Column(String(255), nullable=True)
    is_online = Column(Boolean, default=False)
