export interface Tag {
    // TODO
}

export interface Metadata {
    color?: string,
    icon?: string,
    tags?: Tag[],
    counters?: any,
}

export interface TracingNode {
    uid: string;
    name: string;
    kind?: string;
    state?: "open" | "error";
    inputs?: any;
    output?: any;
    error?: any;
    meta?: Metadata;
    children?: TracingNode[];
    start_time?: string;
    end_time?: string;
}