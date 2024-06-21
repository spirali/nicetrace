import parse from 'html-react-parser';

const IMAGE_MIME_TYPES = ["image/jpeg", "image/png"];

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
    let frames = props.frames;
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


export function DataRenderer(props: { data: any }) {
    const d = props.data;
    if (d === null) {
        return <>None</>
    }
    if (typeof d === 'boolean') {
        return <>{d ? "true" : "false"}</>
    }
    if (typeof d === 'number') {
        return <>{d}</>
    }
    if (typeof d === 'string') {
        return <>{d}</>
    }

    if ((d._type === "$html") && d.html) {
        return <>{parse(d.html)}</>;
    }

    // TODO: Remove "Blob" in future version
    if ((d._type === "Blob" || d._type === "$blob") && IMAGE_MIME_TYPES.includes(d.mime_type)) {
        const data = `data:${d.mime_type};base64, ${d.data}`;
        // const height = !isOpen ? 120 : undefined;
        // eslint-disable-next-line jsx-a11y/alt-text
        return <img src={data} />
    }

    if ((d._type === "$traceback")) {
        return <Traceback frames={d.frames} />
    }

    const children = [];
    let type = null;
    for (const property in d) {
        const value = d[property];
        if (property === "_type") {
            // type = value;
            continue;
        }
        children.push({ property, value });
    }

    // const isLong = children.length > 3;

    // if (isLong && !opened.has(props.uid)) {
    //     return <>
    //         {(props.hideType !== type && type) && <>{type}</>}
    //         <Button onClick={() => setOpen(props.uid, OpenerMode.Open)}>Show {children.length} items</Button>
    //     </>
    // }
    // {(props.hideType !== type && type) && <>{type}</>}
    // {isLong && <Button onClick={() => setOpen(props.uid, OpenerMode.Close)}>Hide items</Button>}

    return (<>
        <ul style={{ paddingTop: 0, paddingBottom: 0, margin: 0, paddingLeft: 25 }}>
            {children.map(({ property, value }) => <li style={{ padding: 0, margin: 0 }} key={property}><strong>{property}</strong>: <DataRenderer data={value} /></li>)}
        </ul>
    </>);
}

