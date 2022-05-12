import { Datastore } from "@google-cloud/datastore";

const datastore = new Datastore({
    projectId: "fbe-gcp-project",
    namespace: "practice",
});
datastore.save({
    key: datastore.key(""),
    data: {
        "xxx": 123,
        "yyy": 456,
    }
})
