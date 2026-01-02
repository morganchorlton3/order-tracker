# Order Tracker

A modern web application for managing orders and products from Etsy and TikTok Shop in one centralized location.

## Features

- 📦 **Order Management**: Sync and manage orders from Etsy and TikTok Shop
- 🛍️ **Product Catalog**: Create and manage products in one place
- 🔄 **Bi-directional Sync**: Import orders and export products to/from platforms
- 📊 **Dashboard**: Overview of orders and products
- 🎨 **Modern UI**: Built with React, TypeScript, and Tailwind CSS

## Tech Stack

### Backend
- **FastAPI** - Modern, fast Python web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **Alembic** - Database migrations
- **PostgreSQL/SQLite** - Database (SQLite for development, PostgreSQL for production)

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Query** - Data fetching and caching
- **React Router** - Routing

## Project Structure

```
order-tracker/
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Core configuration
│   │   ├── models/        # Database models
│   │   ├── schemas/       # Pydantic schemas
│   │   └── services/      # Business logic and integrations
│   ├── alembic/           # Database migrations
│   ├── requirements.txt   # Python dependencies
│   └── .env.example       # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   └── services/      # API client
│   └── package.json       # Node dependencies
├── docker-compose.yml     # Docker Compose for PostgreSQL
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- Docker and Docker Compose (for database) - [Install Docker](https://docs.docker.com/get-docker/)

### Database Setup with Docker Compose

The easiest way to run PostgreSQL for development is using Docker Compose:

1. Start the database:
```bash
docker-compose up -d
```

This will start:
- PostgreSQL database on port `5432`
- pgAdmin (optional database management UI) on port `5050`

2. Access pgAdmin (optional):
   - URL: http://localhost:5050
   - Email: `admin@order-tracker.local`
   - Password: `admin`

3. Stop the database when done:
```bash
docker-compose down
```

4. Stop and remove all data:
```bash
docker-compose down -v
```

**Database Connection Details:**
- Host: `localhost`
- Port: `5432`
- Database: `order_tracker`
- Username: `ot_user`
- Password: `password`

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the `backend` directory:
```bash
cp .env.example .env
```

5. Update the `.env` file with your configuration:
   - The default `DATABASE_URL` is already configured for Docker Compose PostgreSQL
   - If using SQLite instead, change to: `DATABASE_URL=sqlite:///./order_tracker.db`
   - Add your API keys for Etsy and TikTok Shop (when available)

6. Initialize the database:
```bash
# Create migrations
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

7. Run the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## API Integration Setup

### Etsy API

1. Create an Etsy app at https://www.etsy.com/developers/
2. Get your API key and secret
3. Add them to your `.env` file:
   ```
   ETSY_API_KEY=your-api-key
   ETSY_API_SECRET=your-api-secret
   ```

**Note**: Etsy uses OAuth 2.0. You'll need to implement OAuth flow to get access tokens. The current implementation has placeholder methods that need to be completed.

### TikTok Shop API

1. Register for TikTok Shop API access
2. Get your API credentials
3. Add them to your `.env` file:
   ```
   TIKTOK_SHOP_API_KEY=your-api-key
   TIKTOK_SHOP_API_SECRET=your-api-secret
   ```

**Note**: TikTok Shop API integration needs to be implemented. The service classes are set up with placeholder methods.

## Development

### Database Migrations

When you modify models, create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

### Running Tests

(To be implemented)

## Next Steps

1. **Complete API Integrations**:
   - Implement OAuth flow for Etsy
   - Complete Etsy order fetching
   - Implement TikTok Shop API integration
   - Add product creation/update methods

2. **Add Authentication**:
   - User registration/login
   - JWT token management
   - Protected routes

3. **Enhanced Features**:
   - Order filtering and search
   - Product variants management
   - Inventory tracking
   - Automated sync scheduling
   - Email notifications

4. **Deployment**:
   - Set up production database
   - Configure environment variables
   - Deploy backend (e.g., Railway, Render, AWS)
   - Deploy frontend (e.g., Vercel, Netlify)

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
