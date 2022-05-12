"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const datastore_1 = require("@google-cloud/datastore");
const datastore = new datastore_1.Datastore({
    projectId: "fbe-gcp-project",
    namespace: "practice",
});
datastore.save({
    key: datastore.key(""),
    data: {
        "xxx": 123,
        "yyy": 456,
    }
});
//# sourceMappingURL=test.js.map