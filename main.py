from clinic import Clinic

class ClinicCLI:
    def __init__(self):
        self.clinic = Clinic()

    @staticmethod
    def get_text(prompt):
        while True:
            value = input(prompt).strip()

            if value:
                return value

            print("This field cannot be empty.")

    @staticmethod
    def get_integer(prompt, minimum=None, maximum=None):
        while True:
            try:
                value = int(input(prompt))

                if minimum is not None and value < minimum:
                    print(f"Enter a number of at least {minimum}.")
                    continue

                if maximum is not None and value > maximum:
                    print(f"Enter a number no greater than {maximum}.")
                    continue

                return value

            except ValueError:
                print("Please enter a valid whole number.")

    def show_patients(self):
        if not self.clinic.patients:
            print("No patients registered.")
            return

        for patient in self.clinic.patients.values():
            print(patient)

    def show_clinicians(self):
        if not self.clinic.clinicians:
            print("No clinicians registered.")
            return

        for clinician in self.clinic.clinicians.values():
            print(clinician)

    def patient_menu(self):
        while True:
            print("\n--- PATIENT MANAGEMENT ---")
            print("1. Register patient")
            print("2. View all patients")
            print("3. Search patient")
            print("4. Update patient")
            print("0. Back")

            choice = input("Choose an option: ").strip()

            try:
                if choice == "1":
                    name = self.get_text("Patient name: ")
                    phone = self.get_text("Phone number: ")
                    age = self.get_integer("Age: ", 0, 130)
                    gender = self.get_text("Gender: ")

                    patient = self.clinic.register_patient(
                        name, phone, age, gender
                    )

                    print("Patient registered successfully.")
                    print(patient)

                elif choice == "2":
                    self.show_patients()

                elif choice == "3":
                    term = self.get_text("Search by ID, name or phone: ")
                    results = self.clinic.search_patients(term)

                    if results:
                        for patient in results:
                            print(patient)
                    else:
                        print("No matching patients found.")

                elif choice == "4":
                    patient_id = self.get_text("Patient ID: ")
                    patient = self.clinic.get_patient(patient_id)

                    print("Leave a field blank to keep its current value.")

                    name = input(f"Name ({patient.name}): ").strip()
                    phone = input(f"Phone ({patient.phone}): ").strip()
                    age_text = input(f"Age ({patient.age}): ").strip()
                    gender = input(f"Gender ({patient.gender}): ").strip()

                    self.clinic.update_patient(
                        patient_id,
                        name=name or None,
                        phone=phone or None,
                        age=int(age_text) if age_text else None,
                        gender=gender or None
                    )

                    print("Patient updated successfully.")

                elif choice == "0":
                    break

                else:
                    print("Invalid option.")

            except (ValueError, OSError) as error:
                print("Error:", error)

    def clinician_menu(self):
        while True:
            print("\n--- CLINICIAN MANAGEMENT ---")
            print("1. Register clinician")
            print("2. View all clinicians")
            print("3. Search clinician")
            print("4. Update clinician")
            print("0. Back")

            choice = input("Choose an option: ").strip()

            try:
                if choice == "1":
                    name = self.get_text("Clinician name: ")
                    phone = self.get_text("Phone number: ")
                    specialization = self.get_text("Specialization: ")

                    clinician = self.clinic.register_clinician(
                        name, phone, specialization
                    )

                    print("Clinician registered successfully.")
                    print(clinician)

                elif choice == "2":
                    self.show_clinicians()

                elif choice == "3":
                    term = self.get_text(
                        "Search by ID, name or specialization: "
                    )
                    results = self.clinic.search_clinicians(term)

                    if results:
                        for clinician in results:
                            print(clinician)
                    else:
                        print("No matching clinicians found.")

                elif choice == "4":
                    clinician_id = self.get_text("Clinician ID: ")
                    clinician = self.clinic.get_clinician(clinician_id)

                    print("Leave a field blank to keep its current value.")

                    name = input(f"Name ({clinician.name}): ").strip()
                    phone = input(f"Phone ({clinician.phone}): ").strip()
                    specialization = input(
                        f"Specialization ({clinician.specialization}): "
                    ).strip()

                    self.clinic.update_clinician(
                        clinician_id,
                        name=name or None,
                        phone=phone or None,
                        specialization=specialization or None
                    )

                    print("Clinician updated successfully.")

                elif choice == "0":
                    break

                else:
                    print("Invalid option.")

            except (ValueError, OSError) as error:
                print("Error:", error)

    def appointment_menu(self):
        manager = self.clinic.appointment_manager

        while True:
            print("\n--- APPOINTMENT MANAGEMENT ---")
            print("1. Schedule appointment")
            print("2. View all appointments")
            print("3. Reschedule appointment")
            print("4. Cancel appointment")
            print("5. Mark appointment completed")
            print("6. Search appointments")
            print("0. Back")

            choice = input("Choose an option: ").strip()

            try:
                if choice == "1":
                    self.show_patients()
                    patient_id = self.get_text("Patient ID: ")

                    self.show_clinicians()
                    clinician_id = self.get_text("Clinician ID: ")

                    appointment_date = self.get_text("Date (YYYY-MM-DD): ")
                    appointment_time = self.get_text("Time (HH:MM): ")
                    purpose = self.get_text("Purpose: ")

                    duration = self.get_integer(
                        "Duration in minutes (1-480): ",
                        1,
                        480
                    )

                    appointment = manager.schedule_appointment(
                        patient_id,
                        clinician_id,
                        appointment_date,
                        appointment_time,
                        purpose,
                        duration
                    )

                    print("Appointment scheduled successfully.")
                    print(appointment)

                elif choice == "2":
                    if manager.appointments:
                        for appointment in manager.appointments.values():
                            print(appointment)
                    else:
                        print("No appointments found.")

                elif choice == "3":
                    appointment_id = self.get_text("Appointment ID: ")
                    new_date = self.get_text("New date (YYYY-MM-DD): ")
                    new_time = self.get_text("New time (HH:MM): ")

                    appointment = manager.reschedule_appointment(
                        appointment_id,
                        new_date,
                        new_time
                    )

                    print("Appointment rescheduled.")
                    print(appointment)

                elif choice == "4":
                    appointment_id = self.get_text("Appointment ID: ")
                    manager.cancel_appointment(appointment_id)
                    print("Appointment cancelled.")

                elif choice == "5":
                    appointment_id = self.get_text("Appointment ID: ")
                    manager.complete_appointment(appointment_id)
                    print("Appointment marked as completed.")

                elif choice == "6":
                    term = self.get_text(
                        "Enter appointment ID, patient ID or purpose: "
                    )
                    results = manager.search_appointments(term)

                    if results:
                        for appointment in results:
                            print(appointment)
                    else:
                        print("No matching appointments found.")

                elif choice == "0":
                    break

                else:
                    print("Invalid option.")

            except (ValueError, OSError) as error:
                print("Error:", error)

    def report_menu(self):
        manager = self.clinic.appointment_manager

        while True:
            print("\n--- REPORTS ---")
            print("1. Patient appointment history")
            print("2. Clinician schedule")
            print("3. Appointments on a selected date")
            print("4. Daily summary")
            print("0. Back")

            choice = input("Choose an option: ").strip()

            try:
                if choice == "1":
                    patient_id = self.get_text("Patient ID: ")
                    self.clinic.get_patient(patient_id)

                    results = manager.get_patient_appointments(patient_id)

                    if results:
                        for appointment in results:
                            print(appointment)
                    else:
                        print("No appointments for this patient.")

                elif choice == "2":
                    clinician_id = self.get_text("Clinician ID: ")
                    self.clinic.get_clinician(clinician_id)

                    results = manager.get_clinician_appointments(clinician_id)

                    if results:
                        for appointment in results:
                            print(appointment)
                    else:
                        print("No appointments for this clinician.")

                elif choice == "3":
                    selected_date = self.get_text("Date (YYYY-MM-DD): ")
                    results = manager.get_appointments_by_date(selected_date)

                    if results:
                        for appointment in results:
                            print(appointment)
                    else:
                        print("No appointments on this date.")

                elif choice == "4":
                    selected_date = self.get_text("Date (YYYY-MM-DD): ")
                    report = manager.generate_daily_report(selected_date)

                    print(f"\nDaily report for {report['date']}")
                    print("Scheduled:", report["summary"]["scheduled"])
                    print("Completed:", report["summary"]["completed"])
                    print("Cancelled:", report["summary"]["cancelled"])

                    for appointment in report["appointments"]:
                        print(appointment)

                elif choice == "0":
                    break

                else:
                    print("Invalid option.")

            except (ValueError, OSError) as error:
                print("Error:", error)

    def run(self):
        print("====================================")
        print(" CLINIC APPOINTMENT MANAGEMENT SYSTEM")
        print("====================================")

        while True:
            print("\nMAIN MENU")
            print("1. Patient management")
            print("2. Clinician management")
            print("3. Appointment management")
            print("4. Reports")
            print("0. Exit")

            choice = input("Choose an option: ").strip()

            if choice == "1":
                self.patient_menu()

            elif choice == "2":
                self.clinician_menu()

            elif choice == "3":
                self.appointment_menu()

            elif choice == "4":
                self.report_menu()

            elif choice == "0":
                print("Thank you for using the clinic system.")
                break

            else:
                print("Invalid option. Try again.")

if __name__ == "__main__":
    try:
        application = ClinicCLI()
        application.run()

    except (ValueError, OSError) as error:
        print("Could not start the application:", error)
