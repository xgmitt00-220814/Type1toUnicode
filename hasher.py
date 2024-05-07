import hashlib
import os
import json
import subprocess
from argparse import ArgumentParser

class Hash:
    @classmethod
    def find_hash_in_json(cls, json_file_path, dir_path):
        try:
            # Načítanie hashov z JSON súboru do slovníka
            with open(json_file_path, 'r') as file:
                data = json.load(file)
            # Získanie všetkých hashov z JSON súboru
            json_hashes = set()
            def collect_hashes(year_dict):
                for month, value in year_dict.items():
                    if isinstance(value, dict):
                        collect_hashes(value)  # Rekurzívne prehľadávanie pre vnorené slovníky
                    else:
                        json_hashes.add(value)

            for magazine in data["magazines"].values():
                collect_hashes(magazine)

            # Prechádzanie všetkých .pdf súborov v zadanom adresári a výpočet ich hashov
            for filename in os.listdir(dir_path):
                if filename.endswith(".pdf"):
                    file_path = os.path.join(dir_path, filename)
                    with open(file_path, 'rb') as file:
                        file_content = file.read()
                        file_hash = hashlib.sha256(file_content).hexdigest()
                        # Porovnanie hashu súboru s hashmi z JSON súboru
                        if file_hash in json_hashes:
                            subprocess.run(['insert_table.exe', '-p', file_path, '-f', 'to_unicode.json'], check=True)
                        else:
                            print(f"Hash nenájdený")

        except FileNotFoundError:
            print("Súbor nebol nájdený.")
        except json.JSONDecodeError:
            print("Súbor nie je platný JSON.")
        except subprocess.CalledProcessError:
            print("Chyba pri spúšťaní insert_table.exe.")
        except Exception as e:
            print(f"Vyskytla sa chyba: {e}")

def main():
    argparser = ArgumentParser()
    argparser.add_argument('-d', '--pdf_dir', type=str, required=True)
    args = argparser.parse_args()
    Hash.find_hash_in_json('magazine_hash.json', args.pdf_dir)

if __name__ == '__main__':
    main()