
export interface TracingNode {
    uid: string;
    name: string;
    kind?: string;
    state?: "open" | "error";
    inputs?: any;
    output?: any;
    meta?: any;
    children?: TracingNode[];
    start_time?: string;
    end_time?: string;
}