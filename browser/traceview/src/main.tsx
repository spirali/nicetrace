import React from 'react'
import ReactDOM from 'react-dom/client'
import './index.css'
import { TracingNode } from './model/Node.ts'
import { NodeView } from './components/NodeView.tsx'
import App from './App.tsx'


function mountTraceView(element: HTMLElement, node: TracingNode) {
  ReactDOM.createRoot(element).render(
    <React.StrictMode>
      <NodeView root={node} enableActions={false} />
    </React.StrictMode>,
  )
}

function mountTraceManager(element: HTMLElement, url: string) {
  ReactDOM.createRoot(element).render(
    <React.StrictMode>
      <App url={url} />
    </React.StrictMode>,
  )
}

declare global {
  interface Window {
    mountTraceView: unknown;
    mountTraceManager: unknown;
  }
}

window.mountTraceView = mountTraceView
window.mountTraceManager = mountTraceManager
