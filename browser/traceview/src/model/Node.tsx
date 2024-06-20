
export interface TracingNode {
    uid: string;
    name: string;
    kind?: string;
    inputs?: any;
    output?: any;
    children?: TracingNode[];
}