
import type { HttpFunction } from '@google-cloud/functions-framework/build/src/functions';
import { Datastore } from "@google-cloud/datastore"
import { notImplementError } from './util';
import { v4 as uuidv4 } from "uuid";

const datastore = new Datastore({
    projectId: "fbe-gcp-project",
    namespace: "fbe",
});
const tmpSaveKey = datastore.key("tmpSave");

export const tmpSave: HttpFunction = (req, res) => {
    console.log("# request", req.method)
    try {
        enableCors(req, res);
        if (req.method === "GET") {
            return handleGet(req, res);
        } else if (req.method === "POST") {
            return handlePost(req, res);
        } else if (req.method == "OPTIONS") {
            return res;
        } else {
            throw notImplementError(`invalid method : ${req.method}`);
        }
    } catch (e) {
        console.error(e)
        console.log(e)
        console.trace()
        res.status(500).json({
            "message": "error",
            "error": e,
        })
    }
};

const handleGet: HttpFunction = async (req, res) => {
    const key = tmpSaveKey;
    const id = req.query.id;
    if (!(typeof id === "string")) throw notImplementError(`invalid id : ${id}`);
    console.log("id", id)
    const query = datastore.createQuery(key.kind);
    query.filter("tmpSaveId", id);
    const [results] = await query.run();
    if (results.length !== 1) throw notImplementError(`not exists result , id : ${id}`);
    const result = results[0].fbe;
    if (!result) throw notImplementError(`invalid fbe : ${result}`);
    res.json({
        message: "ok",
        result,
    })
}
const handlePost: HttpFunction = async (req, res) => {
    const key = tmpSaveKey;
    const tmpSaveId = uuidv4();
    const fbe = req.body.fbe;
    await datastore.save({
        key,
        excludeLargeProperties: true,
        data: {
            tmpSaveId,
            fbe,
        }
    });
    console.log("tmpSaveId", tmpSaveId)
    res.json({
        message: "ok",
        tmpSaveId,
    })
}


const enableCors: HttpFunction = (req, res) => {
    res.set('Access-Control-Allow-Origin', '*');

    // Send response to OPTIONS requests
    res.set('Access-Control-Allow-Methods', ["GET", "POST"]);
    res.set('Access-Control-Allow-Headers', 'Content-Type');
    res.set('Access-Control-Max-Age', '3600');
    if (req.method === 'OPTIONS') {
        res.status(204).send('').end();
    }
}

