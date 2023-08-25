from collections import UserDict
from datetime import datetime, date
from typing import Optional, List, Union
import pickle

class Field:
    def __init__(self, value: Union[str, int, date]):
        self.set_value(value)
    
    def get_value(self) -> Union[str, int, date]:
        return self._value
    
    def set_value(self, value: Union[str, int, date]):
        self._value = value

class Name(Field):
    pass

class Phone(Field):
    def set_value(self, value: str):
        if not self.validate_phone(value):
            raise ValueError("Invalid phone number")
        self._value = value
    
    def validate_phone(self, phone: str) -> bool:        
        if not isinstance(phone, str) or not phone.isdigit():
            return False
        return True

class Birthday(Field):
    def set_value(self, value: date):
        if not self.validate_birthday(value):
            raise ValueError("Invalid birthday")
        self._value = value

    def validate_birthday(self, birthday: date) -> bool:
        try:
            formatted_birthday = birthday.strftime('%Y-%m-%d')
            datetime.strptime(formatted_birthday, '%Y-%m-%d')
        except ValueError: 
            return False
        else:            
            return True        

    def get_month(self) -> int:
        return self._value.month

    def get_day(self) -> int:
        return self._value.day

class Record:
    def __init__(self, name: str, phone: Optional[str] = None, birthday: Optional[date] = None):
        self.name = Name(name)
        self.phones: List[Phone] = []
        self.birthday = Birthday(birthday) if birthday else None

        if phone:
            self.add_phone(phone)
    
    def add_phone(self, phone: Union[str, Phone]):
        if isinstance(phone, str):
            self.phones.append(Phone(phone))
        elif isinstance(phone, Phone):
            self.phones.append(phone)
        else:
            raise ValueError("Invalid phone type")
    
    def remove_phone(self, phone: Union[str, Phone]):
        inx = self.get_index_by_phone(phone)
        if inx is None:
            raise ValueError(f"The phone not found {phone}") 
        del self.phones[inx]
        return f"The phone deleted {phone}"
    
    def get_index_by_phone(self, phone: Union[str, Phone]) -> Optional[int]:
        if isinstance(phone, Phone):
            phone = phone.get_value()
        for inx, _phone in enumerate(self.phones):
            if _phone.get_value() == phone:
                return inx
        return None

    def edit_phone(self, old_phone: Union[str, Phone], new_phone: str):
        for phone in self.phones:
            if phone.get_value() == old_phone:
                phone.set_value(new_phone)
                break
    
    def days_to_birthday(self) -> Optional[int]:
        if not self.birthday:
            return None        

        today = datetime.now().date()        
        next_birthday = datetime(today.year, self.birthday.get_month(), self.birthday.get_day()).date()
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
        
        days_remaining = (next_birthday - today).days
        return days_remaining

class AddressBook(UserDict):
    def __iter__(self):
        self._index = 0
        self._keys = list(self.data.keys())
        return self
    
    def __next__(self):
        if self._index < len(self._keys):
            record = self.data[self._keys[self._index]]
            self._index += 1
            return record
        raise StopIteration
    
    def iterator(self, page_size: int):
    
        self._index = 0
        self._keys = list(self.data.keys())
        while self._index < len(self._keys):
            yield self.data[self._keys[self._index]]
            self._index += 1
    
    def add_record(self, name: str, phones: Optional[List[str]] = None, birthday: Optional[date] = None):
        record = Record(name, birthday=birthday)
        if phones:
            for phone in phones:
                record.add_phone(phone)
        self.data[name] = record    
    
    def delete_record(self, name: str):
        del self.data[name]

    def edit_record(self, name: str, new_name: Optional[str] = None, new_phones: Optional[List[str]] = None):
        if name not in self.data:           
            return f"{name} Name not found "
        record = self.data[name]
        if new_name:
            record.name.set_value(new_name)

        if new_phones:
            record.phones = []
            for phone in new_phones:
                record.add_phone(phone)

    def find_records_by_name(self, name: str):
        results = []
        for record in self.data.values():
            if record.name.get_value() == name:
                results.append(record)
        return results

    def find_records_by_phone(self, phone: str):
        results = []
        for record in self.data.values():
            for record_phone in record.phones:
                if record_phone.get_value() == phone:
                    results.append(record)
                    break
        return results
    
    # Save Records to File
    def save_to_file(self, filename: str):
        with open(filename, "wb") as file:
            pickle.dump(self.data, file)  

    # Load Records from File
    def load_from_file(self, filename: str):
        try:
            with open(filename, "rb") as file:
                self.data = pickle.load(file)  
        except FileNotFoundError:
            print("File not found. Starting with an empty address book.")

if __name__ == "__main__":
    address_book = AddressBook()

    while True:
        print("1. Add Record")
        print("2. Delete Record")
        print("3. Edit Record")
        print("4. Find Record")
        print("5. Show Records")
        print("6. Save to File")
        print("7. Load from File")
        print("8. Exit")
        
        choice = input("Enter your choice: ")

        # Add Record
        if choice == "1":
            name = input("Enter name: ")
            phone = input("Enter phone: ")
            birthday_str = input("Enter birthday (YYYY-MM-DD): ")
            if birthday_str:
                birthday = datetime.strptime(birthday_str, "%Y-%m-%d").date()
            else:
                birthday = None
            address_book.add_record(name, [phone], birthday)

        # Delete Record
        elif choice == "2":
            name = input("Enter name to delete: ")
            if name in address_book.data:
                del address_book.data[name]
                print(f"{name} deleted from the address book.")
            else:
                print(f"{name} not found in the address book.")

        # Edit Record
        elif choice == "3":
            name = input("Enter name to edit: ")
            new_name = input("Enter new name (press Enter to keep existing): ")
            new_phone = input("Enter new phone (press Enter to keep existing): ")
            if name in address_book.data:
                address_book.edit_record(name, new_name, [new_phone] if new_phone else None)
                print(f"{name} edited in the address book.")
            else:
                print(f"{name} not found in the address book.")

        # Find Record
        elif choice == '4':
            name = input("Enter name to find: ")
            results = address_book.find_records_by_name(name)    
            if not results:
                   print(f"No records found for name: {name}")
            else:
                for result in results:
                    print(f"Name: {result.name.get_value()}")
                    print("Phones:", ', '.join([phone.get_value() for phone in result.phones]))
                    print("Birthday:", result.birthday.get_value() if result.birthday else "N/A")
                    print("Days to Birthday:", result.days_to_birthday() if result.birthday else "N/A")
                    print()

        # Show Records
        elif choice == '5':
            page_size = int(input("Enter page size: "))
            record_iterator = address_book.iterator(page_size)

            page_number = 1
            while True:
                print(f"Page {page_number}:")
                try:
                    record = next(record_iterator)
                    print(f"Name: {record.name.get_value()}")
                    print("Phones:", ', '.join([phone.get_value() for phone in record.phones]))
                    print("Birthday:", record.birthday.get_value() if record.birthday else "N/A")
                    print("Days to Birthday:", record.days_to_birthday() if record.birthday else "N/A")
                    print()
                    page_number += 1
                except StopIteration:
                    break
        # Save Records to File
        if choice == "6":
            filename = input("Enter filename to save: ")
            address_book.save_to_file(filename)
            print("Address book saved to file.")

        # Load Records from File
        elif choice == "7":
            filename = input("Enter filename to load: ")
            address_book.load_from_file(filename)
            print("Address book loaded from file.")

        elif choice == "8":
            print("Goodbye!")
            break

    