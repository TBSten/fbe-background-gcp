"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.debugReport = void 0;
const datastore_1 = require("@google-cloud/datastore");
const types_1 = require("./types");
const util_1 = require("./util");
const datastore = new datastore_1.Datastore({
    projectId: "fbe-gcp-project",
    namespace: "fbe",
});
const debugReport = (req, res) => {
    // const visit = {
    //   timestamp: new Date(),
    //   fromIp: req.ip,
    // };
    // console.log("visit", visit)
    // return insertVisit(visit).then(result => {
    //   console.log(result);
    //   res.status(200).json({
    //     "message": "ok",
    //     visit,
    //   })
    // })
    console.log("# request", req.method);
    try {
        enableCors(req, res);
        if (req.method === "POST") {
            return handlePost(req, res);
        }
        if (req.method == "OPTIONS") {
            return res;
        }
        else {
            throw (0, util_1.notImplementError)(`invalid method : ${req.method}`);
        }
    }
    catch (e) {
        console.error(e);
        console.log(e);
        res.status(500).json({
            "message": "error",
            "error": e,
        });
    }
};
exports.debugReport = debugReport;
const handlePost = (req, res) => {
    var _a;
    const logs = (_a = req === null || req === void 0 ? void 0 : req.body) === null || _a === void 0 ? void 0 : _a.logs;
    const reportNo = Math.floor(Math.random() * 1000000000000000);
    const created_at = new Date().valueOf();
    console.log("reportNo", reportNo);
    if (!(0, types_1.isLogArray)(logs))
        throw (0, util_1.notImplementError)(`invalid req.body.logs ${logs}`);
    const key = datastore.key("debug_report");
    // console.log("logs", logs);
    return datastore.save({
        key,
        excludeLargeProperties: true,
        data: {
            logs: [
                ...logs.map(log => ({
                    ...log,
                })),
            ],
            reportNo,
            created_at,
        }
    }).then(result => {
        // console.log("result", result);
        res.status(200).json({
            "message": "success",
            reportNo,
        });
    }).catch(e => {
        console.error("error", e);
        res.status(500).json({
            "message": "error",
            "error": e,
        });
    });
};
const enableCors = (req, res) => {
    res.set('Access-Control-Allow-Origin', '*');
    // Send response to OPTIONS requests
    res.set('Access-Control-Allow-Methods', ["GET", "POST"]);
    res.set('Access-Control-Allow-Headers', 'Content-Type');
    res.set('Access-Control-Max-Age', '3600');
    if (req.method === 'OPTIONS') {
        res.status(204).send('').end();
    }
};
//# sourceMappingURL=index.js.map