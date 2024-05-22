from decorators import input_error
from collections import UserDict
from datetime import datetime, timedelta
import pickle

# Classes for this app
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        
    def __str__(self):
        return self.value.strftime("%d.%m.%Y")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        phone = Phone(phone_number)
        if phone not in self.phones:
            self.phones.append(phone)
        else:
            raise ValueError(f"Phone number {phone_number} already exists.")

    def remove_phone(self, phone):
        phone = Phone(phone)
        for user_phone in self.phones:
            if user_phone.value == phone.value:
                self.phones.remove(user_phone)
                break

    def edit_phone(self, old_phone, new_phone):
        phone = self.find_phone(old_phone)
        if phone:
            self.remove_phone(old_phone)
            self.add_phone(new_phone)
        else:
            raise ValueError("Phone number not found")
        
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)
    
    def find_phone(self, phone_number):
        for phone in self.phones:
            if str(phone) == phone_number:
                return phone
        return None

    def __str__(self):
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name}, phones: {'; '.join(p.value for p in self.phones)}{birthday_str}"

class AddressBook(UserDict):
    def __init__(self):
        super().__init__()

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def adjust_for_weekend(self, date_obj):
        if date_obj.weekday() == 5:  # Saturday
            return date_obj + timedelta(days=2)
        elif date_obj.weekday() == 6:  # Sunday
            return date_obj + timedelta(days=1)
        return date_obj

    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = datetime.today()
        next_week = today + timedelta(days=days)

        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year)
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)
                birthday_this_year = self.adjust_for_weekend(birthday_this_year)

                if today <= birthday_this_year <= next_week:
                    upcoming_birthdays.append((record, birthday_this_year))

        return upcoming_birthdays


# Add contact function. Accepts 2 argument (name of the user and phone number) and ignores everything else
@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


# Change number function. Accepts 3 args (contact name, old phone and new phone)
@input_error
def change_number(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return 'Contact has been updated.'
    return 'No matches found. Contact not updated.'
    
# Function that prints requested phone number
@input_error
def show_phone(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record:
        return f"{name}'s phone number is: {'; '.join(str(phone) for phone in record.phones)}"
    return 'Contact not found.'

# Function that add birthday date to existing contact
@input_error
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday for {name} added as {birthday}."
    return 'Contact not found.'

# Show birthday function
@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record:
        if record.birthday:
            return f"{name}'s birthday is on {record.birthday}."
        return f"{name} does not have a birthday set."
    return 'Contact not found.'

# Birthdays function that returns all upcoming birthdays (next 7 days from now). Data is taken from AddressBook class method
@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if upcoming:
        return 'Upcoming birthdays:\n' + '\n'.join(f"{record.name}: {date.strftime('%d.%m.%Y')}" for record, date in upcoming)
    return 'No upcoming birthdays in the next week.'


# Function that contains main commands, greeting, exit logic, addressbook save and load logic, response.
def main():
    #Search for existing addressbook file. In case if not found - create new
    def load_data(filename="addressbook.pkl"):
        try:
            with open(filename, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return AddressBook()
        
    book = load_data()
    print('Welcome to the assistant bot!')
    while True:
        user_input = input('Enter a command: ')
        # Removes extra spaces from input and makes all in lower case
        command, *args = user_input.split()
        command = command.strip().lower()

        if command in ['close', 'exit']:
            #call to addressbook save function
            save_data(book)
            print('Good bye')
            break
        elif command == 'hello':
            print('How can I help you?')
        elif command == 'add':
            print(add_contact(args, book))
        elif command == 'change':
            print(change_number(args, book))
        elif command == 'phone':
            print(show_phone(args, book))
        elif command == 'add-birthday':
            print(add_birthday(args, book))
        elif command == 'show-birthday':
            print(show_birthday(args, book))
        elif command == 'birthdays':
            print(birthdays(args, book))
        elif command == 'all':
            for name, record in book.items():
                print(record)
        else:
            print('Invalid command')
#Function for data save in to addressbook file
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

if __name__ == '__main__':
    main()