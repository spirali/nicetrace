import { useMemo, useState } from 'react';
import './App.css'
import { TreeView } from './components/TreeView'
import { TracingNode } from './model/Node'
import { NodeDetail } from './components/NodeDetail';
import { createNodeIcon } from './common/icons';

export interface TreeState {
  opened: Set<string>
  selected: TracingNode
}

function collapseNode(node: TracingNode): TracingNode {
  if (!node.children) {
    return node;
  }
  const children: TracingNode[] = [];
  let prev = null;
  let id_counter = 100;
  for (const n of node.children) {
    const nn = collapseNode(n);
    if (nn.meta?.collapse && prev) {
      if (nn.meta?.collapse === prev.meta?.collapse) {
        id_counter += 1;
        const new_node: TracingNode = {
          uid: "" + id_counter,
          name: "2 " + prev.meta?.collapse,
          meta: {
            icon: prev.meta?.icon
          },
          children: [prev, nn],
          group_node: prev.meta?.collapse,
        };
        children[children.length - 1] = new_node;
        prev = new_node;
        continue;
      }
      if (nn.meta?.collapse === prev.group_node) {
        prev.children!.push(nn);
        prev.name = "" + prev.children!.length + " " + nn.meta?.collapse;
        prev = nn;
        continue;
      }
    }
    children.push(nn);
    prev = nn;
  }
  return {
    ...node,
    children
  }
}

function App(props: { root: TracingNode }) {
  const cRoot = useMemo(() => collapseNode(props.root), [props.root]);
  const [state, setState] = useState<TreeState>(() => {
    const opened = new Set<string>;
    let node = cRoot;
    while (node?.children?.length == 1) {
      opened.add(node.uid);
      node = node.children[0]
    }
    opened.add(node.uid);
    return { opened, selected: cRoot }
  });
  return (
    <div className="nt-root-container">
      <div className='nt-panel'><TreeView root={cRoot} treeState={state} setTreeState={setState} /></div>
      <div className='nt-main-content'>
        <h1>{createNodeIcon(state.selected)}{state.selected.name}</h1>
        <NodeDetail node={state.selected} />
      </div>
    </div>
  )
}

export default App
