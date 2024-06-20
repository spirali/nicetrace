import { useState } from 'react';
import './App.css'
import { TreeView } from './components/TreeView'
import { TracingNode } from './model/Node'
import { NodeDetail } from './components/NodeDetail';

export interface TreeState {
  opened: Set<string>
  selected: TracingNode
}

function App(props: { root: TracingNode }) {
  const [state, setState] = useState<TreeState>(() => {
    const opened = new Set<string>;
    opened.add(props.root.uid);
    let node = props.root;
    while (node?.children?.length == 1) {
      opened.add(node.uid);
      node = node.children[0]
    }
    return { opened, selected: props.root }
  });
  return (
    <div className="container">
      <div className='panel'><TreeView root={props.root} treeState={state} setTreeState={setState} /></div>
      <div className='content'><NodeDetail node={state.selected} /></div>
    </div>
  )
}

export default App
