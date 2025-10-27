import csv
import os
import re
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

    def inhalt(self):
        with pd.option_context('display.max_columns', None,
                               'display.expand_frame_repr', False,
                               'display.max_colwidth', None,
                               'display.float_format', lambda x: '{:.2f}'.format(x)
                if isinstance(x, (float, int)) else str(x)):
            print(f"Anzahl der geladenen Zeilen: {len(self.df)}\n")
            print("\nErste 5 Zeilen der Tabelle:")
            print(self.df.head())

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
            # Anzeigeoptionen setzen
            # Alle Anzeigeoptionen in einem Dictionary
            self.inhalt()
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
            return False

    def process_verwendungszweck(self):
        if self.df is not None:
            print("\nTokenisiere Verwendungszwecke:\n")
            def tokenize_text(text):
                if not isinstance(text, str):
                    return []
                # Normalisiere Klassennamen (z.B. "4.c" zu "4c")
                text = re.sub(r'(\d+)\.([a-zA-Z])', r'\1\2', text)

                # Erst nach Klassenkürzel suchen
                tokens = []
                parts = text.split()
                for part in parts:
                    # Wenn alle Buchstaben groß sind, als eigenes Token behalten
                    if part.isalpha() and part.isupper():
                        tokens.append(part)
                        continue
            
                    # Finde Klassenkürzel (z.B. "4c")
                    class_match = re.match(r'^(\d+[a-zA-Z])(.*)', part)
                    if class_match:
                        class_token, remaining = class_match.groups()
                        tokens.append(class_token)
                        if remaining:
                            # Verarbeite den Rest des Strings
                            current_word = ''
                            for char in remaining:
                                if char.isupper() and current_word:
                                    tokens.append(current_word)
                                    current_word = char
                                else:
                                    current_word += char
                            if current_word:
                                tokens.append(current_word)
                    else:
                        # Wenn kein Klassenkürzel gefunden wurde
                        current_word = ''
                        for char in part:
                            if char.isupper() and current_word:
                                tokens.append(current_word)
                                current_word = char
                            else:
                                current_word += char
                        if current_word:
                            tokens.append(current_word)

                # Dann nach Separatoren trennen
                separators = ['.', ' ', ':', ',', ';', '_', '-', '(', ')']
                final_tokens = []
                for token in tokens:
                    # Wenn Token komplett in Großbuchstaben ist, nicht weiter trennen
                    if token.isalpha() and token.isupper():
                        final_tokens.append(token)
                        continue
            
                    for sep in separators:
                        token = ' '.join(t.strip() for t in token.split(sep))
                    final_tokens.extend(token.split())

                # Bereinigung: Leere Strings und Zahlen entfernen
                # Großbuchstaben-Tokens bleiben erhalten, Rest wird kleingeschrieben
                cleaned_tokens = []
                for token in final_tokens:
                    token = token.strip()
                    # Wenn Token komplett in Großbuchstaben ist, beibehalten
                    if token.isalpha() and token.isupper():
                        if token and not token.replace('.', '').isdigit() and token != 'SPENDENLAUF':
                            cleaned_tokens.append(token)
                    else:
                        # Ansonsten zu Kleinbuchstaben konvertieren
                        token = token.lower()
                        if token and not token.replace('.', '').isdigit() and token != 'spendenlauf':
                            cleaned_tokens.append(token)

                return list(set(cleaned_tokens))  # Duplikate entfernen

            # Neue Spalte für die Token-Listen erstellen
            self.df['verwendungszweck_tokens'] = self.df['Verwendungszweck'].apply(tokenize_text)
            self.df['beguenstigter_tokens'] = self.df['Beguenstigter/Zahlungspflichtiger'].apply(tokenize_text)

            # Beispielausgabe der ersten Einträge

            # for idx, row in self.df.iterrows():
            #     print(f"\nOriginal: {row['Verwendungszweck']}")
            #     print(f"Tokens: {row['verwendungszweck_tokens']}")

            return True
        else:
            print("Keine Daten geladen.")
            return False

    def save_to_sql_format(self, output_path=None):
        """
        Speichert die verarbeiteten Daten in einem SQL-freundlichen CSV-Format.
        
        Args:
            output_path (str, optional): Zielverzeichnis für die Ausgabedatei.
                                       Wenn None, wird das Verzeichnis der Eingabedatei verwendet.
        
        Returns:
            str: Pfad zur erstellten Datei oder None bei Fehler
        """
        if self.df is None:
            print("Keine Daten zum Speichern vorhanden.")
            return None
            
        try:
            # Erstelle einen neuen DataFrame für die SQL-freundliche Ausgabe
            sql_ready_data = []
            
            # Verarbeite jede Zeile
            for idx, row in self.df.iterrows():
                betrag = row['Betrag']
                original_verwendungszweck = row['Verwendungszweck']
                tokens = row['verwendungszweck_tokens']
                beguenstigter = row['Beguenstigter/Zahlungspflichtiger']
                
                # Extrahiere Klasse (wenn vorhanden)
                klasse = next((token for token in tokens if re.match(r'^\d+[a-zA-Z]$', token)), None)
                
                # Erstelle einen Datensatz pro Zeile
                sql_ready_data.append({
                    'ID': idx + 1,
                    'Klasse': klasse if klasse else '',
                    'Original_Verwendungszweck': original_verwendungszweck,
                    'Tokens': ', '.join(sorted(tokens)),
                    'Beguenstigter': beguenstigter,
                    'Betrag': betrag
                })
            
            # Erstelle neuen DataFrame
            sql_df = pd.DataFrame(sql_ready_data)
            
            # Bestimme den Ausgabepfad
            if output_path is None:
                base_path = os.path.splitext(self.file_path)[0]
            else:
                base_name = os.path.basename(os.path.splitext(self.file_path)[0])
                base_path = os.path.join(output_path, base_name)
                
            sql_ready_path = f"{base_path}_SQL_Ready.csv"
            index = 1
            while os.path.exists(sql_ready_path):
                sql_ready_path = f"{base_path}_SQL_Ready_{index}.csv"
                index += 1
            
            # Speichere mit angepassten Einstellungen
            sql_df.to_csv(sql_ready_path, 
                         index=False,
                         sep=';',
                         encoding='utf-8',
                         quoting=csv.QUOTE_ALL)
            
            print(f"\nSQL-freundliche Datei wurde erstellt: {sql_ready_path}")
            print("\nErste Zeilen der neuen Datei:")
            print(sql_df.head())
            return sql_ready_path
            
        except Exception as e:
            print(f"Fehler beim Speichern der SQL-freundlichen Datei: {e}")
            return None

    def sortierung(self):
        """
        Veraltete Methode - bitte save_to_sql_format() verwenden
        """
        print("Warnung: Diese Methode ist veraltet. Bitte verwenden Sie save_to_sql_format().")
        return self.save_to_sql_format()




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
        # print(f"Start load_data mit self.files: {self.files}")  # Debug-Ausgabe

        if self.files:
            self.pfad = os.path.dirname(self.files[0])
            # print(f"Pfad: {self.pfad}")  # Debug-Ausgabe

            files_to_process.extend([f for f in self.files if isinstance(f, str) and f.lower().endswith('.csv')])
            # print(f"files_to_process nach extend: {files_to_process}")  # Debug-Ausgabe
        else:
            raise ValueError("Es wurde weder ein gültiges Verzeichnis angegeben noch wurden Dateien ausgewählt.")

        # print(f"Anzahl der zu verarbeitenden Dateien: {len(files_to_process)}")  # Debug-Ausgabe

        self.files = []
        for file_path in files_to_process:
            # print(f"\nVerarbeite Datei: {file_path}")
            csv_file_obj = CSVFile(file_path)
            # csv_file_obj.preview_columns()
            csv_file_obj.load_and_analyse()
            csv_file_obj.show_columns()
            csv_file_obj.process_verwendungszweck()
            csv_file_obj.show_columns()
            csv_file_obj.inhalt()
            sql_file_path = csv_file_obj.save_to_sql_format(self.pfad)
            if sql_file_path:
                print(f"SQL-Datei erfolgreich gespeichert unter: {sql_file_path}")
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
