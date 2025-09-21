const { Firestore } = require("@google-cloud/firestore");
const firestore = new Firestore();

async function logToFirestore(data) {
  const ref = firestore.collection("analysis_logs");
  await ref.add({
    ...data,
    timestamp: new Date().toISOString(),
  });
}

module.exports = { logToFirestore };
