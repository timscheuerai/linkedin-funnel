import { Config } from "@remotion/cli/config";

// Studio only. Renders go through scripts/render.mjs, which sets codec,
// alpha and scale per job.
Config.setOverwriteOutput(true);
