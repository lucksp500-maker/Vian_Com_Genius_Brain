import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { ActionPreviewPanel } from './command-room/ActionPreviewPanel'
import { LocalSearchResultViewer } from './command-room/LocalSearchResultViewer'
import { DocumentPreviewRoom } from './command-room/DocumentPreviewRoom'
import { AuditLedgerViewer } from './command-room/AuditLedgerViewer'
import { UndoJournalViewer } from './command-room/UndoJournalViewer'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        {/* WO-003: Action Preview */}
        <Route path="/command-room/preview/:actionId" element={<ActionPreviewPanel />} />
        {/* WO-004: Local Search */}
        <Route path="/command-room/local-search" element={
          <div className="h-screen">
            <LocalSearchResultViewer
              onSelectFile={(path) => window.open(
                `/command-room/preview-local?path=${encodeURIComponent(path)}`, '_self'
              )}
            />
          </div>
        } />
        {/* WO-004: Document Preview */}
        <Route path="/command-room/preview-local" element={
          <div className="h-screen">
            <DocumentPreviewRoom
              filePath={new URLSearchParams(window.location.search).get('path') ?? ''}
              onClose={() => window.history.back()}
            />
          </div>
        } />
        {/* WO-006: Audit Ledger */}
        <Route path="/command-room/audit" element={<div className="h-screen"><AuditLedgerViewer /></div>} />
        {/* WO-006: Undo Journal */}
        <Route path="/command-room/undo" element={<div className="h-screen"><UndoJournalViewer /></div>} />
        <Route path="*" element={
          <div className="flex items-center justify-center min-h-screen bg-[#13131b] text-[#e4e1ed]">
            Vian CommandOS
          </div>
        } />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
)
