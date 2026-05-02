import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { CommandHUD } from './hud/CommandHUD'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <CommandHUD />
  </StrictMode>
)
