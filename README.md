# Insights - Backend-Driven Analytics Platform
Live URL:-https://insights-frontend-v2n9.onrender.com/login
A minimal, production-ready frontend for a data analytics platform that is fully integrated with a FastAPI backend. This is a **thin client** - all analytics logic, dashboard generation, and insights are driven by the backend.

## Architecture Principle

The frontend contains **zero analytics logic**. It is purely a presentation layer that:
- Fetches data from the backend
- Renders UI based on backend responses
- Polls for status updates
- Handles user interactions

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
VITE_BACKEND_BASE_URL=http://localhost:8000
```

This allows you to point the frontend to any backend instance without code changes.

## Backend API Integration

### Authentication Flow

1. **Register**: `POST /auth/register`
2. **Login**: `POST /auth/login` (returns JWT token)
3. **Token Storage**: JWT stored in localStorage
4. **Protected Routes**: Token sent as `Authorization: Bearer <token>`

### Data Pipeline

```
Upload → Processing → Dashboard → Insights
```

#### 1. Dataset Upload
- User uploads CSV/Excel file
- `POST /datasets/upload` → returns `{ status: "PROCESSING" }`
- Frontend polls `GET /datasets` every 6 seconds
- When status becomes `READY`, "Generate Dashboard" button is enabled

#### 2. Dashboard Generation
- User clicks "Generate Dashboard"
- `POST /dashboards?dataset_id=...` → creates dashboard
- Navigate to dashboard view
- `GET /dashboards/by-dataset/{dataset_id}` → fetches dashboard with widgets

#### 3. Dynamic Widget Rendering
Widgets are rendered based on backend response:

**KPI Widgets:**
```json
{
  "type": "kpi",
  "metric": "Total Records",
  "value": 24563,
  "format": "number"
}
```

**Chart Widgets:**
```json
{
  "type": "chart",
  "chart_type": "line",
  "x": "month",
  "y": "revenue",
  "data": [{ "month": "Jan", "revenue": 5000 }, ...]
}
```

The frontend dynamically switches on `chart_type` to render:
- `line` → Line chart
- `bar` → Bar chart  
- `scatter` → Scatter plot

#### 4. Insights Generation
- On dashboard load, call `POST /insights/generate?dataset_id=...` (once)
- Poll `GET /insights/{dataset_id}` every 5 seconds
- Stop polling when insights are returned
- Display insights grouped by type: `trend`, `anomaly`, `data_quality`

### Profile Page
- `GET /users/profile` → fetches user info and usage stats
- Displays:
  - Name, email, account created date
  - Datasets uploaded count
  - Dashboards created count
  - Insights generated count

## Key Features

### ✅ Model-Driven UI
- All dashboard layouts determined by backend
- No hardcoded chart configurations
- Widget types and data structures defined by API

### ✅ Real-Time Status Updates
- Dataset processing status polling
- Insights generation polling
- Visual indicators for loading states

### ✅ Clean Error Handling
- API errors displayed to user
- Graceful fallbacks for missing data
- Loading states for all async operations

### ✅ Responsive Design
- Desktop-first layout
- Mobile-friendly tables and cards
- Minimal, professional B2B SaaS aesthetic

## Project Structure

```
/
├── .env                          # Backend configuration
├── lib/
│   ├── api-types.ts              # TypeScript types matching backend models
│   ├── api-client.ts             # API client with all endpoints
│   └── auth-context.tsx          # Authentication context provider
├── components/
│   ├── LoginPage.tsx             # Authentication
│   ├── RegisterPage.tsx          # User registration
│   ├── HomePage.tsx              # Dataset upload + polling
│   ├── DashboardPage.tsx         # Dynamic dashboard + insights polling
│   ├── ProfilePage.tsx           # User profile + stats
│   ├── Navbar.tsx                # Top navigation
│   ├── ProtectedRoute.tsx        # Route guard
│   └── widgets/
│       ├── WidgetRenderer.tsx    # Widget type switch
│       ├── KPIWidget.tsx         # Metric card renderer
│       └── ChartWidget.tsx       # Chart renderer (line/bar/scatter)
└── App.tsx                       # Router configuration
```

## Running the Application

1. Install dependencies:
```bash
npm install
```

2. Configure backend URL in `.env`

3. Start development server:
```bash
npm run dev
```

4. Ensure your FastAPI backend is running at the configured URL

## Backend Requirements

The backend must implement these endpoints:

**Auth:**
- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`

**Users:**
- `GET /users/profile`

**Datasets:**
- `POST /datasets/upload` (multipart/form-data)
- `GET /datasets`
- `GET /datasets/{dataset_id}`

**Dashboards:**
- `POST /dashboards?dataset_id=...`
- `GET /dashboards/by-dataset/{dataset_id}`

**Insights:**
- `POST /insights/generate?dataset_id=...`
- `GET /insights/{dataset_id}`

## Design Philosophy

This frontend is designed as a **thin client** to clearly demonstrate the separation of concerns:
- Backend = Data processing, analytics, insights generation
- Frontend = UI rendering, user interactions, API consumption

No analytics logic exists in the frontend. Everything is API-driven.
