export interface Tag {
    // TODO
}

export interface Metadata {
    color?: string,
    icon?: string,
    tags?: Tag[],
    counters?: any,
    collapse?: string,
}

export interface Entry {
    kind: string,
    name?: string,
    value: unknown,
}

export interface TracingNode {
    uid: string;
    name: string;
    kind?: string;
    state?: "open" | "error";
    entries?: Entry[],
    meta?: Metadata;
    children?: TracingNode[];
    start_time?: string;
    end_time?: string;

    group_node?: string,
}