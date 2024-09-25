export function computeComplexity(data: any): number {
    const d = data;
    if (d === null || typeof d === 'boolean' || typeof d === 'number') {
        return 1;
    }
    if (typeof d === 'string') {
        return nLines(d)
    }
    let complexity = 1;
    for (const property in d) {
        if (property === "_type") {
            continue;
        }
        complexity += computeComplexity(d[property]);
    }
    return complexity;
}


function nLines(s: string) {
    let count = 1;
    for (let i = 0; i < s.length; ++i) {
        if (s[i] == '\n') {
            count++;
        }
    }
    return count;
}