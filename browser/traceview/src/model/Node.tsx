
export interface TracingNode {
    uid: string;
    name: string;
    kind?: string;
    children?: TracingNode[];
}