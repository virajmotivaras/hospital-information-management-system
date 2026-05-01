# Hospital Desk User Manual

This manual is for hospital staff reviewing the first prototype.

## Purpose

The system is designed for a gynecology and pediatrics focused hospital. The first version focuses on reducing time at the front desk and making the doctor's consultation flow easier.

## Main Screens

### Login

Every staff member should log in with their own username and password.

The first roles are:

- `Reception`: check in patients, search patients, and schedule appointments.
- `Doctor`: view patients, consult the queue, write prescriptions, and print prescriptions.
- `Admin`: manage users, hospital profile, master data, and backups.

Admin users also need Django `staff status` enabled so they can enter the admin panel.

### Patient Desk

Use this screen when a patient arrives.

Required:

- patient name
- department

Optional but useful:

- mobile number
- age
- gender
- parent or guardian name for pediatric patients
- reason for visit
- temperature, weight, and blood pressure

The goal is to let staff check in the patient quickly while continuing to speak with them. More details can be added later.

### Waiting Queue

After check-in, the patient appears in the waiting queue.

The queue shows:

- patient name
- new or repeat visit
- department
- age and mobile number when available
- reason for visit

Click `Consult` to select the patient for prescription.

### Patients

Use this screen to search registered patients by:

- name
- mobile number
- guardian name

This helps staff confirm whether the patient is new or returning.

### Appointments

Use this screen to schedule future visits.

The appointment form can also create the patient record if the patient is not already registered.

### Prescription

The doctor can select a patient from the consultation queue, enter:

- doctor name
- diagnosis
- medicines
- advice
- follow-up date

After saving, the system opens a printable prescription page.

## New Patient Flow

1. Open `Patient Desk`.
2. Enter the patient's name.
3. Select `Gynecology` or `Pediatrics`.
4. Add mobile, age, guardian, or vitals if quickly available.
5. Click `Check In Patient`.
6. Patient appears in the waiting queue as `NEW`.

## Repeat Patient Flow

1. Open `Patient Desk`.
2. Enter the patient name and mobile number.
3. Click `Check In Patient`.
4. If the mobile number exists, the system reuses the patient record.
5. Patient appears in the waiting queue as `REPEAT`.

If mobile is not available, entering the same patient name and guardian name can also help identify repeat pediatric patients.

## Prescription Printing

1. Open `Prescription`.
2. Select a patient from the consultation queue.
3. Enter diagnosis and medicine details.
4. Click `Save and Print Prescription`.
5. A print-friendly prescription opens in a new tab.
6. Click `Print`.

## Hospital Name, Logo, and Prescription Header

Admin workflow:

1. Log in as an Admin user.
2. Open `/admin/`.
3. Open `Hospital profile`.
4. Edit:
   - hospital name
   - tagline
   - logo
   - address
   - phone number
5. Save.

The hospital name and logo appear in the application sidebar and on printed prescriptions.

There should normally be only one hospital profile record.

## Backup Folder

You are not overthinking this. For a local server, backups are important.

Admin workflow:

1. Create an empty folder on the server machine, for example `D:\HospitalBackups`.
2. Log in as Admin.
3. Open `/admin/`.
4. Open `Hospital profile`.
5. Enter the backup folder path.
6. Save.
7. Select the hospital profile row.
8. Choose `Create database backup now`.

The system copies the current SQLite database file into that folder with a timestamped name.

Important notes:

- This is a useful fallback for the prototype and early local trials.
- For a serious multi-user installation, PostgreSQL plus scheduled automated backups is recommended.
- The backup folder should ideally be on a different drive or synced to a safe location.
- Staff should test restoring from backup before relying on it.

## Review Questions For Hospital Users

- Is the quick check-in form short enough?
- Are any fields missing for gynecology?
- Are any fields missing for pediatrics?
- Should the prescription include hospital address, registration number, or logo?
- Is the waiting queue clear enough for reception and doctors?
- Are Reception, Doctor, and Admin permissions correct?
- Is the backup workflow understandable for the Admin user?
- Which existing system features should be added next?
- Which existing system features should be deliberately left out?
