import csv
from dataclasses import dataclass

@dataclass
class Person:
    first_name: str
    last_name: str
    email: str
    age: int

def load_people(path):
    with open(path, newline="", encoding="utf-8") as f:
        return [
            Person(**{**row, "age": int(row["age"])})
            for row in csv.DictReader(f)
        ]

if __name__ == "__main__":
    people = load_people("people.csv")
    for person in people:
        print(person)

