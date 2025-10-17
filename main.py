import os
import pandas as pd
from pprint import pprint
from tkinter.filedialog import askdirectory, askopenfilenames
from tkinter import Tk

def get_unique_file_name(self):
    """
    Überprüft, ob eine Datei bereits unter dem angegebenen Pfad existiert.
    Falls ja, wird eine neue Datei mit einem Index erstellt.
    Returns:
    str: Ein eindeutiger Dateiname.
    """

    diagram_string = os.path.join(self.pfad, self.diagram_name)
    if not os.path.exists(diagram_string):
        return diagram_string  # Wenn die Datei nicht existiert, verwendest du den ursprünglichen Pfad.

    base, extension = os.path.splitext(diagram_string)  # Trennt den Dateinamen von der Extension.
    index = 1

    new_file_path = f"{base}_{index}{extension}"
    while os.path.exists(new_file_path):
        index += 1
        new_file_path = f"{base}_{index}{extension}"

    return new_file_path

def select_file():
    """
    Öffnet ein Dialogfenster, um eine Datei auszuwählen.
    """
    Tk().withdraw()
    files = askopenfilenames(
        title="Wählen Sie Dateien aus",
        filetypes=[("CSV-Dateien", "*.csv"), ("Alle Dateien", "*.*")]
    )
    if not files:
        print("Keine Datei ausgewählt.")
    else:
        print(f"Ausgewählte Datei: {files}")
    return files

class CSVFile:
    def __init__(self, file_path):
        self.df = None
        self.file_path = file_path
        self.betrag = None
        self.spender = None
        self.zweck = None
        self.klasse = None

    def preview_columns(self):
        # Liest nur die Header-Zeile ein
        headers = pd.read_csv(self.file_path, nrows=0, sep=';', encoding='latin1')
        print("Verfügbare Spalten in der CSV-Datei:")
        for col in headers.columns:
            print(f"- {col}")

    def load_and_analyse(self):
        try:
            columns_to_keep = ['Verwendungszweck', 'Beguenstigter/Zahlungspflichtiger', 'Betrag']
            print(f"Versuche Datei zu laden: {self.file_path}")
            self.df = pd.read_csv(self.file_path, usecols=columns_to_keep, sep=';', encoding='latin1')
            print(f"Anzahl der geladenen Zeilen: {len(self.df)}")
            print("\nErste 5 Zeilen der Tabelle:")
            print(self.df.head())
        except Exception as e:
            print(f"Fehler beim Laden der Datei: {e}")

    # Spalten einer CSV-Datei anzeigen
    def show_columns(self):
        if self.df is not None:
            print("Verfügbare Spalten:")
            for col in self.df.columns:
                print(f"- {col}")
        else:
            print("Keine Daten geladen.")

class CSVAnalyser:
    def __init__(self, folder_path=None, select_file=None ):
        self.files = select_file if select_file else []

    def load_data(self):
        """
        Processes and loads CSV files from the provided file paths. The method checks the given
        file paths for valid CSV files, initializes `CSVFile` objects for each valid file, and
        executes operations to preview, analyze, and load their content. If no valid file paths
        are supplied, an error is raised.

        :raises ValueError: Raised when neither a valid directory is given nor files are
            selected.

        :return: None
        """
        files_to_process = []
        print(f"Start load_data mit self.files: {self.files}")  # Debug-Ausgabe

        if self.files:
            self.pfad = os.path.dirname(self.files[0])
            print(f"Pfad: {self.pfad}")  # Debug-Ausgabe

            files_to_process.extend([f for f in self.files if isinstance(f, str) and f.lower().endswith('.csv')])
            print(f"files_to_process nach extend: {files_to_process}")  # Debug-Ausgabe
        else:
            raise ValueError("Es wurde weder ein gültiges Verzeichnis angegeben noch wurden Dateien ausgewählt.")

        print(f"Anzahl der zu verarbeitenden Dateien: {len(files_to_process)}")  # Debug-Ausgabe

        self.files = []
        for file_path in files_to_process:
            print(f"\nVerarbeite Datei: {file_path}")
            csv_file_obj = CSVFile(file_path)
            csv_file_obj.preview_columns()
            csv_file_obj.load_and_analyse()
            csv_file_obj.show_columns()
            self.files.append(csv_file_obj)


def main():
    def einzeldateien():
        files = select_file()
        folder_path = None
        return folder_path, files

    folder_path, files = einzeldateien()
    datenpaket = CSVAnalyser(folder_path, files)
    datenpaket.load_data()

if __name__ == '__main__':
    main()
