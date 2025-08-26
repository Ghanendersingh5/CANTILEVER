📚 Contact Book Application
This is a desktop Contact Book application built using Python with a Graphical User Interface (GUI). It allows users to manage their contacts efficiently, including names, phone numbers, and email addresses. All contact data is stored persistently.

✨ Features
Add New Contacts: Easily input and save new contact details.

Update Existing Contacts: Modify details of any selected contact.

Delete  Contacts: Remove unwanted contacts from the list.

Search Contacts: Find specific contacts by name, phone, or email.

Sort Contacts: Organize your contacts alphabetically by name or numerically by phone.

Clear Input Fields: Resets the text entry areas.

Reset All Contacts: A confirmed option to delete all saved contacts.

Persistent Data Storage: All contacts are saved to a file and loaded automatically.

Input Validation: Provides immediate visual feedback (blinking fields) and popup error messages for incorrect or missing data.

💻 Technologies Used
Python: The primary programming language for the application logic.

Tkinter: Python's standard library used for creating the Graphical User Interface (GUI).

File I/O (JSON): Utilized for saving and loading contact data to and from a contacts.json file, ensuring data persists between sessions.

re module: Python's built-in module for regular expressions, used to validate the format of phone numbers and email addresses.

🚀 How to Run the Application
To run this application on your local machine, follow these steps:

Clone the Repository:
Open your terminal or command prompt and execute the following command:

Bash

git clone https://github.com/Ghanendersingh5/cantilever.git
Navigate to the Project Directory:
Change your current directory to the cloned project folder:

Bash

cd cantilever
Run the Python Script:
Execute the main application file:

Bash

python contact_book_gui.py
# Use 'python3 contact_book_gui.py' if 'python' refers to an older version.
🛠️ Basic Usage
Add: Enter contact details in the fields and click "Add".

Update: Select a contact from the list, modify fields, and click "Update".

Delete: Select a contact and click "Delete". Confirm in the dialog box.

Search: Click "Search" and type your query in the popup window.

Sort: Use "Sort by Name" or "Sort by Phone" buttons.

Clear Fields: Clears text from Name, Phone, and Email input boxes.

Reset All: Click to delete all contacts after a confirmation prompt.

📄 License
This project is licensed under the MIT License.
