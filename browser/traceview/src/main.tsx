import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import { TracingNode } from './model/Node.tsx'


function mountTraceView(element: HTMLElement, node: TracingNode) {
  ReactDOM.createRoot(element).render(
    <React.StrictMode>
      <App root={node} />
    </React.StrictMode>,
  )
}

declare global {
  interface Window {
    mountTraceView: unknown;
  }
}

window.mountTraceView = mountTraceView

