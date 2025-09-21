const { BigQuery } = require("@google-cloud/bigquery");
const bigquery = new BigQuery();

const datasetId = "misinfo_logs";
const tableId = "analysis";

async function logToBigQuery(data) {
  try {
    await bigquery.dataset(datasetId).table(tableId).insert([{
      ...data,
      timestamp: new Date().toISOString(),
    }]);
  } catch (err) {
    console.error("BigQuery Insert Error:", err);
  }
}

module.exports = { logToBigQuery };
