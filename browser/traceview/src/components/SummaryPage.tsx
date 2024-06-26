import axios from "axios";
import { useEffect, useState } from "react";
import BarLoader from "react-spinners/BarLoader";
import { SummaryList } from "./SummaryList";
import { Summary } from "../model/Summary";

function sortSummaries(summaries: Summary[]): Summary[] {
    summaries.sort((a, b) => {
        if (a.state === "open" && b.state !== "open") {
            return -1;
        }
        if (a.state !== "open" && b.state === "open") {
            return 1;
        }
        const date_a = new Date(a.start_time);
        const date_b = new Date(b.start_time);
        if (date_a == date_b) {
            return 0;
        }
        return date_a > date_b ? -1 : 1;
    })
    return summaries;
}

export function SummaryPage(props: { url: string }) {
    const [data, setData] = useState<Summary[] | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [loaded, setLoaded] = useState(false);

    useEffect(() => {
        axios
            .get(props.url + "api/list")
            .then((response) => setData(sortSummaries(response.data)))
            .catch((error) => setError("Could not fetch data: " + error.message))
            .finally(() => setLoaded(true));
    }, [props.url]);

    if (!loaded) {
        return <BarLoader style={{ margin: "auto" }} />
    }
    if (error) {
        return <div className="nt-app-error">Error: {error}</div>
    }

    return (<div className="nt-summary-page">
        <SummaryList summaries={data!} />
    </div>)
}