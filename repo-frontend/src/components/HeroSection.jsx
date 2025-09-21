import { motion } from "framer-motion";

const HeroSection = () => {
  const title = "TrueScope build tools for People".split(" ");

  return (
    <div className="flex flex-col items-center mt-6 lg:mt-20">
      {/* Title animation */}
      <h1 className="text-4xl sm:text-6xl lg:text-7xl text-center tracking-wide font-bold">
        {title.map((word, i) => (
          <motion.span
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.15, duration: 0.6, ease: "easeOut" }}
            className={
              word === "for" || word === "People"
                ? "bg-gradient-to-r from-orange-500 to-red-800 text-transparent bg-clip-text inline-block mr-2"
                : "inline-block mr-2"
            }
          >
            {word}
          </motion.span>
        ))}
      </h1>

      {/* Subtitle shimmer */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: title.length * 0.15 + 0.5, duration: 1 }}
        className="mt-10 text-lg text-center text-neutral-500 max-w-4xl relative overflow-hidden"
      >
        <span className="bg-gradient-to-r from-neutral-400 via-white to-neutral-400 bg-[length:200%_100%] bg-clip-text text-transparent animate-shimmer">
          Empowering digital citizens in India with AI-driven tools to detect,
          understand, and resist misinformation — fostering awareness beyond
          fact-checking.
        </span>
      </motion.p>

      {/* Buttons with hover animation */}
      <div className="flex justify-center my-10">
        <motion.a
          href="#workflow"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="bg-gradient-to-r from-orange-500 to-orange-800 py-3 px-4 mx-3 rounded-md text-white shadow-lg"
        >
          About Us
        </motion.a>
        <motion.a
          href="#inputform"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="py-3 px-4 mx-3 rounded-md border shadow-sm"
        >
          Upload
        </motion.a>
      </div>
    </div>
  );
};

export default HeroSection;
