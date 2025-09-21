import { motion } from "framer-motion";
import { useState } from "react";
import PropTypes from "prop-types";

const ResponseDisplay = ({ response }) => {
  const [showRaw, setShowRaw] = useState(false);

  if (!response) return null;

  // Determine if it's an image response or text response
  const isImage = response.type === "image" && response.misinformation_analysis;
  const results = isImage
    ? response.misinformation_analysis
    : response.results || {};

  // Normalize fields for text responses
  const assessment = results.assessment || "N/A";
  const confidenceLevel =
    results.confidence_level || results.confidence || "N/A";
  const fakeScore =
    results.final_fake_score !== undefined ? results.final_fake_score : 0;

  if (!results) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="mt-8 w-full bg-neutral-800 p-6 rounded-2xl shadow-xl border border-neutral-700"
    >
      <h3 className="text-2xl font-bold text-orange-400 mb-6 text-center">
        Analysis Result
      </h3>

      {/* For image: show extracted text */}
      {isImage && response.extracted?.image_text && (
        <div className="mb-6 p-4 bg-neutral-900 rounded-xl border border-neutral-700">
          <p className="text-neutral-300 font-medium mb-2">
            Extracted Text from Image:
          </p>
          <p className="text-neutral-200">{response.extracted.image_text}</p>
        </div>
      )}

      {/* Summary */}
      <div className="p-4 bg-neutral-900 rounded-xl border border-neutral-700">
        <p className="text-sm text-neutral-400">Assessment</p>
        <p className="text-lg font-semibold text-white">{assessment}</p>
      </div>
      <div className="p-4 bg-neutral-900 rounded-xl border border-neutral-700">
        <p className="text-sm text-neutral-400">Confidence</p>
        <p className="text-lg font-semibold text-blue-400">{confidenceLevel}</p>
      </div>
      <div className="p-4 bg-neutral-900 rounded-xl border border-neutral-700">
        <p className="text-sm text-neutral-400">Fake Score</p>
        <p className="text-lg font-semibold text-red-400">
          {(fakeScore * 100).toFixed(1)}%
        </p>
      </div>

      {/* Claim Validations */}
      {results.claim_validations?.length > 0 && (
        <div className="mb-6">
          <h4 className="text-xl font-semibold text-white mb-4">
            Claim Validations
          </h4>
          {results.claim_validations.map((claim, idx) => (
            <div
              key={idx}
              className="p-4 mb-4 bg-neutral-900 rounded-xl border border-neutral-700"
            >
              <p className="text-lg font-bold text-orange-400 mb-2">
                {claim.claim}
              </p>
              <p className="text-sm text-neutral-300 mb-2">
                Confidence:{" "}
                <span className="text-blue-400">
                  {claim.confidence || claim.credibility_score}
                </span>
              </p>
              {claim.source_assessment && (
                <p className="text-sm text-neutral-300 mb-2">
                  Source:{" "}
                  <span className="text-red-400">
                    {claim.source_assessment}
                  </span>
                </p>
              )}
              {claim.explanation && (
                <p className="text-neutral-300 mb-2">{claim.explanation}</p>
              )}
              {claim.red_flags?.length > 0 && (
                <div className="mt-2">
                  <p className="text-sm text-red-400 font-semibold mb-1">
                    Red Flags:
                  </p>
                  <ul className="list-disc list-inside text-sm text-neutral-300">
                    {claim.red_flags.map((flag, fIdx) => (
                      <li key={fIdx}>{flag}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Stance Detections */}
      {results.stance_detections?.length > 0 && (
        <div className="mb-6">
          <h4 className="text-xl font-semibold text-white mb-4">
            Stance Detections
          </h4>
          {results.stance_detections.map((stance, idx) => (
            <div
              key={idx}
              className="p-4 mb-4 bg-neutral-900 rounded-xl border border-neutral-700"
            >
              <p className="text-lg font-bold text-orange-400 mb-2">
                {stance.claim}
              </p>
              <p className="text-sm text-neutral-300 mb-2">
                Stance: <span className="text-yellow-400">{stance.stance}</span>
              </p>
              <p className="text-sm text-neutral-300 mb-2">
                Confidence:{" "}
                <span className="text-blue-400">
                  {(stance.confidence * 100).toFixed(1)}%
                </span>
              </p>
              {stance.explanation && (
                <p className="text-neutral-300 mb-2">{stance.explanation}</p>
              )}
              {stance.key_phrases?.length > 0 && (
                <p className="text-sm text-neutral-400">
                  Key Phrases:{" "}
                  <span className="text-neutral-300">
                    {stance.key_phrases.join(", ")}
                  </span>
                </p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Indicators & Risks */}
      <div className="flex flex-wrap gap-2 mb-6">
        {results.credibility_indicators?.map((ind, idx) => (
          <span
            key={idx}
            className="px-3 py-1 rounded-full text-xs bg-green-600 text-white"
          >
            {ind}
          </span>
        ))}
        {results.risk_factors?.map((risk, idx) => (
          <span
            key={idx}
            className="px-3 py-1 rounded-full text-xs bg-red-600 text-white"
          >
            {risk}
          </span>
        ))}
      </div>

      {/* Processing Info (collapsible) */}
      {results.processing_info && (
        <details className="mb-6">
          <summary className="cursor-pointer text-orange-400 font-semibold">
            Processing Info
          </summary>
          <pre className="mt-2 text-sm text-neutral-300 bg-neutral-900 p-3 rounded-xl overflow-x-auto">
            {JSON.stringify(results.processing_info, null, 2)}
          </pre>
        </details>
      )}

      {/* Raw JSON toggle */}
      <button
        type="button"
        onClick={() => setShowRaw(!showRaw)}
        className="text-sm text-neutral-400 underline hover:text-orange-400 mt-4"
      >
        {showRaw ? "Hide Raw JSON" : "Show Raw JSON"}
      </button>

      {showRaw && (
        <pre className="mt-2 text-sm text-neutral-300 bg-neutral-900 p-3 rounded-xl overflow-x-auto">
          {JSON.stringify(response, null, 2)}
        </pre>
      )}
    </motion.div>
  );
};

ResponseDisplay.propTypes = {
  response: PropTypes.object.isRequired,
};

export default ResponseDisplay;
