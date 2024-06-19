import { TreeState } from "../App";
import { TracingNode } from "../model/Node"
import "./TreeView.css"
import { FaCaretDown, FaCaretRight } from "react-icons/fa6"

function TreeNode(props: { node: TracingNode, treeState: TreeState, setTreeState: (n: TreeState) => void }) {
    const node = props.node;
    const isSelected = node.uid === props.treeState.selected.uid;
    const isOpen = props.treeState.opened.has(node.uid);
    let children;
    if (isOpen && node.children && node.children.length > 0) {
        children = <ul>{node.children.map((c) => <TreeNode node={c} treeState={props.treeState} setTreeState={props.setTreeState} />)}</ul>;
    }

    const onSelect = (event: React.MouseEvent<unknown>) => {
        props.setTreeState({
            ...props.treeState,
            selected: node,
        })
        event.preventDefault();
        event.stopPropagation();
    };

    const onToggle = (event: React.MouseEvent<unknown>) => {
        const clonedSet = new Set(props.treeState.opened);
        if (isOpen) {
            clonedSet.delete(node.uid);
        } else {
            clonedSet.add(node.uid);
        }

        props.setTreeState({
            ...props.treeState,
            opened: clonedSet,
        })

        event.stopPropagation()
        event.preventDefault()
    };

    let icon;
    if (node.children) {
        if (!isOpen) {
            icon = <FaCaretRight className="icon" onClick={onToggle} />
        } else {
            icon = <FaCaretDown className="icon" onClick={onToggle} />
        }
    }

    return (<li><div className={(isSelected ? "selected" : "") + " box"} onClick={onSelect}>
        {icon}<span>{node.name}</span></div><div className="tree-children">{children}</div></li>)
}

export function TreeView(props: { root: TracingNode, treeState: TreeState, setTreeState: (n: TreeState) => void }) {
    return (<div className="tree">
        <ul>
            <TreeNode node={props.root} treeState={props.treeState} setTreeState={props.setTreeState} />
        </ul>
    </div>);
}