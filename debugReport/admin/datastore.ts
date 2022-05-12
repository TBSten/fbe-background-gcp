import { Datastore } from "@google-cloud/datastore"


async function main() {
    const datastore = new Datastore({
        projectId: "fbe-gcp-project",
        namespace: "fbe",
    });
    const key = datastore.key([5714489739575296]);
    const res = await datastore.get(key);
    console.log(res);

}

main();
