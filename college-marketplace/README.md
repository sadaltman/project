# College Marketplace

A web platform for college students to buy, sell, and rent items within their campus community. This application allows registered students to create listings across various categories including textbooks, electronics, furniture, mess meals, food, and more.

## Features

- **User Authentication**: Secure registration and login system for college students (requires .edu email)
- **Listing Management**: Create, edit, and delete listings for items to buy, sell, or rent
- **Category Browsing**: Browse listings by categories
- **Search Functionality**: Search for specific items across all categories
- **Responsive Design**: Mobile-friendly interface for on-the-go access

## Categories

The platform includes the following categories:
- Textbooks
- Electronics
- Furniture
- Clothing
- Mess Meals
- Food
- Services
- Housing/Rentals
- Transportation
- Other

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML, CSS, JavaScript
- **UI Framework**: Bootstrap 5
- **Authentication**: Flask-Login

## Setup Instructions

1. Clone the repository:
```
git clone <repository-url>
cd college-marketplace
```

2. Create a virtual environment and activate it:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required dependencies:
```
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with the following content:
```
SECRET_KEY=your-secret-key-here
```

5. Run the application:
```
python app.py
```

6. Open your browser and navigate to `http://localhost:5000`

## Project Structure

```
college-marketplace/
├── app.py                  # Main application file
├── requirements.txt        # Python dependencies
├── static/                 # Static files
│   ├── css/                # CSS stylesheets
│   ├── js/                 # JavaScript files
│   └── images/             # Image files and uploads
├── templates/              # HTML templates
│   ├── base.html           # Base template
│   ├── index.html          # Homepage
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   ├── create_listing.html # Create listing page
│   └── ...                 # Other templates
└── README.md               # Project documentation
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
