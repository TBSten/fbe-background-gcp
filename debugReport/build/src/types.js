"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.isLogArray = exports.isLog = void 0;
function isLog(arg) {
    return (typeof arg === "object" &&
        typeof arg.level === "number");
}
exports.isLog = isLog;
function isLogArray(arg) {
    // console.log("isLogArray", arg)
    return (arg &&
        arg instanceof Array &&
        arg.reduce((ans, e) => (ans && isLog(e)), true));
}
exports.isLogArray = isLogArray;
//# sourceMappingURL=types.js.map