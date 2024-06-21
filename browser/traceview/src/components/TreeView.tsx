import { TreeState } from "../App";
import { createNodeIcon } from "../common/icons";
import { humanReadableDuration, nodeDuration } from "../common/time";
import { TracingNode } from "../model/Node"
import "./TreeView.css"
import { FaCaretDown, FaCaretRight } from "react-icons/fa6"
import { MdError } from "react-icons/md";

function TreeNode(props: { node: TracingNode, treeState: TreeState, setTreeState: (n: TreeState) => void }) {
    const node = props.node;
    const isSelected = node.uid === props.treeState.selected.uid;
    const isOpen = props.treeState.opened.has(node.uid);
    let children;
    if (isOpen && node.children && node.children.length > 0) {
        children = <div className="tree-children"><ul>{node.children.map((c) => <TreeNode node={c} treeState={props.treeState} setTreeState={props.setTreeState} />)}</ul></div>;
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

    let expandIcon;
    if (node.children) {
        if (!isOpen) {
            expandIcon = <FaCaretRight className="icon" onClick={onToggle} />
        } else {
            expandIcon = <FaCaretDown className="icon" onClick={onToggle} />
        }
    }

    let statusIcon;
    if (node.state === "error") {
        statusIcon = <MdError color="red" className="icon" />
    } else if (node.state === "open") {
        statusIcon = null;
    }

    const duration = nodeDuration(node);

    return (<li>
        <div className={"box" + (isSelected ? " selected" : "")} onClick={onSelect}>
            {expandIcon} <span className={node.state === "error" ? "nt-tree-error" : ""}>{createNodeIcon(node, 20)}{statusIcon}{node.name}</span> {duration && <span className="nt-node-duration">{humanReadableDuration(duration)}</span>}</div >
        {children}</li >)
}


export function TreeView(props: { root: TracingNode, treeState: TreeState, setTreeState: (n: TreeState) => void }) {
    return (<div className="tree">
        <ul>
            <TreeNode node={props.root} treeState={props.treeState} setTreeState={props.setTreeState} />
        </ul>
    </div>);
}