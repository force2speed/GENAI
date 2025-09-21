import { motion, useInView } from "framer-motion";
import { useRef, useState } from "react";
import PropTypes from "prop-types";

// The ResponseDisplay component is now defined in the same file to resolve the import error.
const ResponseDisplay = ({ response }) => {
  const [showRaw, setShowRaw] = useState(false);

  if (!response) return null;

  // MODIFIED: Updated logic to handle 'audio' type responses.
  let results;
  const isImage = response.type === "image" && response.misinformation_analysis;
  const isText = response.type === "text" && response.results?.results;
  const isDocument =
    response.type === "document" && response.misinformation_analysis;
  const isAudio = response.type === "audio" && response.misinformation_analysis;

  if (isImage || isDocument || isAudio) {
    // Image, document, and audio responses have analysis in misinformation_analysis
    results = response.misinformation_analysis;
  } else if (isText) {
    // Text responses have a nested results object
    results = response.results.results;
  } else {
    // Fallback for other potential response structures
    results = response.results || {};
  }

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
      className="mt-8 w-full max-w-2xl bg-neutral-800 p-6 rounded-2xl shadow-xl border border-neutral-700"
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

      {/* For document (PDF): show extracted text */}
      {isDocument && response.extracted?.document_text && (
        <div className="mb-6 p-4 bg-neutral-900 rounded-xl border border-neutral-700">
          <h4 className="text-neutral-300 font-medium mb-2">
            Extracted Text from Document:
          </h4>
          <pre className="text-neutral-200 whitespace-pre-wrap font-sans text-sm max-h-60 overflow-y-auto">
            {response.extracted.document_text}
          </pre>
        </div>
      )}

      {/* ADDED: For audio: show extracted transcript */}
      {isAudio && response.extracted?.audio_transcript && (
        <div className="mb-6 p-4 bg-neutral-900 rounded-xl border border-neutral-700">
          <h4 className="text-neutral-300 font-medium mb-2">
            Extracted Audio Transcript:
          </h4>
          <p className="text-neutral-200 italic">
            &quot;{response.extracted.audio_transcript}&quot;
          </p>
        </div>
      )}

      {/* Summary */}
      <div className="p-4 bg-neutral-900 rounded-xl border border-neutral-700 mb-4">
        <p className="text-sm text-neutral-400">Assessment</p>
        <p className="text-lg font-semibold text-white">{assessment}</p>
      </div>
      <div className="p-4 bg-neutral-900 rounded-xl border border-neutral-700 mb-4">
        <p className="text-sm text-neutral-400">Confidence</p>
        <p className="text-lg font-semibold text-blue-400">{confidenceLevel}</p>
      </div>
      <div className="p-4 bg-neutral-900 rounded-xl border border-neutral-700 mb-4">
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

const InputForm = () => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [shortPrompt, setShortPrompt] = useState("");
  const [prompt, setPrompt] = useState("");
  const [files, setFiles] = useState({
    Image: null,
    Audio: null,
    Text: null,
    Video: null, // Kept for logic consistency, though not in UI
    PDF: null,
  });
  const [responseData, setResponseData] = useState(null);
  const [selectedFileType, setSelectedFileType] = useState("");

  const inputRefs = {
    Image: useRef(null),
    Audio: useRef(null),
    Text: useRef(null),
    Video: useRef(null),
    PDF: useRef(null),
  };

  const inputVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: (i) => ({
      opacity: 1,
      y: 0,
      transition: { delay: i * 0.2, duration: 0.5, ease: "easeOut" },
    }),
  };

  const handleFileChange = (type, file) => {
    const newFiles = {
      Image: null,
      Audio: null,
      Text: null,
      Video: null,
      PDF: null,
    };
    Object.keys(inputRefs).forEach((key) => {
      if (key !== type && inputRefs[key].current)
        inputRefs[key].current.value = "";
    });
    newFiles[type] = file;
    setFiles(newFiles);
  };

  const handleRemoveFile = (type) => {
    setFiles({ Image: null, Audio: null, Text: null, Video: null, PDF: null });
    if (inputRefs[type].current) inputRefs[type].current.value = "";
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const hasFile = Object.values(files).some((f) => f !== null);
    const hasPrompt = prompt.trim().length > 0;
    const hasShortPrompt = shortPrompt.trim().length > 0;

    if (!hasFile && !hasPrompt && !hasShortPrompt) {
      setSubmitted(false);
      return;
    }

    setLoading(true);
    setError("");
    setResponseData(null);

    try {
      let response;
      let data;

      if ((hasPrompt || hasShortPrompt) && !hasFile) {
        response = await fetch(
          "https://misinfo-backend-622658282319.asia-south1.run.app/analyze-misinformation/detailed",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              text: hasShortPrompt ? shortPrompt : prompt,
            }),
          }
        );
        data = await response.json();
        data = { type: "text", results: data };
      }

      if (hasFile) {
        const formData = new FormData();
        let endpoint = "";

        if (files.Image) {
          formData.append("file", files.Image);
          endpoint =
            "https://misinfo-backend-622658282319.asia-south1.run.app/analyze-image";
        } else if (files.Audio) {
          formData.append("file", files.Audio);
          endpoint =
            "https://misinfo-backend-622658282319.asia-south1.run.app/analyze-audio";
        } else if (files.PDF) {
          formData.append("file", files.PDF);
          endpoint =
            "https://misinfo-backend-622658282319.asia-south1.run.app/analyze-document";
        } else if (files.Text) {
          const textContent = await files.Text.text();
          response = await fetch(
            "https://misinfo-backend-622658282319.asia-south1.run.app/analyze-misinformation/detailed",
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ text: textContent }),
            }
          );
          data = await response.json();
          data = { type: "text", results: data };
        }

        if (endpoint) {
          response = await fetch(endpoint, { method: "POST", body: formData });
          if (!response.ok)
            throw new Error(`HTTP error! status: ${response.status}`);
          data = await response.json();
          if (files.Image) data.type = "image";
          // We can trust the backend to set the type for audio and document
        }
      }

      setResponseData(data);
      setSubmitted(true);
    } catch (err) {
      console.error("❌ Submission failed:", err);
      setError("Failed to analyze the content. Please try again.");
      setSubmitted(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      ref={ref}
      className="relative mt-20 border-b border-neutral-800 min-h-[600px] flex flex-col justify-center items-center px-4"
    >
      <motion.h1
        initial={{ opacity: 0, y: -30 }}
        animate={isInView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.7, ease: "easeOut" }}
        className="text-4xl sm:text-5xl font-bold text-center mb-12"
      >
        <span className="bg-gradient-to-r from-orange-500 to-red-700 text-transparent bg-clip-text">
          Submit Your Content
        </span>
      </motion.h1>

      <motion.form
        initial={{ opacity: 0, scale: 0.9 }}
        animate={isInView ? { opacity: 1, scale: 1 } : {}}
        transition={{ duration: 0.6, ease: "easeOut" }}
        onSubmit={handleSubmit}
        className="w-full max-w-2xl bg-neutral-900 p-8 sm:p-10 rounded-3xl shadow-2xl border border-neutral-800"
      >
        <motion.h2
          initial={{ opacity: 0, y: -20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="text-3xl sm:text-4xl text-center font-semibold mb-10"
        >
          <span className="bg-gradient-to-r from-orange-500 to-orange-800 text-transparent bg-clip-text">
            Upload & Submit
          </span>
        </motion.h2>

        <motion.input
          custom={0}
          variants={inputVariants}
          initial="hidden"
          animate={isInView ? "visible" : "hidden"}
          type="text"
          placeholder="Enter a short text claim..."
          value={shortPrompt}
          onChange={(e) => setShortPrompt(e.target.value)}
          className="w-full p-4 mb-6 rounded-2xl bg-neutral-800 text-white text-lg border border-neutral-700 shadow-inner focus:outline-none focus:ring-4 focus:ring-orange-500 focus:ring-opacity-50 hover:shadow-lg transition-all duration-300 placeholder:text-neutral-500 placeholder:italic"
        />
        <motion.textarea
          custom={1}
          variants={inputVariants}
          initial="hidden"
          animate={isInView ? "visible" : "hidden"}
          placeholder="Write your detailed prompt here..."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          className="w-full h-40 p-6 mb-8 rounded-2xl bg-neutral-800 text-white text-lg border border-neutral-700 shadow-inner focus:outline-none focus:ring-4 focus:ring-orange-500 focus:ring-opacity-50 hover:shadow-lg transition-all duration-300 placeholder:text-neutral-500 placeholder:italic"
        />

        <div className="space-y-6 mb-8">
          <motion.div
            custom={2}
            variants={inputVariants}
            initial="hidden"
            animate={isInView ? "visible" : "hidden"}
          >
            <label
              htmlFor="fileType"
              className="block mb-2 text-sm font-medium text-neutral-400"
            >
              Or, upload a file
            </label>
            <select
              id="fileType"
              value={selectedFileType}
              onChange={(e) => {
                setSelectedFileType(e.target.value);
                setFiles({
                  Image: null,
                  Audio: null,
                  Text: null,
                  Video: null,
                  PDF: null,
                });
              }}
              className="w-full p-4 rounded-2xl bg-neutral-800 text-white text-lg border border-neutral-700 shadow-inner focus:outline-none focus:ring-4 focus:ring-orange-500 focus:ring-opacity-50 transition-all duration-300"
            >
              <option value="">Select file type...</option>
              <option value="Image">Image</option>
              <option value="Audio">Audio</option>
              <option value="Text">Text (.txt)</option>
              <option value="PDF">PDF</option>
            </select>
          </motion.div>

          {selectedFileType && (
            <motion.div
              key={selectedFileType}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
            >
              <label className="block mb-2 text-sm font-medium text-neutral-400">
                Upload {selectedFileType}
              </label>
              <input
                ref={inputRefs[selectedFileType]}
                type="file"
                accept={
                  selectedFileType === "Image"
                    ? "image/*"
                    : selectedFileType === "Audio"
                    ? "audio/*"
                    : selectedFileType === "PDF"
                    ? "application/pdf"
                    : ".txt"
                }
                onChange={(e) =>
                  handleFileChange(selectedFileType, e.target.files[0])
                }
                className="w-full text-sm text-neutral-300 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-orange-600 file:text-white hover:file:bg-orange-700 transition"
              />

              {files[selectedFileType] && (
                <div className="flex flex-col mt-3 bg-neutral-800 p-3 rounded-lg w-full">
                  <span className="text-sm text-neutral-300 break-words truncate">
                    {files[selectedFileType].name}
                  </span>
                  <button
                    type="button"
                    onClick={() => handleRemoveFile(selectedFileType)}
                    className="mt-2 px-3 py-1 text-sm bg-red-600 hover:bg-red-700 text-white rounded-lg transition self-start"
                  >
                    Remove
                  </button>
                </div>
              )}
            </motion.div>
          )}
        </div>

        <button
          type="submit"
          disabled={loading}
          className={`w-full py-3 px-6 rounded-2xl font-semibold text-lg transform transition duration-300 shadow-md ${
            loading
              ? "bg-neutral-700 text-neutral-400 cursor-not-allowed"
              : "bg-gradient-to-r from-orange-500 to-orange-800 text-white hover:scale-105 hover:shadow-lg"
          }`}
        >
          {loading ? "Analyzing..." : "Submit for Analysis"}
        </button>

        {error && (
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6 text-center text-red-400 font-medium"
          >
            {error}
          </motion.p>
        )}
      </motion.form>

      {submitted && responseData && <ResponseDisplay response={responseData} />}
    </div>
  );
};

export default InputForm;
