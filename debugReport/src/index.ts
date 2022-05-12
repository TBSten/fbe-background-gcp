
import type { HttpFunction } from '@google-cloud/functions-framework/build/src/functions';
import { Datastore } from "@google-cloud/datastore"
import { isLogArray } from './types';
import { notImplementError } from './util';

const datastore = new Datastore({
  projectId: "fbe-gcp-project",
  namespace: "fbe",
});
export const debugReport: HttpFunction = (req, res) => {
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
  console.log("# request", req.method)
  try {
    enableCors(req, res);
    if (req.method === "POST") {
      return handlePost(req, res);
    } if (req.method == "OPTIONS") {
      return res;
    } else {
      throw notImplementError(`invalid method : ${req.method}`);
    }
  } catch (e) {
    console.error(e)
    console.log(e)
    res.status(500).json({
      "message": "error",
      "error": e,
    })
  }
};
const handlePost: HttpFunction = (req, res) => {
  const logs = req?.body?.logs;
  const reportNo = Math.floor(Math.random() * 1000000000000000)
  const created_at = new Date().valueOf();
  console.log("reportNo", reportNo);
  if (!isLogArray(logs)) throw notImplementError(`invalid req.body.logs ${logs}`);
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
    })
  }).catch(e => {
    console.error("error", e);
    res.status(500).json({
      "message": "error",
      "error": e,
    })
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

