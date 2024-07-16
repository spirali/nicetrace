import axios from "axios";
import { useCallback, useEffect, useState } from "react";
import BarLoader from "react-spinners/BarLoader";
import { useParams } from "react-router-dom";
import { NodeView } from "./NodeView";
import { TracingNode } from "../model/Node";

export function TracePage(props: { url: string }) {
    const { traceId } = useParams()
    const [data, setData] = useState<TracingNode | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [loaded, setLoaded] = useState(false);

    const reload = useCallback(() => {
        axios
            .get(props.url + "api/traces/" + traceId)
            .then((response) => setData(response.data))
            .catch((error) => setError("Could not fetch data: " + error.message))
            .finally(() => setLoaded(true));
    }, [props.url, traceId])

    useEffect(() => {
        reload()
    }, [reload]);

    if (!loaded) {
        return <BarLoader style={{ margin: "auto" }} />
    }
    if (error) {
        return <div className="nt-app-error">Error: {error}</div>
    }

    return <NodeView root={data!} enableActions={true} reload={reload} />
}