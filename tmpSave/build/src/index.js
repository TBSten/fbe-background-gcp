"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.tmpSave = void 0;
const datastore_1 = require("@google-cloud/datastore");
const util_1 = require("./util");
const uuid_1 = require("uuid");
const datastore = new datastore_1.Datastore({
    projectId: "fbe-gcp-project",
    namespace: "fbe",
});
const tmpSaveKey = datastore.key("tmpSave");
const tmpSave = (req, res) => {
    console.log("# request", req.method);
    try {
        enableCors(req, res);
        if (req.method === "GET") {
            return handleGet(req, res);
        }
        else if (req.method === "POST") {
            return handlePost(req, res);
        }
        else if (req.method == "OPTIONS") {
            return res;
        }
        else {
            throw (0, util_1.notImplementError)(`invalid method : ${req.method}`);
        }
    }
    catch (e) {
        console.error(e);
        console.log(e);
        console.trace();
        res.status(500).json({
            "message": "error",
            "error": e,
        });
    }
};
exports.tmpSave = tmpSave;
const handleGet = async (req, res) => {
    const key = tmpSaveKey;
    const id = req.query.id;
    if (!(typeof id === "string"))
        throw (0, util_1.notImplementError)(`invalid id : ${id}`);
    console.log("id", id);
    const query = datastore.createQuery(key.kind);
    query.filter("tmpSaveId", id);
    const [results] = await query.run();
    if (results.length !== 1)
        throw (0, util_1.notImplementError)(`not exists result , id : ${id}`);
    const result = results[0].fbe;
    if (!result)
        throw (0, util_1.notImplementError)(`invalid fbe : ${result}`);
    res.json({
        message: "ok",
        result,
    });
};
const handlePost = async (req, res) => {
    const key = tmpSaveKey;
    const tmpSaveId = (0, uuid_1.v4)();
    const fbe = req.body.fbe;
    await datastore.save({
        key,
        excludeLargeProperties: true,
        data: {
            tmpSaveId,
            fbe,
        }
    });
    console.log("tmpSaveId", tmpSaveId);
    res.json({
        message: "ok",
        tmpSaveId,
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