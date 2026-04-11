# Nyaradzo Insurance Churn Prediction — Frontend

React-based frontend for the Nyaradzo Insurance Policyholder Churn Prediction System. Provides dashboards, analytics, policy management, and churn prediction visualizations.

## Technologies

- [Vite](https://vitejs.dev/) — Build tool
- [React](https://react.dev/) — UI framework
- [TypeScript](https://www.typescriptlang.org/) — Type safety
- [shadcn/ui](https://ui.shadcn.com/) — Component library
- [Tailwind CSS](https://tailwindcss.com/) — Styling
- [Axios](https://axios-http.com/) — HTTP client
- [React Router](https://reactrouter.com/) — Routing

## Getting Started

### Prerequisites

- Node.js 16+ and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)

### Setup

```sh
# Clone the repository
git clone <YOUR_GIT_URL>

# Navigate to the frontend directory
cd Frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The app will be available at **http://localhost:5173/**.

### Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server with hot reload |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build locally |
| `npm run lint` | Run ESLint |
| `npm run test` | Run tests |

## Project Structure

```
Frontend/src/
├── components/    # Reusable UI components
├── contexts/      # React context providers (Auth, etc.)
├── hooks/         # Custom hooks (useApiData, etc.)
├── lib/           # API service, utilities
├── pages/         # Page components (Dashboard, Reports, etc.)
└── main.tsx       # Application entry point
```

## Connecting to the Backend

The frontend communicates with the Django REST API backend. Set the API URL in your environment:

```sh
# .env.local
VITE_API_URL=http://127.0.0.1:8000
```

Refer to the [Backend README](../Backend/README.md) for backend setup instructions.

## Deployment

1. Build the production bundle:
   ```sh
   npm run build
   ```
2. Deploy the contents of the `dist/` directory to your hosting provider.
