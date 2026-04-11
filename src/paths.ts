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

	// 1. Try absolute path
	if (path.isAbsolute(modelVal) && fs.existsSync(modelVal)) {
		return modelVal;
	}

	const nameOnly = path.basename(modelVal);
	const searchPaths: string[] = [];

	// Add custom directory from config if set
	if (config.customModelsDir && fs.existsSync(config.customModelsDir)) {
		searchPaths.push(config.customModelsDir);
	}

	// Add default local directory
	searchPaths.push(MODELS_DIR);

	// Add classic user directory ~/.voice/models
	const defaultUserDir = path.join(os.homedir(), ".voice", "models");
	if (fs.existsSync(defaultUserDir)) {
		searchPaths.push(defaultUserDir);
	}

	// 2. Try looking in all search paths for the exact model name or filename
	for (const dir of searchPaths) {
		const fullPath = path.join(dir, modelVal);
		if (fs.existsSync(fullPath)) return fullPath;

		const namePath = path.join(dir, nameOnly);
		if (fs.existsSync(namePath)) return namePath;
	}

	// 3. Fallback to default in local dir
	const fallbackDefault = path.join(MODELS_DIR, DEFAULT_MODEL);
	if (fs.existsSync(fallbackDefault)) {
		return fallbackDefault;
	}

	// 4. Final search for any .onnx in any search path
	for (const dir of searchPaths) {
		if (fs.existsSync(dir)) {
			const files = fs.readdirSync(dir);
			const onnxFile = files.find((f) => f.endsWith(".onnx"));
			if (onnxFile) {
				return path.join(dir, onnxFile);
			}
		}
	}

	return null;
}
