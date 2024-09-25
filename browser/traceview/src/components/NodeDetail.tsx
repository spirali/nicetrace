import copy from "copy-to-clipboard";
import { Entry, TracingNode } from "../model/Node";
import { DataRenderer } from "./DataRenderer";
import "./NodeDetail.css";
import { useState } from "react";
import { GiEntryDoor } from "react-icons/gi";

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
    if (copy(dataToText(obj))) {
        setCopied(true)
    }
};

function DataBox(props: { entry: Entry }) {
    const [copied, setCopied] = useState<boolean>(false);
    const entry = props.entry;
    let className;
    if (entry.kind == "error") {
        className = "nt-error-box";
    } else if (entry.kind == "output") {
        className = "nt-output";
    } else {
        className = "nt-input"
    }

    const kind = entry.kind.charAt(0).toUpperCase() + entry.kind.slice(1);

    return (<div className={"nt-box " + className}>
        <div className="nt-box-title">
            <span><span className="nt-box-kind">{kind}</span> {entry.name}</span>
            <div>{copied ? "Copied " : null}<button className="small-button" onClick={() => copyToClipboard(entry.value, setCopied)}>Copy</button></div>
        </div>
        <hr />
        <div className="nt-box-content"><DataRenderer data={entry.value} /></div></div>);
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
    const counters = new Map;
    collectCounters(node, counters);
    let counterPanel;
    if (counters.size > 0) {
        const entries = [...counters.entries()];
        counterPanel = <div className="nt-counters">{entries.map(([key, value]) => <CounterBox value={key + ": " + value} />)}</div>
    }
    return <div>{counterPanel}{props.node.entries ? props.node.entries.map((e, i) => <DataBox key={props.node.uid + "/" + i} entry={e} />) : null}</div>
}