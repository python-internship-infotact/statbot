# StatBot Pro Frontend

Modern React frontend for StatBot Pro - an AI-powered CSV data analysis tool.

## Features

- Modern React + TypeScript + Vite setup
- Beautiful UI with shadcn/ui components
- Real-time chat interface for data analysis
- Drag-and-drop CSV file upload
- Interactive results display with charts
- Responsive design with Tailwind CSS

## Development

### Prerequisites

- Node.js 18+ and npm
- Backend server running on http://localhost:8001

### Getting Started

1. **Install dependencies:**
```bash
npm install
```

2. **Start development server:**
```bash
npm run dev
```

3. **Open your browser:**
```
http://localhost:8080
```

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm test` - Run tests

## Project Structure

```
frontend/
├── src/
│   ├── components/     # React components
│   │   ├── statbot/   # StatBot-specific components
│   │   └── ui/        # Reusable UI components
│   ├── pages/         # Page components
│   ├── lib/           # Utilities and API client
│   ├── types/         # TypeScript type definitions
│   └── hooks/         # Custom React hooks
├── public/            # Static assets
└── dist/             # Production build output
```

## API Integration

The frontend communicates with the FastAPI backend through:
- REST API calls for file upload and question processing
- Real-time updates for analysis progress
- Chart image serving for visualizations

## Technologies Used

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI component library
- **React Router** - Client-side routing
- **React Query** - Server state management
- **Recharts** - Chart components

## Contributing

1. Follow the existing code style
2. Add TypeScript types for new features
3. Test components thoroughly
4. Update documentation as needed