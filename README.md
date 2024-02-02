Flask API for Library Mangement System. <br><br>

To run the program, install necessary dependencies as:
```
pip install -r requirements.txt
```

After installing all the dependencies, run librarymanagement.py file with Python as:
```
python librarymanagement.py
```
<br>
The database used in this project is SQLite. So, you'll need DB Browser for SQLite installed on your computer in order to view the database.
<br> <br>
API usage documentation: <br>

# User API <br>
/users <br>
Required Parameters: ["Name", "Email", "MembershipDate"] <br>

# Book API <br>
/books <br>
Required Parameters: ["Title", "ISBN", "PublishedDate", "Genre"] <br>
/books/<book_id>/details <br>
Required Parameters: ["BookID", "NumberOfPages", "Publisher", "Language"] <br>

# BorrowedBooks API <br>
/borrow <br>
Required Parameters: ["UserID", "BookID", "BorrowDate"] <br>

/return/<user_id>/<book_id> <br>
Required Parameters: ["ReturnDate"] <br>

/borrowed-books <br>


# Check out the source code for more clarity on API usage.


