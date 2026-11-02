# Clinic Appointment Management System

## Project Description

This is a Python command-line application designed to manage
clinic patients, clinicians and appointments.

## Features

- Register patients.
- Search and update patient records.
- Register clinicians.
- Search and update clinician records.
- Schedule appointments.
- Reschedule appointments.
- Cancel appointments.
- Mark appointments as completed.
- Prevent overlapping clinician appointments.
- Generate appointment reports.
- Save information using JSON.
- Load saved records when the application starts.

## Technologies Used

- Python 3
- Object-Oriented Programming
- JSON
- Git
- Visual Studio Code

## Project Structure

- person.py: Base Person class.
- patient.py: Patient class.
- clinician.py: Clinician class.
- appointment.py: Appointment class.
- decorators.py: Custom decorators.
- json_storage.py: JSON storage.
- appointment_manager.py: Appointment management.
- clinic.py: Main clinic operations.
- main.py: Command-line interface.

## Installation and How to Run

1. Install Python 3.10 or later if it is not already available.
2. Open the project folder in VS Code and open a terminal there.
3. Run:

   `python main.py`

   On Windows, use `py main.py` if `python` is unavailable.

The project uses only Python's standard library; no package installation is
required.

## Sample Data

The JSON files include fictional demonstration records. The scheduled sample
appointment is on 2026-12-15 at 09:00. To demonstrate conflict prevention,
try scheduling another appointment for clinician `C001` on that date at
09:15. The completed and cancelled examples are available in the daily
reports for 2026-10-15 and 2026-10-20.

The application saves changes to these same files, so back them up before
using the application for data you want to keep.

## Data Storage

The system uses three JSON files:

- patients.json
- clinicians.json
- appointments.json

Each file stores a JSON list. New or empty files are treated as having no
records, and malformed JSON is reported without replacing the original data.
The files are stored alongside the project code.

## Files

- `person.py`: shared person fields and validation.
- `patient.py`: patient details, age validation, and updates.
- `clinician.py`: clinician specialisation and updates.
- `appointment.py`: appointment fields, date/time validation, and status changes.
- `decorators.py`: operation logging and elapsed-time logging.
- `json_storage.py`: JSON load/save operations.
- `appointment_manager.py`: appointment scheduling, conflict checks, and reports.
- `clinic.py`: registration, search, updates, and loading/saving records.
- `main.py`: interactive command-line menus.
- `test_clinic.py`: workflow tests using Python's standard `unittest` module.

## Object-Oriented Programming

The system uses inheritance, encapsulation, properties,
static methods and classes.

Patient and Clinician inherit from Person.

## Custom Decorators

`log_operation` records operation start, success, and failures in `clinic.log`.
It re-raises errors so failures remain visible to the caller.

`measure_time` records how long a report operation takes without changing its
return value.

## Run the tests

Run the workflow tests with:

`python -m unittest`

On Windows, `py -m unittest` can be used instead.

The tests cover record validation and search, JSON loading and saving,
appointment conflicts and rescheduling, status changes, chronological report
ordering, and the CLI's conflict message. They use temporary JSON files so
they do not alter the demonstration records.

## Demonstration Walkthrough

1. Run `python main.py`.
2. Open patient management and view the sample patient, `P001`.
3. Open clinician management and view the sample clinician, `C001`.
4. Open reports and select 2026-12-15 to see the scheduled sample appointment.
5. Try scheduling another appointment for `C001` on 2026-12-15 at 09:15.
   The system should reject it because it overlaps the existing 09:00
   appointment.
6. Try 09:30 instead to demonstrate that appointments can be back-to-back.
7. View the daily summaries for 2026-10-15 and 2026-10-20 to see completed
   and cancelled appointment statuses.

Changes made during the walkthrough are saved to the JSON files.

## Project Management and Version Control

Use an approved project board (for example, Jira or Trello) to track work.
Suggested cards are: patient and clinician records, appointment scheduling
and conflict checks, JSON persistence, CLI and reports, and tests/documentation.
Move each card through the board as the work progresses.

Use Git feature branches and meaningful commits for the implementation and
testing work. The project directory must be initialized as a Git repository
and pushed to the hosting service required by your course if repository
evidence is part of the submission.

## Author

Add your name here.
