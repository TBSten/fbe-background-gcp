export interface Log {
    message: any,
    level: number,
}


export function isLog(arg: any): arg is Log {
    return (
        typeof arg === "object" &&
        typeof arg.level === "number"
    );
}
export function isLogArray(arg: any): arg is Log[] {
    // console.log("isLogArray", arg)
    return (
        arg &&
        arg instanceof Array &&
        arg.reduce((ans, e) => (ans && isLog(e)), true)
    );
}

