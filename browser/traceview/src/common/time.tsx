import { TracingNode } from "../model/Node";

export function humanReadableDuration(value: number) {
    if (value < 500) {
        return `${value}ms`
    }
    value /= 1000;
    if (value < 120) {
        return `${(value).toFixed(1)}s`
    }
    value /= 60;
    if (value < 120) {
        return `${(value).toFixed(0)}m`
    }
    value /= 60;
    if (value < 48) {
        return `${(value).toFixed(0)}h`
    }
    value /= 24;
    return `${(value).toFixed(0)} days`

}

export function nodeDuration(ctx: TracingNode): number | null {
    if (ctx.start_time && ctx.end_time) {
        const start = new Date(ctx.start_time);
        const end = new Date(ctx.end_time);
        return end.getTime() - start.getTime();
    } else if (ctx.start_time && !ctx.end_time && ctx.state === "open") {
        const start = new Date(ctx.start_time);
        return Date.now() - start.getTime();
    } else {
        return null;
    }
}