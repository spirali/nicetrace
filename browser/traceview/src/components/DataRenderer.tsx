import parse from 'html-react-parser';
import { useState } from 'react';
import { computeComplexity } from '../common/complexity';

const IMAGE_MIME_TYPES = ["image/jpeg", "image/png"];
const COMPLEXITY_LIMIT = 10;
const MAX_LINES = 12;
const MAX_LINE_CHARS = 140;

type TracebackFrame = {
    line: string,
    name: string,
    filename: string,
    lineno: number,
}

function Frame(props: { frame: TracebackFrame }) {
    return <div>
        <div>
            File <strong>{props.frame.filename}</strong>, line <strong>{props.frame.lineno}</strong>, in <strong>{props.frame.name}</strong>
        </div>
        <div style={{ color: "#dd5555" }}>
            <strong>{props.frame.line}</strong>
        </div>
    </div >
}

function Traceback(props: { frames: TracebackFrame[] }) {
    const frames = props.frames;
    if (!frames || !(frames.length >= 1)) {
        return <span>Invalid traceback</span>;
    }
    // const isOpened = props.env.opened.has(props.uid);
    // if (!isOpened) {
    //     frames = frames.slice(-2);
    // }

    return <div style={{ fontFamily: 'Monospace' }}>
        {frames.map((frame, i) => <Frame frame={frame} key={i} />)}
        {/* </Box>
        {props.frames.length > 2 && isOpened && <Button onClick={() => props.env.setOpen(props.uid, OpenerMode.Close)}>Hide full traceback</Button>}
        {props.frames.length > 2 && !isOpened && <Button onClick={() => props.env.setOpen(props.uid, OpenerMode.Open)}> Show all {props.frames.length} frames</Button>} */}
    </div>

}


function shortenString(str: string, max_lines: number, max_line_length: number): [string, number] {
    let lines = str.split('\n');
    let skippedChars = 0;
    if (lines.length > max_lines) {
        skippedChars += lines.slice(max_lines).join('\n').length;
        lines = lines.slice(0, max_lines);
    }
    lines = lines.map(line => {
        if (line.length > max_line_length + 4) {
            skippedChars += line.length - max_line_length;
            return line.slice(0, max_line_length) + '...';
        }
        return line;
    });
    return [lines.join('\n'), skippedChars]
}


export function DataRenderer(props: { data: any }) {
    const [open, setOpen] = useState<boolean>(false);
    const d = props.data;
    let result;
    let showButton = null;
    if (d === null) {
        return <>None</>
    } else if (typeof d === 'boolean') {
        return <>{d ? "true" : "false"}</>
    } else if (typeof d === 'number') {
        return <>{d}</>
    } else if (typeof d === 'string') {
        if (open) {
            result = <>{d}</>
            showButton = `Hide full string`
        } else {
            const [s, skippedChars] = shortenString(d, MAX_LINES, MAX_LINE_CHARS);
            result = <>{s}</>
            if (skippedChars > 0) {
                showButton = `Show remaing ${skippedChars} characters`
            }
        }
    } else if ((d._type === "$html") && d.html) {
        result = parse(d.html);
    } else if ((d._type === "$blob") && IMAGE_MIME_TYPES.includes(d.mime_type)) {
        const data = `data:${d.mime_type};base64, ${d.data}`;
        result = <img src={data} />
    } else if ((d._type === "$traceback")) {
        result = <Traceback frames={d.frames} />
    } else {
        const children = [];
        let complexity = 0;
        let skipped = 0;
        for (const property in d) {
            if (property === "_type") {
                continue;
            }
            const value = d[property];

            if (skipped == 0) {
                complexity += computeComplexity(value)
            }
            if (complexity > COMPLEXITY_LIMIT) {
                skipped += 1;
                if (!open) {
                    continue
                }
            }

            children.push({ property, value });
        }
        if (skipped > 0) {
            if (!open) {
                showButton = `Show remaing ${skipped} items`
            } else {
                showButton = `Hide items`
            }
        }
        result =
            <ul style={{ paddingTop: 0, paddingBottom: 0, margin: 0, paddingLeft: 25 }}>
                {children.map(({ property, value }) => <li style={{ padding: 0, margin: 0 }} key={property}><strong>{property}</strong>: <DataRenderer data={value} /></li>)}
            </ul>;
    }
    if (showButton) {
        const button = <button onClick={() => setOpen(!open)}>{showButton}</button>;
        return <><div>{result}</div><div>{button}</div></>
    } else {
        return result
    }
    // if (computeComplexity(d) > 10) {
    //     const button = <button onClick={() => setOpen(!open)}>{open ? "Hide value" : "Show value"}</button>;
    //     return <div>{button}{open ? result : null}</div>
    // } else {
    //     return result
    // }
}
