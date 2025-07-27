# Bank Statements Analyzer

A web application built with Django and React/TypeScript for analyzing and categorizing bank statements.

## Features

- Upload and parse bank statements from multiple banks (Access Bank, GTBank, UBA, Zenith Bank)
- Automatically categorize transactions
- Visualize spending patterns
- Edit transaction details
- Manage custom categories

## Technologies Used

- Backend: Django
- Frontend: React + TypeScript
- Styling: Tailwind CSS
- Build Tool: Vite

## Setup

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Installation

1. Clone the repository

   ```bash
   git clone [repository-url]
   cd bank-statements-analyzer
   ```

2. Install backend dependencies

   ```bash
   pip install -r requirements.txt
   ```

3. Install frontend dependencies

   ```bash
   npm install
   ```

4. Run migrations

   ```bash
   python manage.py migrate
   ```

5. Create default categories

   ```bash
   python manage.py create_default_categories
   ```

### Running the application

1. Start the Django server

   ```bash
   python manage.py runserver
   ```

2. In another terminal, start the frontend development server

   ```bash
   npm run dev
   ```

3. Open your browser and navigate to `http://localhost:8000`

## License

[Add license information here]
