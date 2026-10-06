import hashlib
import hmac
import math
import time
from datetime import datetime

import folium
import pandas as pd
import streamlit as st
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
    inspect,
    text,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from streamlit_folium import st_folium


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AegisCare Emergency",
    page_icon="🚑",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# DATABASE
# =========================================================

Base = declarative_base()

engine = create_engine(
    "sqlite:///aegiscare.db",
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine)


# =========================================================
# DATABASE MODELS
# =========================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    username = Column(String, unique=True)
    password_hash = Column(String)
    role = Column(String)
    phone = Column(String, default="")
    specialty = Column(String, default="")
    verified = Column(Boolean, default=True)


class Ambulance(Base):
    __tablename__ = "ambulances"

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)

    lat = Column(Float)
    lon = Column(Float)

    status = Column(String, default="Available")

    equipment = Column(
        String,
        default="Oxygen"
    )

    driver = Column(
        String,
        default=""
    )

    driver_phone = Column(
        String,
        default=""
    )

    hospital = Column(
        String,
        default="AegisCare Central"
    )


class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True)

    name = Column(String)

    lat = Column(Float)
    lon = Column(Float)

    emergency = Column(
        Boolean,
        default=True
    )

    icu_beds = Column(
        Integer,
        default=0
    )

    emergency_beds = Column(
        Integer,
        default=0
    )

    ventilators = Column(
        Integer,
        default=0
    )


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True)

    name = Column(String)

    hospital_id = Column(Integer)

    specialty = Column(String)

    available = Column(
        Boolean,
        default=True
    )


class EmergencyCase(Base):
    __tablename__ = "emergency_cases"

    id = Column(Integer, primary_key=True)

    patient_name = Column(String)

    patient_username = Column(String)

    age = Column(Integer)

    condition = Column(String)

    severity = Column(String)

    pickup_lat = Column(Float)

    pickup_lon = Column(Float)

    ambulance_code = Column(String)

    hospital_name = Column(String)

    doctor_name = Column(String)

    bed_type = Column(String)

    status = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.now
    )

    eta_minutes = Column(
        Integer,
        default=0
    )


# =========================================================
# CREATE TABLES
# =========================================================

Base.metadata.create_all(engine)


# =========================================================
# DATABASE MIGRATION
# =========================================================

def migrate_database():

    inspector = inspect(engine)

    tables = inspector.get_table_names()

    if "ambulances" not in tables:
        return

    columns = [
        column["name"]
        for column in inspector.get_columns("ambulances")
    ]

    if "driver_phone" not in columns:

        with engine.begin() as connection:

            connection.execute(
                text(
                    "ALTER TABLE ambulances "
                    "ADD COLUMN driver_phone VARCHAR DEFAULT ''"
                )
            )


migrate_database()


# =========================================================
# PASSWORD SECURITY
# =========================================================

def hash_password(password):

    salt = b"aegiscare-static-demo-salt"

    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        120000
    ).hex()


def verify_password(password, stored):

    return hmac.compare_digest(
        hash_password(password),
        stored
    )


# =========================================================
# SEED DEMO DATA
# =========================================================

def seed():

    db = SessionLocal()

    # -----------------------------------------------------
    # USERS
    # -----------------------------------------------------

    if db.query(User).count() == 0:

        demo = [

            (
                "System Admin",
                "admin",
                "Admin",
                "admin123",
                "",
                ""
            ),

            (
                "Dr. Priya Rao",
                "doctor1",
                "Doctor",
                "doctor123",
                "9999999991",
                "Cardiology"
            ),

            (
                "Arjun Dispatcher",
                "dispatcher1",
                "Dispatcher",
                "dispatch123",
                "9999999992",
                ""
            ),

            (
                "Ravi Driver",
                "driver1",
                "Ambulance",
                "driver123",
                "9876543210",
                ""
            ),

            (
                "City Hospital Staff",
                "hospital1",
                "Hospital",
                "hospital123",
                "9999999994",
                ""
            ),
        ]

        for (
            name,
            username,
            role,
            password,
            phone,
            specialty
        ) in demo:

            db.add(
                User(
                    name=name,
                    username=username,
                    role=role,
                    password_hash=hash_password(password),
                    phone=phone,
                    specialty=specialty
                )
            )


    # -----------------------------------------------------
    # AMBULANCES
    # -----------------------------------------------------

    if db.query(Ambulance).count() == 0:

        db.add_all(

            [

                Ambulance(
                    code="A-101",
                    lat=17.3850,
                    lon=78.4867,
                    status="Available",
                    equipment="Oxygen, ECG",
                    driver="Ravi Kumar",
                    driver_phone="9876543210",
                    hospital="AegisCare Central"
                ),

                Ambulance(
                    code="A-102",
                    lat=17.4000,
                    lon=78.4700,
                    status="Available",
                    equipment="Oxygen, Ventilator",
                    driver="Suresh Kumar",
                    driver_phone="9876543211",
                    hospital="AegisCare Central"
                ),

                Ambulance(
                    code="A-103",
                    lat=17.3600,
                    lon=78.5000,
                    status="Available",
                    equipment="Oxygen, First Aid",
                    driver="Manoj Kumar",
                    driver_phone="9876543212",
                    hospital="City Emergency Hospital"
                ),

                Ambulance(
                    code="A-104",
                    lat=17.4100,
                    lon=78.5100,
                    status="Available",
                    equipment="Oxygen, ECG",
                    driver="Imran Khan",
                    driver_phone="9876543213",
                    hospital="Metro Heart & Trauma"
                ),

            ]

        )


    # -----------------------------------------------------
    # HOSPITALS
    # -----------------------------------------------------

    if db.query(Hospital).count() == 0:

        db.add_all(

            [

                Hospital(
                    name="AegisCare Central",
                    lat=17.3950,
                    lon=78.4900,
                    icu_beds=4,
                    emergency_beds=8,
                    ventilators=3
                ),

                Hospital(
                    name="City Emergency Hospital",
                    lat=17.4200,
                    lon=78.4750,
                    icu_beds=2,
                    emergency_beds=5,
                    ventilators=1
                ),

                Hospital(
                    name="Metro Heart & Trauma",
                    lat=17.3650,
                    lon=78.5200,
                    icu_beds=3,
                    emergency_beds=4,
                    ventilators=2
                ),

            ]

        )

        db.flush()

        hospitals = db.query(Hospital).all()

        specs = [

            (
                "Dr. Priya Rao",
                "Cardiology"
            ),

            (
                "Dr. Arjun Mehta",
                "Emergency Medicine"
            ),

            (
                "Dr. Neha Sharma",
                "Pulmonology"
            ),

            (
                "Dr. Vikram Singh",
                "Orthopedics"
            ),

            (
                "Dr. Ananya Rao",
                "Emergency Medicine"
            ),

        ]

        for i, (
            name,
            spec
        ) in enumerate(specs):

            db.add(

                Doctor(
                    name=name,
                    hospital_id=hospitals[
                        i % len(hospitals)
                    ].id,
                    specialty=spec,
                    available=True
                )

            )


    db.commit()

    db.close()


seed()


# =========================================================
# LOAD CSS
# =========================================================

def load_css():

    try:

        with open(
            "style.css",
            "r",
            encoding="utf-8"
        ) as f:

            st.markdown(
                f"<style>{f.read()}</style>",
                unsafe_allow_html=True
            )

    except FileNotFoundError:

        pass


load_css()


# =========================================================
# INTRO ANIMATION
# =========================================================

def intro():

    if st.session_state.get(
        "intro_seen"
    ):

        return

    st.session_state.intro_seen = True

    holder = st.empty()

    holder.markdown(
        """
        <div class="intro-screen">

          <div class="cloud cloud-a">☁️</div>

          <div class="cloud cloud-b">☁️</div>

          <div class="cloud cloud-c">☁️</div>

          <div class="intro-ambulance">
            🚑
          </div>

          <div class="intro-title">
            AEGIS<span>CARE</span>
          </div>

          <div class="intro-sub">
            Emergency response. Connected care.
          </div>

          <div class="intro-line"></div>

        </div>
        """,
        unsafe_allow_html=True
    )

    time.sleep(1.25)

    holder.empty()


intro()


# =========================================================
# HELPERS
# =========================================================

def distance_km(
    lat1,
    lon1,
    lat2,
    lon2
):

    r = 6371

    p1 = math.radians(lat1)
    p2 = math.radians(lat2)

    dp = math.radians(
        lat2 - lat1
    )

    dl = math.radians(
        lon2 - lon1
    )

    a = (
        math.sin(dp / 2) ** 2
        +
        math.cos(p1)
        *
        math.cos(p2)
        *
        math.sin(dl / 2) ** 2
    )

    return (
        2
        *
        r
        *
        math.asin(
            math.sqrt(a)
        )
    )


def required_specialty(
    condition
):

    c = condition.lower()

    if any(
        x in c
        for x in [
            "cardiac",
            "heart",
            "chest pain"
        ]
    ):

        return "Cardiology"

    if any(
        x in c
        for x in [
            "breath",
            "asthma",
            "oxygen",
            "lung"
        ]
    ):

        return "Pulmonology"

    if any(
        x in c
        for x in [
            "accident",
            "fracture",
            "bone",
            "trauma"
        ]
    ):

        return "Orthopedics"

    return "Emergency Medicine"


def choose_resources(
    lat,
    lon,
    condition,
    severity
):

    db = SessionLocal()

    ambulances = (
        db.query(Ambulance)
        .filter(
            Ambulance.status
            == "Available"
        )
        .all()
    )

    hospitals = (
        db.query(Hospital)
        .filter(
            Hospital.emergency
            == True
        )
        .all()
    )

    specialty = required_specialty(
        condition
    )

    # -----------------------------------------------------
    # AMBULANCE SCORING
    # -----------------------------------------------------

    amb_scores = []

    for a in ambulances:

        d = distance_km(
            lat,
            lon,
            a.lat,
            a.lon
        )

        score = d

        if (
            severity == "Critical"
            and "Oxygen"
            in a.equipment
        ):

            score -= 1

        if (
            severity == "Critical"
            and "Ventilator"
            in a.equipment
        ):

            score -= 1

        amb_scores.append(
            (
                score,
                d,
                a
            )
        )

    amb_scores.sort(
        key=lambda x: x[0]
    )


    # -----------------------------------------------------
    # HOSPITAL SCORING
    # -----------------------------------------------------

    hospital_scores = []

    for h in hospitals:

        d = distance_km(
            lat,
            lon,
            h.lat,
            h.lon
        )

        doctors = (
            db.query(Doctor)
            .filter(
                Doctor.hospital_id
                == h.id,

                Doctor.specialty
                == specialty,

                Doctor.available
                == True
            )
            .all()
        )

        capability_bonus = 0

        if doctors:

            capability_bonus -= 3

        if (
            severity == "Critical"
            and h.icu_beds > 0
        ):

            capability_bonus -= 3

        if (
            severity == "Critical"
            and h.ventilators > 0
        ):

            capability_bonus -= 1

        if h.emergency_beds <= 0:

            capability_bonus += 10

        hospital_scores.append(
            (
                d + capability_bonus,
                d,
                h,
                doctors
            )
        )

    hospital_scores.sort(
        key=lambda x: x[0]
    )


    result = {

        "ambulance":
            amb_scores[0]
            if amb_scores
            else None,

        "hospital":
            hospital_scores[0]
            if hospital_scores
            else None,

        "specialty":
            specialty

    }

    db.close()

    return result


def badge(
    text,
    kind="blue"
):

    return (
        f'<span class="badge '
        f'{kind}">{text}</span>'
    )


def header(
    title,
    subtitle=""
):

    st.markdown(
        f"""
        <div class="page-header">

          <div>

            <h1>
              {title}
            </h1>

            <p>
              {subtitle}
            </p>

          </div>

        </div>
        """,
        unsafe_allow_html=True
    )


def metric_cards(
    items
):

    cols = st.columns(
        len(items)
    )

    for col, (
        label,
        value,
        icon
    ) in zip(
        cols,
        items
    ):

        col.markdown(
            f"""
            <div class="metric-card">

              <div class="metric-icon">
                {icon}
              </div>

              <div class="metric-value">
                {value}
              </div>

              <div class="metric-label">
                {label}
              </div>

            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# LOGIN
# =========================================================

def login():

    st.markdown(
        """
        <div class="login-wrap">

          <div class="brand-mark">
            ✚
          </div>

          <h1>
            AEGIS<span>CARE</span>
          </h1>

          <p>
            AI-powered emergency coordination
          </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    tab1, tab2 = st.tabs(
        [
            "🔐 Secure Login",
            "👤 Patient Registration"
        ]
    )


    # -----------------------------------------------------
    # LOGIN
    # -----------------------------------------------------

    with tab1:

        role_hint = st.selectbox(
            "Portal",
            [
                "Admin",
                "Patient",
                "Doctor",
                "Dispatcher",
                "Ambulance",
                "Hospital"
            ]
        )

        username = st.text_input(
            "Username"
        )

        password = st.text_input(
            "Password",
            type="password"
        )


        if st.button(
            "Sign in securely",
            use_container_width=True,
            type="primary"
        ):

            db = SessionLocal()

            u = (
                db.query(User)
                .filter(
                    User.username
                    == username
                )
                .first()
            )


            if (
                u
                and verify_password(
                    password,
                    u.password_hash
                )
            ):

                if (
                    role_hint != "Patient"
                    and u.role
                    != role_hint
                ):

                    st.error(
                        f"This account belongs "
                        f"to the {u.role} portal."
                    )

                else:

                    st.session_state.user = {

                        "id": u.id,

                        "name": u.name,

                        "username":
                            u.username,

                        "role":
                            u.role,

                        "phone":
                            u.phone,

                        "specialty":
                            u.specialty

                    }

                    st.rerun()

            else:

                st.error(
                    "Invalid username or password."
                )

            db.close()


        st.caption(
            "Demo accounts: "
            "admin/admin123 • "
            "doctor1/doctor123 • "
            "dispatcher1/dispatch123 • "
            "driver1/driver123 • "
            "hospital1/hospital123"
        )


    # -----------------------------------------------------
    # PATIENT REGISTRATION
    # -----------------------------------------------------

    with tab2:

        st.info(
            "Patients can create their own "
            "account and request an ambulance immediately."
        )

        name = st.text_input(
            "Full name",
            key="reg_name"
        )

        phone = st.text_input(
            "Mobile number",
            key="reg_phone"
        )

        username = st.text_input(
            "Create username",
            key="reg_user"
        )

        password = st.text_input(
            "Create password",
            type="password",
            key="reg_pass"
        )


        if st.button(
            "Create patient account",
            use_container_width=True
        ):

            db = SessionLocal()

            if (
                db.query(User)
                .filter(
                    User.username
                    == username
                )
                .first()
            ):

                st.error(
                    "Username already exists."
                )

            elif not all(
                [
                    name,
                    username,
                    password
                ]
            ):

                st.warning(
                    "Please complete the required fields."
                )

            else:

                db.add(

                    User(
                        name=name,
                        username=username,
                        phone=phone,
                        password_hash=
                            hash_password(
                                password
                            ),
                        role="Patient",
                        verified=True
                    )

                )

                db.commit()

                st.success(
                    "Account created. "
                    "You can now sign in."
                )

            db.close()


# =========================================================
# PATIENT PORTAL
# =========================================================

def patient_portal(
    user
):

    header(
        "Emergency Care",
        "Request an ambulance and coordinate hospital pre-arrival care."
    )

    db = SessionLocal()

    cases = (
        db.query(EmergencyCase)
        .filter(
            EmergencyCase.patient_username
            == user["username"]
        )
        .order_by(
            EmergencyCase.id.desc()
        )
        .all()
    )


    if cases:

        c = cases[0]

        st.markdown(
            f"""
            <div class="case-banner">

              <div>

                <b>
                  Active case #{c.id}
                </b>

                <br>

                {c.condition}
                •
                {c.severity}

              </div>

              <div>
                {badge(
                    c.status,
                    "green"
                )}
              </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with st.container(
        border=True
    ):

        st.subheader(
            "🚨 Request Emergency Ambulance"
        )

        col1, col2 = st.columns(2)


        with col1:

            age = st.number_input(
                "Patient age",
                0,
                120,
                35
            )

            condition = st.selectbox(
                "Emergency condition",
                [
                    "Severe breathing difficulty",
                    "Chest pain / cardiac emergency",
                    "Accident / trauma",
                    "Unconscious / critical",
                    "High fever / serious illness",
                    "Other emergency"
                ]
            )

            severity = st.selectbox(
                "Priority",
                [
                    "Critical",
                    "High",
                    "Medium"
                ]
            )


        with col2:

            lat = st.number_input(
                "Pickup latitude",
                value=17.3850,
                format="%.5f"
            )

            lon = st.number_input(
                "Pickup longitude",
                value=78.4867,
                format="%.5f"
            )

            note = st.text_area(
                "Additional symptoms / notes",
                placeholder=
                "Describe the emergency briefly."
            )


        if st.button(
            "🚑 Find Ambulance & Hospital",
            type="primary",
            use_container_width=True
        ):

            result = choose_resources(
                lat,
                lon,
                condition,
                severity
            )


            if (
                not result["ambulance"]
                or not result["hospital"]
            ):

                st.error(
                    "No suitable emergency "
                    "resources are currently available."
                )

            else:

                (
                    _,
                    amb_dist,
                    amb
                ) = result["ambulance"]

                (
                    _,
                    hosp_dist,
                    hosp,
                    doctors
                ) = result["hospital"]

                doctor = (
                    doctors[0]
                    if doctors
                    else None
                )

                bed = (
                    "ICU"
                    if (
                        severity == "Critical"
                        and hosp.icu_beds > 0
                    )
                    else "Emergency"
                )

                eta = max(
                    3,
                    round(
                        amb_dist * 3
                        +
                        hosp_dist * 2
                    )
                )


                amb.status = "Assigned"


                if bed == "ICU":

                    hosp.icu_beds -= 1

                else:

                    hosp.emergency_beds -= 1


                case = EmergencyCase(

                    patient_name=
                        user["name"],

                    patient_username=
                        user["username"],

                    age=age,

                    condition=condition,

                    severity=severity,

                    pickup_lat=lat,

                    pickup_lon=lon,

                    ambulance_code=
                        amb.code,

                    hospital_name=
                        hosp.name,

                    doctor_name=
                        (
                            doctor.name
                            if doctor
                            else "Emergency Team"
                        ),

                    bed_type=bed,

                    status=
                        "Pre-arrival Confirmed",

                    eta_minutes=eta
                )


                db.add(case)

                db.commit()


                st.session_state.last_case = (
                    case.id
                )


                st.success(
                    "Emergency coordination started. "
                    "Hospital pre-arrival notification created."
                )

                st.rerun()


    if cases:

        st.subheader(
            "📍 Your emergency history"
        )

        st.dataframe(

            pd.DataFrame(

                [

                    {
                        "Case":
                            c.id,

                        "Condition":
                            c.condition,

                        "Ambulance":
                            c.ambulance_code,

                        "Hospital":
                            c.hospital_name,

                        "Doctor":
                            c.doctor_name,

                        "Bed":
                            c.bed_type,

                        "ETA":
                            f"{c.eta_minutes} min",

                        "Status":
                            c.status

                    }

                    for c in cases

                ]

            ),

            use_container_width=True,

            hide_index=True

        )


    db.close()


# =========================================================
# ADMIN PORTAL
# =========================================================

def admin_portal():

    header(
        "Command Center",
        "Complete operational view — restricted to authorized administrators."
    )

    db = SessionLocal()

    users = db.query(User).all()

    ambs = db.query(Ambulance).all()

    hospitals = db.query(Hospital).all()

    doctors = db.query(Doctor).all()

    cases = (
        db.query(EmergencyCase)
        .order_by(
            EmergencyCase.id.desc()
        )
        .all()
    )


    # =====================================================
    # ADMIN METRICS
    # =====================================================

    metric_cards(

        [

            (
                "Active emergencies",

                len(
                    [
                        c
                        for c in cases
                        if c.status != "Closed"
                    ]
                ),

                "🚨"
            ),

            (
                "Available ambulances",

                len(
                    [
                        a
                        for a in ambs
                        if a.status
                        == "Available"
                    ]
                ),

                "🚑"
            ),

            (
                "Available doctors",

                len(
                    [
                        d
                        for d in doctors
                        if d.available
                    ]
                ),

                "👨‍⚕️"
            ),

            (
                "Hospitals connected",

                len(hospitals),

                "🏥"
            ),

        ]

    )


    st.markdown("---")


    tabs = st.tabs(

        [

            "🚨 Emergencies",

            "🚑 Fleet",

            "🏥 Hospitals",

            "👨‍⚕️ Doctors",

            "👥 Users",

            "🔐 Audit"

        ]

    )


    # =====================================================
    # EMERGENCIES
    # =====================================================

    with tabs[0]:

        st.subheader(
            "🚨 Emergency Operations"
        )

        st.dataframe(

            pd.DataFrame(

                [

                    {

                        "Case":
                            c.id,

                        "Patient":
                            c.patient_name,

                        "Condition":
                            c.condition,

                        "Priority":
                            c.severity,

                        "Ambulance":
                            c.ambulance_code,

                        "Hospital":
                            c.hospital_name,

                        "Doctor":
                            c.doctor_name,

                        "Bed":
                            c.bed_type,

                        "ETA":
                            c.eta_minutes,

                        "Status":
                            c.status

                    }

                    for c in cases

                ]

            ),

            use_container_width=True,

            hide_index=True

        )


    # =====================================================
    # FLEET
    # =====================================================

    with tabs[1]:

        st.subheader(
            "🚑 Ambulance & Driver Management"
        )

        st.caption(
            "Restricted operational information "
            "for authorized administrators."
        )


        ambulance_data = []


        for a in ambs:

            ambulance_data.append(

                {

                    "Ambulance No.":
                        a.code,

                    "Driver Name":
                        a.driver,

                    "Driver Phone":
                        a.driver_phone
                        or "Not available",

                    "Status":
                        a.status,

                    "Equipment":
                        a.equipment,

                    "Assigned Hospital":
                        a.hospital,

                    "Location":
                        f"{a.lat:.5f}, "
                        f"{a.lon:.5f}"

                }

            )


        ambulance_df = pd.DataFrame(
            ambulance_data
        )


        st.dataframe(

            ambulance_df,

            use_container_width=True,

            hide_index=True

        )


        st.markdown("---")


        # =================================================
        # SELECT AMBULANCE
        # =================================================

        st.subheader(
            "📋 Ambulance Details"
        )


        if ambs:

            selected_ambulance = st.selectbox(

                "Select Ambulance",

                [
                    a.code
                    for a in ambs
                ]

            )


            selected = next(

                (
                    a
                    for a in ambs
                    if a.code
                    == selected_ambulance
                ),

                None

            )


            if selected:

                col1, col2, col3, col4 = st.columns(4)


                with col1:

                    st.metric(
                        "🚑 Ambulance",
                        selected.code
                    )


                with col2:

                    st.metric(
                        "👤 Driver",
                        selected.driver
                    )


                with col3:

                    st.metric(
                        "📞 Driver Phone",
                        selected.driver_phone
                        or "N/A"
                    )


                with col4:

                    st.metric(
                        "🟢 Status",
                        selected.status
                    )


                st.markdown(
                    f"""
                    <div class="case-banner">

                      <div>

                        <b>
                          🚑 {selected.code}
                        </b>

                        <br>

                        Driver:
                        {selected.driver}

                        <br>

                        Phone:
                        {selected.driver_phone
                         or "Not available"}

                        <br>

                        Equipment:
                        {selected.equipment}

                        <br>

                        Hospital:
                        {selected.hospital}

                        <br>

                        Location:
                        {selected.lat:.5f},
                        {selected.lon:.5f}

                      </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


    # =====================================================
    # HOSPITALS
    # =====================================================

    with tabs[2]:

        st.subheader(
            "🏥 Hospital Resources"
        )

        st.dataframe(

            pd.DataFrame(

                [

                    {

                        "Hospital":
                            h.name,

                        "Emergency Beds":
                            h.emergency_beds,

                        "ICU Beds":
                            h.icu_beds,

                        "Ventilators":
                            h.ventilators

                    }

                    for h in hospitals

                ]

            ),

            use_container_width=True,

            hide_index=True

        )


    # =====================================================
    # DOCTORS
    # =====================================================

    with tabs[3]:

        st.subheader(
            "👨‍⚕️ Doctor Management"
        )

        st.dataframe(

            pd.DataFrame(

                [

                    {

                        "Doctor":
                            d.name,

                        "Specialty":
                            d.specialty,

                        "Hospital":
                            next(

                                (
                                    h.name
                                    for h in hospitals
                                    if h.id
                                    == d.hospital_id
                                ),

                                ""

                            ),

                        "Available":
                            d.available

                    }

                    for d in doctors

                ]

            ),

            use_container_width=True,

            hide_index=True

        )


    # =====================================================
    # USERS
    # =====================================================

    with tabs[4]:

        st.subheader(
            "👥 User Management"
        )

        st.dataframe(

            pd.DataFrame(

                [

                    {

                        "Name":
                            u.name,

                        "Username":
                            u.username,

                        "Role":
                            u.role,

                        "Phone":
                            u.phone,

                        "Verified":
                            u.verified

                    }

                    for u in users

                ]

            ),

            use_container_width=True,

            hide_index=True

        )


    # =====================================================
    # AUDIT
    # =====================================================

    with tabs[5]:

        st.info(

            "Production version should persist "
            "immutable audit events for login, "
            "patient access, resource changes "
            "and emergency decisions."

        )


    db.close()


# =========================================================
# RESTRICTED PORTALS
# =========================================================

def restricted_portal(
    user
):

    role = user["role"]


    header(
        f"{role} Portal",
        f"Signed in as {user['name']}"
    )


    db = SessionLocal()


    cases = (

        db.query(EmergencyCase)

        .order_by(
            EmergencyCase.id.desc()
        )

        .limit(20)

        .all()

    )


    # =====================================================
    # DOCTOR
    # =====================================================

    if role == "Doctor":

        metric_cards(

            [

                (
                    "Incoming cases",
                    len(cases),
                    "🚨"
                ),

                (
                    "My specialty",
                    user["specialty"]
                    or "Emergency",
                    "🩺"
                ),

                (
                    "Hospital readiness",
                    "ON",
                    "🏥"
                )

            ]

        )


        st.subheader(
            "Incoming emergency cases"
        )


        st.dataframe(

            pd.DataFrame(

                [

                    {

                        "Case":
                            c.id,

                        "Condition":
                            c.condition,

                        "Priority":
                            c.severity,

                        "Hospital":
                            c.hospital_name,

                        "Ambulance":
                            c.ambulance_code,

                        "ETA":
                            f"{c.eta_minutes} min",

                        "Bed":
                            c.bed_type

                    }

                    for c in cases

                ]

            ),

            use_container_width=True,

            hide_index=True

        )


    # =====================================================
    # DISPATCHER
    # =====================================================

    elif role == "Dispatcher":

        metric_cards(

            [

                (
                    "Live cases",
                    len(cases),
                    "🚨"
                ),

                (
                    "Dispatch mode",
                    "ONLINE",
                    "📡"
                ),

                (
                    "Response focus",
                    "FAST",
                    "⚡"
                )

            ]

        )


        st.subheader(
            "Dispatch board"
        )


        st.dataframe(

            pd.DataFrame(

                [

                    {

                        "Case":
                            c.id,

                        "Priority":
                            c.severity,

                        "Ambulance":
                            c.ambulance_code,

                        "Destination":
                            c.hospital_name,

                        "ETA":
                            f"{c.eta_minutes} min",

                        "Status":
                            c.status

                    }

                    for c in cases

                ]

            ),

            use_container_width=True,

            hide_index=True

        )


    # =====================================================
    # AMBULANCE DRIVER
    # =====================================================

    elif role == "Ambulance":

        metric_cards(

            [

                (
                    "Assigned trips",
                    len(cases),
                    "🚑"
                ),

                (
                    "Driver",
                    user["name"],
                    "👤"
                ),

                (
                    "Status",
                    "ONLINE",
                    "🟢"
                )

            ]

        )


        st.subheader(
            "Trip information"
        )


        st.dataframe(

            pd.DataFrame(

                [

                    {

                        "Case":
                            c.id,

                        "Patient":
                            c.patient_name,

                        "Pickup":
                            (
                                f"{c.pickup_lat:.4f}, "
                                f"{c.pickup_lon:.4f}"
                            ),

                        "Hospital":
                            c.hospital_name,

                        "ETA":
                            f"{c.eta_minutes} min",

                        "Status":
                            c.status

                    }

                    for c in cases

                ]

            ),

            use_container_width=True,

            hide_index=True

        )


    # =====================================================
    # HOSPITAL
    # =====================================================

    elif role == "Hospital":

        hospitals = (
            db.query(Hospital)
            .all()
        )


        h = hospitals[0]


        metric_cards(

            [

                (
                    "Emergency beds",
                    h.emergency_beds,
                    "🛏️"
                ),

                (
                    "ICU",
                    h.icu_beds,
                    "🏥"
                ),

                (
                    "Ventilators",
                    h.ventilators,
                    "🫁"
                ),

                (
                    "Incoming",
                    len(cases),
                    "🚑"
                )

            ]

        )


        st.subheader(
            "Pre-arrival coordination"
        )


        st.dataframe(

            pd.DataFrame(

                [

                    {

                        "Case":
                            c.id,

                        "Condition":
                            c.condition,

                        "Priority":
                            c.severity,

                        "Ambulance":
                            c.ambulance_code,

                        "Doctor":
                            c.doctor_name,

                        "Bed":
                            c.bed_type,

                        "ETA":
                            f"{c.eta_minutes} min"

                    }

                    for c in cases

                ]

            ),

            use_container_width=True,

            hide_index=True

        )


    db.close()


# =========================================================
# MAIN APPLICATION
# =========================================================

if "user" not in st.session_state:

    login()

else:

    user = st.session_state.user


    # =====================================================
    # SIDEBAR
    # =====================================================

    with st.sidebar:

        st.markdown(
            "### 🚑 AEGISCARE"
        )

        st.caption(
            f"{user['name']} • "
            f"{user['role']}"
        )

        st.markdown("---")


        if user["role"] == "Admin":

            st.success(
                "🔐 Full administrative access"
            )

        elif user["role"] == "Patient":

            st.info(
                "👤 Patient access"
            )

        else:

            st.info(
                f"🔒 {user['role']} access"
            )


        if st.button(
            "Logout",
            use_container_width=True
        ):

            st.session_state.clear()

            st.rerun()


    # =====================================================
    # ROUTING
    # =====================================================

    if user["role"] == "Patient":

        patient_portal(user)

    elif user["role"] == "Admin":

        admin_portal()

    else:

        restricted_portal(user)