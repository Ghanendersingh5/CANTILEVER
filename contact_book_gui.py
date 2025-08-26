import tkinter as tk
from tkinter import messagebox, simpledialog, Listbox, Scrollbar, END
import json
import os
import re # For regular expressions, useful for email/phone validation

# --- Configuration ---
CONTACTS_FILE = 'contacts.json' # The file where contacts will be saved
BLINK_COLOR = '#FFCCCC' # Light red for blinking error
DEFAULT_ENTRY_BG = '#e0e0e0' # Default background color for entry fields

# --- Contact Class (reused from CLI version) ---
class Contact:
    """
    Represents a single contact with name, phone, and email.
    """
    def __init__(self, name, phone, email):
        self.name = name
        self.phone = phone
        self.email = email

    def __str__(self):
        """
        Returns a string representation of the contact for display.
        """
        return f"Name: {self.name}, Phone: {self.phone}, Email: {self.email}"

    def to_dict(self):
        """
        Converts the Contact object to a dictionary for JSON serialization.
        """
        return {'name': self.name, 'phone': self.phone, 'email': self.email}

    @staticmethod
    def from_dict(data):
        """
        Creates a Contact object from a dictionary (e.g., loaded from JSON).
        """
        return Contact(data['name'], data['phone'], data['email'])

# --- ContactBook Class (reused from CLI version, with minor adjustments for GUI feedback) ---
class ContactBook:
    """
    Manages a collection of contacts, including loading, saving,
    adding, viewing, searching, and deleting.
    """
    def __init__(self, filename=CONTACTS_FILE):
        self.filename = filename
        self.contacts = []
        self._load_contacts() # Load contacts automatically when ContactBook is initialized

    def _load_contacts(self):
        """
        Loads contacts from the specified JSON file.
        If the file doesn't exist, it starts with an empty list.
        Returns a message string indicating success or failure.
        """
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    self.contacts = [Contact.from_dict(d) for d in data]
                return f"Loaded {len(self.contacts)} contacts from {self.filename}."
            except json.JSONDecodeError:
                self.contacts = []
                return f"Error: Could not decode JSON from {self.filename}. Starting with empty contacts."
            except Exception as e:
                self.contacts = []
                return f"An unexpected error occurred while loading contacts: {e}. Starting with empty contacts."
        else:
            return "Contact file not found. Starting with an empty contact book."

    def _save_contacts(self):
        """
        Saves the current list of contacts to the JSON file.
        Returns a message string indicating success or failure.
        """
        try:
            with open(self.filename, 'w') as f:
                json.dump([c.to_dict() for c in self.contacts], f, indent=4)
            return "Contacts saved successfully."
        except Exception as e:
            return f"Error: Could not save contacts to {self.filename}. {e}"

    def _validate_contact_data(self, name, phone, email, is_new_contact=True, current_phone_to_exclude=None):
        """
        Performs basic validation on contact data.
        Returns (True, "Success", None) or (False, "Error Message", "field_name").
        is_new_contact: True if adding a new contact, False if updating.
        current_phone_to_exclude: The phone of the contact being updated, to ignore when checking duplicates.
        """
        if not name.strip():
            return False, "Name cannot be empty.", 'name'
        if not phone.strip():
            return False, "Phone number cannot be empty.", 'phone'
        # Basic phone number validation: digits and at least 5 characters
        if not re.fullmatch(r'^\d{5,}$', phone.strip()):
            return False, "Phone number must contain only digits and be at least 5 characters long.", 'phone'
        # Basic email validation
        if email.strip() and not re.fullmatch(r'[^@]+@[^@]+\.[^@]+', email.strip()):
            return False, "Invalid email format.", 'email'

        # Check for duplicate phone numbers
        # If it's an update, exclude the contact being updated from the duplicate check
        for contact in self.contacts:
            if contact.phone == phone and contact.phone != current_phone_to_exclude:
                return False, f"A contact with phone number {phone} already exists.", 'phone'

        return True, "Validation successful.", None

    def add_contact(self, name, phone, email):
        """
        Adds a new contact to the contact book and saves the changes.
        Returns a tuple: (success_boolean, message_string, field_name_for_error)
        """
        is_valid, validation_msg, error_field = self._validate_contact_data(name, phone, email, is_new_contact=True)
        if not is_valid:
            return False, validation_msg, error_field

        new_contact = Contact(name, phone, email)
        self.contacts.append(new_contact)
        save_msg = self._save_contacts()
        return True, f"Contact '{name}' added. {save_msg}", None

    def update_contact(self, old_phone, new_name, new_phone, new_email):
        """
        Updates an existing contact's details based on their old phone number.
        Returns a tuple: (success_boolean, message_string, field_name_for_error)
        """
        is_valid, validation_msg, error_field = self._validate_contact_data(new_name, new_phone, new_email,
                                                                          is_new_contact=False,
                                                                          current_phone_to_exclude=old_phone)
        if not is_valid:
            return False, validation_msg, error_field

        contact_found = False
        for contact in self.contacts:
            if contact.phone == old_phone:
                contact.name = new_name
                contact.phone = new_phone
                contact.email = new_email
                contact_found = True
                break

        if contact_found:
            save_msg = self._save_contacts()
            return True, f"Contact with phone '{old_phone}' updated. {save_msg}", None
        else:
            return False, f"Contact with phone '{old_phone}' not found for update.", None


    def search_contact(self, query):
        """
        Searches for contacts by name, phone number, or email (case-insensitive).
        Returns a list of matching contacts.
        """
        matches = [
            contact for contact in self.contacts
            if query.lower() in contact.name.lower() or
               query in contact.phone or
               (contact.email and query.lower() in contact.email.lower())
        ]
        return matches

    def delete_contact(self, identifier):
        """
        Deletes a contact by phone number.
        For GUI, we'll usually pass the phone number for precise deletion.
        Returns a tuple: (success_boolean, message_string)
        """
        contact_to_delete = None
        for contact in self.contacts:
            if contact.phone == identifier: # Assuming identifier is exact phone for GUI delete
                contact_to_delete = contact
                break
        
        if contact_to_delete:
            self.contacts.remove(contact_to_delete)
            save_msg = self._save_contacts()
            return True, f"Contact '{contact_to_delete.name}' deleted. {save_msg}"
        else:
            return False, f"No contact found matching '{identifier}'. Please select a contact using its unique phone number."

    def sort_contacts(self, key='name'):
        """
        Sorts the contacts list by a specified key (e.g., 'name', 'phone', 'email').
        """
        if key == 'name':
            self.contacts.sort(key=lambda c: c.name.lower())
        elif key == 'phone':
            self.contacts.sort(key=lambda c: c.phone)
        elif key == 'email':
            self.contacts.sort(key=lambda c: c.email.lower() if c.email else '') # Handle empty emails
        # Can add more sorting options if needed
        return "Contacts sorted."

    def clear_all_contacts(self):
        """
        Clears all contacts from the contact book and the file.
        Returns a tuple: (success_boolean, message_string)
        """
        self.contacts = []
        return True, self._save_contacts()


# --- Tkinter GUI Application ---
class ContactBookApp:
    """
    The main Tkinter application for the Contact Book.
    Handles GUI layout and interaction.
    """
    def __init__(self, master):
        self.master = master
        master.title("Contact Book Application")
        master.geometry("700x650") # Adjust initial window size
        master.resizable(True, True) # Allow resizing

        self.contact_book = ContactBook()

        # UI Styling (basic)
        master.option_add('*Font', 'Inter 10')
        master.option_add('*Button.pady', 5)
        master.option_add('*Button.padx', 10)
        master.option_add('*Entry.relief', 'flat')
        master.option_add('*Entry.bg', DEFAULT_ENTRY_BG) # Use default entry background constant
        master.option_add('*Button.fg', 'white') # Default text color for buttons


        # Initialize UI elements
        self.create_widgets()
        self._update_contact_list_display() # Show contacts on startup

        # Display initial load message
        load_message = self.contact_book._load_contacts() # Re-call to get message for GUI
        self._show_message(load_message)

        # Bind listbox selection to populate entries
        self.contact_listbox.bind('<<ListboxSelect>>', self.load_selected_contact_to_entries)


    def create_widgets(self):
        """
        Creates all the Tkinter widgets (labels, entry fields, buttons, listbox)
        and arranges them using the grid layout manager.
        """
        # --- Input Frame ---
        input_frame = tk.LabelFrame(self.master, text="Contact Details", padx=15, pady=15, bd=2, relief="groove")
        input_frame.pack(fill=tk.X, padx=10, pady=10) # Pack fills horizontally, with padding

        tk.Label(input_frame, text="Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.name_entry = tk.Entry(input_frame, width=50)
        self.name_entry.grid(row=0, column=1, pady=5, padx=5)

        tk.Label(input_frame, text="Phone:").grid(row=1, column=0, sticky="w", pady=5)
        self.phone_entry = tk.Entry(input_frame, width=50)
        self.phone_entry.grid(row=1, column=1, pady=5, padx=5)

        tk.Label(input_frame, text="Email:").grid(row=2, column=0, sticky="w", pady=5)
        self.email_entry = tk.Entry(input_frame, width=50)
        self.email_entry.grid(row=2, column=1, pady=5, padx=5)

        # --- Action Buttons Frame ---
        action_button_frame = tk.Frame(self.master, padx=10, pady=5)
        action_button_frame.pack(fill=tk.X, pady=5)

        # Use a consistent width for buttons for better aesthetics
        button_width = 15

        tk.Button(action_button_frame, text="Add", command=self.add_contact_gui, width=button_width, bg='#2196F3').pack(side=tk.LEFT, padx=5) # Blue
        tk.Button(action_button_frame, text="Update", command=self.update_contact_gui, width=button_width, bg='#FFC107').pack(side=tk.LEFT, padx=5) # Amber
        tk.Button(action_button_frame, text="Delete", command=self.delete_contact_gui, width=button_width, bg='#F44336').pack(side=tk.LEFT, padx=5) # Red
        tk.Button(action_button_frame, text="Clear Fields", command=self.clear_entries, width=button_width, bg='#9E9E9E').pack(side=tk.LEFT, padx=5) # Grey
        tk.Button(action_button_frame, text="Reset All", command=self.reset_contacts_gui, width=button_width, bg='#795548').pack(side=tk.LEFT, padx=5) # Brown


        # --- List Display Frame ---
        list_display_frame = tk.LabelFrame(self.master, text="Contacts List", padx=15, pady=10, bd=2, relief="groove")
        list_display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.contact_listbox = Listbox(list_display_frame, height=15, selectmode=tk.SINGLE)
        self.contact_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a scrollbar to the listbox
        scrollbar = Scrollbar(list_display_frame, orient="vertical", command=self.contact_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.contact_listbox.config(yscrollcommand=scrollbar.set)

        # --- View/Sort/Search Buttons ---
        view_sort_search_frame = tk.Frame(self.master, padx=10, pady=5)
        view_sort_search_frame.pack(fill=tk.X, pady=5)

        tk.Button(view_sort_search_frame, text="View All", command=self.view_contacts_gui, width=button_width, bg='#009688').pack(side=tk.LEFT, padx=5) # Teal
        tk.Button(view_sort_search_frame, text="Sort by Name", command=lambda: self.sort_contacts_gui('name'), width=button_width, bg='#00BCD4').pack(side=tk.LEFT, padx=5) # Cyan
        tk.Button(view_sort_search_frame, text="Sort by Phone", command=lambda: self.sort_contacts_gui('phone'), width=button_width, bg='#8BC34A').pack(side=tk.LEFT, padx=5) # Light Green
        tk.Button(view_sort_search_frame, text="Search", command=self.search_contact_gui, width=button_width, bg='#673AB7').pack(side=tk.LEFT, padx=5) # Deep Purple


        # --- Status Message Label ---
        self.status_message_label = tk.Label(self.master, text="", fg="blue", padx=10, pady=5, wraplength=600)
        self.status_message_label.pack(fill=tk.X, pady=5)

    def _show_message(self, message, is_error=False):
        """
        Displays a status message to the user in the GUI.
        """
        self.status_message_label.config(text=message, fg="red" if is_error else "blue")

    def _blink_entry_field(self, entry_widget, num_blinks=3, delay_ms=150):
        """
        Makes an entry widget blink by changing its background color.
        """
        original_bg = DEFAULT_ENTRY_BG # Use the constant
        
        def blink_step(count):
            if count % 2 == 0:
                entry_widget.config(bg=BLINK_COLOR)
            else:
                entry_widget.config(bg=original_bg)
            
            if count > 0:
                self.master.after(delay_ms, blink_step, count - 1)
            else:
                entry_widget.config(bg=original_bg) # Ensure it ends on original color

        blink_step(num_blinks * 2) # Multiply by 2 for on/off cycles


    def _update_contact_list_display(self, contacts_to_display=None):
        """
        Clears the listbox and populates it with contacts.
        If contacts_to_display is None, it shows all contacts.
        Otherwise, it shows the provided list of contacts (e.g., search results).
        """
        self.contact_listbox.delete(0, END) # Clear existing items
        self.contact_listbox.item_data = {} # Clear stored item data as well

        if contacts_to_display is None:
            contacts_to_display = self.contact_book.contacts

        if not contacts_to_display:
            self.contact_listbox.insert(END, "No contacts to display.")
            return

        for i, contact in enumerate(contacts_to_display):
            # Store the full contact object in a dictionary for easy retrieval
            # and display the name for better user selection
            self.contact_listbox.insert(END, f"{contact.name} ({contact.phone})")
            # Store the actual Contact object as item data (not directly visible)
            self.contact_listbox.item_data[i] = contact


    def load_selected_contact_to_entries(self, event):
        """
        Loads the details of the selected contact from the listbox
        into the entry fields.
        """
        selected_indices = self.contact_listbox.curselection()
        if not selected_indices:
            return

        selected_index = selected_indices[0]
        # Retrieve the Contact object using the index and stored item_data
        selected_contact = self.contact_listbox.item_data.get(selected_index)

        if selected_contact:
            self.clear_entries() # Clear first
            self.name_entry.insert(0, selected_contact.name)
            self.phone_entry.insert(0, selected_contact.phone)
            self.email_entry.insert(0, selected_contact.email)
            self._show_message(f"Contact '{selected_contact.name}' loaded for editing.")


    def clear_entries(self):
        """
        Clears the text in all input entry fields.
        """
        self.name_entry.delete(0, END)
        self.phone_entry.delete(0, END)
        self.email_entry.delete(0, END)
        self._show_message("Input fields cleared.") # Clear status message
        # Reset backgrounds to default
        self.name_entry.config(bg=DEFAULT_ENTRY_BG)
        self.phone_entry.config(bg=DEFAULT_ENTRY_BG)
        self.email_entry.config(bg=DEFAULT_ENTRY_BG)

    def add_contact_gui(self):
        """
        Handles adding a contact based on GUI input.
        """
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()

        success, message, error_field = self.contact_book.add_contact(name, phone, email)
        if success:
            self._update_contact_list_display()
            self.clear_entries()
            self._show_message(message, is_error=False)
        else:
            self._show_message(message, is_error=True)
            messagebox.showerror("Input Error", message) # Popup error message
            if error_field == 'name':
                self._blink_entry_field(self.name_entry)
            elif error_field == 'phone':
                self._blink_entry_field(self.phone_entry)
            elif error_field == 'email':
                self._blink_entry_field(self.email_entry)


    def update_contact_gui(self):
        """
        Handles updating a contact based on GUI input.
        Assumes the user selects a contact from the listbox,
        and then modifies the entry fields. The original phone
        number (from the selected contact) is used to identify
        which contact to update.
        """
        selected_indices = self.contact_listbox.curselection()
        if not selected_indices:
            self._show_message("Please select a contact from the list to update.", is_error=True)
            return

        selected_index = selected_indices[0]
        original_contact = self.contact_listbox.item_data.get(selected_index)

        if not original_contact:
            self._show_message("Error: Could not retrieve original contact for update.", is_error=True)
            return

        # Get updated data from entry fields
        new_name = self.name_entry.get().strip()
        new_phone = self.phone_entry.get().strip()
        new_email = self.email_entry.get().strip()

        # Use the original phone as the identifier to find the contact
        old_phone_identifier = original_contact.phone

        success, message, error_field = self.contact_book.update_contact(old_phone_identifier, new_name, new_phone, new_email)

        if success:
            self._update_contact_list_display()
            self.clear_entries()
            self._show_message(message, is_error=False)
        else:
            self._show_message(message, is_error=True)
            messagebox.showerror("Input Error", message) # Popup error message
            if error_field == 'name':
                self._blink_entry_field(self.name_entry)
            elif error_field == 'phone':
                self._blink_entry_field(self.phone_entry)
            elif error_field == 'email':
                self._blink_entry_field(self.email_entry)


    def view_contacts_gui(self):
        """
        Handles displaying all contacts.
        """
        self._update_contact_list_display()
        self.clear_entries()
        self._show_message("Displaying all contacts.")

    def search_contact_gui(self):
        """
        Handles searching for contacts based on user input from a dialog box.
        """
        search_query = simpledialog.askstring("Search Contact", "Enter name, phone, or email to search:")
        if search_query:
            matches = self.contact_book.search_contact(search_query)
            if matches:
                self._update_contact_list_display(matches)
                self._show_message(f"Found {len(matches)} matching contacts for '{search_query}'.")
            else:
                self._update_contact_list_display([]) # Clear list if no matches
                self._show_message(f"No contacts found for '{search_query}'.", is_error=True)
        else:
            self._show_message("Search cancelled.", is_error=False)

    def delete_contact_gui(self):
        """
        Handles deleting a selected contact from the listbox.
        """
        selected_indices = self.contact_listbox.curselection()
        if not selected_indices:
            self._show_message("Please select a contact to delete.", is_error=True)
            return

        selected_index = selected_indices[0]
        contact_to_delete = self.contact_listbox.item_data.get(selected_index)

        if not contact_to_delete:
            self._show_message("Error: Could not retrieve contact details for deletion.", is_error=True)
            return

        # Confirmation dialog before deleting
        if messagebox.askyesno("Delete Contact", f"Are you sure you want to delete:\nName: {contact_to_delete.name}\nPhone: {contact_to_delete.phone}?"):
            # Use the phone number as the unique identifier for deletion
            success, message = self.contact_book.delete_contact(contact_to_delete.phone)
            if success:
                self._update_contact_list_display()
                self.clear_entries() # Clear entries after deleting
                self._show_message(message, is_error=False)
            else:
                self._show_message(message, is_error=True)
        else:
            self._show_message("Deletion cancelled.")

    def reset_contacts_gui(self):
        """
        Prompts for confirmation then clears all contacts from the book and file.
        """
        if messagebox.askyesno("Reset All Contacts", "Are you absolutely sure you want to delete ALL contacts? This action cannot be undone."):
            success, message = self.contact_book.clear_all_contacts()
            if success:
                self._update_contact_list_display()
                self.clear_entries()
                self._show_message("All contacts have been reset and deleted.", is_error=False)
            else:
                self._show_message(f"Error resetting contacts: {message}", is_error=True)
        else:
            self._show_message("Reset cancelled.", is_error=False)


    def sort_contacts_gui(self, key):
        """
        Sorts contacts and updates the display.
        """
        self.contact_book.sort_contacts(key)
        self._update_contact_list_display()
        self._show_message(f"Contacts sorted by {key}.")

# Extend Listbox to store item data
class ExtendedListbox(Listbox):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self.item_data = {} # Dictionary to store actual Contact objects

# Replace standard Listbox with ExtendedListbox
# This must be done BEFORE creating the ContactBookApp instance
tk.Listbox = ExtendedListbox

if __name__ == "__main__":
    root = tk.Tk()
    app = ContactBookApp(root)
    root.mainloop()
