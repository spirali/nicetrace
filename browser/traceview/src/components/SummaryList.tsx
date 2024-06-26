import { Link } from "react-router-dom";
import { humanReadableDuration } from "../common/time";
import { Summary } from "../model/Summary";
import "./SummaryList.css"
import { PulseLoader } from "react-spinners";


function getAge(time: string | null): number | null {
    if (time) {
        const start = new Date(time);
        return Date.now() - start.getTime();
    } else {
        return null;
    }
}

function StateLabel(props: { state: string }) {
    // let color;
    // if (props.state === "error") {
    //     color = "red";
    if (props.state === "open") {
        return <PulseLoader margin={1} color="orange" style={{ marginRight: 10 }} speedMultiplier={0.7} size={7} className="icon" />
    }
    return <>{props.state}</>
}

export function SummaryList(props: { summaries: Summary[] }) {
    if (props.summaries.length === 0) {
        return <div>No traces</div>
    }
    return <table className="nt-summary-tab">
        <thead>
            <tr>
                <th>Id</th>
                <th>Name</th>
                <th>State</th>
                <th>Age</th>
                <th>Finished at</th>
            </tr>
        </thead>
        {props.summaries.map((s) => {
            let color;
            if (s.state === "error") {
                color = "red";
            }
            if (s.state === "open") {
                color = "orange";
            }
            const age = getAge(s.start_time);
            return (<tr style={{ color }}>
                <td className="nt-summary-td"><Link to={"/traces/" + s.uid}>{s.uid}</Link></td>
                <td>{s.name}</td>
                <td><StateLabel state={s.state} /></td>
                <td>{age ? humanReadableDuration(age) : null}</td>
                <td>{s.end_time}</td></tr>);
        })}

    </table >
}