export interface Log {
    message: any;
    level: number;
}
export declare function isLog(arg: any): arg is Log;
export declare function isLogArray(arg: any): arg is Log[];
