import fs from "fs";
import path from "path";
import os from "os";
import { BIN_DIR, MODELS_DIR, DEFAULT_MODEL } from "./constants";
import { loadConfig } from "./config";

export function getBinPath(binName: string): string | null {
	const envPath = process.env.VOICE_PIPER_PATH;
	if (binName === "piper" && envPath && fs.existsSync(envPath)) {
		return envPath;
	}

	const system = os.platform();
	let fullBinName = binName;
	let subDir: string;

	if (system === "win32") {
		subDir = "windows";
		if (!fullBinName.endsWith(".exe")) fullBinName += ".exe";
	} else if (system === "linux") {
		subDir = "linux";
	} else {
		return null;
	}

	const binPath = path.join(BIN_DIR, subDir, fullBinName);
	return fs.existsSync(binPath) ? binPath : null;
}

export function getModelPath(): string | null {
	const envPath = process.env.VOICE_MODEL_PATH;
	if (envPath && fs.existsSync(envPath)) {
		return envPath;
	}

	const config = loadConfig();
	const modelVal = config.model || DEFAULT_MODEL;
	const modelPath = path.isAbsolute(modelVal) ? modelVal : path.join(MODELS_DIR, modelVal);

	if (fs.existsSync(modelPath)) {
		return modelPath;
	}

	// Try without extension if it fails
	const nameOnly = path.basename(modelVal);
	const namePath = path.join(MODELS_DIR, nameOnly);
	if (fs.existsSync(namePath)) {
		return namePath;
	}

	// Fallback to default
	const fallbackDefault = path.join(MODELS_DIR, DEFAULT_MODEL);
	if (fs.existsSync(fallbackDefault)) {
		return fallbackDefault;
	}

	// Final search for any .onnx
	if (fs.existsSync(MODELS_DIR)) {
		const files = fs.readdirSync(MODELS_DIR);
		const onnxFile = files.find((f) => f.endsWith(".onnx"));
		if (onnxFile) {
			return path.join(MODELS_DIR, onnxFile);
		}
	}

	return null;
}
