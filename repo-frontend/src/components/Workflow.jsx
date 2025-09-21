import { motion, useInView } from "framer-motion";
import { useRef } from "react";
import { CheckCircle2 } from "lucide-react";
import codeImg from "../assets/code.jpg";

const Workflow = () => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  const updatedChecklist = [
    {
      title: "Detect Misinformation",
      description:
        "Leverage AI to automatically identify content that may be false or misleading across social media and messaging platforms.",
    },
    {
      title: "Educate Users",
      description:
        "Provide insights and explanations on why a piece of content might be misleading, fostering critical thinking and digital literacy.",
    },
    {
      title: "Verify Credibility",
      description:
        "Help users quickly assess the trustworthiness of sources and the accuracy of information in real time.",
    },
    {
      title: "Empower Communities",
      description:
        "Encourage informed sharing practices, reducing the spread of fake news and promoting safer online interactions.",
    },
  ];

  const listVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: (i) => ({
      opacity: 1,
      y: 0,
      transition: { delay: i * 0.2, duration: 0.5, ease: "easeOut" },
    }),
  };

  return (
    <div ref={ref} className="mt-20">
      {/* Heading */}
      <motion.h2
        initial={{ opacity: 0, y: -30 }}
        animate={isInView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.7, ease: "easeOut" }}
        className="text-3xl sm:text-5xl lg:text-6xl text-center mt-6 tracking-wide"
      >
        Build an AI-powered tool to{" "}
        <span className="bg-gradient-to-r from-orange-500 to-orange-800 text-transparent bg-clip-text">
          combat misinformation
        </span>
      </motion.h2>

      <div className="flex flex-wrap justify-center">
        {/* Image */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={isInView ? { opacity: 1, scale: 1 } : {}}
          transition={{ duration: 0.8, ease: "easeOut", delay: 0.3 }}
          className="p-2 w-full lg:w-1/2"
        >
          <img src={codeImg} alt="Coding" className="rounded-2xl shadow-lg" />
        </motion.div>

        {/* Checklist */}
        <div className="pt-12 w-full lg:w-1/2">
          {updatedChecklist.map((item, index) => (
            <motion.div
              key={index}
              custom={index}
              variants={listVariants}
              initial="hidden"
              animate={isInView ? "visible" : "hidden"}
              className="flex mb-12"
            >
              <div className="text-green-400 mx-6 bg-neutral-900 h-10 w-10 p-2 flex justify-center items-center rounded-full shadow-md">
                <CheckCircle2 />
              </div>
              <div>
                <h5 className="mt-1 mb-2 text-xl font-semibold">
                  {item.title}
                </h5>
                <p className="text-md text-neutral-500">{item.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Workflow;
