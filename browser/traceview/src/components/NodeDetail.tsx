import { TracingNode } from "../model/Node";
import { DataRenderer } from "./DataRenderer";
import "./NodeDetail.css";

function InputBox(props: { name: string, value: unknown }) {
    return (<div className="nt-box nt-input">
        <div className="nt-box-title"><span className="nt-box-kind">Input</span> {props.name}<hr /></div>
        <div className="nt-box-content"><DataRenderer data={props.value} /></div></div>);
}


function OutputBox(props: { value: unknown }) {
    return (<div className="nt-box nt-output">
        <div className="nt-box-title"><span className="nt-box-kind">Output</span><hr /></div>
        <div className="nt-box-content"><DataRenderer data={props.value} /></div></div>);
}

function ErrorBox(props: { value: unknown }) {
    return (<div className="nt-box nt-error-box">
        <div className="nt-box-title"><span className="nt-box-kind">Error</span><hr /></div>
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
            const element = <InputBox name={property} value={value} />;
            boxes.push(element);
        }
    }

    if (node.output !== undefined) {
        boxes.push(<OutputBox value={node.output} />)
    }

    if (node.error !== undefined) {
        boxes.push(<ErrorBox value={node.error} />)
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