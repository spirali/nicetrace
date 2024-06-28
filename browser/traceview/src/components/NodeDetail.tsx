import copy from "copy-to-clipboard";
import { TracingNode } from "../model/Node";
import { DataRenderer } from "./DataRenderer";
import "./NodeDetail.css";
import { useState } from "react";

const dataToText = (obj: unknown): string => {
    if (obj === null) {
        return "None"
    }
    if (typeof obj === 'boolean') {
        return obj ? "true" : "false"
    }
    if (typeof obj === 'number') {
        return "" + obj
    }
    if (typeof obj === 'string') {
        return obj
    }
    return JSON.stringify(obj, null, 2);
}

const copyToClipboard = (obj: unknown, setCopied: (x: boolean) => void) => {
    console.log("COPY")
    console.log(dataToText(obj))
    if (copy(dataToText(obj))) {
        setCopied(true)
    }
};

function DataBox(props: { className: string, typeName: string, name?: string, value: unknown }) {
    const [copied, setCopied] = useState<boolean>(false);

    return (<div className={"nt-box " + props.className}>
        <div className="nt-box-title">
            <span><span className="nt-box-kind">{props.typeName}</span> {props.name}</span>
            <div>{copied ? "Copied " : null}<button onClick={() => copyToClipboard(props.value, setCopied)}>Copy</button></div>
        </div>
        <hr />
        <div className="nt-box-content"><DataRenderer data={props.value} /></div></div>);
}

export function CounterBox(props: { value: string }) {
    return <span className="nt-counter-box">{props.value}</span>
}


function collectCounters(node: TracingNode, map: Map<string, number>) {
    if (node.meta && node.meta?.counters) {
        for (const property in node.meta.counters) {
            const value = node.meta.counters[property];
            if (map.has(property)) {
                map.set(property, value + map.get(property));
            } else {
                map.set(property, value);

            }
        }
    }
    if (node.children) {
        for (const n of node.children) {
            collectCounters(n, map);
        }
    }
}


export function NodeDetail(props: { node: TracingNode }) {
    const node = props.node;
    const boxes = [];
    if (node.inputs) {
        for (const property in node.inputs) {
            const value = node.inputs[property];
            const element = <DataBox key={props.node.uid + "/" + boxes.length} className="nt-input" name={property} typeName="Input" value={value} />;
            boxes.push(element);
        }
    }

    if (node.output !== undefined) {
        boxes.push(<DataBox key={props.node.uid + "/" + boxes.length} className="nt-output" typeName="Output" value={node.output} />)
    }

    if (node.error !== undefined) {
        boxes.push(<DataBox key={props.node.uid + "/" + boxes.length} className="nt-error-box" typeName="Error" value={node.error} />)
    }

    const counters = new Map;
    collectCounters(node, counters);
    let counterPanel;
    if (counters.size > 0) {
        const entries = [...counters.entries()];
        counterPanel = <div className="nt-counters">{entries.map(([key, value]) => <CounterBox value={key + ": " + value} />)}</div>
    }
    return <div>{counterPanel}{boxes}</div>
}