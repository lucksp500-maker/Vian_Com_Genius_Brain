import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { ActionPreviewPanel } from './command-room/ActionPreviewPanel'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/command-room/preview/:actionId" element={<ActionPreviewPanel />} />
        <Route path="*" element={<div className="flex items-center justify-center min-h-screen bg-background text-on-surface">Vian CommandOS</div>} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
)
