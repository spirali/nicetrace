import { useState } from 'react';
import './App.css'
import { TreeView } from './components/TreeView'
import { TracingNode } from './model/Node'

export interface TreeState {
  opened: Set<string>
  selected: TracingNode
}

function App(props: { root: TracingNode }) {
  const [state, setState] = useState<TreeState>({ opened: new Set, selected: props.root });
  return (
    <div className="container">
      <div className='panel'><TreeView root={props.root} treeState={state} setTreeState={setState} /></div>
      <div className='content'>XXXX</div>
    </div>
  )
}

export default App
