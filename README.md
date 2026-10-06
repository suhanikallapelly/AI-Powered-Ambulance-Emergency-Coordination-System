# AegisCare — AI Emergency Response & Hospital Coordination

A professional Streamlit MVP for emergency ambulance-to-hospital coordination.

## Core flow
Patient login → Emergency request → nearest suitable ambulance → condition-based hospital matching → doctor availability → emergency/ICU bed check → pre-arrival coordination.

## Demo accounts
- Admin: `admin` / `admin123`
- Doctor: `doctor1` / `doctor123`
- Dispatcher: `dispatcher1` / `dispatch123`
- Ambulance: `driver1` / `driver123`
- Hospital: `hospital1` / `hospital123`

Patients can register normally.

## Run
```cmd
py -3.11 -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

This is a prototype. For real hospital deployment, add production authentication/MFA, HTTPS, encrypted secrets, a production database, immutable audit logging, consent/privacy controls, backups, monitoring, and required healthcare/legal compliance.
