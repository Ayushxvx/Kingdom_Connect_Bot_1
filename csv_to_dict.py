import csv

def csv_to_dict(name="commandments.csv"):
    with open(name,encoding='utf-8') as f:
        dict_reader = csv.DictReader(f)
        my_dict = {}
        for row in dict_reader:
            ref = row['reference_id'].strip()
            verse = row['scripture_english'].strip()
            my_dict[ref] = verse
    
        return my_dict