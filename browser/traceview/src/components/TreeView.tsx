import PulseLoader from "react-spinners/PulseLoader";
import { TreeState } from "./NodeView";
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
        children = <div className="nt-tree-children"><ul>{node.children.map((c) => <TreeNode key={c.uid} node={c} treeState={props.treeState} setTreeState={props.setTreeState} />)}</ul></div>;
    }
    let color = node?.meta?.color;
    if (node.state === "error") {
        color = "red";
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
            expandIcon = <FaCaretRight className="nt-expand-icon" onClick={onToggle} size={20} />
        } else {
            expandIcon = <FaCaretDown className="nt-expand-icon" onClick={onToggle} size={20} />
        }
    } else {
        expandIcon = <span className="nt-no-expand" />
    }

    let statusIcon;
    if (node.state === "error") {
        statusIcon = <MdError color="red" className="icon" size={20} />
    } else if (node.state === "open") {
        statusIcon = <PulseLoader color={color} margin={1} style={{ marginRight: 10 }} speedMultiplier={0.7} size={7} className="icon" />;
    }

    const duration = nodeDuration(node);

    let name;
    if (node.group_node) {
        name = <span className="nt-group">{node.name}</span>
    } else {
        name = node.name;
    }

    return (<li>
        <div className={"nt-tree-row" + (isSelected ? " nt-tree-selected" : "")} onClick={onSelect}>
            {expandIcon} <span style={{ color }}>{createNodeIcon(node, 20)}{statusIcon}{name}</span> {duration && <span className="nt-node-duration">{humanReadableDuration(duration)}</span>}</div >
        {children}</li >)
}


export function TreeView(props: { root: TracingNode, treeState: TreeState, setTreeState: (n: TreeState) => void }) {
    return (<div className="nt-tree">
        <ul>
            <TreeNode node={props.root} treeState={props.treeState} setTreeState={props.setTreeState} />
        </ul>
    </div>);
}