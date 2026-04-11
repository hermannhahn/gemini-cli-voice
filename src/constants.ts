import path from "path";
import os from "os";

export const BASE_DIR = path.resolve(__dirname, "..");
export const MODELS_DIR = path.join(BASE_DIR, "models");
export const BIN_DIR = path.join(BASE_DIR, "bin");
export const CONFIG_DIR = path.join(os.homedir(), ".gemini");
export const CONFIG_FILE = path.join(CONFIG_DIR, "gemini-cli-voice.json");
export const DEFAULT_MODEL = "en_US-bryce-medium.onnx";
