import csv
import dataclasses
import io
from archilog.models import create_entry, get_all_entries, Entry

def export_to_csv():
    file_stream = io.StringIO()
    csv_writer = csv.writer(file_stream)

    # Write the header
    csv_writer.writerow(["ID", "Category", "Name", "Amount"])

    # Write the data rows
    for entry in get_all_entries():
        # Convert the Entry object to a list of its attributes
        csv_writer.writerow([entry.id, entry.category, entry.name, entry.amount])

    # Return the file stream
    return file_stream




def import_from_csv(csv_file):
    # Use io.StringIO to handle the in-memory file (which is a file-like object)
    file_stream = io.StringIO(csv_file.read().decode('utf-8'))
    csv_reader = csv.DictReader(file_stream, fieldnames=['name', 'amount', 'category'])

    # Skip the header row (if present)
    next(csv_reader, None)

    for row in csv_reader:
        # Handle missing or empty values gracefully by providing default values
        name = row.get("name", "Unknown")
        amount = row.get("amount", "0")
        category = row.get("category", "Aucune catégorie")

        # Make sure amount can be converted to float
        try:
            amount = float(amount)
        except ValueError:
            print(f"Invalid amount '{amount}' in row {row}. Setting amount to 0.")
            amount = 0.0

        # Create an entry with the available data
        create_entry(
            name=name,
            amount=amount,
            category=category
        )
