# SNS Agent Frontend

This is the visual frontend for the **Xiaohongshu MCP Agent System**. It provides a "Canva-like" interface for designing posts and an AI Assistant chat box.

## 📂 Project Structure

This project is a **Next.js 16** application using the **App Router**.

### Core Source Code (`frontend/app/`)
- **`frontend/app/page.tsx`**: Entry point. Renders the main `AIPostApp`.
- **`frontend/app/aipost/`**: Contains the core logic for the editor.
  - **`App.tsx`**: Main application state manager (Canvas elements, Undo/Redo, AI Chat state).
  - **`components/`**: UI Components.
    - `Canvas.tsx`: The main drawing area.
    - `Toolbar.tsx`: Tools for adding text, images, etc.
    - `AIDialog.tsx`: The chat interface for AI interaction.
    - `PropertiesPanel.tsx`: Settings for selected elements.
- **`frontend/app/api/`**: Next.js API Routes. These act as a proxy or mock layer for the AI features.
  - `api/ai/suggestions`: Endpoint for getting AI prompt suggestions.
  - `api/ai/apply`: Endpoint for applying AI edits to the canvas.

### Documentation (`frontend/docs/`)
- **`AI_API.md`**: Detailed specification of the API contract between Frontend and Backend.
- **`Backend_AI_Integration.md`**: Guide for implementing the Python backend logic.

### Configuration
- **`frontend/next.config.ts`**: Next.js configuration.
- **`frontend/tailwind.config.ts`** (implicit in v4): Styling configuration.

## 🔗 Integration

This frontend is designed to work with the **Python Backend (`agent_server.py`)** located in the parent directory.

-   **Chat Box**: Sends requests to `http://127.0.0.1:8000/chat`
-   **Publish Button**: Sends requests to `http://127.0.0.1:8000/publish`

## 🚀 Getting Started

### 1. Prerequisites
Ensure the Python Backend is running first! (See `README.md`)

### 2. Install Dependencies
```bash
cd frontend
npm install
```

### 3. Run Development Server
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser.

## 🛠️ Tech Stack
-   **Framework**: Next.js 16 (App Router)
-   **UI**: Tailwind CSS, Lucide React
-   **Drag & Drop**: React DnD
-   **Language**: TypeScript

## ⚠️ Note
If the AI Chat or Publish features are not working, check that:
1.  The Python server is running on port 8000.
2.  There are no CORS issues (though the Next.js API route proxies requests to avoid this).

## 🚧 Current Placeholders & Mock Data

The frontend currently contains several placeholders and fallback mechanisms to allow UI testing without a running backend.

### 1. AI Suggestions (`frontend/app/api/ai/suggestions`)
-   **Status**: Mocked.
-   **Behavior**: The API route currently returns an empty list.
-   **Fallback**: `AIDialog.tsx` uses hardcoded arrays (`singleElementSuggestions`, `multiElementSuggestions`, `globalSuggestions`) when no suggestions are returned from the API.

### 2. AI Modifications (`frontend/app/api/ai/apply`)
-   **Status**: Hybrid (Proxy + Fallback).
-   **Behavior**: Tries to forward requests to `http://127.0.0.1:8000/chat`.
-   **Fallback**: If the backend is offline, `App.tsx` executes local keyword-based logic (e.g., "make it bigger", "change color to red") to simulate AI changes.

### 3. Publishing (`frontend/app/api/ai/publish`)
-   **Status**: Proxy.
-   **Behavior**: Forwards requests to `http://127.0.0.1:8000/publish`.
-   **Note**: Hardcoded to localhost:8000.

### 4. Hardcoded URLs
-   The API routes currently point to `http://127.0.0.1:8000`. This should be moved to environment variables (`.env`) for production.
