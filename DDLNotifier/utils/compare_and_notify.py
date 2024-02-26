import os
from datetime import datetime
from DDLNotifier.config import CONFIG
from DDLNotifier.email_sender import send_email

recipient_email = CONFIG.RECIPEINT_EMAIL

def compare_and_notify(old_data, new_data, log_path, school_name):
    with open(log_path, "a") as log_file:
        log_file.write(f"Function called at {datetime.now()}\n")

    if old_data.empty:
        print("No old data to compare with. Saving new data.")
        return

    # Check for any differences
    if not old_data.equals(new_data):
        print("Data differences detected...")

        changes_detected = []
        new_rows_detected = []
        deleted_rows_detected = []

        for index, new_row in new_data.iterrows():
            # Check if the row exists in the old data
            old_row = old_data.loc[
                old_data['Programme'] == new_row['Programme']]

            # If the row exists, check for deadline changes
            if not old_row.empty:
                if old_row['Deadline'].values[0] != new_row['Deadline']:
                    changes_detected.append({
                        'Programme': new_row['Programme'],
                        'Old Deadline': old_row['Deadline'].values[0],
                        'New Deadline': new_row['Deadline']
                    })
            else:
                # If the row does not exist in old data, it's a new addition
                new_rows_detected.append(new_row)

        # Check for deleted programmes
        for index, old_row in old_data.iterrows():
            new_row = new_data.loc[
                new_data['Programme'] == old_row['Programme']]
            if new_row.empty:
                deleted_rows_detected.append(old_row)

        # Preparing email content
        subject = f"Changes Detected in School: {school_name}'s Programmes"
        body = ""

        if changes_detected:
            body += "Deadline changes detected:\n\n"
            for change in changes_detected:
                body += (
                    f"School: {school_name}, Programme: {change['Programme']}\n"
                    f"Old Deadline: {change['Old Deadline']}\n"
                    f"New Deadline: {change['New Deadline']}\n\n")

        if new_rows_detected:
            body += "New programmes added:\n\n"
            for new_row in new_rows_detected:
                body += (
                    f"School: {school_name}, Programme: {new_row['Programme']}\n"
                    f"Deadline: {new_row['Deadline']}\n\n")

        if deleted_rows_detected:
            body += "Programmes deleted:\n\n"
            for del_row in deleted_rows_detected:
                body += f"School: {school_name}, Programme: {del_row['Programme']}\n\n"

        # Sending the email if there are any changes
        if changes_detected or new_rows_detected or deleted_rows_detected:
            send_email(subject, body, recipient_email)
            with open(log_path, "a") as log_file:
                log_file.write(f"Email sent: {subject} | {body}\n")
            print("Email notification sent for the detected changes.")
        else:
            print("No changes detected.")

    else:
        print("No changes detected in the data content.")